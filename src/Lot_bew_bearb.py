from mapper import Tool, Lot, PTime, Workflow, ProdFlow
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_connection import get_database_url
import datetime
import random

def test_if_tool_is_done(tool):
    if(tool.state == "PROC"):
        # in Lot-Tabelle nach Lot suchen, das von dem Tool bearbeitet wird
        lot = session_d.query(Lot).filter(Lot.disptool == tool.tool).first()
        if lot is None:
            tool.state = "IDLE" #da kein Lot gefunden wurde das von Tool bearbeitet wird, ist das Tool IDLE
            session_d.add(tool)
            session_d.commit()
            return False
        route = lot.route
        oper = lot.oper
        # Suche in Ptime nach Prozesszeit für die Operation der Route und das Tool (für das Lot mit spezifischen Produkt)
        ptime = session_d.query(PTime).filter(PTime.route == route).filter(PTime.oper == oper).filter(PTime.tool == tool.tool).filter(PTime.product == lot.product).first()
        if ptime is None:
            #TODO: Was passiert, wenn Datensätze in PTime fehlen?
            tool.state = "DOWN"
            session_d.add(tool)
            session_d.commit()
            lot.state = "SCRAP"
            session_d.add(lot)
            session_d.commit()
            return False

        # Wenn PROCSTART + Prozesszeit (in Sekunden) < aktuelle Zeit, dann ist das Tool fertig
        #konvertiere procstart in datetime
        procstart = datetime.datetime.strptime(str(lot.procstart), '%Y-%m-%d %H:%M:%S.%f')
        # muss auch mit Jahreszahl gemacht werden, weil die Prozesszeit auch in Jahren sein kann
        finisheddatetime = datetime.timedelta(seconds=ptime.ptime) + procstart

        # aktuelle Zeit
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
def lotop_finished(session_d):
    print("Checking if a tool is done")
    tools = session_d.query(Tool).filter(Tool.state == "PROC").all()
    for tool in tools:
        if test_if_tool_is_done(tool):
            print("Tool " + tool.tool + " is done (PROC -> IDLE)")
            tool.state = "IDLE" 
            # tool nicht in session_d ist (nur in session_d.query(Tool)), deshalb muss tool in session_d gespeichert werden
            session_d.add(tool)
            session_d.commit()
            # Lot-Tabelle aktualisieren
            lot = session_d.query(Lot).filter(Lot.disptool == tool.tool).first()
            lot.state = "OP_COMP"
            print("Lot " + lot.lotid + " is OP_COMP now\n")
            # TODO: Zu einer bestimmten Prozentzahl ist das Lot Ausschuss:
            '''
            # zu 5% geht es in Zustand SCRAP und zu 10% in Zustand HOLD
            if random.randint(1, 100) <= 5:
                lot.state = "SCRAP"
            elif random.randint(1, 100) <= 10:
                lot.state = "HOLD"
            else:
                lot.state = "OP_COMP"
            '''
            lot.disptool = None
            lot.procstart = None
            session_d.commit()
        else:
            print("Tool " + tool.tool + " is not done\n")

'''Maschinen suchen nach einem Lot, das auf diese wartet'''
#TODO: Laufzeitoptimierung
def tool_searches_for_lots(session_d):
    print("Searching for tools that are IDLE and waiting for lots")
    # tools-Liste erzeugen und alle Tools in IDLE-Zustand suchen
    tools = []
    tools = session_d.query(Tool).filter(Tool.state == "IDLE").all()
    waiting_lots = []
    for tool in tools:
        #Liste an Operationen, die das Tool bearbeiten kann und Routen dazu
        #TODO: Einbezug oder Fix von Operationen/Routen, welche keinen PTime-Eintrag haben und so auch keinem Tool zugeordnet werden können
        route_oper_list = session_d.query(PTime).filter(PTime.tool == tool.tool).all()
        # nach Lot suchen, die auf das Tool warten
        for route_oper in route_oper_list:
            lot = session_d.query(Lot).filter(Lot.route == route_oper.route).filter(Lot.oper == route_oper.oper).filter(Lot.state == "WAIT").first()
            if lot is not None:
                waiting_lots.append(lot)

        # wenn es keine Lots gibt, die auf das Tool warten, dann bleibt das Tool IDLE
        if len(waiting_lots) == 0:
            #print("Tool " + tool.tool + " keep being IDLE, because there are no lots waiting for it\n")
            continue
        else:
            print("There are lots waiting for the tool " + tool.tool + " in IDLE state")
            #sortieren der Lots nach frühster ENTEROPER-Zeit, die bei WAIT neu gesetzt wird (aber in reverse)
            waiting_lots.sort(key=lambda x: x.enteroper, reverse=True)
            #das Tool, das am längsten wartet, wird ausgewählt
            lot = waiting_lots[0]
            print("Lot " + lot.lotid + " is selected to be processed by tool " + tool.tool)
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
                print("Tool " + tool.tool + " is PROC now\n")
            waiting_lots.clear()


