# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
# Lot_start.py
from mapper import Tool, Lot, PTime, Workflow, ProdFlow
from database_connection import database_connection, database_disconnection
import datetime

def start_lot(session):
    print(f"\n### Starting Lots ({datetime.datetime.now()}) ###")
    # alle Lose in Zustand INIT prüfen
    lots = session.query(Lot).filter(Lot.state == "INIT").all()
    # Prüfen, ob das Startdatum des Loses erreicht ist (nur Datum, keine Uhrzeit)
    for lot in lots:
        if(lot.startdate <= datetime.datetime.now().date()):
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
            print(f"Lot {lot.lotid} is now in WAIT state (started at {datetime.datetime.now()})")
    session.close()

session = database_connection()
start_lot(session)
database_disconnection(session)

