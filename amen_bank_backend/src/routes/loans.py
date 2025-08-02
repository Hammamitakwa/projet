from flask import Blueprint, request, jsonify, session
from src.models.database import DatabaseConnection, LoanApplication

loans_bp = Blueprint('loans', __name__)

def require_auth():
    """Vérifier si l'utilisateur est authentifié"""
    if 'user_id' not in session:
        return False
    return True

@loans_bp.route('/loans/simulate', methods=['POST'])
def simulate_loan():
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        data = request.get_json()
        amount = data.get('amount')
        years = data.get('years')
        annual_rate = data.get('annual_rate', 0.07)  # Taux par défaut de 7%
        
        if not amount or not years:
            return jsonify({'error': 'Montant et durée sont obligatoires'}), 400
        
        if amount <= 0 or years <= 0:
            return jsonify({'error': 'Montant et durée doivent être positifs'}), 400
        
        # Connexion à la base de données pour utiliser la méthode de calcul
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        loan_model = LoanApplication(db)
        monthly_payment = loan_model.calculate_monthly_payment(amount, years, annual_rate)
        
        db.disconnect()
        
        total_payment = monthly_payment * years * 12
        total_interest = total_payment - amount
        
        return jsonify({
            'simulation': {
                'requested_amount': amount,
                'loan_term_years': years,
                'annual_rate': annual_rate * 100,  # Convertir en pourcentage
                'monthly_payment': round(monthly_payment, 3),
                'total_payment': round(total_payment, 3),
                'total_interest': round(total_interest, 3),
                'currency': 'TND'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@loans_bp.route('/loans/apply', methods=['POST'])
def apply_for_loan():
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        data = request.get_json()
        amount = data.get('amount')
        years = data.get('years')
        
        if not amount or not years:
            return jsonify({'error': 'Montant et durée sont obligatoires'}), 400
        
        if amount <= 0 or years <= 0:
            return jsonify({'error': 'Montant et durée doivent être positifs'}), 400
        
        user_id = session['user_id']
        
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        loan_model = LoanApplication(db)
        
        # Calculer la mensualité pour la simulation
        monthly_payment = loan_model.calculate_monthly_payment(amount, years)
        
        # Créer la demande de crédit
        application_id = loan_model.create(user_id, amount, years, monthly_payment)
        
        db.disconnect()
        
        if application_id:
            return jsonify({
                'message': 'Demande de crédit soumise avec succès',
                'application_id': application_id,
                'monthly_payment_simulation': round(monthly_payment, 3),
                'status': 'PENDING'
            }), 201
        else:
            return jsonify({'error': 'Erreur lors de la soumission de la demande'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@loans_bp.route('/loans/applications', methods=['GET'])
def get_loan_applications():
    if not require_auth():
        return jsonify({'error': 'Authentification requise'}), 401
    
    try:
        user_id = session['user_id']
        
        # Connexion à la base de données
        db = DatabaseConnection()
        if not db.connect():
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        loan_model = LoanApplication(db)
        applications = loan_model.get_by_user_id(user_id)
        
        db.disconnect()
        
        # Formatage des demandes
        formatted_applications = []
        for application in applications:
            formatted_application = {
                'application_id': application['application_id'],
                'requested_amount': float(application['requested_amount']),
                'loan_term_years': application['loan_term_years'],
                'application_date': application['application_date'].strftime('%d/%m/%Y %H:%M') if application['application_date'] else None,
                'status': application['status'],
                'monthly_payment_simulation': float(application['monthly_payment_simulation']) if application['monthly_payment_simulation'] else None,
                'currency': 'TND'
            }
            formatted_applications.append(formatted_application)
        
        return jsonify({
            'applications': formatted_applications,
            'count': len(formatted_applications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

@loans_bp.route('/loans/rates', methods=['GET'])
def get_loan_rates():
    """Retourner les taux de crédit actuels"""
    try:
        # Taux fictifs pour la démonstration
        rates = {
            'personal_loan': {
                'name': 'Crédit Personnel',
                'min_rate': 6.5,
                'max_rate': 8.5,
                'currency': 'TND'
            },
            'home_loan': {
                'name': 'Crédit Immobilier',
                'min_rate': 5.0,
                'max_rate': 7.0,
                'currency': 'TND'
            },
            'car_loan': {
                'name': 'Crédit Auto',
                'min_rate': 6.0,
                'max_rate': 8.0,
                'currency': 'TND'
            }
        }
        
        return jsonify({
            'rates': rates,
            'last_updated': '2024-01-01'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

