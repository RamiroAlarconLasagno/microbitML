# app_registry.py
from apps.monitor.app import MonitorApp
from apps.classquiz.app import ClassquizApp

APPS = [
    {"id": "monitor",   "label": "🔍 Monitor USB", "clase": MonitorApp},
    {"id": "classquiz", "label": "🌐 ClassQuiz",   "clase": ClassquizApp},
]