# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
# database_accesses.py
from mapper import Lot, Tool, PTime, Workflow, ProdFlow
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
from config import config


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
    session = database_connection()
    lot_ids = session.query(Lot.lotid).all()
    # Entfernen von (LotID,) zu LotID
    lot_ids = [lot_id[0] for lot_id in lot_ids]
    session.close()
    return lot_ids

def get_all_lots():
    # Hiermit rufen wir alle Lose aus der Datenbank ab und geben sie zurück
    session = database_connection()
    lots = session.query(Lot).all()
    session.close()
    return lots

def get_all_lots(sorttype):
    # Hiermit rufen wir alle Lose aus der Datenbank ab und geben sie zurück
    session = database_connection()
    if(not sorttype):
        lots = session.query(Lot).all()
        session.close()
        return lots
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        lots = session.query(Lot).order_by(attribute).all()
    elif(direction == 'desc'):
        lots = session.query(Lot).order_by(attribute.desc()).all()
    session.close()
    return lots

def get_lot_by_id(lot_id):
    session = database_connection()
    lot = session.query(Lot).filter(Lot.lotid==lot_id).first()
    session.close()
    return lot

def filter_lots_by_state(lot_state_filter, sorttype):
    # Hiermit filtern wir Lose nach Zustand
    session = database_connection()
    if(not sorttype):
        lots = session.query(Lot).filter(Lot.state==lot_state_filter).all()
        session.close()
        return lots
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        lots = session.query(Lot).filter(Lot.state==lot_state_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        lots = session.query(Lot).filter(Lot.state==lot_state_filter).order_by(attribute.desc()).all()
    session.close()
    return lots

def filter_lots_by_id(lot_id_filter, sorttype):
    # Hiermit filtern wir Lose nach Lot-ID
    session = database_connection()
    if(not sorttype):
        lots= session.query(Lot).filter(Lot.lotid==lot_id_filter).all()
        session.close()
        return lots
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter).order_by(attribute.desc()).all()
    session.close()
    return lots

def filter_lots_by_id_and_state(lot_id_filter, lot_state_filter, sorttype):
    # Hiermit filtern wir Lose nach Lot-ID und Zustand
    session = database_connection()
    if(not sorttype):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.state==lot_state_filter).all()
        session.close()
        return lots
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.state==lot_state_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.state==lot_state_filter).order_by(attribute.desc()).all()
    session.close()
    return lots

def get_all_tool_ids():
    # Hiermit rufen wir alle ToolIDs aus der Datenbank ab und geben sie zurück
    session = database_connection()
    tool_ids = session.query(Tool.tool).all()
    # Entfernen von (ToolID,) zu ToolID
    tool_ids = [tool_id[0] for tool_id in tool_ids] # Entfernen von (ToolID,) zu ToolID
    session.close()
    return tool_ids

def get_all_operations():
    session = database_connection()
    operations = session.query()

def get_all_operids():
    session = database_connection()
    prods = session.query(Workflow.oper).all()
    session.close()
    return prods


def get_all_tools():
    # Hiermit rufen wir alle Werkzeuge aus der Datenbank ab und geben sie zurück
    session = database_connection()
    tools = session.query(Tool).all()
    session.close()
    return tools

def get_all_tools(sorttype):
    # Hiermit rufen wir alle Werkzeuge aus der Datenbank ab und geben sie zurück
    session = database_connection()
    if(not sorttype):
        tools = session.query(Tool).all()
        session.close()
        return tools
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        tools = session.query(Tool).order_by(attribute).all()
    elif(direction == 'desc'):
        tools = session.query(Tool).order_by(attribute.desc()).all()
    session.close()
    return tools

def get_tool_by_id(tool_id):
    session = database_connection()
    tool = session.query(Tool).filter(Tool.tool==tool_id).first()
    session.close()
    return tool

