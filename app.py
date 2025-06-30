from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import json
from datetime import datetime
import uuid
import os
from config import config
from security import (
    sanitize_message, sanitize_username, validate_message_length,
    validate_username, check_rate_limit, get_client_ip,
    secure_database_connection, log_security_event
)

# Configuración de la aplicación
env = os.environ.get('FLASK_ENV', 'development')
app_config = config.get(env, config['default'])

app = Flask(__name__)
app.config.from_object(app_config)

# Configurar CORS de forma segura
allowed_origins = app_config.ALLOWED_ORIGINS
if '*' in allowed_origins:
    allowed_origins = "*"

socketio = SocketIO(
    app, 
    cors_allowed_origins=allowed_origins,
    logger=not app_config.DEBUG,
    engineio_logger=not app_config.DEBUG
)

# Colores predefinidos para usuarios
USER_COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
    '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
    '#F8C471', '#82E0AA', '#F1948A', '#85C1E9', '#D2B4DE'
]

# Diccionario para almacenar usuarios conectados
connected_users = {}
user_colors = {}

def init_db():
    try:
        conn = secure_database_connection(app_config.DATABASE_PATH)
        cursor = conn.cursor()
        
        # Tabla de usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                color TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de mensajes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reply_to TEXT DEFAULT NULL,
                message_type TEXT DEFAULT 'text',
                client_ip TEXT,
                FOREIGN KEY (reply_to) REFERENCES messages (message_id)
            )
        ''')
        
        # Tabla de eventos de seguridad (opcional)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                details TEXT,
                client_ip TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        log_security_event("DATABASE_INIT", "Base de datos inicializada correctamente")
        
    except Exception as e:
        log_security_event("DATABASE_ERROR", f"Error inicializando base de datos: {str(e)}")
        raise

def get_user_color(username):
    """Obtener o asignar color a un usuario"""
    if username not in user_colors:
        # Asignar color basado en el hash del nombre
        color_index = hash(username) % len(USER_COLORS)
        user_colors[username] = USER_COLORS[color_index]
    return user_colors[username]

def save_message(username, message, reply_to=None, message_type='text'):
    """Guardar mensaje en la base de datos con validaciones de seguridad"""
    try:
        # Sanitizar datos
        username = sanitize_username(username)
        message = sanitize_message(message)
        
        # Validar longitud
        if not validate_message_length(message, app_config.MAX_MESSAGE_LENGTH):
            raise ValueError("Mensaje inválido o muy largo")
        
        conn = secure_database_connection(app_config.DATABASE_PATH)
        cursor = conn.cursor()
        
        message_id = str(uuid.uuid4())
        client_ip = get_client_ip()
        
        cursor.execute('''
            INSERT INTO messages (message_id, username, message, reply_to, message_type, client_ip)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, username, message, reply_to, message_type, client_ip))
        
        conn.commit()
        conn.close()
        
        return message_id
        
    except Exception as e:
        log_security_event("MESSAGE_SAVE_ERROR", f"Error guardando mensaje: {str(e)}")
        raise

