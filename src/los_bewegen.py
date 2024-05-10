from flask import Blueprint, render_template, request, redirect, url_for, session
from mapper import Lot, Tool, PTime, Workflow, ProdFlow
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from los_starten import get_all_lot_ids
import datetime
import random

los_bewegen_bp = Blueprint('los_bewegen', __name__)

def check_user_session():
    return 'username' in session and session['username'] == 'user1'

@los_bewegen_bp.route("/main/los_bewegen", methods=["GET"])
def los_bewegen_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        products = get_all_products()  # alle Produkte aus ProdFlow abrufen
        lotids = get_all_lot_ids()  # alle LotIDs aus Lot abrufen
        tools = get_all_tools()  # alle Werkzeuge aus Tool abrufen

         # Lot-ID- und Zustandsfilterung
        lot_id_filter = request.args.get('lot_id_f')
        lot_state_filter = request.args.get('lot_state_f')
        lot_tool_filter = request.args.get('lot_tool_f')

        lots = []
        if lot_id_filter and not lot_state_filter and not lot_tool_filter:
            lots = filter_lots_by_id(lot_id_filter)
        elif lot_state_filter and not lot_id_filter and not lot_tool_filter:
            lots = filter_lots_by_state(lot_state_filter)
        elif lot_tool_filter and not lot_id_filter and not lot_state_filter:
            lots = filter_lots_by_tool(lot_tool_filter)
        elif lot_id_filter and lot_state_filter and not lot_tool_filter:
            lots = filter_lots_by_id_state(lot_id_filter, lot_state_filter)
        elif lot_id_filter and lot_tool_filter and not lot_state_filter:
            lots = filter_lots_by_id_tool(lot_id_filter, lot_tool_filter)
        elif lot_state_filter and lot_tool_filter and not lot_id_filter:
            lots = filter_lots_by_state_tool(lot_state_filter, lot_tool_filter)
        elif lot_id_filter and lot_state_filter and lot_tool_filter:
            lots = filter_lots_by_id_state_tool(lot_id_filter, lot_state_filter, lot_tool_filter)
        else:
            lots = get_all_lots()

        usern = session['username']

        return render_template("los_bewegen_page.html", products=products, lotids=lotids, lots=lots, tools=tools, username=usern)
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen

@los_bewegen_bp.route("/main/los_bewegen", methods=["POST"])
def los_bewegen():
    if check_user_session():
        #wenn request von name state kommt:
        if request.form.get("state"):
            DATABASE_URL = get_database_url()
            engine = create_engine(DATABASE_URL)
            Session = sessionmaker(bind=engine)
            db_session = Session()
            if(request.form.get("state") == "scrap"):
                #aus Feld mit name="lotid_hidden" wird die LotID geholt
                lotid = request.form.get("lotid_hidden")
                print("LotID: " + lotid)
                #Lot-Objekt mit der LotID holen
                lot = db_session.query(Lot).filter(Lot.lotid == lotid).first()
                #Lot-Objekt mit dem Zustand "SCRAP" setzen
                lot.state = "SCRAP"
                #Lot-Objekt in Datenbank speichern
                db_session.add(lot)
                db_session.commit()
                db_session.close()
                return render_template("los_bewegen_success.html", success_message="Lot wurde erfolgreich auf SCRAP gesetzt")
            elif(request.form.get("state") == "op_comp"):
                lotid = request.form.get("lotid_hidden")
                lot = db_session.query(Lot).filter(Lot.lotid == lotid).first()
                lot.state = "OP_COMP"
                db_session.add(lot)
                db_session.commit()
                db_session.close()
                return render_template("los_bewegen_success.html", success_message="Lot wurde erfolgreich auf OP_COMP gesetzt")
            return redirect(url_for("los_bewegen.los_bewegen_page"))

        lotid = request.form.get("lot_id")
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        lot = db_session.query(Lot).filter(Lot.lotid == lotid).first()
        
        if lot is None:
            db_session.close()
            return render_template("los_bewegen_error.html", error_message="Lot ID nicht gefunden")
        
        if lot.state == "HOLD":
            return render_template("los_bewegen_hold.html", message="Lot ist möglicherweise defekt - Folgezustand muss manuell gesetzt werden:", lotid=lotid)
        if lot.state != "OP_COMP":
            db_session.close()
            return render_template("los_bewegen_hold.html", message="Lot ist möglicherweise defekt - Folgezustand muss manuell gesetzt werden:", lotid=lotid)

        if move_lot_to_next_station(lot, db_session) == 0:
            db_session.commit()
            db_session.close()
            return render_template("los_bewegen_success.html", success_message="Los wurde bewegt und befindet sich nun in WAIT-Zustand")
        elif move_lot_to_next_station(lot, db_session) == 1:
            db_session.commit()
            db_session.close()
            return render_template("los_bewegen_success.html", success_message="Los wurde erfolgreich bewegt und befindet sich nun im FIN-Zustand, da es den Produktionsfluss abgeschlossen hat")
        else:
            db_session.close()
            return render_template("los_bewegen_error.html", error_message="Keine weitere Route verfügbar oder Fehler beim Bewegen des Loses")
    else:
        return "Unauthorized", 401

