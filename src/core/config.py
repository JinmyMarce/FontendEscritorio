import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la API
API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.fresaterra.shop/api/v1')

# Endpoints de Autenticación
AUTH_ENDPOINTS = {
    'login': 'https://api.fresaterra.shop/api/v1/admin/login',  # <-- Cambiado para admin
    'logout': 'https://api.fresaterra.shop/api/auth/logout',
    'refresh': 'https://api.fresaterra.shop/api/auth/refresh',
}

# Endpoints de Clientes
CLIENTS_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/clients",
    'statistics': f"{API_BASE_URL}/admin/clients/statistics",
    'detail': f"{API_BASE_URL}/admin/users/{{id}}",  # Reutiliza el endpoint de usuarios
    'deactivate': f"{API_BASE_URL}/admin/users/{{id}}/deactivate",
    'reactivate': f"{API_BASE_URL}/admin/users/{{id}}/reactivate",
    'reset_password': f"{API_BASE_URL}/admin/users/{{id}}/reset-password"
}

# Endpoints de Gestión de Inventario
INVENTORY_MANAGEMENT_ENDPOINTS = {
    # Endpoints de Categorías
    'categories': {
        'list': f"{API_BASE_URL}/admin/categories",  # GET - Listar todas las categorías
        'create': f"{API_BASE_URL}/admin/categories",  # POST - Crear nueva categoría
        'detail': f"{API_BASE_URL}/admin/categories/{{id}}",  # GET - Obtener detalles de categoría
        'update': f"{API_BASE_URL}/admin/categories/{{id}}",  # PUT - Actualizar categoría completa
        'partial_update': f"{API_BASE_URL}/admin/categories/{{id}}",  # PATCH - Actualización parcial
        'delete': f"{API_BASE_URL}/admin/categories/{{id}}",  # DELETE - Eliminar categoría
        'statistics': f"{API_BASE_URL}/admin/categories/statistics"  # GET - Estadísticas de categorías
    },
    
    # Endpoints de Productos
    'products': {
        'list': f"{API_BASE_URL}/admin/products",  # GET - Listar todos los productos relacionados a sus categorias
        'by_category': f"{API_BASE_URL}/admin/products?category_id={{category_id}}",  # GET - Productos por categoría
        'create': f"{API_BASE_URL}/admin/products",  # POST - Crear nuevo producto
        'detail': f"{API_BASE_URL}/admin/products/{{id}}",  # GET - Obtener detalles de producto
        'update': f"{API_BASE_URL}/admin/products/{{id}}",  # PUT - Actualizar producto completo
        'partial_update': f"{API_BASE_URL}/admin/products/{{id}}",  # PATCH - Actualización parcial
        'delete': f"{API_BASE_URL}/admin/products/{{id}}",  # DELETE - Eliminar producto
        'update_image': f"{API_BASE_URL}/admin/products/{{id}}/update-image",  # POST - Actualizar producto con imagen (workaround)
        'update_status': f"{API_BASE_URL}/admin/products/{{id}}/status",  # PATCH - Actualizar estado
        'low_stock': f"{API_BASE_URL}/admin/products/low-stock"  # GET - Productos con stock bajo
    },
    
    # Endpoints de Inventario (Stock y Control)
    'inventory': {
        'create_entry': f"{API_BASE_URL}/admin/inventory",  # POST - Crear entrada de inventario
        'products_list': f"{API_BASE_URL}/admin/inventory/products",  # GET - Lista de productos en inventario
        'product_detail': f"{API_BASE_URL}/admin/inventory/products/{{id}}",  # GET - Detalle de producto en inventario
        'update_status': f"{API_BASE_URL}/admin/inventory/products/{{id}}/status",  # PATCH - Actualizar estado en inventario
        'statistics': f"{API_BASE_URL}/admin/inventory/statistics",  # GET - Estadísticas de inventario
        
        # Endpoints de gestión de stock (flexibles)
        'update_stock': f"{API_BASE_URL}/admin/inventory/products/{{id}}/stock",  # PATCH - Actualizar stock (genérico con 'accion')
    }
}

