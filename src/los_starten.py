# los_starten.py
from flask import Blueprint, render_template, request, redirect, url_for,session
from mapper import Lot, ProdFlow, Tool
#from timer import timer
from database_connection import get_database_url
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

los_starten_bp = Blueprint('los_starten', __name__)

# Funktion zur Überprüfung der Benutzeranmeldung
def check_user_session():
    return 'username' in session and session['username'] in ['user1', 'user2']

@los_starten_bp.route("/main/los_starten", methods=["GET"])
def los_starten_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        products = get_all_products()  # alle Produkte aus ProdFlow abrufen
        lotids = get_all_lot_ids()  # alle LotIDs aus Lot abrufen
        tools = get_all_tools()  # alle Werkzeuge aus Tool abrufen

         # Lot-ID- und Zustandsfilterung
        lot_id_filter = request.args.get('lot_id_f')
        lot_state_filter = request.args.get('lot_state_f')
        lot_tool_filter = request.args.get('lot_tool_f')

        if lot_id_filter:
            lots = filter_lots_by_id(lot_id_filter)
        elif lot_state_filter:
            lots = filter_lots_by_state(lot_state_filter)
        elif lot_tool_filter:
            lots = filter_lots_by_tool(lot_tool_filter)
        else:
            lots = get_all_lots()  # Hier implementieren Sie Ihre Logik zum Abrufen von Lots für die angeforderte Seite

        usern = session['username']

        return render_template("los_starten_page.html", products=products, lotids=lotids, lots=lots, tools=tools, username=usern)
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen

@los_starten_bp.route("/main/los_starten", methods=["POST"])
def los_starten():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        product = request.form.get("product_id")
        pieces = request.form.get("amount")
        duedate = request.form.get("target_date")
        customer = request.form.get("customer")
        order = request.form.get("order")
        timeint1 = request.form.get("time_interval1")
        timeint2 = request.form.get("time_interval2")

        if pieces == "":
            return render_template("los_starten_error.html", error_message="Bitte geben Sie eine Anzahl > 0 an", id=1)
        
        if duedate < datetime.datetime.now().strftime("%Y-%m-%d"):
            return render_template("los_starten_error.html", error_message="Bitte geben Sie ein in der Zukunft liegendes Datum an", id=1)
        
        if timeint1 < datetime.datetime.now().strftime("%Y-%m-%d"):
            return render_template("los_starten_error.html", error_message="Bitte geben Sie ein in der Zukunft liegendes Startdatum an", id=1)
        
        if timeint2 < datetime.datetime.now().strftime("%Y-%m-%d"):
            return render_template("los_starten_error.html", error_message="Bitte geben Sie ein in der Zukunft liegendes Enddatum an",id=1)
        
        if timeint1 > timeint2:
            return render_template("los_starten_error.html", error_message="Das Startdatum muss vor dem Enddatum liegen",id=1)
        
        if timeint2 > duedate:
            return render_template("los_starten_error.html", error_message="Das Enddatum, in welchem Lose starten, muss vor dem Fälligkeitsdatum dieser Lose liegen",id=1)

        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        #errechnen, wie viele Lose erstellt werden müssen (pieces / pieces_per_lot)
        pieces_per_lot = 25 #Festwert
        lots_to_create = int(pieces) // pieces_per_lot
        if int(pieces) % pieces_per_lot != 0:
            lots_to_create += 1

        #1. Route des Produkts ermitteln
        route = session.query(ProdFlow.route).filter(ProdFlow.product == product, ProdFlow.seq == 1).first()
        route = route[0]

        # Erstellen der Lose
        lot_ids = []
        for i in range(lots_to_create):
            lot_id = generateLotID(lot_ids, customer, order)
            try:
                if (int(pieces) % pieces_per_lot != 0 and i == lots_to_create-1):
                    new_lot = Lot(lotid=lot_id, priority=10, pieces=int(pieces) % pieces_per_lot, state="INIT", product=product, route=route, customer=customer, order=order, duedate=duedate)
                else:
                    new_lot = Lot(lotid=lot_id, priority=10, pieces=pieces_per_lot, state="INIT", product=product, route=route, customer=customer, order=order, duedate=duedate)
                session.add(new_lot)
                #jede LotID, die hier erstellt wird wird zu Liste hinzugefügt
                lot_ids.append(lot_id)
            except:
                session.rollback()
                session.close()
                return render_template("los_starten_error.html", error_message="Fehler beim Erstellen der Lose", id=1)

        session.commit()
        session.close()

        #ToDO: Fehlerbehandlung, falls falsche Eingaben gemacht wurden oder falls Datenbank nicht erreichbar ist
        
        # errechnen von Zeitabstand zwischen den zwei eingegebenen date-time-Daten time_interval1 und time_interval2
        # Überprüfen, ob die Formulardaten vorhanden sind
        if timeint1 is None or timeint2 is None:
            return render_template("los_starten_error.html", error_message="Bitte geben Sie Start- und Endzeit für das Starten der Lose an", id=1)

        # Datumszeichenfolgen in datetime-Objekte umwandeln
        timeint1 = datetime.datetime.strptime(timeint1, "%Y-%m-%d")
        timeint2 = datetime.datetime.strptime(timeint2, "%Y-%m-%d")
        time_interval = timeint2 - timeint1 # Zeitabstand zwischen den zwei eingegebenen date-time-Daten
        # Zeitabstand in Stunden umrechnen
        time_interval = time_interval.total_seconds() / 3600 + 24 #letzter Tag wird auch berücksichtigt
        # Anzahl der Stunden bis nächstes Los gestartet wird
        time_next_lot = time_interval/lots_to_create

        # Prüfung ob alle Lose erstellt wurden, die erstellt werden sollten
        if len(lot_ids) == lots_to_create:
            startTime=timeint1

            DATABASE_URL = get_database_url()
            engine = create_engine(DATABASE_URL)
            Base = declarative_base()
            Session = sessionmaker(bind=engine)
            session = Session()

            for lot_id in lot_ids:
                # Startzeit des aktuellen Loses in der Datenbank speichern
                lot = session.query(Lot).filter(Lot.lotid == lot_id).first()
                lot.startdate = startTime
                session.commit()

                #startTimer(lotid)

                startTime = startTime + datetime.timedelta(hours=time_next_lot) # Startzeit für das nächste Los wird berechnet (ungenau auf Stunden gerundet)

            session.close()

            return los_starten_success(lot_ids)
        else:
            # Fehlermeldung, falls nicht alle Lose erstellt werden konnten
            return render_template("los_starten_error.html", error_message="Fehler beim Hinzuügen der Lose in die Datenbank", id=1)
    else:
        # Umleitung auf die Login-Seite
        return redirect(url_for('login.login'))

