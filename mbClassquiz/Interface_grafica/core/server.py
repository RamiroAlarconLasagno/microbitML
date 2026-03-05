# core/server.py
from flask import Flask
from flask_socketio import SocketIO
from core import config

app     = Flask(__name__, template_folder='../apps', static_folder='../apps')
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')
app.config['SECRET_KEY'] = config.SECRET_KEY

_blueprint_activo = None

def registrar_app(blueprint):
    global _blueprint_activo
    # Desregistrar blueprint anterior si existe
    if _blueprint_activo:
        app.blueprints.pop(_blueprint_activo.name, None)
    app.register_blueprint(blueprint)
    _blueprint_activo = blueprint

def run():
    print(f"[Server] http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    socketio.run(app, host=config.FLASK_HOST, port=config.FLASK_PORT,
                 debug=False, use_reloader=False, log_output=False)