# los_starten.py
from flask import Blueprint, render_template

los_bearbeiten_bp = Blueprint('los_bearbeiten', __name__)

@los_bearbeiten_bp.route("/los_bearbiten", methods=["GET"])
def los_bearbeiten_page():
    return render_template("los_bearbeiten_page.html")