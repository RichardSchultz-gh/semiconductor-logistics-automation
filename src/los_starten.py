# los_starten.py
from flask import Blueprint, render_template, request, redirect, url_for,session
from mapper import Lot, ProdFlow, Tool, Workflow
from database_connection import get_database_url
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config
import datetime

los_starten_bp = Blueprint('los_starten', __name__)

# Funktion zur Überprüfung der Benutzeranmeldung
def check_user_session():
    return 'username' in session and session['username'] in [config.USER1, config.USER2]

@los_starten_bp.route("/main/los_starten", methods=["GET"])
def los_starten_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        products = get_all_products()  # alle Produkte aus ProdFlow abrufen
        lotids = get_all_lot_ids()  # alle LotIDs aus Lot abrufen
        tools = get_all_tools()  # alle Maschinen aus Tool abrufen

         # Lot-ID- und Zustandsfilterung
        lot_id_filter = request.args.get('lot_id_f')
        lot_state_filter = request.args.get('lot_state_f')
        lot_tool_filter = request.args.get('lot_tool_f')

        # Sortierung
        sorttype = request.args.get('sort')

        sessiond = database_connection()

        lots = []
        if lot_id_filter and not lot_state_filter and not lot_tool_filter:
            lots = sessiond.query(Lot).filter(Lot.lotid == lot_id_filter).order_by(get_sort_order(Lot, sorttype)).all()
        elif lot_state_filter and not lot_id_filter and not lot_tool_filter:
            lots = sessiond.query(Lot).filter(Lot.state == lot_state_filter).order_by(get_sort_order(Lot, sorttype)).all()
        elif lot_tool_filter and not lot_id_filter and not lot_state_filter:
            lots = sessiond.query(Lot).filter(Lot.disptool == lot_tool_filter).order_by(get_sort_order(Lot, sorttype)).all()
        elif lot_id_filter and lot_state_filter and not lot_tool_filter:
            lots = sessiond.query(Lot).filter(Lot.lotid == lot_id_filter, Lot.state == lot_state_filter).order_by(get_sort_order(Lot, sorttype)).all()
        elif lot_id_filter and lot_tool_filter and not lot_state_filter:
            lots = sessiond.query(Lot).filter(Lot.lotid == lot_id_filter, Lot.disptool == lot_tool_filter).order_by(get_sort_order(Lot, sorttype)).all()
        elif lot_state_filter and lot_tool_filter and not lot_id_filter:
            lots = sessiond.query(Lot).filter(Lot.state == lot_state_filter, Lot.disptool == lot_tool_filter).order_by(get_sort_order(Lot, sorttype)).all()
        elif lot_id_filter and lot_state_filter and lot_tool_filter:
            lots = sessiond.query(Lot).filter(Lot.lotid == lot_id_filter, Lot.state == lot_state_filter, Lot.disptool == lot_tool_filter).order_by(get_sort_order(Lot, sorttype)).all()
        else:
            lots = sessiond.query(Lot).order_by(get_sort_order(Lot, sorttype)).all()

        usern = session['username']

        return render_template("los_starten_page.html", products=products, lotids=lotids, lots=lots, tools=tools, username=usern)
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen

@los_starten_bp.route("/main/los_starten", methods=["POST"])
def los_starten():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        # Formulardaten abrufen
        product = request.form.get("product_id")
        pieces = request.form.get("amount")
        duedate = request.form.get("target_date")
        customer = request.form.get("customer")
        order = request.form.get("order")
        timeint1 = request.form.get("time_interval1")
        timeint2 = request.form.get("time_interval2")

        # Konsistenzprüfungen
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

        # Datenbankverbindung herstellen
        session = database_connection()

        #errechnen, wie viele Lose erstellt werden müssen (pieces / pieces_per_lot)
        pieces_per_lot = 25 # Festwert nach Absprache
        lots_to_create = int(pieces) // pieces_per_lot
        if int(pieces) % pieces_per_lot != 0:
            lots_to_create += 1

        # Erstellen der Lose (abhängig von der Anzahl der zu erstellenden Lose)
        lot_ids = []
        for i in range(lots_to_create):
            # Erstellen der LotID
            lot_id = generateLotID(lot_ids, customer, order)
            try:
                # wenn die Anzahl der zu erstellenden Lose nicht durch pieces_per_lot teilbar ist, wird das letzte Los erstellt
                if (int(pieces) % pieces_per_lot != 0 and i == lots_to_create-1):
                    new_lot = Lot(lotid=lot_id, priority=10, pieces=int(pieces) % pieces_per_lot, state="INIT", product=product, customer=customer, order=order, duedate=duedate)
                # sonst wird jedes Los mit pieces_per_lot erstellt (standardmäßig 25 Stücke pro Los)
                else:
                    new_lot = Lot(lotid=lot_id, priority=10, pieces=pieces_per_lot, state="INIT", product=product, customer=customer, order=order, duedate=duedate)
                session.add(new_lot)
                # jede LotID, die hier erstellt wird wird zu Liste hinzugefügt um doppelte LotIDs zu verhindern
                lot_ids.append(lot_id)
            except:
                session.rollback()
                session.close()
                return render_template("los_starten_error.html", error_message="Fehler beim Erstellen der Lose", id=1)

        session.commit()
        session.close()
        
        # Überprüfen, ob die Formulardaten vorhanden sind
        if timeint1 is None or timeint2 is None:
            return render_template("los_starten_error.html", error_message="Bitte geben Sie Start- und Endzeit für das Starten der Lose an", id=1)

        # Datumszeichenfolgen in datetime-Objekte umwandeln
        timeint1 = datetime.datetime.strptime(timeint1, "%Y-%m-%d")
        timeint2 = datetime.datetime.strptime(timeint2, "%Y-%m-%d")
        time_interval = timeint2 - timeint1 # Zeitabstand zwischen den zwei eingegebenen date-time-Daten
        # Zeitabstand in Stunden umrechnen
        time_interval = time_interval.total_seconds() / 3600 + 24 # letzter Tag wird auch berücksichtigt
        # Anzahl der Stunden bis nächstes Los gestartet wird
        time_next_lot = time_interval/lots_to_create

        # Prüfung ob alle Lose erstellt wurden, die erstellt werden sollten
        if len(lot_ids) == lots_to_create:
            startTime=timeint1

            # Datenbankverbindung herstellen
            session = database_connection()

            for lot_id in lot_ids:
                # Startzeit des aktuellen Loses in der Datenbank speichern
                lot = session.query(Lot).filter(Lot.lotid == lot_id).first()
                lot.startdate = startTime
                session.commit()
                startTime = startTime + datetime.timedelta(hours=time_next_lot) # Startzeit für das nächste Los wird berechnet (ungenau auf Stunden gerundet)

            session.close()

            return los_starten_success(lot_ids)
        else:
            # Fehlermeldung, falls nicht alle Lose erstellt werden konnten
            return render_template("los_starten_error.html", error_message="Fehler beim Hinzuügen der Lose in die Datenbank", id=1)
    else:
        # Umleitung auf die Login-Seite falls der Benutzer nicht autorisiert ist
        return redirect(url_for('login.login'))

