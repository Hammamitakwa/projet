from transformers import pipeline
import json
import re
from datetime import datetime
from src.models.database import get_db_connection

class ChatbotHandler:
    def __init__(self):
        # Initialisation du pipeline Hugging Face pour la génération de texte
        # Utilisation d'un modèle plus petit pour des raisons de performance et de taille
        # Pour une meilleure qualité, un modèle plus grand ou un modèle conversationnel serait préférable
        self.generator = pipeline(
            "text-generation", 
            model="distilgpt2", 
            tokenizer="distilgpt2",
            max_new_tokens=100, # Limite la longueur des réponses
            truncation=True
        )
        
        # Contexte bancaire pour l'IA (peut être utilisé pour affiner le prompt du générateur)
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

    def process_message(self, message, user_session=None):
        """Traite un message utilisateur avec Hugging Face Transformers"""
        try:
            # Récupération du contexte utilisateur
            user_id = user_session.get("user_id") if user_session else None
            user_context = self._get_user_context(user_id) if user_id else "Utilisateur non connecté"
            
            # Construction du prompt pour le générateur Hugging Face
            # Nous combinons le system_prompt et le user_prompt pour guider le modèle
            full_prompt = f"{self.system_prompt}\n\nMESSAGE CLIENT: {message}\n\nCONTEXTE UTILISATEUR:\n{user_context}\n\nRéponse de l'assistant:"

            # Appel au générateur Hugging Face
            generated_text = self.generator(full_prompt, num_return_sequences=1)[0]["generated_text"]
            
            # Le modèle peut répéter le prompt, nous extrayons seulement la réponse
            ai_response = generated_text.replace(full_prompt, "").strip()
            
            # Fallback si la réponse est vide ou ne semble pas pertinente
            if not ai_response or len(ai_response) < 10:
                ai_response = "Je n'ai pas bien compris votre demande. Pouvez-vous reformuler ?"

            # Analyse de l'intention et extraction des entités (peut être amélioré avec un modèle NLP dédié)
            intent = self._analyze_intent(message)
            entities = self._extract_entities(message)
            
            # Traitement des actions spécifiques (inchangé)
            if intent in ['consultation_solde', 'consultation_transactions'] and user_id:
                account_data = self._get_account_data(user_id)
                ai_response = self._enhance_response_with_data(ai_response, account_data, intent)
            
            return {
                'response': ai_response,
                'intent': intent,
                'entities': entities,
                'action_required': intent in ['virement', 'demande_credit'],
                'confidence': 0.8 # Confiance ajustée pour un modèle plus petit
            }
            
        except Exception as e:
            print(f"Erreur ChatBot Hugging Face: {e}")
            return {
                'response': "Je rencontre une difficulté technique momentanée avec mon cerveau. 🔧 Un conseiller peut vous aider au 71 000 000. Comment puis-je vous assister autrement ? 🏦",
                'intent': 'erreur',
                'entities': {},
                'action_required': False,
                'confidence': 0.0
            }

    def _get_user_context(self, user_id):
        """Récupère le contexte utilisateur depuis la base de données"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Informations utilisateur
            cursor.execute("SELECT username, full_name FROM users WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return "Utilisateur non trouvé"
            
            # Comptes utilisateur
            cursor.execute("""
                SELECT account_number, account_label, current_balance, account_type 
                FROM accounts WHERE user_id = %s
            """, (user_id,))
            accounts = cursor.fetchall()
            
            # Dernières transactions
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
            
            # Construction du contexte
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
        """Analyse l'intention du message avec des mots-clés (peut être amélioré avec un modèle NLP dédié)"""
        message_lower = message.lower()
        
        # Patterns d'intention
        if any(word in message_lower for word in ['solde', 'combien', 'argent', 'compte']):
            return 'consultation_solde'
        elif any(word in message_lower for word in ['transaction', 'mouvement', 'historique', 'opération']):
            return 'consultation_transactions'
        elif any(word in message_lower for word in ['virement', 'virer', 'transférer', 'envoyer']):
            return 'virement'
        elif any(word in message_lower for word in ['crédit', 'prêt', 'emprunt', 'financement', 'simulation']):
            return 'demande_credit'
        elif any(word in message_lower for word in ['aide', 'help', 'assistance', 'problème']):
            return 'assistance'
        elif any(word in message_lower for word in ['bonjour', 'salut', 'hello', 'bonsoir']):
            return 'salutation'
        elif any(word in message_lower for word in ['au revoir', 'bye', 'merci', 'à bientôt']):
            return 'au_revoir'
        else:
            return 'conversation_generale'

    def _extract_entities(self, message):
        """Extrait les entités du message (peut être amélioré avec un modèle NLP dédié)"""
        entities = {}
        
        # Extraction des montants
        montant_pattern = r'(\d+(?:[.,]\d+)?)\s*(?:tnd|dinar|dt)?'
        montants = re.findall(montant_pattern, message.lower())
        if montants:
            entities['montant'] = float(montants[0].replace(',', '.'))
        
        # Extraction des noms (pour bénéficiaires)
        nom_pattern = r'(?:à|pour)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        noms = re.findall(nom_pattern, message)
        if noms:
            entities['beneficiaire'] = noms[0]
        
        # Extraction des années pour les crédits
        annee_pattern = r'(\d+)\s*(?:ans?|années?)'
        annees = re.findall(annee_pattern, message.lower())
        if annees:
            entities['duree_annees'] = int(annees[0])
        
        return entities

    def _get_account_data(self, user_id):
        """Récupère les données de compte pour enrichir la réponse"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT account_id, account_number, account_label, current_balance, account_type
                FROM accounts WHERE user_id = %s
            """, (user_id,))
            accounts = cursor.fetchall()
            
            conn.close()
            return accounts
            
        except Exception as e:
            print(f"Erreur récupération comptes: {e}")
            return []

    def _enhance_response_with_data(self, ai_response, account_data, intent):
        """Enrichit la réponse IA avec des données réelles"""
        if not account_data:
            return ai_response
        
        if intent == 'consultation_solde':
            # Ajouter les soldes réels avec formatage moderne
            soldes_info = "\n\n💰 **Vos soldes actuels:**\n"
            total = 0
            for account in account_data:
                balance = account['current_balance']
                total += balance
                status_emoji = "✅" if balance >= 0 else "⚠️"
                soldes_info += f"{status_emoji} **{account['account_label']}**: {balance:,.3f} TND\n"
            
            soldes_info += f"\n📊 **Solde total**: {total:,.3f} TND"
            return ai_response + soldes_info
        
        elif intent == 'consultation_transactions':
            # Ajouter un lien vers l'historique complet
            trans_info = "\n\n📋 Pour consulter votre historique complet, utilisez l'onglet 'Transactions' de votre tableau de bord."
            return ai_response + trans_info
        
        return ai_response

    def get_suggestions(self):
        """Retourne des suggestions de questions fréquentes""" 
        return [
            "Quel est le solde de mon compte courant ?",
            "Affiche mes dernières transactions",
            "Effectue un virement de 1000 TND à Ahmed Ben Salah",
            "Simule un crédit de 50000 TND sur 7 ans",
            "Quels sont vos taux de crédit actuels ?",
            "Comment faire un virement permanent ?",
            "Aide-moi à comprendre mes frais bancaires"
        ]

# Instance globale
chatbot_handler = ChatbotHandler()


