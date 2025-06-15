# Sistema de Administración

Sistema de administración para la gestión de inventario, pedidos y clientes desarrollado con Python y CustomTkinter.

## Características

- Sistema de autenticación con roles y permisos
- Gestión de inventario
- Gestión de pedidos y envíos
- Gestión de clientes
- Sistema de notificaciones
- Reportes de ventas con gráficos
- Interfaz moderna y amigable

## Requisitos

- Python 3.8 o superior
- MySQL 8.0 o superior

## Instalación

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>
```

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

5. Crear archivo .env:
```bash
cp .env.example .env
```

6. Configurar las variables de entorno en el archivo .env:
```
DB_HOST=localhost
DB_NAME=bdfresaterra
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
API_BASE_URL=http://localhost:8000/api/v1
```

## Uso

1. Activar el entorno virtual si no está activo:

Windows:
```bash
venv\Scripts\activate
```

Linux/Mac:
```bash
source venv/bin/activate
```

2. Ejecutar la aplicación:
```bash
python main.py
```

## Estructura del Proyecto

```
.
├── main.py                 # Archivo principal
├── config.py              # Configuraciones y endpoints
├── utils.py               # Utilidades y funciones comunes
├── login.py              # Sistema de login
├── dashboard.py          # Dashboard principal
├── GestionInventario.py  # Módulo de inventario
├── GestionPedidos.py     # Módulo de pedidos
├── GestionClientes.py    # Módulo de clientes
├── GestionNotificaciones.py # Módulo de notificaciones
├── ReporteVenta.py      # Módulo de reportes
├── requirements.txt      # Dependencias
└── README.md            # Este archivo
```

## Roles y Permisos

El sistema maneja tres roles principales:

1. Administrador
   - Acceso total al sistema
   - Gestión de usuarios y roles
   - Acceso a todos los módulos

2. Gerente
   - Gestión de inventario
   - Gestión de pedidos
   - Visualización de clientes
   - Acceso a reportes

3. Empleado
   - Visualización de inventario
   - Visualización de pedidos
   - Visualización de clientes

## Base de Datos

El sistema utiliza MySQL como base de datos. La estructura de las tablas principales es:

### Roles
```sql
CREATE TABLE IF NOT EXISTS `roles` (
  `id_rol` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `descripcion` TEXT NULL,
  `fecha_creacion` TIMESTAMP NOT NULL,
  PRIMARY KEY (`id_rol`)
);
```

### Usuarios
```sql
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) NOT NULL,
  `apellidos` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `telefono` VARCHAR(12) NOT NULL,
  `fecha_creacion` TIMESTAMP NOT NULL,
  `estado` TINYINT NOT NULL,
  `roles_id_rol` INT NOT NULL,
  PRIMARY KEY (`id_usuario`),
  FOREIGN KEY (`roles_id_rol`) REFERENCES `roles` (`id_rol`)
);
```

## API Endpoints

La aplicación se comunica con una API REST. Los principales endpoints son:

### Autenticación
- POST /auth/login
- POST /auth/register
- POST /auth/logout
- POST /auth/refresh
- GET /auth/verify

### Clientes
- GET /admin/clientes
- GET /admin/clientes/{id}
- POST /admin/clientes
- PUT /admin/clientes/{id}
- DELETE /admin/clientes/{id}
- PATCH /admin/clientes/{id}/estado
- POST /admin/clientes/{id}/password

### Inventario
- GET /admin/inventario
- GET /admin/inventario/{id}
- POST /admin/inventario/register
- PUT /admin/inventario/update/{id}
- DELETE /admin/inventario/{id}
- GET /admin/inventario/categorias

### Pedidos
- GET /admin/pedidos
- GET /admin/pedidos/{id}
- POST /admin/pedidos
- PUT /admin/pedidos/{id}
- DELETE /admin/pedidos/{id}
- PUT /admin/pedidos/{id}/envio

### Notificaciones
- GET /admin/notificaciones
- GET /admin/notificaciones/{id}
- POST /admin/notificaciones/send
- PUT /admin/notificaciones/{id}/read

### Reportes
- GET /admin/reportes/ventas
- GET /admin/reportes/inventario
- GET /admin/reportes/clientes
- GET /admin/reportes/pedidos

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. 