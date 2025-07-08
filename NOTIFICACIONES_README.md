# 📧 Sistema de Notificaciones - Aplicación de Escritorio

## 🚀 Características Implementadas

### ✅ Funcionalidades Principales

1. **📤 Envío de Notificaciones**
   - ✉️ **Usuario Específico**: Envía notificación por email + campanita
   - 📢 **Todos los Usuarios**: Envía solo campanita a todos los usuarios registrados
   - ⚡ **Prioridades**: Baja, Normal, Alta, Urgente

2. **📋 Gestión de Notificaciones**
   - 🔍 **Búsqueda y Filtrado**: Por contenido, estado, tipo
   - 👁️ **Visualización**: Lista completa con detalles
   - 🗑️ **Eliminación**: Eliminar notificaciones individuales
   - 🔄 **Actualización en Tiempo Real**: Sincronización con API

3. **📊 Panel de Estadísticas**
   - 📈 Estadísticas generales (total, leídas, no leídas)
   - 🏷️ Distribución por tipo de notificación
   - 📊 Estado de las notificaciones
   - 👥 Información de usuarios

### 🔧 Integración con API

El sistema está completamente integrado con la API del hosting:

**Endpoints Utilizados:**
- `GET /admin/notificaciones` - Listar notificaciones
- `POST /admin/notificaciones` - Envío masivo
- `POST /notificaciones/enviar-campanita-con-email` - Envío individual
- `DELETE /admin/notificaciones/{id}` - Eliminar notificación
- `GET /admin/users/registered` - Lista de usuarios
- `GET /admin/users/count` - Conteo de usuarios

## 🎯 Cómo Usar

### 1. Enviar Notificación Individual (Email + Campanita)
1. Clic en **"➕ Nueva Notificación"**
2. Seleccionar **"👤 Usuario Específico (Email + Campanita)"**
3. Completar:
   - 📧 **Asunto**: Título de la notificación
   - 💬 **Contenido**: Mensaje detallado
   - 👤 **Usuario**: Seleccionar de la lista
   - ⚡ **Prioridad**: Elegir nivel de importancia
4. Clic en **"📤 Enviar Notificación"**

### 2. Enviar Notificación Masiva (Solo Campanita)
1. Clic en **"➕ Nueva Notificación"**
2. Seleccionar **"📢 Todos los Usuarios (Solo Campanita)"**
3. Completar:
   - 📧 **Asunto**: Título del anuncio
   - 💬 **Contenido**: Mensaje para todos
   - ⚡ **Prioridad**: Nivel de importancia
4. Clic en **"📤 Enviar Notificación"**

### 3. Gestionar Notificaciones Existentes
- **🔍 Buscar**: Usar el campo de búsqueda para filtrar
- **👁️ Ver Detalles**: Doble clic en una notificación
- **🗑️ Eliminar**: Seleccionar y presionar `Delete` o clic derecho
- **🔄 Refrescar**: Actualizar desde la API

### 4. Ver Estadísticas
- Clic en **"📊 Estadísticas"** para ver:
  - 📈 Resumen general
  - 🏷️ Tipos de notificaciones
  - 📊 Estados de lectura
  - 👥 Información de usuarios

## 📱 Interfaz de Usuario

### 🎨 Elementos Principales

1. **🔍 Barra de Búsqueda**
   - Campo de búsqueda por contenido
   - Filtro por estado (Todos, Pendiente, Leído, Enviado)

2. **🎛️ Panel de Acciones**
   - ➕ Nueva Notificación
   - 🔄 Refrescar datos
   - 📊 Ver estadísticas
   - 📈 Contador de notificaciones

3. **📋 Tabla de Notificaciones**
   - 🆔 ID
   - 🏷️ Tipo
   - 💬 Contenido (truncado)
   - 📊 Estado
   - 📅 Fecha
   - 👤 Usuario

4. **🖱️ Menú Contextual (Clic Derecho)**
   - 👁️ Ver Detalles
   - 🗑️ Eliminar
   - 🔄 Refrescar

### ⌨️ Atajos de Teclado
- `Enter`: Ver detalles de la notificación seleccionada
- `Delete`: Eliminar notificación seleccionada
- `Clic Derecho`: Mostrar menú contextual

## 🔧 Configuración Técnica

### 📁 Archivos Importantes

1. **`src/services/notifications_service.py`**
   - Servicio principal para API de notificaciones
   - Métodos para envío, eliminación y consulta

2. **`src/interfaces/management/notifications_management.py`**
   - Interfaz principal del sistema
   - Diálogos y gestión de eventos

3. **`src/core/config.py`**
   - Configuración de endpoints de la API
   - Variables de configuración

### 🌐 Endpoints API Configurados

```python
NOTIFICATIONS_ENDPOINTS = {
    'list': f"{API_BASE_URL}/admin/notificaciones",
    'send': f"{API_BASE_URL}/admin/notificaciones",
    'send_campanita_email': f"{API_BASE_URL}/notificaciones/enviar-campanita-con-email",
    'delete': f"{API_BASE_URL}/admin/notificaciones/{{id}}",
    'users_list': f"{API_BASE_URL}/admin/users/registered",
    'users_count': f"{API_BASE_URL}/admin/users/count"
}
```

## 🧪 Pruebas

Para probar el sistema, ejecutar:

```bash
cd FontendEscritorio
python test_notifications.py
```

Esto verificará:
- ✅ Conexión con la API
- ✅ Obtención de usuarios
- ✅ Listado de notificaciones
- ✅ Envío de notificaciones (individual y masivo)

## 🎯 Tipos de Notificación

### 1. 👤 Usuario Específico
- **Método**: Email + Campanita
- **Endpoint**: `/notificaciones/enviar-campanita-con-email`
- **Uso**: Mensajes importantes, confirmaciones personales

### 2. 📢 Envío Masivo
- **Método**: Solo Campanita
- **Endpoint**: `/admin/notificaciones` (con `todos_los_usuarios: true`)
- **Uso**: Anuncios generales, mantenimiento, promociones

## 🔄 Estados de Notificación

- **📬 No leído**: Notificación nueva
- **✅ Leído**: Usuario ha visto la notificación
- **📤 Enviado**: Notificación entregada exitosamente

## 🎨 Colores y Estilos

- **🟢 Verde (#2E6B5C)**: Acciones principales, éxito
- **🟠 Naranja (#FF9800)**: Advertencias, no leídas
- **🔴 Rojo (#E64A19)**: Eliminación, errores
- **🔵 Azul (#17a2b8)**: Información, estadísticas

## 📝 Notas Importantes

1. **🔐 Autenticación**: Requiere token de administrador válido
2. **🌐 Conexión**: Necesita conexión a internet para API
3. **⚡ Tiempo Real**: Los datos se actualizan automáticamente
4. **📱 Responsive**: Interfaz adaptable a diferentes tamaños

## 🚀 Próximas Mejoras

- 📅 Programación de notificaciones
- 📁 Plantillas de mensajes
- 📈 Reportes avanzados
- 🔔 Notificaciones push en tiempo real
- 📧 Editor HTML para emails
- 🎯 Segmentación de usuarios
