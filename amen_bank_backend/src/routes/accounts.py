from flask import Blueprint, request, jsonify, session
from src.models.database import DatabaseConnection, Account, Transaction

accounts_bp = Blueprint('accounts', __name__)

def require_auth():
    """Vérifier si l'utilisateur est authentifié"""
    if 'user_id' not in session:
        return False
    return True

@accounts_bp.route('/accounts', methods=['GET'])
def get_accounts():
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        user_id = session['user_id']
        
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        account_model = Account(db)
        accounts = account_model.get_by_user_id(user_id)
        
        db.disconnect()
        
        # Formatage des données pour l'affichage
        formatted_accounts = []
        total_balance = 0
        
        for account in accounts:
            formatted_account = {
                'account_id': account['account_id'],
                'account_number': account['account_number'],
                'account_label': account['account_label'],
                'currency': account['currency'],
                'current_balance': float(account['current_balance']),
                'account_type': account['account_type'],
                'date_opened': account['date_opened'].strftime('%d/%m/%Y') if account['date_opened'] else None
            }
            formatted_accounts.append(formatted_account)
            total_balance += float(account['current_balance'])
        
        return jsonify({
            'accounts': formatted_accounts,
            'total_balance': round(total_balance, 3),
            'currency': 'TND'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@accounts_bp.route('/accounts/<int:account_id>/balance', methods=['GET'])
def get_account_balance(account_id):
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        user_id = session['user_id']
        
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        account_model = Account(db)
        accounts = account_model.get_by_user_id(user_id)
        
        # Vérifier que le compte appartient à l'utilisateur
        account = None
        for acc in accounts:
            if acc['account_id'] == account_id:
                account = acc
                break
        
        if not account:
            db.disconnect()
            return jsonify({'error': 'Compte non trouvé'}), 404
        
        db.disconnect()
        
        return jsonify({
            'account_number': account['account_number'],
            'account_label': account['account_label'],
            'current_balance': float(account['current_balance']),
            'currency': account['currency']
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@accounts_bp.route('/accounts/<int:account_id>/transactions', methods=['GET'])
def get_account_transactions(account_id):
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        user_id = session['user_id']
        limit = request.args.get('limit', 50, type=int)
        
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        # Vérifier que le compte appartient à l'utilisateur
        account_model = Account(db)
        accounts = account_model.get_by_user_id(user_id)
        
        account_exists = any(acc['account_id'] == account_id for acc in accounts)
        if not account_exists:
            db.disconnect()
            return jsonify({'error': 'Compte non trouvé'}), 404
        
        transaction_model = Transaction(db)
        transactions = transaction_model.get_by_account_id(account_id, limit)
        
        db.disconnect()
        
        # Formatage des transactions
        formatted_transactions = []
        for transaction in transactions:
            formatted_transaction = {
                'transaction_id': transaction['transaction_id'],
                'transaction_date': transaction['transaction_date'].strftime('%d/%m/%Y %H:%M') if transaction['transaction_date'] else None,
                'description': transaction['description'],
                'transaction_type': transaction['transaction_type'],
                'amount': float(transaction['amount']),
                'debit_credit_indicator': transaction['debit_credit_indicator'],
                'piece_number': transaction['piece_number'],
                'value_date': transaction['value_date'].strftime('%d/%m/%Y') if transaction['value_date'] else None
            }
            formatted_transactions.append(formatted_transaction)
        
        return jsonify({
            'transactions': formatted_transactions,
            'count': len(formatted_transactions)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

