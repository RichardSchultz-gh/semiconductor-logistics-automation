from flask import Blueprint, render_template, request, redirect, url_for, session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mapper import Entities
from database_connection import get_database_url
from config import config

entities_bp = Blueprint('entities', __name__, url_prefix='/main')

DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Funktion zur Überprüfung der Benutzeranmeldung
def check_user_session():
    return 'username' in session and session['username'] in [config.USER1, config.USER2]

@entities_bp.route("/entities", methods=["GET", "POST"])
def entities_index():
    # Überprüfen, ob der Benutzer angemeldet ist und die erforderliche Berechtigung hat
    if check_user_session():
        show_data = False
        if request.method == "POST" and "show_data" in request.form:
            show_data = True

        session_e = Session()
        records = session_e.query(Entities).all()
        session_e.close()
        usern=session['username']

        return render_template("entities_page.html", records=records, show_data=show_data, username=usern)
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen


@entities_bp.route("/entities/insert", methods=["POST"])
def entities_insert_data():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        # Führen Sie die Einfügeoperation nur aus, wenn der Benutzer angemeldet ist
        entity = request.form.get("entity")
        class_i = request.form.get("class")
        enabled = request.form.get("enabled", 0)
        note = request.form.get("note")
        state = request.form.get("state")

        session = Session()
        new_entity = Entities(entity=entity, class_=class_i, enabled=enabled, note=note, state=state)
        session.add(new_entity)
        session.commit()
        session.close()

        return redirect(url_for("entities.entities_index"))
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen


@entities_bp.route("/entities/delete", methods=["POST"])
def entities_delete_data():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        # Führen Sie die Löschoperation nur aus, wenn der Benutzer angemeldet ist
        entity = request.form.get("d_entity")
        class_i = request.form.get("d_class")
        enabled = request.form.get("d_enabled", 0)
        note = request.form.get("d_note")
        state = request.form.get("d_state")

        session = Session()
        session.query(Entities).filter(
            Entities.entity == entity,
            Entities.class_ == class_i,
            Entities.enabled == enabled,
            Entities.note == note,
            Entities.state == state
        ).delete()
        session.commit()
        session.close()

        return redirect(url_for("entities.entities_index"))
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen
