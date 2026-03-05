# apps/classquiz/socketio_manager.py
import socketio as sio_client
import time
from threading import Thread

_pregunta_actual   = None
_opciones_actuales = []

def conectar_dispositivo(device_id, info, url, pin, estado):
    nombre  = info.get('nombre', device_id[:8])
    cliente = sio_client.Client(reconnection=True, reconnection_attempts=5)

    @cliente.event
    def connect():
        cliente.emit('join_game', {'username': nombre, 'game_pin': pin,
                                   'captcha': None, 'custom_field': None})

    @cliente.event
    def disconnect():
        if device_id in estado['dispositivos']:
            estado['dispositivos'][device_id]['conectado'] = False

    @cliente.on('joined_game')
    def on_joined(data):
        estado['dispositivos'][device_id]['conectado'] = True
        estado['dispositivos'][device_id]['estado']    = 'online'

    @cliente.on('set_question_number')
    def on_pregunta(data):
        global _pregunta_actual, _opciones_actuales
        # Solo el primer dispositivo actualiza el estado global
        if list(estado['dispositivos'].keys())[0] == device_id:
            _pregunta_actual   = data.get('question_index', 0)
            answers            = data.get('question', {}).get('answers', [])
            _opciones_actuales = [a.get('answer', '') for a in answers] or ['A','B','C','D']

    @cliente.on('time_sync')
    def on_time_sync(data):
        cliente.emit('echo_time_sync', data)

    estado['dispositivos'][device_id]['cliente'] = cliente

    try:
        cliente.connect(url, transports=['websocket', 'polling'])
        time.sleep(2)
    except Exception as e:
        print(f"[SocketIO] Error conectando {nombre}: {e}")

def conectar_todos(estado):
    url = estado['url']
    pin = estado['pin']
    for idx, (device_id, info) in enumerate(estado['dispositivos'].items()):
        if not info.get('cliente'):
            Thread(target=conectar_dispositivo,
                   args=(device_id, info, url, pin, estado),
                   daemon=True).start()
            time.sleep(0.5)

def desconectar_todos(estado):
    for device_id, info in list(estado['dispositivos'].items()):
        cliente = info.get('cliente')
        if cliente:
            try:
                cliente.disconnect()
            except:
                pass
        info['cliente']   = None
        info['conectado'] = False

def enviar_respuesta(device_id, respuesta_lista, estado):
    global _pregunta_actual, _opciones_actuales
    info    = estado['dispositivos'].get(device_id, {})
    cliente = info.get('cliente')
    if not cliente or not info.get('conectado'):
        return

    # Mapear letras a texto de opcion
    letras = ['A', 'B', 'C', 'D']
    textos = []
    for letra in respuesta_lista:
        if letra in letras:
            idx = letras.index(letra)
            textos.append(_opciones_actuales[idx] if idx < len(_opciones_actuales) else letra)

    answer_text = textos[0] if len(textos) == 1 else ','.join(textos)

    try:
        cliente.emit('submit_answer', {
            'question_index': _pregunta_actual,
            'answer': answer_text
        })
    except Exception as e:
        print(f"[SocketIO] Error enviando respuesta: {e}")