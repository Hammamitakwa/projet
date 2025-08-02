import os
import sys
# DON\"T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
from src.routes.auth import auth_bp
from src.routes.accounts import accounts_bp
from src.routes.transfers import transfers_bp
from src.routes.loans import loans_bp
from src.routes.chatbot import chatbot_bp
from src.models.database import DatabaseConnection, User # Import User and DatabaseConnection

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Activer CORS pour toutes les routes (une seule fois)
CORS(app, supports_credentials=True)

# Enregistrer les blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(accounts_bp, url_prefix='/api')
app.register_blueprint(transfers_bp, url_prefix='/api')
app.register_blueprint(loans_bp, url_prefix='/api')
app.register_blueprint(chatbot_bp, url_prefix='/api')

# Route de connexion déplacée ici pour le test
@app.route("/login", methods=["POST"])
def login():
    print("--- Début de la fonction login (dans main.py) ---")
    try:
        data = request.get_json()
        print(f"Requête JSON reçue: {data}")
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            print("Erreur: Nom d'utilisateur ou mot de passe manquant.")
            return jsonify({'error': 'Nom d\'utilisateur et mot de passe requis'}), 400
        
        print("Tentative de connexion à la base de données...")
        db = DatabaseConnection()
        if not db.connect():
            print("Erreur: Impossible de se connecter à la base de données.")
            return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
        
        print(f"Authentification de l'utilisateur: {username}")
        user_model = User(db)
        user = user_model.authenticate(username, password)
        
        if user:
            print(f"Utilisateur {username} authentifié avec succès.")
            # Stocker l'ID utilisateur dans la session
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            
            db.disconnect()
            print("Connexion réussie. Envoi de la réponse.")
            return jsonify({
                'message': 'Connexion réussie',
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user['email']
                }
            }), 200
        else:
            db.disconnect()
            print("Nom d'utilisateur ou mot de passe incorrect.")
            return jsonify({'error': 'Nom d\'utilisateur ou mot de passe incorrect'}), 401
            
    except Exception as e:
        print(f"--- Erreur inattendue dans login (main.py): {str(e)} ---")
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

# Nouvelle route de test (déplacée sous /api)
@app.route('/api/test_post', methods=['POST'])
def test_post():
    try:
        data = request.get_json()
        return jsonify({'message': 'Requête POST reçue avec succès!', 'data': data}), 200
    except Exception as e:
        return jsonify({'error': f'Erreur lors du test POST: {str(e)}'}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)