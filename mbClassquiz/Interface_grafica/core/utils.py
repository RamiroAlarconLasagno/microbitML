# core/utils.py
import os
from datetime import datetime

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def crear_directorio_data():
    os.makedirs('data', exist_ok=True)