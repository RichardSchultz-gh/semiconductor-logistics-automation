import unittest
import sys
# Pfad muss ggf. geändert werden
sys.path.insert(0, 'C:\\Users\\pulst\\Documents\\SE_II_Projekt\\i04-projekt-frau-holle\\src')

from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mapper import Lot
from Lot_bew_bearb import moveLot
from database_connection import get_database_url

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session_d = Session()

class UC2_TID2(unittest.TestCase):
    def test_case_TID1(self):
        
        #Test-Los in Datenbank einfügen (Voraussetzung: sonstige Testdatensätze (PRODFLOW etc. sind vorhanden))
        test_lot_data = {
            'lotid': 'TestLotUC2',
            'priority': 44,
            'pieces': 10,
            'state': 'OP_COMP',
            'product': 'TestProductA',
            'route': 'RouteA',
            'oper': '0100',
            'customer': 'TestCustomer',
            'duedate': datetime(2024, 7, 6),
            'startdate': datetime(2024, 2, 2),
            'enteroper': None,
            'procstart': None,
            'disptool': None
        }
        test_lot = Lot(**test_lot_data)
        session_d.add(test_lot)
        session_d.commit()

        state = 'OP_COMP'

        #while state != 'FIN':
        for _ in range(6):
            #Ausgabe des Test-Loses
            current_lot = session_d.query(Lot).filter(Lot.lotid == 'TestLotUC2').first()
            print(f"Ausgabe TC | Lot ID: {current_lot.lotid}, Operation {current_lot.oper}, Route: {current_lot.route}, State: {current_lot.state}")

           #Ausführung moveLot
            moveLot(session_d)

            #Ausgabe des Test-Loses
            current_lot = session_d.query(Lot).filter(Lot.lotid == 'TestLotUC2').first()
            print(f"Ausgabe TC | Lot ID: {current_lot.lotid}, Operation: {current_lot.oper}, Route: {current_lot.route}, State: {current_lot.state}")

            #Zustand auf OP_COMP setzen
            current_lot.state = 'OP_COMP'
            session_d.commit()

            #Zustand aktualisieren
            state = current_lot.state

        print("Ausgabe TC | Das Los hat erfolgreich den Fertigungsprozess durchlaufen.")

if __name__ == '__main__':
    unittest.main()