def get_recent_messages(limit=None):
    """Obtener mensajes recientes con límite de seguridad"""
    if limit is None:
        limit = app_config.MAX_MESSAGES_HISTORY
    
    # Asegurar que el límite no sea excesivo
    limit = min(limit, app_config.MAX_MESSAGES_HISTORY)
    
    try:
        conn = secure_database_connection(app_config.DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.message_id, m.username, m.message, m.timestamp, m.reply_to, m.message_type,
                   r.username as replied_username, r.message as replied_message
            FROM messages m
            LEFT JOIN messages r ON m.reply_to = r.message_id
            ORDER BY m.timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        messages = cursor.fetchall()
        conn.close()
        
        # Convertir a formato JSON y agregar colores
        formatted_messages = []
        for msg in reversed(messages):
            message_data = {
                'id': msg[0],
                'username': sanitize_username(msg[1]),
                'message': sanitize_message(msg[2]),
                'timestamp': msg[3],
                'reply_to': msg[4],
                'message_type': msg[5],
                'color': get_user_color(msg[1])
            }
            
            # Agregar información del mensaje respondido si existe
            if msg[4] and msg[6]:  # Si hay reply_to y replied_username
                message_data['replied_to'] = {
                    'username': sanitize_username(msg[6]),
                    'message': sanitize_message(msg[7]),
                    'color': get_user_color(msg[6])
                }
            
            formatted_messages.append(message_data)
        
        return formatted_messages
        
    except Exception as e:
        log_security_event("MESSAGE_FETCH_ERROR", f"Error obteniendo mensajes: {str(e)}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def on_connect():
    client_ip = get_client_ip()
    print(f'Cliente conectado: {request.sid} desde {client_ip}')
    log_security_event("CLIENT_CONNECT", f"Conexión desde {client_ip}")

@socketio.on('disconnect')
def on_disconnect():
    client_ip = get_client_ip()
    print(f'Cliente desconectado: {request.sid} desde {client_ip}')
    
    # Remover usuario de la lista de conectados
    username_to_remove = None
    for username, sid in connected_users.items():
        if sid == request.sid:
            username_to_remove = username
            break
    
    if username_to_remove:
        del connected_users[username_to_remove]
        emit('user_left', {
            'username': sanitize_username(username_to_remove),
            'users_count': len(connected_users)
        }, broadcast=True)
        
        log_security_event("USER_DISCONNECT", f"Usuario {username_to_remove} desconectado")

@socketio.on('join_chat')
def on_join_chat(data):
    client_ip = get_client_ip()
    
    # Verificar rate limiting
    if not check_rate_limit(client_ip, app_config.RATE_LIMIT_MESSAGES, app_config.RATE_LIMIT_WINDOW):
        emit('join_error', {'message': 'Demasiadas solicitudes. Intenta más tarde.'})
        log_security_event("RATE_LIMIT_EXCEEDED", f"Rate limit excedido para join_chat", client_ip)
        return
    
    try:
        username = sanitize_username(data.get('username', '').strip())
        
        # Validar nombre de usuario
        is_valid, error_message = validate_username(
            username, 
            app_config.MIN_USERNAME_LENGTH, 
            app_config.MAX_USERNAME_LENGTH
        )
        
        if not is_valid:
            emit('join_error', {'message': error_message})
            log_security_event("INVALID_USERNAME", f"Nombre inválido: {username}", client_ip)
            return
        
        # Verificar si el nombre de usuario ya está en uso
        if username in connected_users:
            emit('join_error', {'message': 'El nombre de usuario ya está en uso'})
            log_security_event("DUPLICATE_USERNAME", f"Intento de uso de nombre duplicado: {username}", client_ip)
            return
        
        # Agregar usuario a la lista de conectados
        connected_users[username] = request.sid
        
        # Guardar usuario en la base de datos
        try:
            conn = secure_database_connection(app_config.DATABASE_PATH)
            cursor = conn.cursor()
            
            color = get_user_color(username)
            cursor.execute('''
                INSERT OR REPLACE INTO users (username, color, last_activity) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (username, color))
            conn.commit()
            conn.close()
            
        except Exception as db_error:
            log_security_event("DATABASE_ERROR", f"Error guardando usuario: {str(db_error)}", client_ip)
        
        # Confirmar unión al chat
        emit('join_success', {
            'username': username,
            'color': get_user_color(username),
            'users_count': len(connected_users)
        })
        
        # Enviar mensajes recientes
        recent_messages = get_recent_messages()
        emit('recent_messages', {'messages': recent_messages})
        
        # Enviar lista de usuarios online al usuario que se acaba de conectar
        users_list = []
        for online_username in connected_users.keys():
            users_list.append({
                'username': sanitize_username(online_username),
                'color': get_user_color(online_username)
            })
        
        emit('online_users', {
            'users': users_list,
            'count': len(users_list)
        })
        
        # Notificar a otros usuarios
        emit('user_joined', {
            'username': username,
            'users_count': len(connected_users)
        }, broadcast=True, include_self=False)
        
        log_security_event("USER_JOINED", f"Usuario {username} se unió al chat", client_ip)
        
    except Exception as e:
        emit('join_error', {'message': 'Error interno del servidor'})
        log_security_event("JOIN_ERROR", f"Error en join_chat: {str(e)}", client_ip)

@socketio.on('send_message')
def on_send_message(data):
    client_ip = get_client_ip()
    
    # Verificar rate limiting
    if not check_rate_limit(client_ip, app_config.RATE_LIMIT_MESSAGES, app_config.RATE_LIMIT_WINDOW):
        emit('message_error', {'message': 'Demasiados mensajes. Espera un momento.'})
        log_security_event("RATE_LIMIT_EXCEEDED", f"Rate limit excedido para send_message", client_ip)
        return
    
    try:
        username = sanitize_username(data.get('username', ''))
        message = sanitize_message(data.get('message', '').strip())
        reply_to = data.get('reply_to')
        message_type = data.get('message_type', 'text')
        
        # Validaciones de seguridad
        if not message:
            emit('message_error', {'message': 'El mensaje no puede estar vacío'})
            return
        
        if not validate_message_length(message, app_config.MAX_MESSAGE_LENGTH):
            emit('message_error', {'message': f'El mensaje es demasiado largo (máximo {app_config.MAX_MESSAGE_LENGTH} caracteres)'})
            return
        
        # Verificar que el usuario esté conectado
        if username not in connected_users:
            emit('message_error', {'message': 'Usuario no autorizado'})
            log_security_event("UNAUTHORIZED_MESSAGE", f"Intento de mensaje no autorizado: {username}", client_ip)
            return
        
        # Guardar mensaje en la base de datos
        message_id = save_message(username, message, reply_to, message_type)
        
        # Preparar datos del mensaje
        message_data = {
            'id': message_id,
            'username': username,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'color': get_user_color(username),
            'reply_to': reply_to,
            'message_type': message_type
        }
        
        # Si es una respuesta, obtener información del mensaje original
        if reply_to:
            try:
                conn = secure_database_connection(app_config.DATABASE_PATH)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, message FROM messages WHERE message_id = ?
                ''', (reply_to,))
                replied_msg = cursor.fetchone()
                conn.close()
                
                if replied_msg:
                    message_data['replied_to'] = {
                        'username': sanitize_username(replied_msg[0]),
                        'message': sanitize_message(replied_msg[1]),
                        'color': get_user_color(replied_msg[0])
                    }
            except Exception as e:
                log_security_event("REPLY_FETCH_ERROR", f"Error obteniendo mensaje de respuesta: {str(e)}", client_ip)
        
        # Enviar mensaje a todos los usuarios conectados
        emit('new_message', message_data, broadcast=True)
        
        log_security_event("MESSAGE_SENT", f"Mensaje enviado por {username}", client_ip)
        
    except Exception as e:
        emit('message_error', {'message': 'Error interno del servidor'})
        log_security_event("SEND_MESSAGE_ERROR", f"Error en send_message: {str(e)}", client_ip)

@socketio.on('typing')
def on_typing(data):
    try:
        username = sanitize_username(data.get('username', ''))
        is_typing = data.get('is_typing', False)
        
        # Verificar que el usuario esté conectado
        if username not in connected_users:
            return
        
        emit('user_typing', {
            'username': username,
            'is_typing': is_typing
        }, broadcast=True, include_self=False)
        
    except Exception as e:
        log_security_event("TYPING_ERROR", f"Error en typing: {str(e)}")

@socketio.on('get_online_users')
def on_get_online_users():
    try:
        users_list = []
        for username in connected_users.keys():
            users_list.append({
                'username': sanitize_username(username),
                'color': get_user_color(username)
            })
        
        emit('online_users', {
            'users': users_list,
            'count': len(users_list)
        })
        
    except Exception as e:
        log_security_event("GET_USERS_ERROR", f"Error obteniendo usuarios: {str(e)}")

if __name__ == '__main__':
    # Inicializar base de datos
    try:
        init_db()
        print("🚀 Servidor de chat iniciado correctamente")
        print(f"🔧 Modo: {'Desarrollo' if app_config.DEBUG else 'Producción'}")
        print(f"🌐 Dirección: http://{app_config.HOST}:{app_config.PORT}")
        print("💬 Los usuarios pueden conectarse y comenzar a chatear")
        print(f"🔒 Seguridad: Rate limiting, sanitización y logging activados")
        
        # Ejecutar servidor
        socketio.run(
            app, 
            debug=app_config.DEBUG, 
            host=app_config.HOST, 
            port=app_config.PORT
        )
        
    except Exception as e:
        print(f"❌ Error iniciando el servidor: {str(e)}")
        log_security_event("SERVER_START_ERROR", f"Error iniciando servidor: {str(e)}")