def move_lot_to_next_station(lot, db_session):
    route = lot.route
    oper_int = int(lot.oper)
    #Oper = '0100' soll zu '0200' werden usw...
    if(oper_int < 1000):
        next_oper = '0' + str(oper_int+100)
    else:
        next_oper = str(oper_int+100)
    next = db_session.query(Workflow).filter(Workflow.route == route).filter(Workflow.oper == next_oper).first()
    if next is None:
        route = db_session.query(ProdFlow).filter(ProdFlow.product == lot.product).filter(ProdFlow.route == route).first()
        newseq = route.seq + 1
        next_route = db_session.query(ProdFlow).filter(ProdFlow.product == lot.product).filter(ProdFlow.seq == newseq).first()
        if next_route is None:
            print("Produktionsfluss von Lot"+ lot.lotid + "ist zu Ende")
            lot.state = "FIN"
            db_session.add(lot)
            db_session.commit()
            return 1
        #Erste Operation der Route setzen
        workflows_per_route = db_session.query(Workflow).filter(Workflow.route == next_route.route).all()
        # sortieren nach kleinster oper-Zahl (zuerst in INT-Wert umwandeln)
        min_oper = 10000
        for wf in workflows_per_route:
            if(int(wf.oper) < min_oper):
                min_oper = int(wf.oper)
                next_oper = wf.oper
        lot.route = next_route.route
        db_session.add(lot)
        db_session.commit()
        next = db_session.query(Workflow).filter(Workflow.route == next_route.route).filter(Workflow.oper == next_oper).first()
    lot.oper = next.oper

    #Test, ob Mandatory-Flag gesetzt ist
    if next.mandatory == 1:
        lot.state = "WAIT"
        lot.enteroper = datetime.datetime.now()
        db_session.add(lot)
        db_session.commit()
        print("Lot " + lot.lotid + " is WAIT now (next operation: " + lot.oper + ")")
    else: #falls Los nicht zwingend in nächste Operation muss
        print("Lot " + lot.lotid + " is not mandatory for next operation: " + lot.oper)
        # erzeuge Random Wert zwischen 1 und 100 für Simulation der Wahrscheinlichkeit
        random_value = random.randint(1, 100)
        #Test, ob random_value kleiner als stepperc ist
        if random_value < next.stepperc:
            lot.state = "WAIT"
            lot.enteroper = datetime.datetime.now()
            db_session.add(lot)
            db_session.commit()
            print("Lot " + lot.lotid + " is WAIT now (next operation: " + lot.oper + ")")
        else:
            print("Lot " + lot.lotid + " skips next operation: " + lot.oper)
            db_session.add(lot)
            db_session.commit()
            move_lot_to_next_station(lot, db_session)
    return 0

if __name__ == '__main__':
    los_bewegen_bp.run(debug=True)



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
    # Hiermit filtern wir Lose nach ZustandE
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

def filter_lots_by_id_state(lot_id_filter, lot_state_filter):
    # Hiermit filtern wir Lose nach Lot-ID und Zustand
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.state==lot_state_filter).all()
    session.close()
    return lots

def filter_lots_by_id_tool(lot_id_filter, lot_tool_filter):
    # Hiermit filtern wir Lose nach Lot-ID und Werkzeug
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.disptool==lot_tool_filter).all()
    session.close()
    return lots

def filter_lots_by_state_tool(lot_state_filter, lot_tool_filter):
    # Hiermit filtern wir Lose nach Zustand und Werkzeug
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lots = session.query(Lot).filter(Lot.state==lot_state_filter, Lot.disptool==lot_tool_filter).all()
    session.close()
    return lots

def filter_lots_by_id_state_tool(lot_id_filter, lot_state_filter, lot_tool_filter):
    # Hiermit filtern wir Lose nach Lot-ID, Zustand und Werkzeug
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.state==lot_state_filter, Lot.disptool==lot_tool_filter).all()
    session.close()
    return lots

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
