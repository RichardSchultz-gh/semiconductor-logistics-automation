# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
# los_bearbeiten.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from mapper import Lot, Tool, PTime
from database_connection import get_database_url, database_connection, database_disconnection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import config
import random
import datetime

los_bearbeiten_bp = Blueprint('los_bearbeiten', __name__)

def check_user_session():
    return 'username' in session and session['username'] == config.USER1

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

        # Filterung von Losen und Werkzeugen
        sort_type_Lots = request.args.get('Lsort')
        sort_type_Tools = request.args.get('Tsort')

        # Datenbankverbindung herstellen
        sessiond = database_connection()

        if lot_id_filter and not lot_state_filter:
            lots = sessiond.query(Lot).filter(Lot.lotid == lot_id_filter).order_by(get_sort_order(Lot, sort_type_Lots)).all()
        elif lot_state_filter and not lot_id_filter:
            lots = sessiond.query(Lot).filter(Lot.state == lot_state_filter).order_by(get_sort_order(Lot, sort_type_Lots)).all()
        elif lot_id_filter and lot_state_filter:
            lots = sessiond.query(Lot).filter(Lot.lotid == lot_id_filter, Lot.state == lot_state_filter).order_by(get_sort_order(Lot, sort_type_Lots)).all()
        else:
            lots = sessiond.query(Lot).order_by(get_sort_order(Lot, sort_type_Lots)).all()

        if tool_filter and not tool_state_filter:
            tools = sessiond.query(Tool).filter(Tool.tool == tool_filter).order_by(get_sort_order(Tool, sort_type_Tools)).all()
        elif tool_state_filter and not tool_filter:
            tools = sessiond.query(Tool).filter(Tool.state == tool_state_filter).order_by(get_sort_order(Tool, sort_type_Tools)).all()
        elif tool_filter and tool_state_filter:
            tools = sessiond.query(Tool).filter(Tool.tool == tool_filter, Tool.state == tool_state_filter).order_by(get_sort_order(Tool, sort_type_Tools)).all()
        else:
            tools = sessiond.query(Tool).order_by(get_sort_order(Tool, sort_type_Tools)).all()

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
    
    # Auswahl einer Maschine für das Los (per Zufall)
    randomindex = random.randint(0, len(tools_for_lotoper)-1)
    PTIMEtool = tools_for_lotoper[randomindex]
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
    return render_template("los_bearbeiten_success.html", username=session['username'], success_message=f"Lot with ID {lot_id} is now in PROC state and is processed by tool {tool.tool}")


def get_all_lot_ids():
    # Hiermit rufen wir alle LotIDs aus der Datenbank ab und geben sie zurück
    session = database_connection()
    lot_ids = session.query(Lot.lotid).all()
    # Entfernen von (LotID,) zu LotID
    lot_ids = [lot_id[0] for lot_id in lot_ids]
    session.close()
    return lot_ids

def get_all_tool_ids():
    # Hiermit rufen wir alle ToolIDs aus der Datenbank ab und geben sie zurück
    session = database_connection()
    tool_ids = session.query(Tool.tool).all()
    # Entfernen von (ToolID,) zu ToolID
    tool_ids = [tool_id[0] for tool_id in tool_ids] # Entfernen von (ToolID,) zu ToolID
    session.close()
    return tool_ids

def get_sort_order(model, sort_type):
    if(model == Lot):
        if sort_type == 'lasc':
            return model.lotid.asc()
        elif sort_type == 'ldesc':
            return model.lotid.desc()
        elif sort_type == 'zasc':
            return model.state.asc()
        elif sort_type == 'zdesc':
            return model.state.desc()   
        else:
            return model.lotid.asc()
    elif(model == Tool):
        if sort_type == 'tasc':
            return model.tool.asc()
        elif sort_type == 'tdesc':
            return model.tool.desc()
        elif sort_type == 'sasc':
            return model.state.asc()
        elif sort_type == 'sdesc':
            return model.state.desc()
        else:
            return model.tool.asc()