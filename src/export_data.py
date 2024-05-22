from flask import Blueprint, render_template, request, redirect, url_for, session, send_file
from mapper import Lot
from database_connection import get_database_url
from sqlalchemy import create_engine
from los_starten import get_all_lot_ids
from sqlalchemy.orm import sessionmaker
from config import config
import datetime
import csv

export_data_bp = Blueprint('export_data', __name__)

def check_user_session():
    return 'username' in session and session['username'] == config.USER1


def database_disconnection(session_d):
    session_d.close()

@export_data_bp.route("/main/export_data", methods=["GET"])
def export_data_page():
    if check_user_session():
        lotids = get_all_lot_ids()  # alle LotIDs aus Lot abrufen
        lot_id_filter = request.args.get('lot_id_f')
        lot_state_filter = request.args.get('lot_state_f')
        sort_type_Lots = request.args.get('sort')

        session_d = database_connection()

        if lot_id_filter and not lot_state_filter:
            lots = session_d.query(Lot).filter(Lot.lotid == lot_id_filter).order_by(get_sort_order(Lot, sort_type_Lots)).all()
        elif lot_state_filter and not lot_id_filter:
            lots = session_d.query(Lot).filter(Lot.state == lot_state_filter).order_by(get_sort_order(Lot, sort_type_Lots)).all()
        elif lot_id_filter and lot_state_filter:
            lots = session_d.query(Lot).filter(Lot.lotid == lot_id_filter, Lot.state == lot_state_filter).order_by(get_sort_order(Lot, sort_type_Lots)).all()
        else:
            lots = session_d.query(Lot).order_by(get_sort_order(Lot, sort_type_Lots)).all()

        usern = session['username']
        return render_template("export_data_page.html", lots=lots, lotids=lotids, username=usern)
    else:
        return "Unauthorized", 401



def get_sort_order(model, sort_type):
    if sort_type == 'lasc':
        return model.lotid.asc()
    elif sort_type == 'ldesc':
        return model.lotid.desc()
    elif sort_type == 'zasc':
        return model.state.asc()
    elif sort_type == 'zdesc':
        return model.state.desc()
    else:
        return model.lotid.asc()

@export_data_bp.route("/main/export_data", methods=["POST"])
def export_to_csv():
    lot_ids = request.form.getlist('lot_ids')
    if not lot_ids:
        return redirect(url_for('export_data.export_data_page'))

    session_d = database_connection()
    lots = session_d.query(Lot).filter(Lot.lotid.in_(lot_ids)).all()
    database_disconnection(session_d)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")  # Zeitstempel erzeugen
    csv_file = f"CSV/exported_data_{timestamp}.csv"  # Dateiname mit Zeitstempel
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Lot ID", "Priority", "Pieces",  "State", "Product", "Route", "Oper", "Customer", "Order", "Due Date", "Start Date", "Enter Oper", "Proc Start", "Disp Tool"])
        for lot in lots:
            writer.writerow([lot.lotid, lot.priority, lot.pieces, lot.state, lot.product, lot.route, lot.oper, lot.customer, lot.order, lot.duedate, lot.startdate, lot.enteroper, lot.procstart, lot.disptool])

    return send_file(csv_file, as_attachment=True)



def filter_lots_by_id(lot_id_filter, sorttype):
    # Hiermit filtern wir Lose nach Lot-ID
    session = database_connection()
    if(not sorttype):
        lots= session.query(Lot).filter(Lot.lotid==lot_id_filter).all()
        session.close()
        return lots
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter).order_by(attribute.desc()).all()
    session.close()
    return lots

def filter_lots_by_state(lot_state_filter, sorttype):
    # Hiermit filtern wir Lose nach Zustand
    session = database_connection()
    if(not sorttype):
        lots = session.query(Lot).filter(Lot.state==lot_state_filter).all()
        session.close()
        return lots
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        lots = session.query(Lot).filter(Lot.state==lot_state_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        lots = session.query(Lot).filter(Lot.state==lot_state_filter).order_by(attribute.desc()).all()
    session.close()
    return lots

def filter_lots_by_id_state(lot_id_filter, lot_state_filter, sorttype):
    # Hiermit filtern wir Lose nach Lot-ID und Zustand
    session = database_connection()
    if(not sorttype):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.state==lot_state_filter).all()
        session.close()
        return lots
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.state==lot_state_filter).order_by(attribute).all()
    elif(direction == 'desc'):
        lots = session.query(Lot).filter(Lot.lotid==lot_id_filter, Lot.state==lot_state_filter).order_by(attribute.desc()).all()
    session.close()
    return lots

def get_all_lots():
    # Hiermit rufen wir alle Lose aus der Datenbank ab und geben sie zurück
    session = database_connection()
    lots = session.query(Lot).all()
    session.close()
    return lots

def get_all_lots(sorttype):
    # Hiermit rufen wir alle Lose aus der Datenbank ab und geben sie zurück
    session = database_connection()
    if(not sorttype):
        lots = session.query(Lot).all()
        session.close()
        return lots
    direction = getDirection(sorttype)
    attribute = getAttribute(sorttype)
    if(direction == 'asc'):
        lots = session.query(Lot).order_by(attribute).all()
    elif(direction == 'desc'):
        lots = session.query(Lot).order_by(attribute.desc()).all()
    session.close()
    return lots

def database_connection():
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session_d = Session()
    return session_d

def getDirection(sorttype):
    # aus String sorttype 1. Buchstaben entfernen
    direction = sorttype[1:]
    print(direction)
    return direction

def getAttribute(sorttype):
    # 1. Buchstaben des Strings sorttype
    attribute = sorttype[0]
    if(attribute == 'l'):
        attribute = Lot.lotid
    elif(attribute == 'z'):
        attribute = Lot.state
    return attribute

if __name__ == '__main__':
    export_data_bp.run(debug=True)