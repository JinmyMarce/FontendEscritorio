# Sistema de Administración FRESAS

Sistema de administración para la gestión de inventario, pedidos y clientes desarrollado en Python con CustomTkinter.

---

## 📦 Estructura del Proyecto

```
FontendEscritorio/
├── main.py                  # Punto de entrada principal
├── requirements.txt         # Dependencias del proyecto
├── assets/                  # Imágenes y fuentes
└── src/
    ├── core/                # Configuración y constantes globales
    ├── shared/              # Utilidades y helpers
    └── interfaces/
        ├── auth/            # Login y autenticación
        ├── dashboard/       # Panel principal
        ├── management/      # Gestión de inventario, pedidos, clientes, usuarios, etc.
        └── reports/         # Reportes y estadísticas
```

---

## 🚀 Guía para Ejecutar el Proyecto

### 1. Clona el repositorio

```bash
git clone <url-del-repositorio>
cd FontendEscritorio
```

### 2. Crea y activa un entorno virtual

```bash
python -m venv venv
# En Windows
venv\Scripts\activate
# En Linux/Mac
source venv/bin/activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. (Opcional) Configura variables de entorno

Si necesitas personalizar la URL de la API u otras variables, crea un archivo `.env` en la raíz:

```
API_BASE_URL=https://api.fresaterra.shop/api/v1
```

### 5. Ejecuta la aplicación

```bash
python main.py
```

---

## 📝 Características Principales

- Login seguro con roles y permisos
- Gestión de inventario, pedidos, clientes y usuarios
- Notificaciones y reportes
- Interfaz moderna y responsiva (CustomTkinter)
- Integración con API REST (configurable)
- Soporte para imágenes y recursos estáticos

---

## 🛠️ Tecnologías Utilizadas

- Python 3.11+
- CustomTkinter
- Pillow
- Requests
- Matplotlib
- Pandas
- MySQL Connector
- python-dotenv

---

## 📋 Organización y buenas prácticas

- Código modular y organizado por responsabilidad
- Configuración centralizada en `src/core/config.py`
- Datos de ejemplo y persistencia en `data/`
- Recursos estáticos en `assets/`
- Todas las dependencias en `requirements.txt`
- `.gitignore` configurado para excluir entornos virtuales y cachés

---

## 🤝 Contribución

1. Haz fork del proyecto
2. Crea una rama (`git checkout -b feature/mi-feature`)
3. Realiza tus cambios y commitea (`git commit -am "feat: mi feature"`)
4. Haz push a tu rama (`git push origin feature/mi-feature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

> **Nota:** Este README refleja la estructura y procesos actualizados del proyecto. Para dudas técnicas, revisa los módulos en `src/` y la configuración en `src/core/config.py`.
