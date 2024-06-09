# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
import sys
import unittest
# Pfad muss ggf. geändert werden
sys.path.insert(0, 'C:\\Users\\pulst\\Documents\\SE_II_Projekt\\i04-projekt-frau-holle\\src')
#sys.path.insert(0, 'C:\\Users\\marxp\\Documents\\i04-projekt-frau-holle\\src')
#Voraussetzung für diesen Test: kein anderes Los vor TMachineA
import time
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
        #Erstes Test-Los einfügen
        test_lot_data_1 = {
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
        test_lot_1 = Lot(**test_lot_data_1)
        session_d.add(test_lot_1)
        session_d.commit()

        #5 Sekunden schlafen
        time.sleep(5)

        #Zweites Test-Los mit späterem Zeitstempel bei ENTEROPER
        test_lot_data_2 = {
            'lotid': 'TestLotUC45',
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
        test_lot_2 = Lot(**test_lot_data_2)
        session_d.add(test_lot_2)
        session_d.commit()

        #Zustände beider Test-Lose ausgeben
        test_lot_before_1 = session_d.query(Lot).filter_by(lotid='TestLotUC44').first()
        test_lot_before_2 = session_d.query(Lot).filter_by(lotid='TestLotUC45').first()
        print(f"Zustand des ersten Test-Loses: {test_lot_before_1.state}")
        print(f"Zustand des zweiten Test-Loses: {test_lot_before_2.state}")

        #TMachineA auf IDLE setzen
        tool_tmachinea = session_d.query(Tool).filter_by(tool='TMachineA').first()
        tool_tmachinea.state = 'IDLE'
        session_d.commit()

        #tool_searches_for_lots ausführen
        tool_searches_for_lots(session_d)

        #Zustände ausgeben
        test_lot_after_1 = session_d.query(Lot).filter_by(lotid='TestLotUC44').first()
        test_lot_after_2 = session_d.query(Lot).filter_by(lotid='TestLotUC45').first()
        print(f"Zustand des ersten Test-Loses nach tool_searches_for_lots: {test_lot_after_1.state}")
        print(f"Zustand des zweiten Test-Loses nach tool_searches_for_lots: {test_lot_after_2.state}")
        print(f"Zustand von TMachineA nach tool_searches_for_lots: {tool_tmachinea.state}")

        #Test auf: 1. Los wird als 1. bearbeitet
        if test_lot_after_1.state == 'PROC':
            print("Der Test ist erfolgreich.")
            self.assertTrue(True)
        else:
            print("Der Test ist fehlgeschlagen.")
            self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()