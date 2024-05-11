import unittest
import sys
# Pfad muss ggf. geändert werden
sys.path.insert(0, 'C:\\Users\\pulst\\Documents\\SE_II_Projekt\\i04-projekt-frau-holle\\src')
#sys.path.insert(0, 'C:\\Users\\marxp\\Documents\\i04-projekt-frau-holle\\src')
#Voraussetzung für diesen Test: kein anderes Los vor TMachineA

import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mapper import Lot, Tool
from Lot_bew_bearb import tool_searches_for_lots, lotop_finished
from database_connection import get_database_url

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session_d = Session()

class UC3_TID1(unittest.TestCase):
    def test_case_TID1(self):
        #Test-Los einfügen
        test_lot_data = {
            'lotid': 'TestLotUC44',
            'priority': 44,
            'pieces': 10,
            'state': 'WAIT',
            'product': 'TestProductA',
            'route': 'RouteA',
            'oper': '0100',
            'customer': 'TestCustomer',
            'duedate': datetime.datetime(2024, 7, 6),
            'startdate': datetime.datetime(2024, 2, 2),
            'enteroper': datetime.datetime.now(),  
            'procstart': None,
            'disptool': None
        }
        test_lot = Lot(**test_lot_data)
        session_d.add(test_lot)
        session_d.commit()

        #Setze TMachineA auf IDLE
        tool_tmachinea = session_d.query(Tool).filter_by(tool='TMachineA').first()
        tool_tmachinea.state = 'IDLE'
        session_d.commit()

        #Zustände ausgeben
        test_lot_after = session_d.query(Lot).filter_by(lotid='TestLotUC44').first()
        print(f"Zustand des Test-Loses VOR Ausführung von lotop_finished: {test_lot_after.state}")
        print(f"Zustand von TMachineA VOR Ausführung von lotop_finished: {tool_tmachinea.state}")


        #Führe die Funktion lotop_finished aus -> für Start der Bearbeitung
        tool_searches_for_lots(session_d)
        
        #warte 20 Sekunden (ptime=15 Sekunden)
        import time
        time.sleep(20)
        
        #Führe die Funktion lotop_finished aus -> für Prüfung, ob Bearbeitung beendet ist
        lotop_finished(session_d)

        #Zustände erneut ausgeben
        test_lot_after = session_d.query(Lot).filter_by(lotid='TestLotUC44').first()
        print(f"Zustand des Test-Loses nach Ausführung von lotop_finished: {test_lot_after.state}")
        print(f"Zustand der Maschine nach Ausführung von lotop_finished: {tool_tmachinea.state}")

        #Prüfung, ob Test bestanden ist und Produktion erfoglreich druchlaufen worden istapp
        if tool_tmachinea.state == 'IDLE' and test_lot_after.state in ['SCRAP', 'HOLD', 'OP_COMP']:
            print("Der Test ist erfolgreich.")
            self.assertTrue(True)
        else:
            print("Der Test ist fehlgeschlagen.")
            self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()