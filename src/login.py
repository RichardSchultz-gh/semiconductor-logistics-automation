# login.py
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from config import config

login_bp = Blueprint('login', __name__)

# Dummy-Benutzerdaten mit gehashten Passwörtern
# aus config.py Daten lesen
users = {
    config.USER1: generate_password_hash(config.PASSWORD_USER1),
    config.USER2: generate_password_hash(config.PASSWORD_USER2),
}

@login_bp.route("/", methods=["GET"])
def login():
    """
    Zeigt die Login-Seite an
    :return: HTML-Seite mit dem Login-Formular
    """
    return render_template("login_page.html")

@login_bp.route('/login_check', methods=['POST'])
def login_check():
    """
    Überprüft die Benutzerdaten und setzt die Sitzungsinformationen
    :return: JSON-Antwort mit Status und Nachricht
    """
    data = request.json
    #print(data)  # Debugging-Anweisung
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'})

    username = data.get('username')
    password = data.get('password')
    #print("Username:", username)  # Debugging-Anweisung
    #print("Password:", password)  # Debugging-Anweisung

    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username or password missing'})

    # Authentifizierung überprüfen
    if username in users and check_password_hash(users[username], password):
        # Sitzungsinformationen setzen
        session['username'] = username
        return jsonify({'status': 'success', 'message': 'Login successful', 'user': username})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'})

@login_bp.route('/logout', methods=['GET'])
def logout():
    """
    Löscht die Sitzungsinformationen und leitet den Benutzer zur Login-Seite weiter
    :return: Weiterleitung zur Login-Seite
    """
    # Session löschen, um den Benutzer auszuloggen
    session.pop('username', None)
    # Weiterleitung zur Login-Seite
    return redirect(url_for('login.login'))
