# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
# Lot_bew_bearb.py
from mapper import Tool, Lot, PTime, Workflow, ProdFlow
from database_connection import get_database_url, database_connection, database_disconnection
import datetime
import random

def test_if_tool_is_done(tool):
    if(tool.state == "PROC"):
        # in Lot-Tabelle nach Lot suchen, das von dem Tool bearbeitet wird
        lot = session_d.query(Lot).filter(Lot.disptool == tool.tool).first()
        if lot is None:
            # da kein Lot gefunden wurde das von Tool bearbeitet wird, ist das Tool IDLE
            return True # Tool ist fertig (PROC -> IDLE)
        route = lot.route
        oper = lot.oper
        # Suche in Ptime nach Prozesszeit für die Operation der Route und das Tool (für das Lot mit spezifischen Produkt)
        ptime = session_d.query(PTime).filter(PTime.route == route).filter(PTime.oper == oper).filter(PTime.tool == tool.tool).filter(PTime.product == lot.product).first()
        if ptime is None:
            #TODO: Was passiert, wenn Datensätze in PTime fehlen?
            tool.state = "DOWN"
            session_d.add(tool)
            session_d.commit()
            lot.state = "HOLD"
            session_d.add(lot)
            session_d.commit()
            return False

        # Wenn PROCSTART + Prozesszeit (in Sekunden) < aktuelle Zeit, dann ist das Tool fertig
        procstart = datetime.datetime.strptime(str(lot.procstart), '%Y-%m-%d %H:%M:%S.%f')
        # Datum und Zeit, wenn das Tool fertig ist
        finisheddatetime = datetime.timedelta(seconds=ptime.ptime) + procstart

        # aktuelle Zeit ist größer als das Datum und die Zeit, wenn das Tool fertig ist
        if(finisheddatetime < datetime.datetime.now()):
            database_disconnection(session_d)
            return True
        else:
            database_disconnection(session_d)
            return False
    database_disconnection(session_d)
    return False

'''Schauen, ob das Lot, welches eine Maschine bearbeitet, fertig ist'''
def lotop_finished(session_d):
    print("\n*** Checking if a tool is done ***")
    tools = session_d.query(Tool).filter(Tool.state == "PROC").all()
    for tool in tools:
        if test_if_tool_is_done(tool):
            print("Tool " + tool.tool + " is done (PROC -> IDLE)")
            tool.state = "IDLE" 
            # tool nicht in session_d (nur in session_d.query(Tool)), deshalb muss tool in session_d gespeichert werden
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
            # Lot-Informationen zurücksetzen
            lot.disptool = None
            lot.procstart = None
            session_d.commit()
        else:
            print("Tool " + tool.tool + " is not done\n")

'''Maschinen suchen nach einem Lot, das auf diese wartet'''
def tool_searches_for_lots(session_d):
    print(f"\n### Processing Lots ({datetime.datetime.now()}) ###")
    # tools-Liste erzeugen und alle Tools in IDLE-Zustand suchen
    tools = []
    tools = session_d.query(Tool).filter(Tool.state == "IDLE").all()
    # Initialisierung der Liste, die Lots enthält, die auf das Tool warten (für FIFO-Prinzip)
    waiting_lots = []
    for tool in tools:
        #TODO: Einbezug oder Fix von Operationen/Routen, welche keinen PTime-Eintrag haben und so auch keinem Tool zugeordnet werden können
        #Liste an Operationen, die das Tool bearbeiten kann und Routen dazu
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
            #print("There are lots waiting for the tool " + tool.tool + " in IDLE state")
            #sortieren der Lots nach frühster ENTEROPER-Zeit, die bei WAIT neu gesetzt wird (aber in reverse, damit das Lot mit der längsten Wartezeit zuerst bearbeitet wird)
            waiting_lots.sort(key=lambda x: x.enteroper, reverse=True)
            #das Tool, das am längsten wartet, wird ausgewählt
            lot = waiting_lots[0]
            print("Lot " + lot.lotid + " is selected to be processed by tool " + tool.tool)
            lot.state = "PROC"
            lot.disptool = tool.tool
            lot.procstart = datetime.datetime.now()
            session_d.add(lot) 
            session_d.commit()
            # Test, ob das Lot erfolgreich in PROC-Zustand versetzt wurde
            if lot.state == "PROC":
                print("Lot " + lot.lotid + " is PROC now")
            tool.state = "PROC"
            session_d.add(tool)
            session_d.commit()
            # Test, ob das Tool erfolgreich in PROC-Zustand versetzt wurde
            if tool.state == "PROC":
                print("Tool " + tool.tool + " is PROC now\n")
            # Zurücksetzen der Liste, die Lots enthält, die auf das Tool warten für das nächste Tool
            waiting_lots.clear()


