from flask import Blueprint, render_template, request, redirect, url_for, session
from mapper import Lot, Tool
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

los_bewegen_bp = Blueprint('los_bewegen', __name__)

def check_user_session():
    return 'username' in session and session['username'] == 'user1'

@los_bewegen_bp.route("/main/los_bewegen", methods=["GET"])
def los_bewegen_page():
    if check_user_session():
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
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        db_session = Session()
        lot = db_session.query(Lot).filter(Lot.lotid == lotid).first()
        
        if not lot:
            db_session.close()
            return render_template("los_bewegen_error.html", error_message="Lot ID nicht gefunden")
        
        if lot.state != "OP_COMP":
            db_session.close()
            return render_template("los_bewegen_error.html", error_message="Lot befindet sich nicht im Zustand OP_COMP")
        
        if move_lot_to_next_station(lot, db_session):
            db_session.commit()
            db_session.close()
            return render_template("los_bewegen_success.html", message="Lot erfolgreich bewegt.")
        else:
            db_session.close()
            return render_template("los_bewegen_error.html", error_message="Keine weitere Route verfügbar oder Fehler beim Bewegen des Loses")

    else:
        return "Unauthorized", 401

def move_lot_to_next_station(lot, db_session):
    if lot.state == "OP_COMP":
        next_operation = lot.oper + 100  # Beispiel für die Operationenfolge
        if is_next_operation_available(db_session, lot.route, lot.oper):
            lot.oper = next_operation
            lot.state = "WAIT"
        elif is_next_route_available(db_session, lot.product, lot.route):
            lot.route += 1
            lot.state = "WAIT"
            lot.oper = 100  # Annahme, dass 100 der Start der Operationen auf der neuen Route ist
        else:
            lot.state = "FIN"
        return True
    return False

def is_next_operation_available(db_session, route, current_operation):
    next_operation = current_operation + 100  # Beispiel für die Operationenfolge
    result = db_session.execute(
        "SELECT COUNT(*) FROM WORKFLOW WHERE ROUTE = :route AND OPER = :oper",
        {'route': route, 'oper': str(next_operation)}
    ).scalar()
    return result > 0

def is_next_route_available(db_session, product, current_route):
    result = db_session.execute(
        "SELECT COUNT(*) FROM PRODFLOW WHERE PRODUCT = :product AND ROUTE = :next_route",
        {'product': product, 'next_route': current_route + 1}  # Annahme, dass Routen aufsteigend nummeriert sind
    ).scalar()
    return result > 0

if __name__ == '__main__':
    los_bewegen_bp.run(debug=True)