def filter_tools_by_tool(tool_filter, sorttype):
    # Hiermit filtern wir Lose nach Werkzeug
    session = database_connection()
    if(not sorttype):
        tools = session.query(Tool).filter(Tool.tool==tool_filter).all()
        session.close()
        return tools
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        tools = session.query(Tool).filter(Tool.tool==tool_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        tools = session.query(Tool).filter(Tool.tool==tool_filter).order_by(attribute.desc()).all()
    session.close()
    return tools

def filter_tools_by_tool_state(tool_state_filter, sorttype):
    # Hiermit filtern wir Lose nach Werkzeugzustand
    session = database_connection()
    if(not sorttype):
        tools = session.query(Tool).filter(Tool.state==tool_state_filter).all()
        session.close()
        return tools
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        tools = session.query(Tool).filter(Tool.state==tool_state_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        tools = session.query(Tool).filter(Tool.state==tool_state_filter).order_by(attribute.desc()).all()
    session.close()
    return tools

def filter_tools_by_tool_and_state(tool_filter, tool_state_filter, sorttype):
    # Hiermit filtern wir Lose nach Werkzeug und Werkzeugzustand
    session = database_connection()
    if(not sorttype):
        tools = session.query(Tool).filter(Tool.tool==tool_filter).filter(Tool.state==tool_state_filter).all()
        session.close()
        return tools
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        tools = session.query(Tool).filter(Tool.tool==tool_filter).filter(Tool.state==tool_state_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        tools = session.query(Tool).filter(Tool.tool==tool_filter).filter(Tool.state==tool_state_filter).order_by(attribute.desc()).all()
    session.close()
    return tools

def get_all_workflows():
    # Hiermit rufen wir alle Workflows aus der Datenbank ab und geben sie zurück
    session = database_connection()
    workflows = session.query(Workflow).all()
    session.close()
    return workflows

def get_all_workflows(sorttype):
    # Hiermit rufen wir alle Workflow aus der Datenbank ab und geben sie zurück
    session = database_connection()
    if(not sorttype):
        workflows = session.query(Workflow).all()
        session.close()
        return workflows
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        workflows = session.query(Workflow).order_by(attribute).all()
    elif(direction == 'desc'):
        workflows = session.query(Workflow).order_by(attribute.desc()).all()
    session.close()
    return workflows

def filter_workflows_by_route(route_filter, sorttype):
    # Hiermit filtern wir Workflows nach Routen
    session = database_connection()
    if(not sorttype):
        workflows = session.query(Workflow).filter(Workflow.route==route_filter).all()
        session.close()
        return workflows
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        workflows = session.query(Workflow).filter(Workflow.route==route_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        workflows = session.query(Workflow).filter(Workflow.route==route_filter).order_by(attribute.desc()).all()
    session.close()
    return workflows

def filter_workflows_by_oper(oper_filter, sorttype):
    # Hiermit filtern wir Werkzeuge nach Operationen
    session = database_connection()
    if(not sorttype):
        workflows = session.query(Workflow).filter(Workflow.oper==oper_filter).all()
        session.close()
        return workflows
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        workflows = session.query(Workflow).filter(Workflow.oper==oper_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        workflows = session.query(Workflow).filter(Workflow.oper==oper_filter).order_by(attribute.desc()).all()
    session.close()
    return workflows

def filter_workflows_by_route_and_oper(route_filter, oper_filter, sorttype):
    # Hiermit filtern wir Workflows nach Routen und Operationen
    session = database_connection()
    if(not sorttype):
        workflows = session.query(Workflow).filter(Workflow.route==route_filter).filter(Workflow.oper==oper_filter).all()
        session.close()
        return workflows
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        workflows = session.query(Workflow).filter(Workflow.route==route_filter).filter(Workflow.oper==oper_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        workflows = session.query(Workflow).filter(Workflow.route==route_filter).filter(Workflow.oper==oper_filter).order_by(attribute.desc()).all()
    session.close()
    return workflows

def get_all_prodflows():
    # Hiermit rufen wir alle Prodflows aus der Datenbank ab und geben sie zurück
    session = database_connection()
    prodflows = session.query(ProdFlow).all()
    session.close()
    return prodflows

def get_all_prodflows(sorttype):
    # Hiermit rufen wir alle Prodflows aus der Datenbank ab und geben sie zurück
    session = database_connection()
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        prodflows = session.query(Tool).order_by(attribute).all()
    elif(direction == 'desc'):
        prodflows = session.query(Tool).order_by(attribute.desc()).all()
        session.close()
    return prodflows

def get_all_prodflows(sorttype):
    # Hiermit rufen wir alle Prodflows aus der Datenbank ab und geben sie zurück
    session = database_connection()
    if(not sorttype):
        prodflows = session.query(ProdFlow).all()
        session.close()
        return prodflows
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        prodflows = session.query(ProdFlow).order_by(attribute).all()
    elif(direction == 'desc'):
        prodflows = session.query(ProdFlow).order_by(attribute.desc()).all()
    session.close()
    return prodflows

def get_prodflow(prod, route, seq):
    session = database_connection()
    prodflow = session.query(ProdFlow).filter(ProdFlow.product==prod).filter(ProdFlow.route==route).filter(ProdFlow.seq==seq).first()
    session.close()
    return prodflow

def filter_prodflows_by_route(route_filter, sorttype):
    # Hiermit filtern wir Prodflows nach Routen
    session = database_connection()
    if(not sorttype):
        prodflows = session.query(ProdFlow).filter(ProdFlow.route==route_filter).all()
        session.close()
        return prodflows
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        prodflows = session.query(ProdFlow).filter(ProdFlow.route==route_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        prodflows = session.query(ProdFlow).filter(ProdFlow.route==route_filter).order_by(attribute.desc()).all()
    session.close()
    return prodflows

def filter_prodflows_by_prod(product_filter, sorttype):
    # Hiermit filtern wir Prodflows nach Produkten
    session = database_connection()
    if(not sorttype):
        prodflows = session.query(ProdFlow).filter(ProdFlow.product==product_filter).all()
        session.close()
        return prodflows
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        prodflows = session.query(ProdFlow).filter(ProdFlow.product==product_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        prodflows = session.query(ProdFlow).filter(ProdFlow.product==product_filter).order_by(attribute.desc()).all()
    session.close()
    return prodflows

def filter_prodflows_by_route_and_prod(route_filter, product_filter, sorttype):
    # Hiermit filtern wir Prodflows nach Routen und Produkten
    session = database_connection()
    if(not sorttype):
        prodflows = session.query(ProdFlow).filter(ProdFlow.route==route_filter).filter(ProdFlow.product==product_filter).all()
        session.close()
        return prodflows
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        prodflows = session.query(ProdFlow).filter(ProdFlow.route==route_filter).filter(ProdFlow.product==product_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        prodflows = session.query(ProdFlow).filter(ProdFlow.route==route_filter).filter(ProdFlow.product==product_filter).order_by(attribute.desc()).all()
    session.close()
    return prodflows

def get_all_ptimes():
    # Hiermit rufen wir alle PTimes aus der Datenbank ab und geben sie zurück
    session = database_connection()
    ptimes = session.query(PTime).all()
    session.close()
    return ptimes

def get_all_ptimes(sorttype):
    # Hiermit rufen wir alle PTimes aus der Datenbank ab und geben sie zurück
    session = database_connection()
    if(not sorttype):
        ptimes = session.query(PTime).all()
        session.close()
        return ptimes
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        ptimes = session.query(PTime).order_by(attribute).all()
    elif(direction == 'desc'):
        ptimes = session.query(PTime).order_by(attribute.desc()).all()
    session.close()
    return ptimes

def filter_ptimes_by_route(route_filter, sorttype):
    # Hiermit filtern wir PTimes nach Routen
    session = database_connection()
    if(not sorttype):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).all()
        session.close()
        return ptimes
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).order_by(attribute.desc()).all()
    session.close()
    return ptimes

def filter_ptimes_by_prod(product_filter, sorttype):
    # Hiermit filtern wir PTimes nach Produkten
    session = database_connection()
    if(not sorttype):
        ptimes = session.query(PTime).filter(PTime.product==product_filter).all()
        session.close()
        return ptimes
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        ptimes = session.query(PTime).filter(PTime.product==product_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        ptimes = session.query(PTime).filter(PTime.product==product_filter).order_by(attribute.desc()).all()
    session.close()
    return ptimes

def filter_ptimes_by_tool(tool_filter, sorttype):
    # Hiermit filtern wir PTimes nach Werkzeugen
    session = database_connection()
    if(not sorttype):
        ptimes = session.query(PTime).filter(PTime.tool==tool_filter).all()
        session.close()
        return ptimes
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        ptimes = session.query(PTime).filter(PTime.tool==tool_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        ptimes = session.query(PTime).filter(PTime.tool==tool_filter).order_by(attribute.desc()).all()
    session.close()
    return ptimes

def filter_ptimes_by_route_and_product(route_filter, product_filter, sorttype):
    # Hiermit filtern wir PTimes nach Routen und Produkten
    session = database_connection()
    if(not sorttype):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.product==product_filter).all()
        session.close()
        return ptimes
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.product==product_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.product==product_filter).order_by(attribute.desc()).all()
    session.close()
    return ptimes

def filter_ptimes_by_route_and_tool(route_filter, tool_filter, sorttype):
    # Hiermit filtern wir PTimes nach Routen und Werkzeugen
    session = database_connection()
    if(not sorttype):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.tool==tool_filter).all()
        session.close()
        return ptimes
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.tool==tool_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.tool==tool_filter).order_by(attribute.desc()).all()
    session.close()
    return ptimes

def filter_ptimes_by_product_and_tool(product_filter, tool_filter, sorttype):
    # Hiermit filtern wir PTimes nach Produkten und Werkzeugen
    session = database_connection()
    if(not sorttype):
        ptimes = session.query(PTime).filter(PTime.product==product_filter).filter(PTime.tool==tool_filter).all()
        session.close()
        return ptimes
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        ptimes = session.query(PTime).filter(PTime.product==product_filter).filter(PTime.tool==tool_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        ptimes = session.query(PTime).filter(PTime.product==product_filter).filter(PTime.tool==tool_filter).order_by(attribute.desc()).all()
    session.close()
    return ptimes

def filter_ptimes_by_route_product_and_tool(route_filter, product_filter, tool_filter, sorttype):
    # Hiermit filtern wir PTimes nach Routen, Produkten und Workzeugen
    session = database_connection()
    if(not sorttype):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.product==product_filter).filter(PTime.tool==tool_filter).all()
        session.close()
        return ptimes
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.product==product_filter).filter(PTime.tool==tool_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        ptimes = session.query(PTime).filter(PTime.route==route_filter).filter(PTime.product==product_filter).filter(PTime.tool==tool_filter).order_by(attribute.desc()).all()
    session.close()
    return ptimes

def get_all_prodids():
    session = database_connection()
    prods = session.query(ProdFlow.product).all()
    session.close()
    return prods

def get_all_routeids():
    session = database_connection()
    route = session.query(ProdFlow.route).all()
    session.close()
    return route

def getDirection(sorttype):
    # aus String sorttype 1. Buchstaben entfernen
    direction = sorttype[1:]
    print(direction)
    return direction

def getAttribute(sorttype):
    # 1. Buchstaben des Strings sorttype
    attribute = sorttype[0]
    if(attribute == 'l'):
        attribute = Lot.lotid
    elif(attribute == 'z'):
        attribute = Lot.state
    elif(attribute == 't'):
        attribute = Tool.tool
    elif(attribute == 's'):
        attribute = Tool.state
    return attribute