'''Schauen, ob ein Lot in OP-COMP-Zustand ist und versetzen des Lot auf nächsten Produktionsschritt'''
def moveLot(session_d):
    print("Checking if a lot is in OP_COMP state")
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
                print("Produktionsfluss von Lot"+ lot.lot + "ist zu Ende")
                lot.state = "FIN"
                session_d.add(lot)
                session_d.commit()
                continue
            #Erste Operation der Route setzen
            workflows_per_route = session_d.query(Workflow).filter(Workflow.route == next_route.route).all()
            # sortieren nach kleinster oper-Zahl (zuerst in INT-Wert umwandeln)
            min_oper = 10000
            for wf in workflows_per_route:
                if(int(wf.oper) < min_oper):
                    min_oper = int(wf.oper)
                    next_oper = wf.oper
            lot.route = next_route.route
            session_d.add(lot)
            session_d.commit()
            next = session_d.query(Workflow).filter(Workflow.route == next_route.route).filter(Workflow.oper == next_oper).first()
        lot.oper = next.oper

        #Test, ob Mandatory-Flag gesetzt ist
        if next.mandatory == 1:
            lot.state = "WAIT"
            lot.enteroper = datetime.datetime.now()
            session_d.add(lot)
            session_d.commit()
            print("Lot " + lot.lotid + " is WAIT now (next operation: " + lot.oper + ")")
        else: #falls Los nicht zwingend in nächste Operation muss
            print("Lot " + lot.lotid + " is not mandatory for next operation: " + lot.oper)
            # erzeuge Random Wert zwischen 1 und 100 für Simulation der Wahrscheinlichkeit
            random_value = random.randint(1, 100)
            #Test, ob random_value kleiner als stepperc ist
            if random_value < next.stepperc:
                lot.state = "WAIT"
                lot.enteroper = datetime.datetime.now()
                session_d.add(lot)
                session_d.commit()
                print("Lot " + lot.lotid + " is WAIT now (next operation: " + lot.oper + ")")
            else:
                # am Ende von lots-Liste wird das Lot nocheinmal angehangen
                lots.append(lot)
                session_d.add(lot)
                session_d.commit()
                print("Lot " + lot.lotid + " skips next operation: " + lot.oper)

def test_if_lots_are_stuck(session_d):
    #alle Lose, die in WAIT-Zustand sind
    lots = session_d.query(Lot).filter(Lot.state == "WAIT").all()
    #Prüfen, ob es für nächste Operation und Route ein PTime-Eintrag gibt
    for lot in lots:
        route = lot.route
        oper = lot.oper
        ptime = session_d.query(PTime).filter(PTime.route == route).filter(PTime.oper == oper).first()
        if ptime is None:
            print("Lot " + lot.lotid + " is stuck")
            lot.state = "SCRAP"
            session_d.add(lot)
            session_d.commit()
        #else:
        #    print("Lot " + lot.lotid + " is not stuck")

# Main
session_d = database_connection()
lotop_finished(session_d)
tool_searches_for_lots(session_d)
test_if_lots_are_stuck(session_d)
moveLot(session_d)
database_disconnection(session_d)