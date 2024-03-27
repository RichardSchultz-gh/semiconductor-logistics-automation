# los_starten.py
from flask import Blueprint, render_template

los_starten_bp = Blueprint('los_starten', __name__)

@los_starten_bp.route("/los_starten", methods=["GET"])
def los_starten_page():
    return render_template("los_starten_page.html")