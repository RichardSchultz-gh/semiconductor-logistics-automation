# los_bearbeiten.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from mapper import Lot, Tool, PTime, Workflow, ProdFlow
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy.ext.declarative import declarative_base

los_bearbeiten_bp = Blueprint('los_bearbeiten', __name__)

def check_user_session():
    return 'username' in session and session['username'] == 'user1'

@los_bearbeiten_bp.route("/main/los_bearbeiten", methods=["GET"])
def los_bearbeiten_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        lotids = get_all_lot_ids()  # alle LotIDs aus Lot abrufen
        toolids = get_all_tool_ids()  # alle ToolIDs aus Tool abrufen

         # Lot-ID- und Zustandsfilterung
        lot_id_filter = request.args.get('lot_id_f')
        print("Lot ID Filter: " + str(lot_id_filter))
        lot_state_filter = request.args.get('lot_state_f')
        tool_filter = request.args.get('tool_f')
        tool_state_filter = request.args.get('tool_state_f')

        if lot_id_filter:
            lots = filter_lots_by_id(lot_id_filter)
        elif lot_state_filter:
            lots = filter_lots_by_state(lot_state_filter)
        else:
            lots = get_all_lots()  # Hier implementieren Sie Ihre Logik zum Abrufen von Lots für die angeforderte Seite

        if tool_filter:
            tools = filter_tools_by_tool(tool_filter)
        elif tool_state_filter:
            tools = filter_tools_by_tool_state(tool_state_filter)
        else:
            tools = get_all_tools()

        usern = session['username']

        return render_template("los_bearbeiten_page.html", lotids=lotids, toolids=toolids, lots=lots, tools=tools, username=usern)
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen


@los_bearbeiten_bp.route("/main/los_bearbeiten", methods=["POST","GET"])
def moveLot():
    session_d = database_connection()
    # übergebenes Los aus der Formularabfrage
    lot_id = request.form.get('lot_id')
    print("Lot " + lot_id + " is selected")
    # Überprüfen, ob das Los in der Datenbank vorhanden ist
    lot = session_d.query(Lot).filter(Lot.lotid == lot_id).first()
    if lot is None:
        print(f"Lot with ID {lot_id} not found")
        return render_template("los_bearbeiten_error.html", username=session['username'], error_message=f"Lot with ID {lot_id} not found")

    # Überprüfen, ob das Los in WAIT-Zustand ist
    if lot.state != "WAIT":
        print(f"Lot with ID {lot_id} is not in WAIT state")
        return render_template("los_bearbeiten_error.html", username=session['username'], error_message=f"Lot with ID {lot_id} is not in WAIT state")

    #Suche in PTime nach Maschinen, die die Operation der Route bearbeiten können
    route = lot.route
    oper = lot.oper
    product = lot.product
    tools_for_lotoper = session_d.query(PTime).filter(PTime.route == route).filter(PTime.oper == oper).filter(PTime.product == product).all()

    # Schauen, ob Maschinen von tools_for_lotoper in IDLE-Zustand sind, falls nicht entfernen
    for tool in tools_for_lotoper:
        state = session_d.query(Tool).filter(Tool.tool == tool.tool).first().state
        if state != "IDLE":
            tools_for_lotoper.remove(tool)

    # Wenn keine Maschine gefunden wird, wird das Los in WAIT-Zustand belassen
    if len(tools_for_lotoper) == 0:
        print(f"No idle-tool found for route {route} and operation {oper} of product {product}")
        return render_template("los_bearbeiten_error.html", username=session['username'], error_message=f"No idle-tool found for route {route} and operation {oper} of product {product}")
    
    # Auswahl einer Maschine für das Los
    PTIMEtool = tools_for_lotoper[0]
    tool = session_d.query(Tool).filter(Tool.tool == PTIMEtool.tool).first()
    print("Lot " + lot.lotid + " is selected to be processed by tool " + tool.tool + "\n")
    lot.state = "PROC"
    lot.disptool = tool.tool
    lot.procstart = datetime.datetime.now()
    session_d.add(lot) 
    session_d.commit()
    if lot.state == "PROC":
        print("Lot " + lot.lotid + " is PROC now")
    tool.state = "PROC"
    session_d.add(tool)
    session_d.commit()
    if tool.state == "PROC":
        print("Tool " + tool.tool + " is PROC now")
    database_disconnection(session_d)
    return redirect(url_for('los_bearbeiten.los_bearbeiten_page'))


def database_connection():
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session_d = Session()
    return session_d

def database_disconnection(session_d):
    session_d.close()

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

def get_all_tools():
    # Hiermit rufen wir alle Werkzeuge aus der Datenbank ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    tools = session.query(Tool).all()
    session.close()
    return tools

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

def filter_tools_by_tool(tool_filter):
    # Hiermit filtern wir Lose nach Werkzeug
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    tools = session.query(Tool).filter(Tool.tool==tool_filter).all()
    session.close()
    return tools

def filter_tools_by_tool_state(tool_state_filter):
    # Hiermit filtern wir Lose nach Werkzeugzustand
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    tools = session.query(Tool).filter(Tool.state==tool_state_filter).all()
    session.close()
    return tools

def get_all_tool_ids():
    # Hiermit rufen wir alle ToolIDs aus der Datenbank ab und geben sie zurück
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Base = declarative_base()
    Session = sessionmaker(bind=engine)
    session = Session()
    tool_ids = session.query(Tool.tool).all()
    # Entfernen von (ToolID,) zu ToolID
    tool_ids = [tool_id[0] for tool_id in tool_ids]
    session.close()
    return tool_ids