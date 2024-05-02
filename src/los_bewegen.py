# los_bewegen.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from mapper import Lot, Tool
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from los_starten import get_all_lot_ids

los_bewegen_bp = Blueprint('los_bewegen', __name__)

def check_user_session():
    return 'username' in session and session['username'] == 'user1'

@los_bewegen_bp.route("/main/los_bewegen", methods=["GET"])
def los_bewegen_page():
    if check_user_session():
        print("Los bewegen")
        username = session['username']
        #Alle Lots aus Datenbank holen
        lotids = get_all_lot_ids()
        return render_template("los_bewegen_page.html", username=username, lotids=lotids)
    else:
        return "Unauthorized", 401
    
@los_bewegen_bp.route("/main/los_bewegen", methods=["POST"])
def los_bewegen():
    if check_user_session():
        lotid = request.form.get("lot_id")
        username = session['username']
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        lot = db_session.query(Lot).filter(Lot.lotid == lotid).first()
        
        if lot is None:
            return render_template("los_bewegen_error.html", username=username, error_message="Lot ID nicht gefunden")
        
        if lot.state == "OP_COMP":
            move_lot_to_next_station(lot)
            db_session.commit()
            db_session.close()
            return redirect(url_for('los_bewegen.los_bewegen_page'))
        else:
            db_session.close()
            return render_template("los_bewegen_error.html", username=username, error_message="Lot befindet sich nicht im Zustand OP_COMP")
        
    else:
        return "Unauthorized", 401
    
def move_lot_to_next_station(lot):
    if lot.state == "OP_COMP":
        next_operation = lot.operation + 100
        if is_next_operation_available(lot.route, next_operation):
            lot.operation = next_operation
            lot.state = "WAIT"
        else:
            next_route = lot.route + 1
            if is_next_route_available(lot.product, next_route):
                lot.route = next_route
                lot.state = "WAIT"
                lot.operation = 100
            else:
                lot.state = "FIN"
    else:
        print("Los ist nicht im Zustand OP_COMP")

def is_next_operation_available(route, next_operation):
    return True 

def is_next_route_available(product, next_route):
    return True 
