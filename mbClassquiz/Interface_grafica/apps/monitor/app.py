# apps/monitor/app.py
from flask import Blueprint, render_template
from flask_socketio import emit
from core.base_app import BaseApp
from core.server import socketio
from core import utils

class MonitorApp(BaseApp):
    id    = "monitor"
    label = "🔍 Monitor USB"

    def get_blueprint(self):
        bp = Blueprint('monitor', __name__,
                       template_folder='templates',
                       url_prefix='/monitor')

        @bp.route('/')
        def index():
            return render_template('monitor/index.html')

        return bp

    def on_start(self):
        print("[Monitor] Iniciado")

    def on_stop(self):
        print("[Monitor] Detenido")

    def on_message(self, msg: dict):
        socketio.emit('usb_message', {
            'msg': msg,
            'timestamp': utils.timestamp()
        })