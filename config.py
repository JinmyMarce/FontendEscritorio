import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'fresaterradb'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Configuración de la API
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api/v1')

# Endpoints de Autenticación
AUTH_ENDPOINTS = {
    'login': 'http://localhost:8000/api/v1/admin/login',  # <-- Cambiado para admin
    'logout': 'http://localhost:8000/api/auth/logout',
    'refresh': 'http://localhost:8000/api/auth/refresh',
}

# Endpoints de Clientes
CLIENTS_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/clientes",
    'detail': f"{API_BASE_URL}/admin/clientes/{{id}}",
    'create': f"{API_BASE_URL}/admin/clientes",
    'update': f"{API_BASE_URL}/admin/clientes/{{id}}",
    'delete': f"{API_BASE_URL}/admin/clientes/{{id}}",
    'update_status': f"{API_BASE_URL}/admin/clientes/{{id}}/estado",
    'reset_password': f"{API_BASE_URL}/admin/clientes/{{id}}/password"
}

# Endpoints de Inventario
INVENTORY_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/inventario",
    'detail': f"{API_BASE_URL}/admin/inventario/{{id}}",
    'register': f"{API_BASE_URL}/admin/inventario/register",
    'update': f"{API_BASE_URL}/admin/inventario/update/{{id}}",
    'delete': f"{API_BASE_URL}/admin/inventario/{{id}}",
    'categories': f"{API_BASE_URL}/admin/inventario/categorias"
}

# Endpoints de Pedidos
ORDERS_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/pedidos",
    'detail': f"{API_BASE_URL}/admin/pedidos/{{id}}",
    'create': f"{API_BASE_URL}/admin/pedidos",
    'update': f"{API_BASE_URL}/admin/pedidos/{{id}}",
    'delete': f"{API_BASE_URL}/admin/pedidos/{{id}}",
    'shipping': f"{API_BASE_URL}/admin/pedidos/{{id}}/envio"
}

# Endpoints de Notificaciones
NOTIFICATIONS_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/notificaciones",
    'detail': f"{API_BASE_URL}/admin/notificaciones/{{id}}",
    'send': f"{API_BASE_URL}/admin/notificaciones/send",
    'mark_read': f"{API_BASE_URL}/admin/notificaciones/{{id}}/read"
}

# Endpoints de Reportes
REPORTS_ENDPOINTS = {
    'sales': f"{API_BASE_URL}/admin/reportes/ventas",
    'inventory': f"{API_BASE_URL}/admin/reportes/inventario",
    'clients': f"{API_BASE_URL}/admin/reportes/clientes",
    'orders': f"{API_BASE_URL}/admin/reportes/pedidos"
}

# Configuración de la UI
UI_CONFIG = {
    'PRIMARY_COLOR': '#2D5A27',  # Verde oscuro
    'SECONDARY_COLOR': '#4A934A',  # Verde medio
    'ACCENT_COLOR': '#EC0617',
    'HIGHLIGHT_COLOR': '#367832',  # Verde para hover
    'SUCCESS_COLOR': '#4CAF50',  # Verde para éxito
    'WARNING_COLOR': '#FFA726',  # Naranja para advertencias
    'ERROR_COLOR': '#FF4444',  # Rojo para errores
    'INFO_COLOR': '#17a2b8',
    'BACKGROUND_COLOR': '#ffffff',
    'TEXT_COLOR': '#000000',
    'FONT_FAMILY': 'Quicksand',
    'FONT_SIZES': {
        'TITLE': 24,
        'SUBTITLE': 20,
        'HEADING': 16,
        'BODY': 12,
        'SMALL': 10
    }
}

# Configuración de la aplicación
APP_CONFIG = {
    'APP_NAME': 'Sistema de Administración',
    'APP_VERSION': '1.0.0',
    'APP_DESCRIPTION': 'Sistema de administración para la gestión de inventario, pedidos y clientes',
    'WINDOW_SIZE': {
        'width': 1280,
        'height': 720
    },
    'MIN_WINDOW_SIZE': {
        'width': 800,
        'height': 600
    }
}

# Configuración de roles y permisos
ROLES_CONFIG = {
    'ADMIN': {
        'id': 1,
        'name': 'Administrador',
        'permissions': ['all']
    },
    'MANAGER': {
        'id': 2,
        'name': 'Gerente',
        'permissions': [
            'view_inventory',
            'edit_inventory',
            'view_orders',
            'edit_orders',
            'view_clients',
            'view_reports'
        ]
    },
    'EMPLOYEE': {
        'id': 3,
        'name': 'Empleado',
        'permissions': [
            'view_inventory',
            'view_orders',
            'view_clients'
        ]
    }
}

# Configuración de mensajes
MESSAGES = {
    'errors': {
        'db_connection': 'Error al conectar con la base de datos',
        'api_connection': 'Error al conectar con la API',
        'invalid_credentials': 'Credenciales inválidas',
        'session_expired': 'La sesión ha expirado',
        'permission_denied': 'No tiene permisos para realizar esta acción',
        'required_fields': 'Por favor complete todos los campos requeridos',
        'invalid_data': 'Los datos ingresados no son válidos'
    },
    'success': {
        'login': 'Inicio de sesión exitoso',
        'logout': 'Sesión cerrada correctamente',
        'data_saved': 'Datos guardados correctamente',
        'data_updated': 'Datos actualizados correctamente',
        'data_deleted': 'Datos eliminados correctamente'
    },
    'info': {
        'loading': 'Cargando datos...',
        'no_data': 'No hay datos para mostrar',
        'confirm_delete': '¿Está seguro de que desea eliminar este registro?',
        'confirm_logout': '¿Está seguro de que desea cerrar sesión?'
    }
}

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "imagen")
ICONS_DIR = os.path.join(IMAGES_DIR, "icons") 