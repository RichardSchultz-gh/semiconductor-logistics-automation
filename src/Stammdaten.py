# Stammdaten.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from mapper import Lot, Tool, PTime, Workflow, ProdFlow
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from config import config
from database_accesses import *
from datetime import datetime

Stammdaten_bp = Blueprint('Stammdaten', __name__)

def check_user_session():
    return 'username' in session and session['username'] == config.USER1

@Stammdaten_bp.route("/main/Stammdaten", methods=["GET"])
def Stammdaten_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        usern = session['username']
        return render_template("Stammdaten_main.html", username=usern)
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen

@Stammdaten_bp.route("/main/Stammdaten/Los", methods=["GET"])
def Stammdaten_Los_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        usern = session['username']
        
        lotids = get_all_lot_ids()  # alle LotIDs aus Lot abrufen
        
         # Lot-ID- und Zustandsfilterung
        lot_id_filter = request.args.get('lot_id_f')
        print("Lot ID Filter: " + str(lot_id_filter))
        lot_state_filter = request.args.get('lot_state_f')


        # Filterung von Losen und Werkzeugen
        sort_type_Lots = request.args.get('Lsort')
        

        if lot_id_filter and not lot_state_filter:
            lots = filter_lots_by_id(lot_id_filter, sort_type_Lots)
        elif lot_state_filter and not lot_id_filter:
            lots = filter_lots_by_state(lot_state_filter, sort_type_Lots)
        elif lot_id_filter and lot_state_filter:
            lots = filter_lots_by_id_and_state(lot_id_filter, lot_state_filter, sort_type_Lots)
        else:
            lots = get_all_lots(sort_type_Lots) # Hier implementieren Sie Ihre Logik zum Abrufen von Lots für die angeforderte Seite

        
        
        lot_to_edit_id = request.args.get('lot_id_s_i')
        lot_to_edit= get_lot_by_id(lot_to_edit_id)


        if(get_args_right('lot_id') != None):
            dbsession=database_connection()
            edit_Lot=get_lot_by_id(get_args_right('lot_id'))


            try:
                if(edit_Lot.priority!=get_args_right('lot_priority')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'priority':get_args_right('lot_priority')})
                

                print("pieces:"+get_args_right('lot_pieces'))
                if(edit_Lot.pieces!=get_args_right('lot_pieces')):
                    print("bin in pieces")
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'pieces':get_args_right('lot_pieces')})

                if(edit_Lot.state!=get_args_right('lot_state')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'state':get_args_right('lot_state')})

                if(edit_Lot.product!=get_args_right('lot_product')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'product':get_args_right('lot_product')})

                if(edit_Lot.route!=get_args_right('lot_route')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'route':get_args_right('lot_route')})

                if(edit_Lot.oper!=get_args_right('lot_oper')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'oper':get_args_right('lot_oper')})

                if(edit_Lot.customer!=get_args_right('lot_customer')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'customer':get_args_right('lot_customer')})

                if(edit_Lot.order!=get_args_right('lot_order')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'order':get_args_right('lot_order')})

                if(edit_Lot.disptool!=get_args_right('lot_disptool')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'disptool':get_args_right('lot_disptool')})

                if(edit_Lot.duedate!=get_args_right('lot_duedate')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'duedate':get_args_right('lot_duedate')})

                if(edit_Lot.startdate!=get_args_right('lot_startdate')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'startdate':get_args_right('lot_startdate')})
                
                if(edit_Lot.enteroper!=get_timestamp_args_right('lot_enteroper')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'enteroper':get_timestamp_args_right('lot_enteroper')})
                
                if(edit_Lot.procstart!=get_timestamp_args_right('lot_procstart')):
                    dbsession.query(Lot).filter(Lot.lotid==get_args_right('lot_id')).update({'procstart':get_timestamp_args_right('lot_procstart')})
                
                dbsession.commit()
                dbsession.close()
            except SQLAlchemyError as e:
                print("Error: "+ e)
                return render_template("Stammdaten_error.html", error=e)

        return render_template("Stammdaten_Los.html", lotids=lotids, lots=lots, username=usern, lot_to_edit=lot_to_edit)
        
    else:
        return "Unauthorized", 401  # Fehlermeldung anzeigen oder Umleitung durchführen

def get_args_right(id):
    lot_attribute= request.args.get(id)
    if(lot_attribute=="None"or lot_attribute== ""):lot_attribute=None
    return lot_attribute

def get_timestamp_args_right(id):
    lot_attribute= request.args.get(id)
    if(lot_attribute=="None" or not lot_attribute):lot_attribute=None
    if(lot_attribute!=None):
        dt= datetime.strptime(lot_attribute, "%Y-%m-%dT%H:%M")
        new_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        return new_timestamp
    else:
        return None


