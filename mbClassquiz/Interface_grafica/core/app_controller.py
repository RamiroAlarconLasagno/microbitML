# core/app_controller.py
import threading
import webbrowser
import sys
from tkinter import messagebox

from core.gui.ventana import Ventana
from core import serial_manager, server, config
from app_registry import APPS

class AppController:
    def __init__(self, root):
        self.root       = root
        self.app_activa = None
        self.ventana    = Ventana(root, APPS)

        self._conectar_eventos()
        self._iniciar_servidor()
        root.after(500, self._detectar_puertos)
        root.protocol("WM_DELETE_WINDOW", self._on_cerrar)

    def _conectar_eventos(self):
        self.ventana.btn_detectar.config(command=self._detectar_puertos)
        self.ventana.btn_conectar.config(command=self._conectar_puerto)
        for app_def in APPS:
            aid = app_def["id"]
            self.ventana.botones_apps[aid].config(
                command=lambda a=aid: self._abrir_app(a))

    def _iniciar_servidor(self):
        threading.Thread(target=server.run, daemon=True).start()

    def _detectar_puertos(self):
        try:
            puertos = serial_manager.detectar_puertos()
            self.ventana.set_puertos([p['port'] for p in puertos])
            if not puertos:
                messagebox.showwarning("Sin puertos", "No se detectaron puertos serie.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _conectar_puerto(self):
        puerto = self.ventana.puerto_seleccionado.get()
        if not puerto:
            messagebox.showwarning("Aviso", "Selecciona un puerto primero.")
            return
        if serial_manager.conectar(puerto):
            self.ventana.set_conectado(True, puerto)
            threading.Thread(target=serial_manager.loop_lectura, daemon=True).start()
        else:
            messagebox.showerror("Error", f"No se pudo conectar a {puerto}")

    def _abrir_app(self, app_id):
        # Detener app anterior
        if self.app_activa:
            self.app_activa.on_stop()
            serial_manager.registrar_callback(None)

        # Instanciar nueva app
        app_def = next(a for a in APPS if a["id"] == app_id)
        self.app_activa = app_def["clase"]()

        # Registrar blueprint y callback
        server.registrar_app(self.app_activa.get_blueprint())
        serial_manager.registrar_callback(self.app_activa.on_message)
        self.app_activa.on_start()

        # Abrir browser
        url = f"http://localhost:{config.FLASK_PORT}/{app_id}/"
        webbrowser.open(url)

    def _on_cerrar(self):
        if messagebox.askokcancel("Salir", "¿Cerrar la aplicación?"):
            if self.app_activa:
                self.app_activa.on_stop()
            serial_manager.desconectar()
            self.root.destroy()
            sys.exit(0)