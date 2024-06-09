# SE Projekt Frau Holle
# Team I04 - Nils Generlich, Yannik-Joel Herrchen, Nico Kroll, Paul Marx, Richard Schulze, Marlene Winter
# MIT Lizenz 2024 
import unittest

#Pfad muss ggf. geändert werden
import sys
sys.path.insert(0, 'C:\\Users\\pulst\\Documents\\SE_II_Projekt\\i04-projekt-frau-holle\\src')  

from Lot_start import start_lot  
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mapper import Lot
from database_connection import get_database_url
from datetime import datetime

DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

#Test der Timer-Funktion lot_start; Datumsvariable muss gesetzt werden & Lose müssen sinnvoll ausgewählt werden
class UC1_TID6(unittest.TestCase):
    def test_case_TID6(self):
        #setze Startdatum
        start_date = datetime(2024, 5, 8)

        #hole alle Lose, die den Zustand INIT aufweisen und dem Startdatum entsprechen
        init_lots = session.query(Lot).filter(Lot.state == "INIT", Lot.startdate == start_date).all()
        
        #Ausgabe zur Kontrolle
        print("Lose im Zustand INIT und mit Startdatum", start_date)
        for lot in init_lots:
            print(lot.lotid)

        #Ausführung der Timer-Funktion start_lot()
        start_lot()
        
        #hole alle Lose, die den Zustand WAIT aufweisen und dem Startdatum entsprechen
        wait_lots = session.query(Lot).filter(Lot.state == "WAIT", Lot.startdate == start_date).all()
        
        #Ausgabe zur Kontrolle
        print("Lose im Zustand WAIT und mit Startdatum", start_date)
        for lot in wait_lots:
            print(lot.lotid)
        
        #Test, ob alle INIT-Lose auf WAIT gesetzt worden sind
        self.assertEqual(len(init_lots), len(wait_lots))
        for lot in init_lots:
            self.assertIn(lot, wait_lots)
        

if __name__ == '__main__':
    unittest.main()

