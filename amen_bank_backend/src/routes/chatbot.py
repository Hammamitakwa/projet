from flask import Blueprint, request, jsonify, session
from src.chatbot.chatbot_handler import chatbot_handler

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal pour le chatbot"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message vide'}), 400
        
        # Traiter le message avec le chatbot
        response = chatbot_handler.process_message(message, session)
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'response': f"Désolé, une erreur s'est produite : {str(e)}",
            'intent': 'error',
            'entities': {}
        }), 500

@chatbot_bp.route('/chat/context', methods=['GET'])
def get_chat_context():
    """Obtenir le contexte de la conversation"""
    try:
        context = {
            'authenticated': 'user_id' in session,
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'available_actions': [
                'consultation_solde',
                'consultation_transactions',
                'virement',
                'simulation_credit',
                'demande_credit',
                'assistance'
            ]
        }
        
        return jsonify(context), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@chatbot_bp.route('/chat/suggestions', methods=['GET'])
def get_suggestions():
    """Obtenir des suggestions de commandes"""
    try:
        suggestions = [
            "Quel est le solde de mon compte courant ?",
            "Affiche mes dernières transactions",
            "Effectue un virement ",
            "Simule un crédit ",
            "Quels sont vos taux de crédit ?",
            "Aide"
        ]
        
        # Adapter les suggestions selon l'état de connexion
        if 'user_id' not in session:
            suggestions = [
                "Bonjour",
                "Aide",
                "Quels sont vos taux de crédit ?",
                "Comment faire un virement ?",
                "Quels documents pour un crédit ?"
            ]
        
        return jsonify({'suggestions': suggestions}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@chatbot_bp.route('/chat/faq', methods=['GET'])
def get_faq():
    """Obtenir les questions fréquemment posées"""
    try:
        faq = [
            {
                'question': 'Quels sont vos taux de crédit en dinars ?',
                'answer': 'Nos taux de crédit varient selon le type :\n• Crédit Personnel : 6.5% à 8.5%\n• Crédit Immobilier : 5.0% à 7.0%\n• Crédit Auto : 6.0% à 8.0%\n\nPour une simulation personnalisée, demandez-moi de simuler un crédit.'
            },
            {
                'question': 'Quels documents sont nécessaires pour un prêt ?',
                'answer': 'Pour une demande de crédit, vous devez fournir :\n• Pièce d\'identité\n• Justificatifs de revenus (3 derniers bulletins de salaire)\n• Relevés bancaires (3 derniers mois)\n• Justificatif de domicile\n• Selon le projet : devis, compromis de vente, etc.'
            },
            {
                'question': 'Comment effectuer un virement ?',
                'answer': 'Pour effectuer un virement, dites-moi :\n• Le montant à transférer\n• Le nom du bénéficiaire\n• Le numéro de compte de destination\n\nJe vous guiderai ensuite pour la validation sécurisée.'
            },
            {
                'question': 'Comment consulter mon solde ?',
                'answer': 'Demandez-moi simplement :\n• "Quel est le solde de mon compte ?"\n• "Affiche mon solde"\n• "Combien j\'ai sur mon compte ?"\n\nJe vous afficherai le solde de tous vos comptes.'
            },
            {
                'question': 'Comment voir mes transactions ?',
                'answer': 'Pour consulter vos transactions, demandez :\n• "Affiche mes transactions"\n• "Historique de mes opérations"\n• "Dernières transactions"\n\nJe vous montrerai vos opérations récentes.'
            }
        ]
        
        return jsonify({'faq': faq}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
