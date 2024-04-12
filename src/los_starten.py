# los_starten.py
from flask import Blueprint, render_template, request, redirect, url_for,session
from mapper import Lot, ProdFlow
#from timer import timer
from database_connection import get_database_url
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

los_starten_bp = Blueprint('los_starten', __name__)

# Funktion zur Überprüfung der Benutzeranmeldung
def check_user_session():
    return 'username' in session and session['username'] in ['user1']

@los_starten_bp.route("/main/los_starten", methods=["GET"])
def los_starten_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        products = get_all_products()  # alle Produkte aus ProdFlow abrufen
        lotids = get_all_lot_ids()  # alle LotIDs aus Lot abrufen

        page = request.args.get('page', 1, type=int)
        per_page = 10
        lots = get_lots_for_page(page, per_page)  # Hier implementieren Sie Ihre Logik zum Abrufen von Lots für die angeforderte Seite
        total_lots = count_total_lots()  # Hier implementieren Sie Ihre Logik zum Zählen der gesamten Lots
        has_next = page * per_page < total_lots
        last_page = total_lots // per_page + (1 if total_lots % per_page > 0 else 0)

        return render_template("los_starten_page.html", products=products, lotids=lotids, lots=lots,page=page, has_next=has_next, last_page=last_page)
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen

# wenn Submit-Button gedrückt wird, wird die Funktion los_starten() aufgerufen
@los_starten_bp.route("/main/los_starten", methods=["POST"])
def los_starten():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        # Hier implementieren Sie den Rest der los_starten-Funktion

        product = request.form.get("product_id")
        pieces = request.form.get("amount")
        duedate = request.form.get("target_date")
        customer = request.form.get("customer")
        order = request.form.get("order")

        if pieces == "":
            return render_template("los_starten_error.html", error_message="Bitte geben Sie eine Anzahl > 0 an")

        # Hiermit rufen wir die Datenbank auf
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Base = declarative_base()
        Session = sessionmaker(bind=engine)
        session = Session()
        #errechnen, wann Startdatum ist
        # dazu wird das DueDate in ein Datum umgewandelt und dann x Tage abgezogen
        # x ist die Zeit, die benötigt wird, um das Produkt zu produzieren
        # die Zeit x bekommen wir, indem wir für Produkt die beste Route raussuchen und alle Operationen zusammenzählen
        # die Zeit x wird dann von DueDate abgezogen

        #TODO: Hier muss die Zeit berechnet werden, die benötigt wird, um das Produkt zu produzieren

        duedate = datetime.datetime.strptime(duedate, "%Y-%m-%d")
        startdate = duedate - datetime.timedelta(days=31) # Std-Wert 31 Tage (ändern)
        print("Startdatum: " + str(startdate))

        #errechnen, wie viele Lose erstellt werden müssen (pieces / pieces_per_lot)
        pieces_per_lot = 10 # woher kommt die Zahl?
        lots_to_create = int(pieces) // pieces_per_lot
        if int(pieces) % pieces_per_lot != 0:
            lots_to_create += 1

        #Route herausfinden
        if product == "A100":
            route = "10-TST"
        elif product == "B200":
            route = "20-TXT"
        elif product == "2009MF":
            route = "GT2"

        # Erstellen der Lose
        lot_ids = []
        for i in range(lots_to_create):
            lot_id = generateLotID(lot_ids)
            try:
                if (int(pieces) % pieces_per_lot != 0 and i == lots_to_create-1):
                    new_lot = Lot(lotid=lot_id, priority=10, pieces=int(pieces) % pieces_per_lot, state="WAIT", product=product, route=route, customer=customer, order=order, duedate=duedate, startdate=startdate)
                else:
                    new_lot = Lot(lotid=lot_id, priority=10, pieces=pieces_per_lot, state="WAIT", product=product, route=route, customer=customer, order=order, duedate=duedate, startdate=startdate)
                session.add(new_lot)
                #jede LotID, die hier erstellt wird wird zu Liste hinzugefügt
                lot_ids.append(lot_id)
            except:
                session.rollback()
                session.close()
                return render_template("los_starten_error.html", error_message="Fehler beim Erstellen der Lose")

        session.commit()
        session.close()

        #ToDO: Fehlerbehandlung, falls falsche Eingaben gemacht wurden
        # Prüfung ob alle Lose erstellt wurden, die erstellt werden sollten
        if len(lot_ids) == lots_to_create:
            # neues timer-Objekt für jedes Los anlegen
            #for lot_id in lot_ids:
                #timer(lot_id, duedate) # Timer wird gestartet
            # Weitergeben des neu eingefügten Loses an die Funktion los_starten_success()
            return los_starten_success(lot_ids)
        else:
            # Fehlermeldung, falls nicht alle Lose erstellt werden konnten
            return render_template("los_starten_error.html", error_message="Fehler beim Hinzuügen der Lose in die Datenbank")
    else:
        # Umleitung auf die Login-Seite
        return redirect(url_for('login.login'))  # Annahme: Ihre Login-Blueprint heißt 'login'

def generateLotID(create_lot_ids):
    lot_ids = get_all_lot_ids()  # Funktion, um alle LotIDs aus der Datenbank abzurufen
    lotid='1'
    while(lotid in lot_ids or lotid in create_lot_ids):
        lotid = str(int(lotid)+1)
    #print(lotid)
    return lotid

def los_starten_success(lot_ids):
    #Anzahl Einträge in der Liste lot_ids
    if check_user_session():
        i = len(lot_ids)
        return render_template("los_starten_success.html", lot_data=lot_ids, amount=i)

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

def get_all_lots():
    # Hiermit rufen wir alle Lose aus der Datenbank ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lots = session.query(Lot).all()
    session.close()
    return lots

def get_lots_for_page(page, per_page):
    # Hiermit rufen wir alle Lose für die angeforderte Seite ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    # sortieren nach Startdatum
    lots = session.query(Lot).order_by(Lot.startdate).limit(per_page).offset((page-1)*per_page).all()
    session.close()
    return lots

def count_total_lots():
    # Hiermit zählen wir alle Lose in der Datenbank
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    total_lots = session.query(Lot).count()
    session.close()
    return total_lots