@los_starten_bp.route("/main/manuell_starten", methods=["POST"])
def manuell_starten():
    print("Manuell Starten")
    # Formulardaten abrufen
    lotid=request.form.get("lot_id")
    # Datenbankverbindung herstellen
    session = database_connection()
    # Lot mit der LotID abrufen
    lot = session.query(Lot).filter(Lot.lotid == lotid).first()
    # Fehlerbehandlung, falls LotID nicht existiert (Fehlermeldung anzeigen)
    if lot is None:
        session.close()
        return render_template("los_starten_error.html", error_message="Das Los mit der ID " + lotid + " existiert nicht.", id=2)
    # Prüfen, ob das Los manuell gestartet werden kann (also im Zustand INIT ist)
    if(lot.state == "INIT"):
        lot.state = "WAIT"
        lot.enteroper = datetime.datetime.now()
        product = lot.product
        #1. Route des Produkts ermitteln
        route = session.query(ProdFlow.route).filter(ProdFlow.product == product, ProdFlow.seq == 1).first()
        route = route[0]
        lot.route = route
        #2. Erste Operation der Route setzen
        workflows_per_route = session.query(Workflow).filter(Workflow.route == route).all()
        #sortieren nach kleinster oper-Zahl (zuerst in INT-Wert umwandeln)
        min_oper = 10000
        for workflow in workflows_per_route:
            if(int(workflow.oper) < min_oper):
                min_oper = int(workflow.oper)
                lot.oper = workflow.oper
        session.add(lot)
        session.commit()
        session.close()
        return render_template("los_starten_success.html", lot_data='', amount=1, id=2, lot_id_1=lotid)
    # Fehlerbehandlung, falls das Los nicht manuell gestartet werden kann (Fehlermeldung anzeigen)
    else:
        session.close()
        return render_template("los_starten_error.html", error_message="Das Los kann nicht manuell gestartet werden, da es bereits gestartet wurde oder beendet ist.", id=2)

def generateLotID(create_lot_ids, customer, order):
    customer_order_code = customer[:2].upper() + order[:2].upper()
    lot_ids = get_all_lot_ids()  # Funktion, um alle LotIDs aus der Datenbank abzurufen
    lotid='1' #Startwert für LotID-Nummerierung
    lotid_with_name = customer_order_code + '-' + lotid #LotID-Name
    while(lotid_with_name in lot_ids or lotid_with_name in create_lot_ids): #Überprüfen, ob die LotID bereits existiert
        lotid = str(int(lotid)+1) #LotID-Nummerierung erhöhen
        lotid_with_name = customer_order_code + '-' + lotid #angepasster LotID-Name

    return lotid_with_name

def los_starten_success(lot_ids):
    #Anzahl Einträge in der Liste lot_ids
    if check_user_session():
        i = len(lot_ids)
        return render_template("los_starten_success.html", lot_data=lot_ids, amount=i, id=1, lot_id_1='')

def get_sort_order(model, sort_type):
    if sort_type == 'lasc':
        return model.lotid.asc()
    elif sort_type == 'ldesc':
        return model.lotid.desc()
    elif sort_type == 'zasc':
        return model.state.asc()
    elif sort_type == 'zdesc':
        return model.state.desc()
    elif sort_type == 'tasc':
        return model.disptool.asc()
    elif sort_type == 'tdesc':
        return model.disptool.desc()
    else:
        return model.lotid.asc()

def get_all_lot_ids():
    # Hiermit rufen wir alle LotIDs aus der Datenbank ab und geben sie zurück
    session = database_connection()
    lot_ids = session.query(Lot.lotid).all()
    # Entfernen von (LotID,) zu LotID
    lot_ids = [lot_id[0] for lot_id in lot_ids]
    session.close()
    return lot_ids

def get_all_products():
    # Hiermit rufen wir alle Produkte aus der Datenbank ab und geben sie zurück
    session = database_connection()
    products = session.query(ProdFlow.product).distinct().all()
    products = [product[0] for product in products]
    session.close()
    return products

def get_all_tools():
    # Hiermit rufen wir alle Maschinen aus der Datenbank ab und geben sie zurück
    session = database_connection()
    tools = session.query(Tool.tool).all()
    tools = [tool[0] for tool in tools]
    session.close()
    return tools

# Datenbankverbindung herstellen
def database_connection():
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session_d = Session()
    return session_d