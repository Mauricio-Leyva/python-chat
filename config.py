import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-temporal-desarrollo-cambiar-en-produccion'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Configuración del servidor
    HOST = os.environ.get('HOST', '127.0.0.1')
    PORT = int(os.environ.get('PORT', 5000))
    
    # Base de datos
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'chat.db')
    
    # Límites de seguridad
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', 500))
    MAX_USERNAME_LENGTH = int(os.environ.get('MAX_USERNAME_LENGTH', 20))
    MIN_USERNAME_LENGTH = int(os.environ.get('MIN_USERNAME_LENGTH', 2))
    MAX_MESSAGES_HISTORY = int(os.environ.get('MAX_MESSAGES_HISTORY', 100))
    
    # Rate limiting
    RATE_LIMIT_MESSAGES = int(os.environ.get('RATE_LIMIT_MESSAGES', 30))
    RATE_LIMIT_WINDOW = int(os.environ.get('RATE_LIMIT_WINDOW', 60))
    
    # CORS
    ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
    
    # Configuración adicional de seguridad
    SESSION_COOKIE_SECURE = not DEBUG
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class ProductionConfig(Config):
    DEBUG = False
    HOST = '0.0.0.0'
    SESSION_COOKIE_SECURE = True

class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '127.0.0.1'

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