@Stammdaten_bp.route("/main/Stammdaten/Tool", methods=["GET"])
def Stammdaten_Tool_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        tool_ids = get_all_tool_ids()  # alle ToolIDs aus Tool abrufen

        tool_filter = request.args.get('tool_f')
        tool_state_filter = request.args.get('tool_state_f')


        sort_type_Tools = request.args.get('Tsort')

        if tool_filter and not tool_state_filter:
            tools = filter_tools_by_tool(tool_filter, sort_type_Tools)
        elif tool_state_filter and not tool_filter:
            tools = filter_tools_by_tool_state(tool_state_filter, sort_type_Tools)
        elif tool_filter and tool_state_filter:
            tools = filter_tools_by_tool_and_state(tool_filter, tool_state_filter, sort_type_Tools)
        else:
            tools = get_all_tools(sort_type_Tools) # Hier implementieren Sie Ihre Logik zum Abrufen von Tools für die angeforderte Seite

        tool_edit = request.args.get('tool_s_i')
        tool_to_edit= get_tool_by_id(tool_edit)



        usern = session['username']

        return render_template("Stammdaten_Tool.html",username=usern, tools=tools, tool_ids=tool_ids, tool_to_edit=tool_to_edit)


@Stammdaten_bp.route("/main/Stammdaten/ProdFlow", methods=["GET"])
def Stammdaten_ProdFlow_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        prod_ids = get_all_prodids()
        route_ids = get_all_routeids()
        prod_filter = request.args.get('prod_f')
        route_filter = request.args.get('route_f')


        sort_type_prodflow = request.args.get('PFsort')

        if prod_filter and not route_filter:
            prodflows = filter_prodflows_by_prod(prod_filter, sort_type_prodflow)
        elif route_filter and not prod_filter:
            prodflows = filter_prodflows_by_route(route_filter, sort_type_prodflow)
        elif prod_filter and route_filter:
            prodflows = filter_prodflows_by_route_and_prod(prod_filter, route_filter, sort_type_prodflow)
        else:
            prodflows = get_all_prodflows(sort_type_prodflow) # Hier implementieren Sie Ihre Logik zum Abrufen von Tools für die angeforderte Seite
        
        prod_edit = request.args.get('prod_s_i')
        route_edit = request.args.get('route_s_i')
        seq_edit = request.args.get('seq_s_i')
        prodflow_to_edit= get_prodflow(prod_edit,route_edit,seq_edit)

        usern = session['username']

        return render_template("Stammdaten_ProdFlow.html",username= usern, prodflows=prodflows, prod_ids=prod_ids, route_ids=route_ids, prodflow_to_edit=prodflow_to_edit)
    
@Stammdaten_bp.route("/main/Stammdaten/WorkFlow", methods=["GET"])
def Stammdaten_WorkFlow_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        route_ids = get_all_routeids()
        oper_ids = get_all_operids()
        route_filter = request.args.get('route_f')
        oper_filter = request.args.get('oper_f')


        sort_type_prodflow = request.args.get('PFsort')

        if oper_filter and not route_filter:
            workflows = filter_prodflows_by_prod(oper_filter, sort_type_prodflow)
        elif route_filter and not oper_filter:
            workflows = filter_prodflows_by_route(route_filter, sort_type_prodflow)
        elif oper_filter and route_filter:
            workflows = filter_prodflows_by_route_and_prod(oper_filter, route_filter, sort_type_prodflow)
        else:
            workflows = get_all_prodflows(sort_type_prodflow) # Hier implementieren Sie Ihre Logik zum Abrufen von Tools für die angeforderte Seite
        
        prod_edit = request.args.get('prod_s_i')
        route_edit = request.args.get('route_s_i')
        seq_edit = request.args.get('seq_s_i')
        workflow_to_edit= get_prodflow(prod_edit,route_edit,seq_edit)

        usern = session['username']

        return render_template("Stammdaten_WorkFlow.html",username= usern, workflows=workflows, oper_ids=oper_ids, route_ids=route_ids, workflow_to_edit=workflow_to_edit)

@Stammdaten_bp.route("/main/Stammdaten/PTime", methods=["GET"])
def Stammdaten_PTime_page():
    if check_user_session():  # Überprüfen, ob der Benutzer angemeldet ist
        route_ids = get_all_routeids()
        oper_ids = get_all_operids()
        route_filter = request.args.get('route_f')
        oper_filter = request.args.get('oper_f')


        sort_type_prodflow = request.args.get('PFsort')

        if oper_filter and not route_filter:
            workflows = filter_prodflows_by_prod(oper_filter, sort_type_prodflow)
        elif route_filter and not oper_filter:
            workflows = filter_prodflows_by_route(route_filter, sort_type_prodflow)
        elif oper_filter and route_filter:
            workflows = filter_prodflows_by_route_and_prod(oper_filter, route_filter, sort_type_prodflow)
        else:
            workflows = get_all_prodflows(sort_type_prodflow) # Hier implementieren Sie Ihre Logik zum Abrufen von Tools für die angeforderte Seite
        
        prod_edit = request.args.get('prod_s_i')
        route_edit = request.args.get('route_s_i')
        seq_edit = request.args.get('seq_s_i')
        workflow_to_edit= get_prodflow(prod_edit,route_edit,seq_edit)

        usern = session['username']

        return render_template("Stammdaten_PTime.html",username= usern, workflows=workflows, oper_ids=oper_ids, route_ids=route_ids, ptime_to_edit=workflow_to_edit)