# Endpoints de Inventario (Mantenido para compatibilidad)
INVENTORY_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/inventory/products",
    'detail': f"{API_BASE_URL}/admin/inventory/products/{{id}}",
    'register': f"{API_BASE_URL}/admin/inventory",
    'update': f"{API_BASE_URL}/admin/products/{{id}}",
    'delete': f"{API_BASE_URL}/admin/products/{{id}}",
    'categories': f"{API_BASE_URL}/admin/categories"
}

# Endpoints de Pedidos
ORDERS_ENDPOINTS = {
    # Para la gestión de pedidos del ADMIN
    'list': f"{API_BASE_URL}/admin/orders",   # GET todos los pedidos (admin)
    'detail': f"{API_BASE_URL}/admin/orders/{{id}}",  # GET detalle de pedido (admin)
    'update': f"{API_BASE_URL}/admin/orders/{{id}}/status",  # PATCH actualizar/cambiar estado (admin)
    # Para el resto de usuarios
    'list_user': f"{API_BASE_URL}/orders",  # GET pedidos del usuario autenticado
    'create': f"{API_BASE_URL}/orders",  # POST crear pedido
    'cancel': f"{API_BASE_URL}/orders/{{id}}/cancel",  # PATCH cancelar pedido
    'payment': f"{API_BASE_URL}/orders/{{id}}/payment"  # GET pagos del pedido
}
# NOTA: El endpoint PATCH /api/v1/admin/orders/{id}/status permite cambiar a cualquier estado válido, incluyendo 'completado'.

# Endpoints de Notificaciones
NOTIFICATIONS_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/notificaciones",
    'detail': f"{API_BASE_URL}/admin/notificaciones/{{id}}",
    'send': f"{API_BASE_URL}/admin/notificaciones",
    'send_to_all': f"{API_BASE_URL}/admin/notificaciones",
    'mark_read': f"{API_BASE_URL}/me/notificaciones/{{id}}",
    'delete': f"{API_BASE_URL}/admin/notificaciones/{{id}}",
    'send_email': f"{API_BASE_URL}/notificaciones/enviar-email",
    'send_campanita': f"{API_BASE_URL}/notificaciones/enviar-campanita",
    'send_campanita_email': f"{API_BASE_URL}/notificaciones/enviar-campanita-con-email",
    'users_list': f"{API_BASE_URL}/admin/users/registered",
    'users_count': f"{API_BASE_URL}/admin/users/count"
}

# Endpoints de Pagos
PAYMENTS_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/payments",
    'statistics': f"{API_BASE_URL}/admin/payments/statistics",
    'detail': f"{API_BASE_URL}/admin/payments/{{id}}",
    'details': f"{API_BASE_URL}/admin/payments/{{id}}/details",  # Detalles completos
    'order_payment': f"{API_BASE_URL}/orders/{{order_id}}/payment",
    'confirm_payment': f"{API_BASE_URL}/payments/confirm",
    'payment_methods': f"{API_BASE_URL}/payments/methods"
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

# Configuración de payloads para operaciones de stock
STOCK_OPERATIONS_CONFIG = {
    'establecer': {
        'accion': 'establecer',
        'payload': {
            'cantidad_disponible': 0,
            'accion': 'establecer'
        },
        'description': 'Establecer stock a una cantidad específica'
    },
    'aumentar': {
        'accion': 'aumentar',
        'payload': {
            'cantidad_disponible': 0,
            'accion': 'aumentar'
        },
        'description': 'Aumentar stock'
    },
    'reducir': {
        'accion': 'reducir',
        'payload': {
            'cantidad_disponible': 0,
            'accion': 'reducir'
        },
        'description': 'Reducir stock'
    }
}