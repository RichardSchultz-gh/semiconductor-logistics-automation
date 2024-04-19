# main.py
from flask import Blueprint, render_template, request, redirect, url_for,session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mapper import Tool, Lot
from database_connection import get_database_url


main_bp = Blueprint('main', __name__)

@main_bp.route('/main', methods=['GET'])
def main():
    if 'username' in session and session['username'] == 'user1':
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Base = declarative_base()
        Session = sessionmaker(bind=engine)
        session_d = Session()
        #Anzahl der Tools in der Datenbank
        toolsanzahl = session_d.query(Tool).count()
        toolsidle = session_d.query(Tool).filter(Tool.state == "IDLE").count()
        toolsprod = session_d.query(Tool).filter(Tool.state == "PROD").count()
        toolsmaint = session_d.query(Tool).filter(Tool.state == "MAINT").count()
        toolsdown = session_d.query(Tool).filter(Tool.state == "DOWN").count()

        #Anzahl Lose in Zustand OP_COMP, HOLD, WAIT oder PROC
        lotsopcomp = session_d.query(Lot).filter(Lot.state == "OP_COMP").count()
        lotshold = session_d.query(Lot).filter(Lot.state == "HOLD").count()
        lotswait = session_d.query(Lot).filter(Lot.state == "WAIT").count()
        lotsproc = session_d.query(Lot).filter(Lot.state == "PROC").count()
        WIPA = lotsopcomp + lotshold + lotswait + lotsproc
        lotsfin = session_d.query(Lot).filter(Lot.state == "FIN").count()
        session_d.close()

        return render_template("main.html", username=session['username'], toolsanzahl=toolsanzahl, toolsidle=toolsidle, toolsprod=toolsprod, toolsmaint=toolsmaint, toolsdown=toolsdown, WIPA=WIPA, lotsfin=lotsfin, lotsopcomp=lotsopcomp, lotshold=lotshold)
    else:
        return "Unauthorized", 401  # Zeigen Sie eine Fehlermeldung oder eine Umleitung an


@main_bp.route('/main2', methods=['GET'])
def main2():
    if 'username' in session and session['username'] == 'user2':
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Base = declarative_base()
        Session = sessionmaker(bind=engine)
        session_d = Session()
        #Anzahl der Tools in der Datenbank
        toolsanzahl = session_d.query(Tool).count()
        print(toolsanzahl)
        toolsidle = session_d.query(Tool).filter(Tool.state == "IDLE").count()
        toolsprod = session_d.query(Tool).filter(Tool.state == "PROD").count()
        toolsmaint = session_d.query(Tool).filter(Tool.state == "MAINT").count()
        toolsdown = session_d.query(Tool).filter(Tool.state == "DOWN").count()
        session_d.close()

        #Anzahl Lose in Zustand OP_COMP, HOLD, WAIT oder PROC
        lotsopcomp = session_d.query(Lot).filter(Lot.state == "OP_COMP").count()
        lotshold = session_d.query(Lot).filter(Lot.state == "HOLD").count()
        lotswait = session_d.query(Lot).filter(Lot.state == "WAIT").count()
        lotsproc = session_d.query(Lot).filter(Lot.state == "PROC").count()
        WIPA = lotsopcomp + lotshold + lotswait + lotsproc
        lotsfin = session_d.query(Lot).filter(Lot.state == "FIN").count()
        session_d.close()

        return render_template("main.html", username=session['username'], toolsanzahl=toolsanzahl, toolsidle=toolsidle, toolsprod=toolsprod, toolsmaint=toolsmaint, toolsdown=toolsdown, WIPA=WIPA, lotsfin=lotsfin, lotsopcomp=lotsopcomp, lotshold=lotshold)
    else:
        return "Unauthorized", 401  # Zeigen Sie eine Fehlermeldung oder eine Umleitung an
