# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
# backup.py
import subprocess
import os
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from database_connection import database_connection, database_disconnection
from flask import Blueprint, render_template, jsonify

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/main/backup', methods=['GET'])
def backup_page():
    last_backup_info = get_last_backup_info()
    return render_template('backup.html', last_backup_info=last_backup_info)

@backup_bp.route('/main/backup', methods=['POST'])
def initiate_backup():
    try:
        session = database_connection()
        result = session.execute(text("SELECT 1"))
        logging.info("Datenbankverbindung erfolgreich.")
        print("Datenbankverbindung erfolgreich.")
        database_disconnection(session)
    
        # Absoluter Pfad zum Shell-Skript, Daten ändern
        shell_script_path = r'C:\xxx\i04-projekt-frau-holle-main\src\backup.sh'
        
        # Überprüfen, ob das Shell-Skript existiert
        if not os.path.exists(shell_script_path):
            raise FileNotFoundError(f"Das Shell-Skript '{shell_script_path}' wurde nicht gefunden.")
        
        # Absoluter Pfad zu Git Bash 
        git_bash_path = r'C:\Program Files\Git\bin\bash.exe'

        # Überprüfen, ob Git Bash existiert
        if not os.path.exists(git_bash_path):
            raise FileNotFoundError(f"Git Bash wurde nicht gefunden unter '{git_bash_path}'")

        # Aufruf des Shell-Skripts mit Git Bash
        result = subprocess.run([git_bash_path, shell_script_path], check=True, capture_output=True, text=True)
        logging.info("Backup erfolgreich gestartet.")
        print("Backup erfolgreich gestartet.")
        
        last_backup_info = get_last_backup_info()
        print("Backup erfolgreich abgeschlossen.")
        return jsonify({'message': "Backup erfolgreich abgeschlossen.", 'path': last_backup_info['path'], 'timestamp': last_backup_info['timestamp']})

    except subprocess.CalledProcessError as e:
        logging.error(f"Ein Fehler ist aufgetreten: {e.stderr}")
        print(f"Ein Fehler ist aufgetreten: {e.stderr}")
        return jsonify({'message': f"Ein Fehler ist aufgetreten: {e.stderr}"}), 500

    except Exception as e:
        logging.error(f"Ein Fehler ist aufgetreten: {e}")
        print(f"Ein Fehler ist aufgetreten: {e}")
        return jsonify({'message': f"Ein Fehler ist aufgetreten: {e}"}), 500

        # Daten ändern    
logging.basicConfig(filename=r'C:\xxx\\i04-projekt-frau-holle-main\backup.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_last_backup_info():
    try:
        backup_dir = r'C:\Users\yanni\Desktop\Projekt_test\projekt\i04-projekt-frau-holle-main\src\backup'
        files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if os.path.isfile(os.path.join(backup_dir, f))]
        latest_file = max(files, key=os.path.getctime)
        return {
            'timestamp': datetime.fromtimestamp(os.path.getctime(latest_file)).strftime('%Y-%m-%d %H:%M:%S'),
            'path': latest_file
        }
    except ValueError:  # Wenn kein Backup gefunden wurde
        return {
            'timestamp': "Nie",
            'path': ""
        }

if __name__ == "__main__":
    initiate_backup()