'''Schauen, ob ein Lot in OP-COMP-Zustand ist und versetzen des Lot auf nächsten Produktionsschritt'''
def moveLot(session_d):
    print(f"\n### Moving Lots ({datetime.datetime.now()}) ###")
    lots = session_d.query(Lot).filter(Lot.state == "OP_COMP").all()
    for lot in lots:
        route = lot.route
        oper_int = int(lot.oper)
        # Oper = '0100' wird zu '0200' usw... (falls Oper<1000 ist, muss eine 0 vorangestellt werden, damit die Oper-Zahl 4-stellig ist)
        if(oper_int < 1000):
            next_oper = '0' + str(oper_int+100)
        else:
            next_oper = str(oper_int+100)
        # Workflow-Informationen für nächste Operation und Route finden
        next = session_d.query(Workflow).filter(Workflow.route == route).filter(Workflow.oper == next_oper).first()
        # falls keine Workflow-Informationen für nächste Operation gefunden wurden kann das Lot in der gleiche Route nicht weiter bearbeitet werden
        if next is None:
            # Route-Informationen für das Lot finden
            route = session_d.query(ProdFlow).filter(ProdFlow.product == lot.product).filter(ProdFlow.route == route).first()
            newseq = route.seq + 1
            # nächste Route finden
            next_route = session_d.query(ProdFlow).filter(ProdFlow.product == lot.product).filter(ProdFlow.seq == newseq).first()
            # falls keine nächste Route gefunden wurde, ist das Lot fertig
            if next_route is None:
                print("Produktionsfluss von Lot "+ lot.lotid + " ist zu Ende (FIN)\n")
                lot.state = "FIN"
                session_d.add(lot)
                session_d.commit()
                continue
            # erste Operation der Route setzen
            workflows_per_route = session_d.query(Workflow).filter(Workflow.route == next_route.route).all()
            # sortieren nach kleinster oper-Zahl
            min_oper = 10000 # initialisieren mit einer hohen Zahl, da es keine Oper >= 10000 gibt
            for wf in workflows_per_route:
                if(int(wf.oper) < min_oper):
                    min_oper = int(wf.oper)
                    next_oper = wf.oper
            # Route setzen
            lot.route = next_route.route
            session_d.add(lot)
            session_d.commit()
            # Workflow-Informationen für nächste Operation und Route finden
            next = session_d.query(Workflow).filter(Workflow.route == next_route.route).filter(Workflow.oper == next_oper).first()
            # falls keine Workflow-Informationen für nächste Operation gefunden wurden, ist DB nicht konsistent und das Lot wird auf HOLD gesetzt
            if(next is None):
                print("Keine Workflow-Informationen für nächste Route gefunden")
                lot.state = "HOLD"
                session_d.add(lot)
                session_d.commit()
                print("Lot " + lot.lotid + " is HOLD now\n")
                continue
        # nächste Operation setzen
        lot.oper = next.oper

        #Test, ob Mandatory-Flag gesetzt ist (also ob das Lot zwingend in die nächste Operation muss)
        if next.mandatory == 1:
            lot.state = "WAIT"
            lot.enteroper = datetime.datetime.now()
            session_d.add(lot)
            session_d.commit()
            print("Lot " + lot.lotid + " is WAIT now (next operation: " + lot.oper + ")\n")
        else: #falls Los nicht zwingend in nächste Operation muss
            print("Lot " + lot.lotid + " is not mandatory for next operation: " + lot.oper)
            # Random Wert zwischen 1 und 100 für Simulation der Wahrscheinlichkeit
            random_value = random.randint(1, 100)
            #Test, ob random_value kleiner als stepperc (Wsk. für Eintreten der Operation) ist
            #falls ja, wird das Lot in WAIT-Zustand versetzt und geht in die nächste Operation
            if random_value < next.stepperc:
                lot.state = "WAIT"
                lot.enteroper = datetime.datetime.now()
                session_d.add(lot)
                session_d.commit()
                print("Lot " + lot.lotid + " is WAIT now (next operation: " + lot.oper + ")\n")
            #falls nein, wird das Lot noch einmal in Liste für Lot-Moving gebracht um weiter bewegt zu werden
            else:
                # am Ende von lots-Liste wird das Lot nocheinmal angehangen
                lots.append(lot)
                session_d.add(lot)
                session_d.commit()
                print("Lot " + lot.lotid + " skips next operation: " + lot.oper + "\n")

'''Prüfen, ob es Lose gibt, die in WAIT-Zustand sind, aber keine PTime-Einträge für nächste Operation und Route haben'''
def test_if_lots_are_stuck(session_d):
    #alle Lose, die in WAIT-Zustand sind
    lots = session_d.query(Lot).filter(Lot.state == "WAIT").all()
    #Prüfen, ob es für nächste Operation und Route ein PTime-Eintrag gibt
    for lot in lots:
        route = lot.route
        oper = lot.oper
        ptime = session_d.query(PTime).filter(PTime.route == route).filter(PTime.oper == oper).first()
        if ptime is None:
            #falls kein PTime-Eintrag gefunden wurde, ist das Lot in HOLD-Zustand (muss manuell bewegt werden)
            print("Lot " + lot.lotid + " is stuck")
            lot.state = "HOLD"
            session_d.add(lot)
            session_d.commit()

# Main
session_d = database_connection()
lotop_finished(session_d)
tool_searches_for_lots(session_d)
test_if_lots_are_stuck(session_d)
moveLot(session_d)
database_disconnection(session_d)