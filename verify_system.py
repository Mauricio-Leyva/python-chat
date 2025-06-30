#!/usr/bin/env python3
"""
Script de verificación del sistema de chat
Verifica que todas las dependencias y configuraciones estén correctas
"""

import sys
import os

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas"""
    required_packages = [
        'flask', 'flask_socketio', 'dotenv', 
        'bleach', 'sqlite3', 'uuid', 'datetime'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            else:
                __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTA")
    
    return len(missing_packages) == 0

def check_config_files():
    """Verificar que los archivos de configuración existan"""
    required_files = [
        'app.py', 'config.py', 'security.py', 
        'templates/index.html', '.env.example'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} - OK")
        else:
            missing_files.append(file)
            print(f"❌ {file} - FALTA")
    
    return len(missing_files) == 0

def check_env_file():
    """Verificar archivo .env"""
    if os.path.exists('.env'):
        print("✅ .env - OK")
        return True
    else:
        print("⚠️  .env - NO EXISTE (usar .env.example como base)")
        return False

def test_security_functions():
    """Probar funciones de seguridad"""
    try:
        from security import sanitize_message, sanitize_username, validate_username
        
        # Test sanitización
        test_message = "<script>alert('xss')</script>Hola mundo"
        sanitized = sanitize_message(test_message)
        print(f"✅ Sanitización de mensajes - OK")
        
        # Test validación de usuario
        is_valid, msg = validate_username("TestUser123")
        if is_valid:
            print(f"✅ Validación de usuarios - OK")
        else:
            print(f"❌ Validación de usuarios - ERROR: {msg}")
        
        return True
        
    except Exception as e:
        print(f"❌ Funciones de seguridad - ERROR: {str(e)}")
        return False

def main():
    print("🔍 Verificando sistema de chat...")
    print("=" * 50)
    
    # Verificar dependencias
    print("\n📦 Verificando dependencias:")
    deps_ok = check_dependencies()
    
    # Verificar archivos
    print("\n📁 Verificando archivos:")
    files_ok = check_config_files()
    
    # Verificar .env
    print("\n⚙️  Verificando configuración:")
    env_ok = check_env_file()
    
    # Verificar seguridad
    print("\n🛡️  Verificando seguridad:")
    security_ok = test_security_functions()
    
    # Resultado final
    print("\n" + "=" * 50)
    
    if deps_ok and files_ok and security_ok:
        print("🎉 ¡Todo está listo! El sistema está preparado para funcionar.")
        print("\n📋 Próximos pasos:")
        print("1. Configura tu archivo .env (usa .env.example como base)")
        print("2. Ejecuta: python app.py")
        print("3. Ve a: http://localhost:5000")
        return 0
    else:
        print("⚠️  Hay problemas que resolver antes de continuar.")
        print("\n🔧 Acciones necesarias:")
        if not deps_ok:
            print("- Instalar dependencias: pip install -r requirements.txt")
        if not files_ok:
            print("- Verificar que todos los archivos estén presentes")
        if not env_ok:
            print("- Crear archivo .env basado en .env.example")
        if not security_ok:
            print("- Revisar módulo de seguridad")
        return 1

if __name__ == "__main__":
    sys.exit(main())
