from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from mapper import Tool, Lot, PTime, Workflow, ProdFlow, Entities
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
from database_connection import get_database_url
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import config
import csv
from io import StringIO

import_data_bp = Blueprint('import_data', __name__)

def check_user_session():
    return 'username' in session and session['username'] == config.USER1

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@import_data_bp.route('/import', methods=['GET', 'POST'])
def import_data():
    if check_user_session():
        if request.method == 'POST':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                csv_data = file.stream.read().decode("utf-8")
                import_from_csv(csv_data, file.filename)
                flash('File successfully imported')
                return redirect(url_for('import_data.import_data'))
            
        usern = session['username']
        return render_template('import_data.html', username=usern)
    else:
        return "Unauthorized", 401

def import_from_csv(csv_data, filename):
    class_name = None
    if filename.startswith('Tool'):
        class_name = 'Tool'
    elif filename.startswith('Lot'):
        class_name = 'Lot'
    elif filename.startswith('ProdFlow'):
        class_name = 'ProdFlow'
    elif filename.startswith('Entities'):
        class_name = 'Entities'
    elif filename.startswith('PTime'):
        class_name = 'PTime'
    elif filename.startswith('Workflow'):
        class_name = 'Workflow'

    if class_name is None:
        flash(f'Class not supported for import from filename: {filename}')
        return

    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    class_mapping = {
        'Tool': Tool,
        'Entities': Entities,
        'Lot': Lot,
        'ProdFlow': ProdFlow,
        'PTime': PTime,
        'Workflow': Workflow
    }

    class_to_add = class_mapping.get(class_name)
    if class_to_add is None:
        return f'Class {class_name} not supported for import'

    csv_file = StringIO(csv_data)
    reader = csv.DictReader(csv_file)
    added_count = 0

    for row in reader:
        try:
            for key in row:
                if row[key] == '':
                    row[key] = None
            instance = class_to_add(**row)
            session.add(instance)
            session.commit()
            added_count += 1
        except IntegrityError as e:
            session.rollback()
            flash(f'IntegrityError: {str(e.orig)}')
        except DataError as e:
            session.rollback()
            flash(f'DataError: {str(e.orig)}')
        except OperationalError as e:
            session.rollback()
            flash(f'OperationalError: {str(e.orig)}')
        except Exception as e:
            session.rollback()
            flash(f'Unexpected error: {str(e)}')

    session.close()
    return f'{added_count} entries were successfully added to the {class_name} table.'



def add_instance(model_class, data):
    engine = create_engine(get_database_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        instance = model_class(**data)
        session.add(instance)
        session.commit()
        flash(f'{model_class.__name__} added successfully.')
    except IntegrityError:
        session.rollback()
        flash(f'Duplicate entry for {model_class.__name__}')
    except DataError:
        session.rollback()
        flash(f'Invalid data format for {model_class.__name__}')
    except Exception as e:
        session.rollback()
        flash(f'Error adding {model_class.__name__}: {e}')
    finally:
        session.close()

@import_data_bp.route('/add_entity', methods=['POST'])
def add_entity():
    data = request.form.to_dict()
    add_instance(Entities, data)
    return redirect(url_for('import_data.import_data'))

@import_data_bp.route('/add_lot', methods=['POST'])
def add_lot():
    data = request.form.to_dict()
    add_instance(Lot, data)
    return redirect(url_for('import_data.import_data'))

@import_data_bp.route('/add_prodflow', methods=['POST'])
def add_prodflow():
    data = request.form.to_dict()
    add_instance(ProdFlow, data)
    return redirect(url_for('import_data.import_data'))

@import_data_bp.route('/add_ptime', methods=['POST'])
def add_ptime():
    data = request.form.to_dict()
    add_instance(PTime, data)
    return redirect(url_for('import_data.import_data'))

@import_data_bp.route('/add_tool', methods=['POST'])
def add_tool():
    data = request.form.to_dict()
    add_instance(Tool, data)
    return redirect(url_for('import_data.import_data'))

@import_data_bp.route('/add_workflow', methods=['POST'])
def add_workflow():
    data = request.form.to_dict()
    add_instance(Workflow, data)
    return redirect(url_for('import_data.import_data'))

if __name__ == '__main__':
    import_data_bp.run(debug=True)
