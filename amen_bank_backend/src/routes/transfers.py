from flask import Blueprint, request, jsonify, session
from src.models.database import DatabaseConnection, Transfer, Account, Transaction, Beneficiary
from datetime import datetime, timedelta
from decimal import Decimal

transfers_bp = Blueprint('transfers', __name__)

def require_auth():
    """Vérifier si l'utilisateur est authentifié"""
    if 'user_id' not in session:
        return False
    return True

def perform_transfer(user_id, from_account_id, to_account_number, beneficiary_name, amount, is_scheduled=False, schedule_frequency=None):
    try:
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return {"success": False, "error": "Erreur de connexion à la base de données"}
        
        # Vérifier que le compte source appartient à l'utilisateur
        account_model = Account(db)
        accounts = account_model.get_by_user_id(user_id)
        
        source_account = None
        for acc in accounts:
            if acc["account_id"] == from_account_id:
                source_account = acc
                break
        
        if not source_account:
            db.disconnect()
            return {"success": False, "error": "Compte source non trouvé ou n'appartient pas à l'utilisateur"}
        
        # Vérifier le solde suffisant
        if float(source_account["current_balance"]) < amount:
            db.disconnect()
            return {"success": False, "error": "Solde insuffisant"}
        
        # Calculer la prochaine date d'exécution pour les virements permanents
        next_execution_date = None
        if is_scheduled and schedule_frequency:
            if schedule_frequency == "MONTHLY":
                next_execution_date = datetime.now() + timedelta(days=30)
            elif schedule_frequency == "WEEKLY":
                next_execution_date = datetime.now() + timedelta(days=7)
        
        # Créer le virement
        transfer_model = Transfer(db)
        transfer_id = transfer_model.create(
            from_account_id, to_account_number, beneficiary_name, 
            amount, is_scheduled, schedule_frequency, next_execution_date
        )
        
        if transfer_id:
            # Mettre à jour le solde du compte source
            new_balance = float(source_account["current_balance"]) - amount
            account_model.update_balance(from_account_id, new_balance)
            
            # Créer une transaction pour le débit
            transaction_model = Transaction(db)
            transaction_model.create(
                from_account_id,
                f"VIREMENT vers {beneficiary_name}",
                "VIREMENT",
                amount,
                "D"
            )
            
            # Marquer le virement comme complété
            transfer_model.update_status(transfer_id, "COMPLETED")
            
            db.disconnect()
            
            return {
                "success": True,
                "message": "Virement effectué avec succès",
                "transfer_id": transfer_id,
                "new_balance": round(new_balance, 3)
            }
        else:
            db.disconnect()
            return {"success": False, "error": "Erreur lors de la création du virement"}
            
    except Exception as e:
        return {"success": False, "error": f"Erreur serveur: {str(e)}"}

@transfers_bp.route("/transfers", methods=["POST"])
def create_transfer():
    if not require_auth():
        return jsonify({"error": "Authentification requise"}), 401
    
    data = request.get_json()
    from_account_id = data.get("from_account_id")
    to_account_number = data.get("to_account_number")
    beneficiary_name = data.get("beneficiary_name")
    amount = data.get("amount")
    is_scheduled = data.get("is_scheduled", False)
    schedule_frequency = data.get("schedule_frequency")
    
    if not all([from_account_id, to_account_number, beneficiary_name, amount]):
        return jsonify({"error": "Tous les champs obligatoires doivent être remplis"}), 400
    
    if amount <= 0:
        return jsonify({"error": "Le montant doit être positif"}), 400
    
    user_id = session["user_id"]
    
    result = perform_transfer(user_id, from_account_id, to_account_number, beneficiary_name, amount, is_scheduled, schedule_frequency)
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify({"error": result["error"]}), 500

@transfers_bp.route('/transfers', methods=['GET'])
def get_transfers():
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        user_id = session['user_id']
        
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        transfer_model = Transfer(db)
        transfers = transfer_model.get_by_user_id(user_id)
        
        db.disconnect()
        
        # Formatage des virements
        formatted_transfers = []
        for transfer in transfers:
            formatted_transfer = {
                'transfer_id': transfer['transfer_id'],
                'from_account_number': transfer['from_account_number'],
                'to_account_number': transfer['to_account_number'],
                'beneficiary_name': transfer['beneficiary_name'],
                'amount': float(transfer['amount']),
                'transfer_date': transfer['transfer_date'].strftime('%d/%m/%Y %H:%M') if transfer['transfer_date'] else None,
                'status': transfer['status'],
                'is_scheduled': transfer['is_scheduled'],
                'schedule_frequency': transfer['schedule_frequency'],
                'next_execution_date': transfer['next_execution_date'].strftime('%d/%m/%Y') if transfer['next_execution_date'] else None
            }
            formatted_transfers.append(formatted_transfer)
        
        return jsonify({
            'transfers': formatted_transfers,
            'count': len(formatted_transfers)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@transfers_bp.route('/beneficiaries', methods=['GET'])
def get_beneficiaries():
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        user_id = session['user_id']
        
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        beneficiary_model = Beneficiary(db)
        beneficiaries = beneficiary_model.get_by_user_id(user_id)
        
        db.disconnect()
        
        # Formatage des bénéficiaires
        formatted_beneficiaries = []
        for beneficiary in beneficiaries:
            formatted_beneficiary = {
                'beneficiary_id': beneficiary['beneficiary_id'],
                'full_name': beneficiary['full_name'],
                'bank_name': beneficiary['bank_name'],
                'account_number': beneficiary['account_number'],
                'rib': beneficiary['rib']
            }
            formatted_beneficiaries.append(formatted_beneficiary)
        
        return jsonify({
            'beneficiaries': formatted_beneficiaries,
            'count': len(formatted_beneficiaries)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@transfers_bp.route('/beneficiaries', methods=['POST'])
def add_beneficiary():
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        data = request.get_json()
        full_name = data.get('full_name')
        bank_name = data.get('bank_name')
        account_number = data.get('account_number')
        rib = data.get('rib')
        
        if not all([full_name, account_number]):
            return jsonify({'error': 'Nom et numéro de compte sont obligatoires'}), 400
        
        user_id = session['user_id']
        
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        beneficiary_model = Beneficiary(db)
        beneficiary_id = beneficiary_model.create(user_id, full_name, bank_name, account_number, rib)
        
        db.disconnect()
        
        if beneficiary_id:
            return jsonify({
                'message': 'Bénéficiaire ajouté avec succès',
                'beneficiary_id': beneficiary_id
            }), 201
        else:
            return jsonify({'error': 'Erreur lors de l\'ajout du bénéficiaire'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500
