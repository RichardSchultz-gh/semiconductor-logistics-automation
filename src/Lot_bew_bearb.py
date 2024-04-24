from mapper import Tool, Lot, PTime, Workflow, ProdFlow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_connection import get_database_url
import datetime

def test_if_tool_is_done(tool):
    if(tool.state == "PROC"):
        # in Lot-Tabelle nach Lot suchen, das von dem Tool bearbeitet wird
        lot = session_d.query(Lot).filter(Lot.disptool == tool.tool).first()
        if lot is None:
            tool.state = "DOWN"
            session_d.add(tool)
            session_d.commit()
            return False
        route = lot.route
        oper = lot.oper
        # Suche in Ptime nach Prozesszeit für die Operation der Route
        ptime = session_d.query(PTime).filter(PTime.route == route).filter(PTime.oper == oper).first()
        print("Prozesszeit: " + str(ptime.ptime))

        # Wenn PROCSTART + Prozesszeit (in Stunden) < aktuelle Zeit, dann ist das Tool fertig
        procstart = lot.procstart
        print("Startzeit: " + str(procstart))
        finisheddatetime = datetime.timedelta(hours=ptime.ptime) + procstart
        print("Fertig um: " + str(finisheddatetime))

        # aktuelle Zeit
        print("Aktuelle Zeit: " + str(datetime.datetime.now()))
        if(finisheddatetime < datetime.datetime.now()):
            database_disconnection(session_d)
            return True
        else:
            database_disconnection(session_d)
            return False
    database_disconnection(session_d)
    return False


def database_connection():
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session_d = Session()
    return session_d

def database_disconnection(session_d):
    session_d.close()

'''Schauen, ob das Lot, welches eine Maschine bearbeitet, fertig ist'''
session_d = database_connection()
tools = session_d.query(Tool).filter(Tool.state == "PROC").all()
for tool in tools:
    if test_if_tool_is_done(tool):
        print("Tool " + tool.tool + " is done")
        tool.state = "IDLE" 
        # tool nicht in session_d ist (nur in session_d.query(Tool)), deshalb muss tool in session_d gespeichert werden
        session_d.add(tool)
        session_d.commit()
        # Lot-Tabelle aktualisieren
        lot = session_d.query(Lot).filter(Lot.disptool == tool.tool).first()
        lot.state = "OP_COMP"
        # TODO: Zu einer bestimmten Prozentzahl ist das Lot Ausschuss
        lot.disptool = None
        lot.procstart = None
        session_d.commit()
    else:
        print("Tool " + tool.tool + " is not done")


'''Maschinen suchen nach einem Lot, das auf diese wartet'''
# tools-Liste leeren und alle Tools in IDLE-Zustand suchen
tools = []
tools = session_d.query(Tool).filter(Tool.state == "IDLE").all()
waiting_lots = []
for tool in tools:
    #Liste an Operationen, die das Tool bearbeiten kann und Routen dazu
    route_oper_list = session_d.query(PTime).filter(PTime.tool == tool.tool).all()
    # nach Lot suchen, die auf das Tool warten
    for route_oper in route_oper_list:
        lot = session_d.query(Lot).filter(Lot.route == route_oper.route).filter(Lot.oper == route_oper.oper).filter(Lot.state == "WAIT").first()
        if lot is not None:
            waiting_lots.append(lot)

    # wenn es keine Lots gibt, die auf das Tool warten, dann wird das Tool in den IDLE-Zustand versetzt
    if len(waiting_lots) == 0:
        for tool in tools:
            tool.state = "IDLE"
            session_d.add(tool)
            session_d.commit()
            print("Tool " + tool.tool + " is IDLE now")
    else:
        print("There are lots waiting for tools")
        #sortieren der Lots nach frühster ENTEROPER-Zeit, die bei WAIT neu gesetzt wird
        waiting_lots.sort(key=lambda x: x.enteroper)
        #das Tool, das am längsten wartet, wird ausgewählt
        lot = waiting_lots[0]
        print("Lot " + lot.lotid + " is selected")
        lot.state = "PROC"
        lot.disptool = tool.tool
        lot.procstart = datetime.datetime.now()
        session_d.add(lot) 
        session_d.commit()
        tool.state = "PROC"
        session_d.add(tool)
        session_d.commit()
        print("Tool " + tool.tool + " is PROC now")
        print("Lot " + lot.lotid + " is PROC now")
        waiting_lots.clear()

'''Schauen, ob ein Lot in OP-COMP-Zustand ist und versetzen des Lot auf nächsten Produktionsschritt'''
lots = session_d.query(Lot).filter(Lot.state == "OP_COMP").all()
for lot in lots:
    route = lot.route
    oper_int = int(lot.oper)
    #Oper = '0100' soll zu '0200' werden usw...
    if(oper_int < 1000):
        next_oper = '0' + str(oper_int+100)
    else:
        next_oper = str(oper_int+100)
    next = session_d.query(Workflow).filter(Workflow.route == route).filter(Workflow.oper == next_oper).first()
    if next is None:
        route = session_d.query(ProdFlow).filter(ProdFlow.product == lot.product).filter(ProdFlow.route == route).first()
        newseq = route.seq + 1
        next_route = session_d.query(ProdFlow).filter(ProdFlow.product == lot.product).filter(ProdFlow.seq == newseq).first()
        if next_route is None:
            print("Produktionsfluss ist zu Ende")
            lot.state = "FIN"
            session_d.add(lot)
            session_d.commit()
            continue
        next_oper = '0100'
        lot.route = next_route.route
        session_d.add(lot)
        session_d.commit()
        next = session_d.query(Workflow).filter(Workflow.route == next_route.route).filter(PTime.oper == next_oper).first()
    lot.oper = next.oper
    lot.state = "WAIT"
    lot.enteroper = datetime.datetime.now()
    session_d.add(lot)
    session_d.commit()

database_disconnection(session_d)