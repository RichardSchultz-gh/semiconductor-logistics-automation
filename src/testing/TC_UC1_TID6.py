import unittest

import sys
sys.path.insert(0, 'C:\\Users\\pulst\\Documents\\SE_II_Projekt\\i04-projekt-frau-holle\\src')  

from Lot_start import start_lot  # Importiert die Funktion start_lot aus Lot_start.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mapper import Tool, Lot, PTime, Workflow, ProdFlow
from database_connection import get_database_url
from datetime import datetime

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

class UC1_TID6(unittest.TestCase):
    def test_something(self):
        start_date = datetime(2024, 5, 9)

        init_lots = session.query(Lot).filter(Lot.state == "INIT", Lot.startdate == start_date).all()
        print("Lose im Zustand INIT und mit Startdatum", start_date)
        for lot in init_lots:
            print(lot.lotid)

        start_lot()
        wait_lots = session.query(Lot).filter(Lot.state == "WAIT", Lot.startdate == start_date).all()
        print("Lose im Zustand WAIT und mit Startdatum", start_date)
        for lot in wait_lots:
            print(lot.lotid)
        
        self.assertEqual(len(init_lots), len(wait_lots))
        for lot in init_lots:
            self.assertIn(lot, wait_lots)
        

if __name__ == '__main__':
    unittest.main()

