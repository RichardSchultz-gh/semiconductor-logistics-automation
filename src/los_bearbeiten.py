# los_bearbeiten.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from mapper import Lot, Tool
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

los_bearbeiten_bp = Blueprint('los_bearbeiten', __name__)

def check_user_session():
    return 'username' in session and session['username'] == 'user1'

@los_bearbeiten_bp.route("/main/los_bearbeiten", methods=["GET"])
def los_bearbeiten_page():
    if check_user_session():
        lots = get_all_lots()  # alle Lose abrufen
        machines = get_all_machines()  # alle Maschinen abrufen

        usern = session['username']

        return render_template("los_bearbeiten_page.html", lots=lots, machines=machines, username=usern)
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen

@los_bearbeiten_bp.route("/main/los_bearbeiten", methods=["POST"])
def bearbeite_lose():
    lot_id = request.form.get("lot_id")
    machine_id = request.form.get("machine_id")
    status = request.form.get("status")

    if not lot_id or not machine_id or not status:
        return render_template("los_bearbeiten_error.html", error_message="Bitte füllen Sie alle Felder aus")

    try:
        lot_id = int(lot_id)
        machine_id = int(machine_id)
    except ValueError:
        return render_template("los_bearbeiten_error.html", error_message="Ungültige Eingabe")

    # Datenbank aufrufen
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()

    # Los abrufen
    lot = db_session.query(Lot).filter_by(id=lot_id).first()

    # Maschine abrufen
    machine = db_session.query(Tool).filter_by(id=machine_id).first()

    if not lot:
        return render_template("los_bearbeiten_error.html", error_message="Los nicht gefunden")

    if not machine:
        return render_template("los_bearbeiten_error.html", error_message="Maschine nicht gefunden")

    # Status aktualisieren
    lot.status = status

    # Maschine aktualisieren
    lot.machine = machine

    db_session.commit()
    db_session.close()

    return redirect(url_for('los_bearbeiten.los_bearbeiten_page'))

def get_all_lots():
    # Hiermit rufen wir alle Lose aus der Datenbank ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    lots = db_session.query(Lot).all()
    db_session.close()
    return lots

def get_all_machines():
    # Hiermit rufen wir alle Maschinen aus der Datenbank ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    machines = db_session.query(Tool).all()
    db_session.close()
    return machines

def filter_lots_by_id(lot_id_filter):
    # Hiermit filtern wir Lose nach Lot-ID
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    lots = db_session.query(Lot).filter(Lot.lotid == lot_id_filter).all()
    db_session.close()
    return lots

def filter_lots_by_state(lot_state_filter):
    # Hiermit filtern wir Lose nach Zustand
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    lots = db_session.query(Lot).filter(Lot.state == lot_state_filter).all()
    db_session.close()
    return lots
