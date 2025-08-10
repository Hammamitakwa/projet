from transformers import pipeline
import json
import re
from datetime import datetime, timedelta
from src.models.database import get_db_connection
from src.routes.transfers import perform_transfer
from src.routes.accounts import get_accounts_data, perform_deposit, perform_withdrawal
from src.routes.loans import perform_loan_simulation, perform_loan_application

class ChatbotHandler:
    def __init__(self):
        self.generator = pipeline(
            "text-generation", 
            model="distilgpt2", 
            tokenizer="distilgpt2",
            max_new_tokens=100, 
            truncation=True
        )
        
        self.system_prompt = """Tu es un assistant bancaire intelligent d'Amen Bank, spécialisé dans les services bancaires en ligne en Tunisie. 

CONTEXTE:
- Tu travailles pour Amen Bank, une banque tunisienne moderne
- Tu communiques en français avec les clients
- Tu peux aider avec: consultation de comptes, virements, crédits, informations bancaires
- La devise principale est le Dinar Tunisien (TND)

CAPACITÉS:
- Consulter les soldes et transactions des comptes
- Effectuer des virements entre comptes
- Simuler et traiter les demandes de crédit
- Fournir des informations bancaires générales
- Répondre aux questions fréquentes

STYLE DE COMMUNICATION:
- Professionnel mais chaleureux
- Précis et informatif
- Utilise des emojis appropriés (💰, 🏦, ✅, etc.)
- Toujours proposer des actions concrètes
- Demander confirmation avant les opérations sensibles

INSTRUCTIONS IMPORTANTES:
- Toujours vérifier l'identité avant les opérations sensibles
- Expliquer clairement les étapes des procédures
- Mentionner les frais éventuels
- Respecter la confidentialité bancaire
- En cas de problème technique, orienter vers un conseiller

Réponds de manière naturelle et utile aux demandes des clients."""
        self.conversation_states = {}

    def process_message(self, message, user_session=None):
        user_id = user_session.get("user_id") if user_session else None
        
        if user_id not in self.conversation_states:
            self.conversation_states[user_id] = {"current_intent": None, "entities": {}}

        state = self.conversation_states[user_id]
        
        # Analyse initiale de l'intention et des entités
        intent = self._analyze_intent(message)
        entities = self._extract_entities(message)

        # Mettre à jour l'intention courante si une nouvelle intention claire est détectée
        if intent != 'conversation_generale' and intent != state["current_intent"]:
            state["current_intent"] = intent
            state["entities"].clear()
        
        # Fusionner les entités extraites avec celles de l'état
        state["entities"].update(entities)

        response_data = {
            'response': "",
            'intent': state["current_intent"],
            'entities': state["entities"],
            'action_required': False,
            'confidence': 0.8
        }

        if state["current_intent"] == 'virement':
            response_data = self._handle_transfer_flow(user_id, state)
        elif state["current_intent"] == 'demande_credit':
            response_data = self._handle_loan_flow(user_id, state)
        elif state["current_intent"] == 'simulation_credit':
            response_data = self._handle_loan_simulation_flow(user_id, state)
        elif state["current_intent"] == 'consultation_solde' and user_id:
            account_data = get_accounts_data(user_id)
            response_data['response'] = self._enhance_response_with_data("", account_data, 'consultation_solde')
            state["current_intent"] = None
        elif state["current_intent"] == 'consultation_transactions' and user_id:
            account_data = get_accounts_data(user_id)
            response_data['response'] = self._enhance_response_with_data("", account_data, 'consultation_transactions')
            state["current_intent"] = None
        elif state["current_intent"] == 'depot':
            response_data = self._handle_deposit_flow(user_id, state)
        elif state["current_intent"] == 'retrait':
            response_data = self._handle_withdrawal_flow(user_id, state)
        else:
            # Utiliser le générateur pour les conversations générales
            user_context = self._get_user_context(user_id) if user_id else "Utilisateur non connecté"
            full_prompt = f"{self.system_prompt}\n\nMESSAGE CLIENT: {message}\n\nCONTEXTE UTILISATEUR:\n{user_context}\n\nRéponse de l'assistant:"
            generated_text = self.generator(full_prompt, num_return_sequences=1)[0]["generated_text"]
            ai_response = generated_text.replace(full_prompt, "").strip()
            if not ai_response or len(ai_response) < 10:
                ai_response = "Je n'ai pas bien compris votre demande. Pouvez-vous reformuler ?"
            response_data['response'] = ai_response
            state["current_intent"] = None

        return response_data

    def _handle_transfer_flow(self, user_id, state):
        if not user_id:
            state["current_intent"] = None
            return {'response': 'Vous devez être connecté pour effectuer un virement. Veuillez vous connecter.', 'intent': 'virement', 'entities': {}, 'action_required': False}

        required_fields = ['montant', 'beneficiaire', 'from_account_id']
        missing_fields = [f for f in required_fields if f not in state['entities']]

        if missing_fields:
            if 'from_account_id' in missing_fields:
                account_data = get_accounts_data(user_id)
                if account_data["success"]:
                    accounts_list = "\n".join([f"- {acc['account_label']} (ID: {acc['account_id']}) - Solde: {acc['current_balance']:.2f} TND" for acc in account_data['accounts']])
                    return {'response': f"Pour effectuer un virement, j'ai besoin de savoir de quel compte vous souhaitez virer les fonds. Voici vos comptes:\n{accounts_list}\nQuel est l'ID du compte source ?", 'intent': 'virement', 'entities': state['entities'], 'action_required': True}
                else:
                    return {'response': 'Je n\'arrive pas à récupérer vos comptes pour le moment. Veuillez réessayer plus tard.', 'intent': 'virement', 'entities': state['entities'], 'action_required': False}
            elif 'montant' in missing_fields:
                return {'response': 'Quel montant souhaitez-vous virer ?', 'intent': 'virement', 'entities': state['entities'], 'action_required': True}
            elif 'beneficiaire' in missing_fields:
                return {'response': 'À qui souhaitez-vous envoyer l\'argent ? (Nom du bénéficiaire et numéro de compte)', 'intent': 'virement', 'entities': state['entities'], 'action_required': True}
        
        if 'confirmation' not in state['entities']:
            confirmation_message = (
                f"Vous souhaitez virer {state['entities']['montant']:.2f} TND "
                f"depuis le compte ID {state['entities']['from_account_id']} "
                f"vers {state['entities']['beneficiaire']}. Confirmez-vous cette opération ? (oui/non)"
            )
            state['entities']['confirmation_pending'] = True
            return {'response': confirmation_message, 'intent': 'virement', 'entities': state['entities'], 'action_required': True}
        
        if state['entities'].get('confirmation') == 'oui':
            result = perform_transfer(
                user_id,
                state['entities']['from_account_id'],
                state['entities'].get('to_account_number', 'UNKNOWN'),
                state['entities']['beneficiaire'],
                state['entities']['montant']
            )
            state["current_intent"] = None
            state["entities"].clear()
            if result['success']:
                return {'response': f"✅ {result['message']} Nouveau solde: {result['new_balance']:.2f} TND", 'intent': 'virement', 'entities': {}, 'action_required': False}
            else:
                return {'response': f"❌ Erreur lors du virement: {result['error']}", 'intent': 'virement', 'entities': {}, 'action_required': False}
        else:
            state["current_intent"] = None
            state["entities"].clear()
            return {'response': 'Virement annulé. N\'hésitez pas si vous avez d\'autres questions.', 'intent': 'virement', 'entities': {}, 'action_required': False}

    def _handle_loan_flow(self, user_id, state):
        if not user_id:
            state["current_intent"] = None
            return {'response': 'Vous devez être connecté pour effectuer une demande de crédit. Veuillez vous connecter.', 'intent': 'demande_credit', 'entities': {}, 'action_required': False}

        required_fields = ['montant', 'duree_annees']
        missing_fields = [f for f in required_fields if f not in state['entities']]

        if missing_fields:
            if 'montant' in missing_fields:
                return {'response': 'Quel montant de crédit souhaitez-vous demander ?', 'intent': 'demande_credit', 'entities': state['entities'], 'action_required': True}
            elif 'duree_annees' in missing_fields:
                return {'response': 'Sur combien d\'années souhaitez-vous étaler le remboursement ?', 'intent': 'demande_credit', 'entities': state['entities'], 'action_required': True}
        
        if 'confirmation' not in state['entities']:
            confirmation_message = (
                f"Vous souhaitez demander un crédit de {state['entities']['montant']:.2f} TND "
                f"sur {state['entities']['duree_annees']} ans. Confirmez-vous cette demande ? (oui/non)"
            )
            state['entities']['confirmation_pending'] = True
            return {'response': confirmation_message, 'intent': 'demande_credit', 'entities': state['entities'], 'action_required': True}

        if state['entities'].get('confirmation') == 'oui':
            result = perform_loan_application(
                user_id,
                state['entities']['montant'],
                state['entities']['duree_annees']
            )
            state["current_intent"] = None
            state["entities"].clear()
            if result['success']:
                return {'response': f"✅ {result['message']} Votre demande de crédit (ID: {result['application_id']}) a été soumise avec succès. Mensualité simulée: {result['monthly_payment_simulation']:.2f} TND", 'intent': 'demande_credit', 'entities': {}, 'action_required': False}
            else:
                return {'response': f"❌ Erreur lors de la demande de crédit: {result['error']}", 'intent': 'demande_credit', 'entities': {}, 'action_required': False}
        else:
            state["current_intent"] = None
            state["entities"].clear()
            return {'response': 'Demande de crédit annulée. N\'hésitez pas si vous avez d\'autres questions.', 'intent': 'demande_credit', 'entities': {}, 'action_required': False}

    def _handle_loan_simulation_flow(self, user_id, state):
        required_fields = ['montant', 'duree_annees']
        missing_fields = [f for f in required_fields if f not in state['entities']]

        if missing_fields:
            if 'montant' in missing_fields:
                return {'response': 'Quel montant souhaitez-vous simuler pour le crédit ?', 'intent': 'simulation_credit', 'entities': state['entities'], 'action_required': True}
            elif 'duree_annees' in missing_fields:
                return {'response': 'Sur combien d\'années souhaitez-vous simuler le crédit ?', 'intent': 'simulation_credit', 'entities': state['entities'], 'action_required': True}
        
        result = perform_loan_simulation(
            state['entities']['montant'],
            state['entities']['duree_annees']
        )
        state["current_intent"] = None
        state["entities"].clear()
        if result['success']:
            simulation_data = result['simulation']
            return {'response': f"✅ Simulation de crédit pour {simulation_data['requested_amount']:.2f} TND sur {simulation_data['loan_term_years']} ans: Mensualité estimée: {simulation_data['monthly_payment']:.2f} TND. Coût total: {simulation_data['total_payment']:.2f} TND (dont {simulation_data['total_interest']:.2f} TND d'intérêts).", 'intent': 'simulation_credit', 'entities': {}, 'action_required': False}
        else:
            return {'response': f"❌ Erreur lors de la simulation de crédit: {result['error']}", 'intent': 'simulation_credit', 'entities': {}, 'action_required': False}

    def _handle_deposit_flow(self, user_id, state):
        if not user_id:
            state["current_intent"] = None
            return {"response": "Vous devez être connecté pour effectuer un dépôt. Veuillez vous connecter.", "intent": "depot", "entities": {}, "action_required": False}

        required_fields = ["montant", "to_account_id"]
        missing_fields = [f for f in required_fields if f not in state["entities"]]

        if missing_fields:
            if "to_account_id" in missing_fields:
                account_data = get_accounts_data(user_id)
                if account_data["success"]:
                    accounts_list = "\n".join([f"- {acc['account_label']} (ID: {acc['account_id']}) - Solde: {acc['current_balance']:.2f} TND" for acc in account_data["accounts"]])
                    return {"response": f"Pour effectuer un dépôt, j'ai besoin de savoir sur quel compte vous souhaitez déposer les fonds. Voici vos comptes:\n{accounts_list}\nQuel est l'ID du compte de destination ?", "intent": "depot", "entities": state["entities"], "action_required": True}
                else:
                    return {"response": "Je n'arrive pas à récupérer vos comptes pour le moment. Veuillez réessayer plus tard.", "intent": "depot", "entities": state["entities"], "action_required": False}
            elif "montant" in missing_fields:
                return {"response": "Quel montant souhaitez-vous déposer ?", "intent": "depot", "entities": state["entities"], "action_required": True}
        
        if "confirmation" not in state["entities"]:
            confirmation_message = (
                f"Vous souhaitez déposer {state['entities']['montant']:.2f} TND "
                f"sur le compte ID {state['entities']['to_account_id']}. Confirmez-vous cette opération ? (oui/non)"
            )
            state["entities"]["confirmation_pending"] = True
            return {"response": confirmation_message, "intent": "depot", "entities": state["entities"], "action_required": True}
        
        if state["entities"].get("confirmation") == "oui":
            result = perform_deposit(
                state["entities"]["to_account_id"],
                state["entities"]["montant"]
            )
            state["current_intent"] = None
            state["entities"].clear()
            if result["success"]:
                return {"response": f"✅ {result['message']} Nouveau solde: {result['new_balance']:.2f} TND", "intent": "depot", "entities": {}, "action_required": False}
            else:
                return {"response": f"❌ Erreur lors du dépôt: {result['error']}", "intent": "depot", "entities": {}, "action_required": False}
        else:
            state["current_intent"] = None
            state["entities"].clear()
            return {"response": "Dépôt annulé. N'hésitez pas si vous avez d'autres questions.", "intent": "depot", "entities": {}, "action_required": False}

    def _handle_withdrawal_flow(self, user_id, state):
        if not user_id:
            state["current_intent"] = None
            return {"response": "Vous devez être connecté pour effectuer un retrait. Veuillez vous connecter.", "intent": "retrait", "entities": {}, "action_required": False}

        required_fields = ["montant", "from_account_id"]
        missing_fields = [f for f in required_fields if f not in state["entities"]]

        if missing_fields:
            if "from_account_id" in missing_fields:
                account_data = get_accounts_data(user_id)
                if account_data["success"]:
                    accounts_list = "\n".join([f"- {acc['account_label']} (ID: {acc['account_id']}) - Solde: {acc['current_balance']:.2f} TND" for acc in account_data["accounts"]])
                    return {"response": f"Pour effectuer un retrait, j'ai besoin de savoir de quel compte vous souhaitez retirer les fonds. Voici vos comptes:\n{accounts_list}\nQuel est l'ID du compte source ?", "intent": "retrait", "entities": state["entities"], "action_required": True}
                else:
                    return {"response": "Je n'arrive pas à récupérer vos comptes pour le moment. Veuillez réessayer plus tard.", "intent": "retrait", "entities": state["entities"], "action_required": False}
            elif "montant" in missing_fields:
                return {"response": "Quel montant souhaitez-vous retirer ?", "intent": "retrait", "entities": state["entities"], "action_required": True}
        
        if "confirmation" not in state["entities"]:
            confirmation_message = (
                f"Vous souhaitez retirer {state['entities']['montant']:.2f} TND "
                f"du compte ID {state['entities']['from_account_id']}. Confirmez-vous cette opération ? (oui/non)"
            )
            state["entities"]["confirmation_pending"] = True
            return {"response": confirmation_message, "intent": "retrait", "entities": state["entities"], "action_required": True}
        
        if state["entities"].get("confirmation") == "oui":
            result = perform_withdrawal(
                state["entities"]["from_account_id"],
                state["entities"]["montant"]
            )
            state["current_intent"] = None
            state["entities"].clear()
            if result["success"]:
                return {"response": f"✅ {result['message']} Nouveau solde: {result['new_balance']:.2f} TND", "intent": "retrait", "entities": {}, "action_required": False}
            else:
                return {"response": f"❌ Erreur lors du retrait: {result['error']}", "intent": "retrait", "entities": {}, "action_required": False}
        else:
            state["current_intent"] = None
            state["entities"].clear()
            return {"response": "Retrait annulé. N'hésitez pas si vous avez d'autres questions.", "intent": "retrait", "entities": {}, "action_required": False}

    def _get_user_context(self, user_id):
        """Récupère le contexte utilisateur depuis la base de données"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT username, full_name FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return "Utilisateur non trouvé"
            
            cursor.execute("""
                SELECT account_number, account_label, current_balance, account_type 
                FROM accounts WHERE user_id = %s
            """, (user_id,))
            accounts = cursor.fetchall()
            
            cursor.execute("""
                SELECT t.description, t.amount, t.debit_credit_indicator, t.transaction_date,
                       a.account_label
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.user_id = %s
                ORDER BY t.transaction_date DESC
                LIMIT 5
            """, (user_id,))
            transactions = cursor.fetchall()
            
            conn.close()
            
            context = f"Client: {user['full_name']} ({user['username']})\n\n"
            
            context += "COMPTES:\n"
            total_balance = 0
            for account in accounts:
                context += f"- {account['account_label']} ({account['account_number']}): {account['current_balance']:.3f} TND\n"
                total_balance += account['current_balance']
            
            context += f"\nSOLDE TOTAL: {total_balance:.3f} TND\n"
            
            context += "\nDERNIÈRES TRANSACTIONS:\n"
            for trans in transactions:
                sign = "+" if trans['debit_credit_indicator'] == 'C' else "-"
                context += f"- {trans['transaction_date']}: {sign}{trans['amount']:.3f} TND - {trans['description']}\n"
            
            return context
            
        except Exception as e:
            print(f"Erreur contexte utilisateur: {e}")
            return "Contexte utilisateur non disponible"

    def _analyze_intent(self, message):
        """Analyse l'intention du message avec des mots-clés"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['solde', 'combien', 'argent', 'compte']):
            return 'consultation_solde'
        elif any(word in message_lower for word in ['transaction', 'mouvement', 'historique', 'opération']):
            return 'consultation_transactions'
        elif any(word in message_lower for word in ['virement', 'virer', 'transférer', 'envoyer']):
            return 'virement'
        elif any(word in message_lower for word in ['crédit', 'prêt', 'emprunt', 'financement']):
            return 'demande_credit'
        elif any(word in message_lower for word in ["simulation", "simuler"]):
            return "simulation_credit"
        elif any(word in message_lower for word in ["depot", "déposer", "verser"]):
            return "depot"
        elif any(word in message_lower for word in ["retrait", "retirer"]):
            return "retrait"
        elif any(word in message_lower for word in ["aide", "help", "assistance", "problème"]):
            return 'assistance'
        elif any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir']):
            return 'salutation'
        else:
            return 'conversation_generale'

    def _extract_entities(self, message):
        """Extrait les entités du message"""
        entities = {}
        
        # Extraction des montants
        montant_pattern = r'(\d+(?:[.,]\d+)?)\s*(?:tnd|dinars?|dt)?'
        montants = re.findall(montant_pattern, message.lower())
        if montants:
            entities['montant'] = float(montants[0].replace(',', '.'))
        
        # Extraction des durées en années
        duree_pattern = r'(\d+)\s*(?:ans?|années?)'
        durees = re.findall(duree_pattern, message.lower())
        if durees:
            entities['duree_annees'] = int(durees[0])
        
        # Extraction des noms de bénéficiaires
        nom_pattern = r'(?:à|pour|vers)\s+([A-Za-z\s]+?)(?:\s|$|,|\.|!|\?|\d)'
        noms = re.findall(nom_pattern, message)
        if noms:
            entities['beneficiaire'] = noms[0].strip()
        
        # Extraction des numéros de compte source (ID)
        account_id_pattern = r'(?:compte|id)\s*(\d+)'
        account_ids = re.findall(account_id_pattern, message.lower())
        if account_ids:
            entities['from_account_id'] = int(account_ids[0])
            entities['to_account_id'] = int(account_ids[0]) # Pour le dépôt
        
        # Extraction des numéros de compte de destination
        to_account_number_pattern = r'(?:numéro de compte|compte)\s*(\d{8,})'
        to_account_numbers = re.findall(to_account_number_pattern, message.lower())
        if to_account_numbers:
            entities['to_account_number'] = to_account_numbers[0]
        
        # Extraction des confirmations
        if any(word in message.lower() for word in ['oui', 'confirme', 'ok', 'valider']):
            entities['confirmation'] = 'oui'
        elif any(word in message.lower() for word in ['non', 'annuler', 'stop']):
            entities['confirmation'] = 'non'
        
        return entities

    def _enhance_response_with_data(self, base_response, data, intent):
        """Améliore la réponse avec les données utilisateur"""
        if intent == 'consultation_solde' and data.get('success'):
            response = "💰 Voici vos soldes de comptes :\n\n"
            for account in data['accounts']:
                response += f"• {account['account_label']}: {account['current_balance']:.3f} TND\n"
            response += f"\n💳 Solde total: {data['total_balance']:.3f} TND"
            return response
        elif intent == 'consultation_transactions' and data.get('success'):
            response = "📊 Voici vos comptes disponibles :\n\n"
            for account in data['accounts']:
                response += f"• {account['account_label']} ({account['account_number']}): {account['current_balance']:.3f} TND\n"
            response += "\nPour voir les transactions d'un compte spécifique, indiquez-moi l'ID du compte."
            return response
        else:
            return base_response or "Je n'ai pas pu récupérer les informations demandées."

    def get_suggestions(self):
        """Retourne des suggestions de questions fréquentes""" 
        return [
            "Quel est le solde de mon compte courant ?",
            "Affiche mes dernières transactions",
            "Effectue un virement de 1000 TND à Ahmed Ben Salah",
            "Simule un crédit de 50000 TND sur 7 ans",
            "Déposer 200 TND sur mon compte épargne",
            "Retirer 50 TND de mon compte courant",
            "Quels sont vos taux de crédit actuels ?",
            "Comment faire un virement permanent ?",
            "Aide-moi à comprendre mes frais bancaires"
        ]

# Instance globale
chatbot_handler = ChatbotHandler()
