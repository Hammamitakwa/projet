from flask import Blueprint, request, jsonify, session
from src.models.database import DatabaseConnection, User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/logout", methods=["POST"])
def logout():
    print("--- Début de la fonction logout ---")
    session.clear()
    print("Déconnexion réussie.")
    return jsonify({"message": "Déconnexion réussie"}), 200

@auth_bp.route("/check-session", methods=["GET"])
def check_session():
    print("--- Début de la fonction check_session ---")
    if "user_id" in session:
        print(f"Session active pour l'utilisateur: {session['user_id']}")
        return jsonify({
            "authenticated": True,
            "user_id": session["user_id"],
            "username": session["username"]
        }), 200
    else:
        print("Aucune session active.")
        return jsonify({"authenticated": False}), 200

