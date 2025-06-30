# 💬 Sistema de Chat Grupal en Tiempo Real

Un sistema de chat moderno y completo desarrollado con Python (Flask-SocketIO) en el backend y HTML/CSS/JavaScript en el frontend.

## ✨ Características

### 🎯 Funcionalidades Principales
- **Chat en tiempo real** con WebSockets
- **Gestión de usuarios** sin duplicados
- **Base de datos SQLite** para persistencia
- **Colores únicos** por usuario
- **Timestamps** en todos los mensajes
- **Interfaz moderna** con Tailwind CSS

### �️ Características de Seguridad

### 🔒 Medidas de Seguridad Implementadas
- **Sanitización de datos**: Prevención de XSS con `bleach`
- **Rate limiting**: Límites por IP para prevenir spam
- **Validación de entrada**: Verificación de longitud y formato
- **Configuración segura**: Variables de entorno y configuración por ambiente
- **Logs de seguridad**: Registro de eventos importantes
- **Conexión segura a BD**: Configuración SQLite con WAL mode
- **Escape HTML**: Prevención de inyección de código
- **CORS controlado**: Orígenes permitidos configurables

### 🔧 Configuración de Seguridad
```env
# Variables de entorno importantes
SECRET_KEY=tu_clave_super_secreta
DEBUG=False  # En producción
RATE_LIMIT_MESSAGES=20  # Mensajes por minuto
MAX_MESSAGE_LENGTH=500  # Caracteres máximos
ALLOWED_ORIGINS=https://tu-dominio.com
```

## �🚀 Funciones Avanzadas
- **Responder a mensajes** específicos
- **Emojis y stickers** integrados
- **Indicador de escritura** en tiempo real
- **Lista de usuarios online**
- **Notificaciones** de entrada/salida
- **Scroll automático** al último mensaje
- **Diseño responsive** y moderno

## 🛠️ Instalación y Configuración

### Prerrequisitos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar** el proyecto
```bash
git clone https://github.com/Mauricio-Leyva/python-chat.git
cd python-chat
```

2. **Crear entorno virtual** (recomendado)
```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En macOS/Linux
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar archivo de ejemplo
copy .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar el servidor**
```bash
python app.py
```

6. **Abrir el navegador**
   - Ve a: `http://localhost:5000`
   - Ingresa tu nombre de usuario
   - ¡Comienza a chatear!

## 📱 Uso del Sistema

### Para los Usuarios
1. **Registro**: Introduce un nombre único (2-20 caracteres)
2. **Chat**: Escribe mensajes y presiona Enter para enviar
3. **Responder**: Haz clic en el ícono 📧 de cualquier mensaje
4. **Emojis**: Usa el botón 😊 para agregar emojis
5. **Estado**: Ve quién está escribiendo en tiempo real

### Funciones de la Interfaz
- **Sidebar izquierdo**: Lista de usuarios conectados
- **Área central**: Mensajes del chat
- **Barra inferior**: Input de mensajes y controles
- **Indicadores visuales**: Colores por usuario, timestamps, estados

## 🏗️ Arquitectura del Sistema

### Backend (Python)
- **Flask**: Framework web principal
- **Flask-SocketIO**: Comunicación WebSocket
- **SQLite**: Base de datos para usuarios y mensajes
- **Gestión de sesiones**: Control de usuarios conectados

### Frontend (Web)
- **HTML5**: Estructura semántica
- **Tailwind CSS**: Estilos modernos y responsive
- **Vanilla JavaScript**: Lógica del cliente
- **Socket.IO Client**: Comunicación en tiempo real

### Base de Datos
```sql
-- Tabla de usuarios
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    color TEXT,
    created_at TIMESTAMP
);

-- Tabla de mensajes
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    message_id TEXT UNIQUE,
    username TEXT,
    message TEXT,
    timestamp TIMESTAMP,
    reply_to TEXT,
    message_type TEXT
);
```

## 🎨 Características de Diseño

### UI/UX Moderno
- **Gradientes**: Colores azul y púrpura
- **Iconos**: Font Awesome para elementos visuales
- **Animaciones**: Transiciones suaves
- **Responsive**: Adaptable a diferentes pantallas

### Experiencia de Usuario
- **Feedback visual**: Estados de carga y errores
- **Shortcuts**: Enter para enviar, Escape para cancelar
- **Accesibilidad**: Colores contrastantes y navegación clara
- **Performance**: Scroll optimizado y updates eficientes

## 🔧 Configuración Avanzada

### Variables del Servidor
```python
# En app.py puedes modificar:
HOST = '0.0.0.0'  # IP del servidor
PORT = 5000       # Puerto del servidor
DEBUG = True      # Modo debug
```

### Personalización
- **Colores de usuario**: Modifica `USER_COLORS` en `app.py`
- **Emojis**: Agrega más emojis en el array `emojis` del JavaScript
- **Límites**: Cambia límites de caracteres y usuarios en el código

## 🚨 Resolución de Problemas

### Problemas Comunes
1. **Puerto ocupado**: Cambia el puerto en `app.py`
2. **Dependencias**: Reinstala con `pip install -r requirements.txt`
3. **Permisos**: Ejecuta como administrador si es necesario
4. **Firewall**: Permite conexiones en el puerto 5000

### Logs del Sistema
El servidor muestra logs en la consola:
- Conexiones/desconexiones de usuarios
- Mensajes enviados
- Errores del sistema

## 📊 Funcionalidades Técnicas

### Seguridad
- **Validación de entrada**: Límites de caracteres y sanitización
- **Nombres únicos**: Prevención de usuarios duplicados
- **Escape HTML**: Prevención de XSS en mensajes

### Performance
- **Límite de mensajes**: Solo se cargan los 50 más recientes
- **Gestión de memoria**: Limpieza automática de conexiones
- **Optimización**: Queries eficientes a la base de datos

## 🤝 Contribución

Este proyecto fue desarrollado como parte del curso de Diseño de Interfaces. 
Las mejoras y sugerencias son bienvenidas.

## 📄 Licencia

Proyecto educativo - Universidad Autónoma de Chihuahua
Cuatrimestre 6 - Diseño de Interfaces

---

### 🎯 Estado del Proyecto: ✅ Completado y Funcional

**Desarrollado con ❤️ para el aprendizaje de desarrollo web**
