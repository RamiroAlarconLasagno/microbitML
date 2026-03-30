---
title: mbClassquiz — Documentación técnica
description: Arquitectura, protocolos y componentes internos del sistema mbClassquiz
---

# mbClassquiz — Documentación técnica

Documentación interna del sistema. Para la guía de uso en el aula, ver el [README de la actividad](README.md).

---

## Arquitectura

```
DOCENTE (ClassQuiz web)
    ↕ Socket.IO
INTERFAZ GRÁFICA (PC, Python/Flask)
    ↕ USB Serial (115200 baud)
CONCENTRADOR (micro:bit V2)
    ↕ Radio 2.4GHz (canal 7)
ALUMNOS (micro:bits V2, hasta ~30)
```

---

## Firmware alumno — classquiz.py

Actividad: `cqz` | Canal: 7 | Roles: A, B, C, D, E, Z

### Protocolo de mensajes

| Mensaje | Dirección | Descripción |
|---|---|---|
| `REPORT` | Concentrador → Alumnos | Solicita identificación |
| `ID` | Alumno → Concentrador | Respuesta con device_id (incluye delay anti-colisión) |
| `ACK` | Concentrador → Alumno | Confirmación de registro |
| `CHECK_REG` | Alumno → Concentrador | Consulta si ya está registrado (al arrancar o reconectar) |
| `REG_STATUS` | Concentrador → Alumno | Respuesta: OK, NO o CONFLICT |
| `QPARAMS` | Concentrador → Alumnos | Tipo de pregunta y cantidad de opciones |
| `POLL` | Concentrador → Alumno | Solicita respuesta de un alumno específico |
| `ANSWER` | Alumno → Concentrador | Opciones seleccionadas (packed) |
| `PING` / `PONG` | Bidireccional | Verificación de conectividad |

### Delay de descubrimiento

Para evitar colisiones cuando todos responden al `REPORT`, cada dispositivo calcula un delay basado en su grupo y rol:

```python
slot = (grupo - 1) * len(roles) + indice_rol
delay = int((slot * 5750) / 53)  # ms
```

### Tipos de pregunta

- `unica`: Seleccionar una opción deselecciona las demás automáticamente
- `multiple`: Permite seleccionar varias opciones simultáneamente

---

## Firmware concentrador — concentrador.py

Actividad: `cqz` | Canal: 7 | UART: 115200 baud

Gateway puro sin lógica de negocio. Traduce entre radio y USB serial.

### Radio → USB

Recibe un objeto `Message` por radio y lo serializa a JSON mínimo:

```json
{"name":"ID","devID":"a1b2c3d4","grp":3,"rol":"A","valores":["cqz"]}
```

### USB → Radio

Lee JSON de la PC, extrae campos y construye el payload radio con `send(CMD=False)`.

### Eventos de botones

Los botones físicos del concentrador generan eventos JSON hacia la PC:

```json
{"event":"button_a"}
{"event":"button_b"}
{"event":"logo_touch"}
```

Al arrancar envía `{"event":"gateway_ready"}`.

!!! warning
    El JSON enviado por serial debe usar `separators=(',',':')` sin espacios. El parser del concentrador falla con espacios después de los dos puntos.

---

## Interfaz gráfica — Interface_grafica/

Python 3.12+ | Flask + Tkinter | localhost:5000

### Componentes

| Archivo | Función |
|---|---|
| `main.py` | Punto de entrada, crea ventana Tkinter |
| `core/app_controller.py` | Controlador principal, gestiona apps y serial |
| `core/serial_manager.py` | USB serial con reconexión automática (10 reintentos) |
| `core/server.py` | Flask + SocketIO |
| `apps/classquiz/app.py` | Lógica de negocio: descubrimiento, polling, respuestas |
| `apps/classquiz/socketio_manager.py` | Clientes Socket.IO hacia ClassQuiz |
| `apps/monitor/app.py` | Monitor USB raw |

### Flujo de una pregunta

1. ClassQuiz emite `set_question_number` vía Socket.IO
2. La interfaz envía `QPARAMS` por serial al concentrador
3. El concentrador hace broadcast radio a todos los alumnos
4. Los alumnos seleccionan opciones con los botones
5. La interfaz inicia polling secuencial: `POLL` a cada device_id registrado
6. Cada alumno responde `ANSWER` con sus opciones
7. El concentrador reenvía por USB
8. La interfaz mapea device_id → username y envía a ClassQuiz vía Socket.IO

### Dependencias

```
pyserial>=3.5
Flask==3.1.3
Flask-SocketIO==5.3.6
python-socketio[client]==5.11.2
python-engineio==4.9.0
requests>=2.31.0
websocket-client>=1.6.0
```