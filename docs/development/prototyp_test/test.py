from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

def get_cars_data():
    # Verbindungsparameter
    host = "localhost"
    port = 5432
    user = "se-project"
    password = "se-project"

    # Verbindung herstellen
    conn = psycopg2.connect(host=host, port=port, user=user, password=password)

    # Cursor erstellen
    cursor = conn.cursor()

    # cars-Tabelle auslesen
    cursor.execute("SELECT * FROM entities;")

    # Ergebnisse in Liste speichern
    records = cursor.fetchall()

    # Verbindung schließen
    cursor.close()
    conn.close()

    return records

@app.route("/", methods=["GET", "POST"])
def index():
    # Überprüfe, ob der Button gedrückt wurde
    show_data = False
    if request.method == "POST" and "show_data" in request.form:
        show_data = True

    # Daten aus der Funktion abrufen
    records = get_cars_data()

    # HTML-Template rendern und Daten übergeben
    return render_template("index.html", records=records, show_data=show_data)

@app.route("/insert", methods=["POST"])
def insert_data():
    # Verbindungsparameter
    host = "localhost"
    port = 5432
    user = "se-project"
    password = "se-project"

    # Daten aus dem Formular abrufen
    entity = request.form.get("entity")
    class_i = request.form.get("class")
    enabled = request.form.get("enabled")
    note = request.form.get("note")
    state = request.form.get("state")

    # Verbindung herstellen
    conn = psycopg2.connect(host=host, port=port, user=user, password=password)

    # Cursor erstellen
    cursor = conn.cursor()

    # Neuen Datensatz einfügen
    cursor.execute("INSERT INTO entities (entity, class, enabled, note, state) VALUES (%s, %s, %s, %s, %s);", (entity, class_i, enabled, note, state))

    # Transaktion bestätigen
    conn.commit()

    # Verbindung schließen
    cursor.close()
    conn.close()

    # Zurück zur Index-Seite
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)