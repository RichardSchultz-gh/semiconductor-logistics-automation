# los_bewegen.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from mapper import Lot, Tool
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from los_starten import get_all_lot_ids

los_bewegen_bp = Blueprint('los_bewegen', __name__)

def check_user_session():
    return 'username' in session and session['username'] in ['user1']

@los_bewegen_bp.route("/main/los_bewegen", methods=["GET"])
def los_bewegen_page():
    if check_user_session():
        print("Los bewegen")
        username = session['username']
        # alle Lots aus der Datenbank holen
        lotids= get_all_lot_ids()
        return render_template("los_bewegen_page.html", username=username, lotids=lotids)
    else:
        return "Unauthorized", 401
    
@los_bewegen_bp.route("/main/los_bewegen", methods=["POST"])
def los_bewegen():
    if check_user_session():
        print("Los bewegen")
        username = session['username']
        lotid = request.form.get("lot_id")
        print("Lot ID: " + lotid)

        # lot für die lot_id holen
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        lot = db_session.query(Lot).filter(Lot.lotid == lotid).first()
        db_session.close()

        print(lot.state)

        if(lot.state == "OP_COMP"): # nur Lots im Zustand OP_COMP dürfen bewegt werden
            # lot in die nächste Station bewegen
            move_lot_to_next_station(lot)
            return redirect(url_for('los_bewegen.los_bewegen_page'))
        else:
            return render_template("los_bewegen_error.html", username=username, error_message="Lot  befindet sich nicht im Zustand OP_COMP")
        
    else:
        return "Unauthorized", 401
    
def move_lot_to_next_station(lot):
    # lot in die nächste Station bewegen
    print('TODO: Lot in die nächste Station bewegen')
    return lot