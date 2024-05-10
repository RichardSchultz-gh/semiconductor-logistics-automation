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



"""

Eventuell notw. SQL-Befehle: 

UPDATE workflow
SET stepperc = '99.00'
WHERE route = 'RouteA' AND oper = '0300';

DELETE FROM LOT WHERE lotid='TestLotUC3'  

"""


class UC2_TID2(unittest.TestCase):
    def test_move_lot(self):
        
        #Test-Los in Datenbank einfügen
        test_lot_data = {
            'lotid': 'TestLotUC3',  
            'priority': 44,
            'pieces': 10,
            'state': 'OP_COMP',
            'product': 'TestProductA',
            'route': 'RouteA',
            #setze die Operation vor der Optionalen Operation
            'oper': '0200',  
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
        
        #Ausführungswahrscheinlichkeit analog zu SEPPERC in der Datenbank setzen
        stepprec_compare = 20  
        
        #Optionale Operation laut workflow
        state_compare = '0300'  

        #Liste zum Zählen der Häufigkeit der optionalen Operation
        optional_operations = []

        #100 Mal Move Lot
        for _ in range(100):
            
            #Print Test-Los
            current_lot = session_d.query(Lot).filter(Lot.lotid == 'TestLotUC3').first()
            print(f"Ausgabe TC | Lot ID: {current_lot.lotid}, Operation: {current_lot.oper}, Route: {current_lot.route}, State: {current_lot.state}")

            #Ausführung der Testfunktion MoveLot
            moveLot(session_d)

            #Aktuelle Operation des Test-Loses abfragen und der Liste anhängen
            optional_operations.append(current_lot.oper)

            #Status und Operation wieder vor die Optionale Operation setzen
            current_lot.state = 'OP_COMP'
            current_lot.oper = '0200'
            session_d.commit()

        #Zähle die Häufigkeit der optionalen Operation
        counter_optional_operation = optional_operations.count(state_compare)

        #Ausgabe der erwarteten und tatsächlichen Häufigkeit
        print(f"Tatsächliche Anzahl Ausführungen: {counter_optional_operation}")
        print(f"Erwartete Anzahl an Ausführungen: {stepprec_compare}")

        #Vergleich, ob die erwartete Wahrscheinlich +/-10% erreicht wird
        self.assertTrue(stepprec_compare - 10 < counter_optional_operation < stepprec_compare + 10)

if __name__ == '__main__':
    unittest.main()