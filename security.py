import bleach
import re
import html
from functools import wraps
import time
from collections import defaultdict
import sqlite3
import hashlib

# Rate limiting por IP
rate_limits = defaultdict(list)

def sanitize_message(message):
    """Sanitizar mensaje para prevenir XSS"""
    if not message:
        return ""
    
    # Limpiar HTML malicioso pero permitir algunos caracteres especiales
    cleaned = bleach.clean(message, tags=[], attributes={}, strip=True)
    
    # Escapar caracteres HTML restantes
    cleaned = html.escape(cleaned)
    
    # Limitar longitud
    return cleaned[:500]

def sanitize_username(username):
    """Sanitizar nombre de usuario"""
    if not username:
        return ""
    
    # Remover espacios al inicio y final
    username = username.strip()
    
    # Solo permitir caracteres alfanuméricos, espacios, guiones y guiones bajos
    username = re.sub(r'[^a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ]', '', username)
    
    # Limitar longitud
    username = username[:20]
    
    # Escapar HTML
    return html.escape(username)

def validate_message_length(message, max_length=500):
    """Validar longitud del mensaje"""
    return len(message.strip()) <= max_length and len(message.strip()) > 0

def validate_username(username, min_length=2, max_length=20):
    """Validar formato y longitud del nombre de usuario"""
    if not username:
        return False, "El nombre de usuario es obligatorio"
    
    username = username.strip()
    
    if len(username) < min_length:
        return False, f"El nombre debe tener al menos {min_length} caracteres"
    
    if len(username) > max_length:
        return False, f"El nombre no puede tener más de {max_length} caracteres"
    
    # Verificar caracteres válidos
    if not re.match(r'^[a-zA-Z0-9\s\-_áéíóúÁÉÍÓÚñÑ]+$', username):
        return False, "El nombre solo puede contener letras, números, espacios, guiones y guiones bajos"
    
    # No permitir solo espacios
    if username.replace(' ', '').replace('-', '').replace('_', '') == '':
        return False, "El nombre debe contener al menos una letra o número"
    
    return True, "Válido"

def check_rate_limit(client_ip, max_requests=30, window_seconds=60):
    """Verificar límite de velocidad por IP"""
    current_time = time.time()
    
    # Limpiar requests antiguos
    rate_limits[client_ip] = [
        req_time for req_time in rate_limits[client_ip]
        if current_time - req_time < window_seconds
    ]
    
    # Verificar límite
    if len(rate_limits[client_ip]) >= max_requests:
        return False
    
    # Agregar request actual
    rate_limits[client_ip].append(current_time)
    return True

def rate_limit_decorator(max_requests=30, window_seconds=60):
    """Decorador para aplicar rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Obtener IP del cliente (considerando proxies)
            client_ip = get_client_ip()
            
            if not check_rate_limit(client_ip, max_requests, window_seconds):
                return {'error': 'Demasiadas solicitudes. Intenta más tarde.'}, 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_client_ip():
    """Obtener IP real del cliente considerando proxies"""
    from flask import request
    
    # Verificar headers de proxy
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def hash_password(password):
    """Hash seguro para contraseñas (si se implementan en el futuro)"""
    import hashlib
    import secrets
    
    salt = secrets.token_hex(32)
    password_hash = hashlib.pbkdf2_hmac('sha256', 
                                       password.encode('utf-8'), 
                                       salt.encode('utf-8'), 
                                       100000)
    return salt + password_hash.hex()

def verify_password(password, hashed_password):
    """Verificar contraseña hasheada"""
    import hashlib
    
    salt = hashed_password[:64]
    stored_hash = hashed_password[64:]
    
    password_hash = hashlib.pbkdf2_hmac('sha256',
                                       password.encode('utf-8'),
                                       salt.encode('utf-8'),
                                       100000)
    
    return password_hash.hex() == stored_hash

def secure_database_connection(db_path):
    """Conexión segura a la base de datos"""
    try:
        conn = sqlite3.connect(db_path, timeout=10.0)
        # Habilitar foreign keys para integridad referencial
        conn.execute('PRAGMA foreign_keys = ON')
        # Configurar journal mode para mejor concurrencia
        conn.execute('PRAGMA journal_mode = WAL')
        return conn
    except sqlite3.Error as e:
        print(f"Error de base de datos: {e}")
        raise

def log_security_event(event_type, details, client_ip=None):
    """Registrar eventos de seguridad"""
    import time
    
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    # Solo obtener IP si estamos en contexto de request
    if client_ip is None:
        try:
            client_ip = get_client_ip()
        except RuntimeError:
            client_ip = "N/A"
    
    log_entry = f"[{timestamp}] SECURITY {event_type}: {details} (IP: {client_ip})"
    print(log_entry)
    
    # En producción, esto debería escribirse a un archivo de log
    # with open('security.log', 'a') as f:
    #     f.write(log_entry + '\n')

def validate_file_upload(file, allowed_extensions=None, max_size=1024*1024):
    """Validar archivos subidos (para futuras funcionalidades)"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    
    if not file or file.filename == '':
        return False, "No se seleccionó archivo"
    
    # Verificar extensión
    if '.' not in file.filename:
        return False, "Archivo sin extensión"
    
    extension = file.filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False, f"Extensión no permitida. Permitidas: {', '.join(allowed_extensions)}"
    
    # Verificar tamaño (esto requeriría leer el archivo)
    # En una implementación real, verificarías el tamaño del archivo
    
    return True, "Archivo válido"
