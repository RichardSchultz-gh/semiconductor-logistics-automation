# los_starten.py
from flask import Blueprint, render_template, request, redirect, url_for
from mapper import Lot, ProdFlow
from database_connection import get_database_url
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

los_starten_bp = Blueprint('los_starten', __name__)

@los_starten_bp.route("/los_starten", methods=["GET"])
def los_starten_page():
    lot_ids = get_all_lot_ids()  # Funktion, um alle LotIDs aus der Datenbank abzurufen
    products = get_all_products() # alle Produkte aus ProdFlow abrufen

    return render_template("los_starten_page.html", lot_ids=lot_ids, products=products)

# wenn Submit-Button gedrückt wird, wird die Funktion los_starten() aufgerufen
@los_starten_bp.route("/los_starten", methods=["POST"])
def los_starten():
    product = request.form.get("product_id")
    lot_id = request.form.get("lot_id")
    pieces = request.form.get("amount")
    duedate = request.form.get("target_date")
    # Hiermit rufen wir die Datenbank auf
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    # Hiermit fügen wir ein neues Los in die Datenbank ein
    new_lot = Lot(lotid=lot_id, priority=1, pieces=pieces, state="WAIT", product=product, route="1", oper="1", customer="1", order="1", duedate=duedate)
    session.add(new_lot)
    session.commit()
    session.close()

    #ToDO: Fehlerbehandlung, wenn Los bereits existiert etc.!

    # Weitergeben des neu eingefügten Loses an die Funktion los_starten_success()
    return los_starten_success(lot_id)

def los_starten_success(lot_id):
    # Zugriff auf LotID um ihre Daten an die Seite zu übergeben
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lot = session.query(Lot).filter(Lot.lotid == lot_id).first()
    session.close()
    
    product=lot.product
    pieces=lot.pieces
    duedate=lot.duedate

    # Weiterleitung auf Seite, die erfolgreiches Starten des Loses bestätigt
    return render_template("los_starten_success.html", lot_id=lot_id, product=product, pieces=pieces, duedate=duedate)

def get_all_lot_ids():
    # Hiermit rufen wir alle LotIDs aus der Datenbank ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lot_ids = session.query(Lot.lotid).all()
    # Entfernen von (LotID,) zu LotID
    lot_ids = [lot_id[0] for lot_id in lot_ids]
    session.close()
    return lot_ids

def get_all_products():
    # Hiermit rufen wir alle Produkte aus der Datenbank ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    products = session.query(ProdFlow.product).distinct().all()
    products = [product[0] for product in products]
    session.close()
    return products