def generateLotID(create_lot_ids, customer, order):
    customer_order_code = customer[:2].upper() + order[:2].upper()
    lot_ids = get_all_lot_ids()  # Funktion, um alle LotIDs aus der Datenbank abzurufen
    lotid='1'
    lotid_with_name = customer_order_code + '-' + lotid
    while(lotid_with_name in lot_ids or lotid_with_name in create_lot_ids):
        lotid = str(int(lotid)+1)
        lotid_with_name = customer_order_code + '-' + lotid

    return lotid_with_name

def los_starten_success(lot_ids):
    #Anzahl Einträge in der Liste lot_ids
    if check_user_session():
        i = len(lot_ids)
        return render_template("los_starten_success.html", lot_data=lot_ids, amount=i, id=1, lot_id_1='')

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

def filter_lots_by_id(lot_id_filter):
    # Hiermit filtern wir Lose nach Lot-ID
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lots = session.query(Lot).filter(Lot.lotid==lot_id_filter).all()
    session.close()
    return lots

def filter_lots_by_state(lot_state_filter):
    # Hiermit filtern wir Lose nach Zustand
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lots = session.query(Lot).filter(Lot.state==lot_state_filter).all()
    session.close()
    return lots

def filter_lots_by_tool(lot_tool_filter):
    # Hiermit filtern wir Lose nach Werkzeug
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lots = session.query(Lot).filter(Lot.disptool==lot_tool_filter).all()
    session.close()
    return lots

def get_all_tools():
    # Hiermit rufen wir alle Werkzeuge aus der Datenbank ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    tools = session.query(Tool.tool).all()
    tools = [tool[0] for tool in tools]
    session.close()
    return tools

@los_starten_bp.route("/main/manuell_starten", methods=["POST"])
def manuell_starten():
    print("Manuell Starten")
    # Hier implementieren Sie Ihre Logik zum manuellen Starten eines Loses
    lotid=request.form.get("lot_id")
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lot = session.query(Lot).filter(Lot.lotid == lotid).first()
    if(lot.state == "INIT"):
        lot.state = "WAIT"
        lot.startdate = datetime.datetime.now()
        #timer(lotid, lot.duedate, datetime.datetime.now()) # Timer wird gestartet
        session.commit()
        session.close()
        return render_template("los_starten_success.html", lot_data='', amount=1, id=2, lot_id_1=lotid)
    else:
        session.close()
        return render_template("los_starten_error.html", error_message="Das Los kann nicht manuell gestartet werden, da es bereits gestartet wurde oder beendet ist.", id=2)

