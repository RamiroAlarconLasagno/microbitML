# core/base_app.py
from flask import Blueprint

class BaseApp:
    id    = "base"
    label = "Base"

    def get_blueprint(self) -> Blueprint:
        raise NotImplementedError

    def on_start(self):
        pass

    def on_stop(self):
        pass

    def on_message(self, msg: dict):
        pass