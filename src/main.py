# main.py
from flask import Blueprint, render_template,session

main_bp = Blueprint('main', __name__)

@main_bp.route('/main', methods=['GET'])
def main():
    if 'username' in session and session['username'] == 'user1':
        return render_template("main_page.html")
    else:
        return "Unauthorized", 401  # Zeigen Sie eine Fehlermeldung oder eine Umleitung an


@main_bp.route('/main2', methods=['GET'])
def main2():
    if 'username' in session and session['username'] == 'user2':
        return render_template("main_page2.html")
    else:
        return "Unauthorized", 401  # Zeigen Sie eine Fehlermeldung oder eine Umleitung an
