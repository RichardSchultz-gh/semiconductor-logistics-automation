# app.py (Hauptprogramm)
from flask import Flask
from login import login_bp
from main import main_bp
from los_starten import los_starten_bp
from entities import entities_bp
from los_bearbeiten import los_bearbeiten_bp
from los_bewegen import los_bewegen_bp

app = Flask(__name__)
app.secret_key = 'Holle'
app.register_blueprint(login_bp)
app.register_blueprint(main_bp)
app.register_blueprint(los_starten_bp)
app.register_blueprint(entities_bp)
app.register_blueprint(los_bearbeiten_bp)
app.register_blueprint(los_bewegen_bp)

if __name__ == "__main__":
    app.run(debug=True)
