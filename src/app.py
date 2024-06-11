# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
# app.py (Hauptprogramm)
from flask import Flask
from login import login_bp
from main import main_bp
from los_starten import los_starten_bp
from entities import entities_bp
from los_bearbeiten import los_bearbeiten_bp
from los_bewegen import los_bewegen_bp
from Stammdaten import Stammdaten_bp
from import_data import import_data_bp
from export_data import export_data_bp
from config import config

app = Flask(__name__)
app.config.from_object(config)
app.register_blueprint(login_bp)
app.register_blueprint(main_bp)
app.register_blueprint(los_starten_bp)
app.register_blueprint(entities_bp)
app.register_blueprint(los_bearbeiten_bp)
app.register_blueprint(los_bewegen_bp)
app.register_blueprint(Stammdaten_bp)
app.register_blueprint(import_data_bp)
app.register_blueprint(export_data_bp)

if __name__ == "__main__":
    # Startet die Anwendung (je nach Konfiguration im Debug-Modus oder nicht)
    app.run(debug=config.DEBUG)
