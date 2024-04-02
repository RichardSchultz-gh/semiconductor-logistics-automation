# login.py

from flask import Blueprint, render_template, request, jsonify

login_bp = Blueprint('login', __name__)

@login_bp.route("/login", methods=["GET"])
def login():
    return render_template("login_page.html")

@login_bp.route('/login_check', methods=['POST'])
def login_check():
    data = request.json  # Die Daten der AJAX-Anfrage erhalten
    username = data.get('username')
    password = data.get('password')

    # Hier führen Sie die Authentifizierung durch
    # Zum Beispiel, Sie überprüfen die Anmeldeinformationen in der Datenbank

    if username == 'user' and password == 'pass':
        return jsonify({'status': 'success', 'message': 'Login successful'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'})
