from src.core.config import MESSAGES, UI_CONFIG
import requests
import json
from datetime import datetime
import customtkinter as ctk
import re
from tkinter import messagebox
from PIL import Image, ImageDraw
import os

class APIHandler:
    @staticmethod
    def _get_auth_token():
        """Obtener token de autenticación de manera segura"""
        try:
            # Acceder directamente a la clase SessionManager sin importación circular
            if hasattr(APIHandler, '_session_manager_ref'):
                return APIHandler._session_manager_ref.get_token()
            # Fallback: buscar en el módulo current_module
            import sys
            current_module = sys.modules[__name__]
            if hasattr(current_module, 'SessionManager'):
                return current_module.SessionManager.get_token()
            return None
        except:
            return None
    
    @staticmethod
    def make_request(method, url, data=None, headers=None, files=None, params=None):
        try:
            method = method.lower()
            if headers is None:
                headers = {}
                
            # Agregar token de autenticación si está disponible
            token = APIHandler._get_auth_token()
            if token:
                headers['Authorization'] = f'Bearer {token}'
                
            # Agregar Content-Type para JSON si no está presente
            if method in ['post', 'put', 'patch'] and 'Content-Type' not in headers and not files:
                headers['Content-Type'] = 'application/json'
                
            # Agregar Accept header para solicitar JSON
            if 'Accept' not in headers:
                headers['Accept'] = 'application/json'
                
            print(f"APIHandler: {method.upper()} {url}")
            print(f"Headers: {headers}")
            if params:
                print(f"Params: {params}")
            if data:
                print(f"Data: {data}")
                
            if method == 'get':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method == 'post':
                if files:
                    response = requests.post(url, headers=headers, data=data, files=files, timeout=30)
                else:
                    response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method == 'put':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method == 'patch':
                response = requests.patch(url, headers=headers, json=data, timeout=30)
            elif method == 'delete':
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                return {'status_code': 400, 'data': {'error': f'Método HTTP no soportado: {method}'}}

            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            # Intentar decodificar JSON, si falla devolver estructura consistente
            try:
                resp_json = response.json()
                print(f"Response JSON: {resp_json}")
            except Exception as json_error:
                print(f"JSON decode error: {json_error}")
                print(f"Response text: {response.text[:500]}...")
                # Si no es JSON válido, crear estructura consistente
                resp_json = {
                    'error': f'Respuesta no válida del servidor',
                    'raw_response': response.text[:1000],  # Limitar el texto
                    'content_type': response.headers.get('content-type', 'unknown')
                }
            
            return {
                'status_code': response.status_code,
                'data': resp_json
            }
        except requests.exceptions.Timeout:
            return {'status_code': 408, 'data': {'error': 'Timeout: El servidor tardó demasiado en responder'}}
        except requests.exceptions.ConnectionError:
            return {'status_code': 503, 'data': {'error': 'Error de conexión: No se pudo conectar al servidor'}}
        except Exception as e:
            print(f"APIHandler exception: {e}")
            return {'status_code': 500, 'data': {'error': f'Error interno: {str(e)}'}}

class UIHelper:
    @staticmethod
    def show_error(title, message):
        error_window = ctk.CTkToplevel()
        error_window.title(title)
        error_window.geometry("400x200")
        
        # Centrar ventana
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (error_window.winfo_screenheight() // 2) - (200 // 2)
        error_window.geometry(f"400x200+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(error_window, fg_color="#FFFFFF")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Icono de error
        error_label = ctk.CTkLabel(
            main_frame,
            text="❌",
            font=("Quicksand", 48)
        )
        error_label.pack(pady=(0, 10))
        
        # Mensaje
        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=("Quicksand", 12),
            wraplength=300
        )
        message_label.pack(pady=(0, 20))
        
        # Botón cerrar
        close_button = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=error_window.destroy
        )
        close_button.pack()
        
    @staticmethod
    def show_success(title, message):
        success_window = ctk.CTkToplevel()
        success_window.title(title)
        success_window.geometry("400x200")
        
        # Centrar ventana
        success_window.update_idletasks()
        x = (success_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (success_window.winfo_screenheight() // 2) - (200 // 2)
        success_window.geometry(f"400x200+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(success_window, fg_color="#FFFFFF")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Icono de éxito
        success_label = ctk.CTkLabel(
            main_frame,
            text="✅",
            font=("Quicksand", 48)
        )
        success_label.pack(pady=(0, 10))
        
        # Mensaje
        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=("Quicksand", 12),
            wraplength=300
        )
        message_label.pack(pady=(0, 20))
        
        # Botón cerrar
        close_button = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=success_window.destroy
        )
        close_button.pack()
        
    @staticmethod
    def show_warning(title, message):
        warning_window = ctk.CTkToplevel()
        warning_window.title(title)
        warning_window.geometry("400x200")
        
        # Centrar ventana
        warning_window.update_idletasks()
        x = (warning_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (warning_window.winfo_screenheight() // 2) - (200 // 2)
        warning_window.geometry(f"400x200+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(warning_window, fg_color="#FFFFFF")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Icono de advertencia
        warning_label = ctk.CTkLabel(
            main_frame,
            text="⚠️",
            font=("Quicksand", 48)
        )
        warning_label.pack(pady=(0, 10))
        
        # Mensaje
        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=("Quicksand", 12),
            wraplength=300
        )
        message_label.pack(pady=(0, 20))
        
        # Botón cerrar
        close_button = ctk.CTkButton(
            main_frame,
            text="Cerrar",
            command=warning_window.destroy
        )
        close_button.pack()
        
    @staticmethod
    def confirm_action(title, message):
        result = {'confirmed': False}
        
        confirm_window = ctk.CTkToplevel()
        confirm_window.title(title)
        confirm_window.geometry("400x200")
        
        # Centrar ventana
        confirm_window.update_idletasks()
        x = (confirm_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (confirm_window.winfo_screenheight() // 2) - (200 // 2)
        confirm_window.geometry(f"400x200+{x}+{y}")
        
        # Frame principal
        main_frame = ctk.CTkFrame(confirm_window, fg_color="#FFFFFF")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        # Icono de pregunta
        question_label = ctk.CTkLabel(
            main_frame,
            text="❓",
            font=("Quicksand", 48)
        )
        question_label.pack(pady=(0, 10))
        
        # Mensaje
        message_label = ctk.CTkLabel(
            main_frame,
            text=message,
            font=("Quicksand", 12),
            wraplength=300
        )
        message_label.pack(pady=(0, 20))
        
        # Frame para botones
        button_frame = ctk.CTkFrame(main_frame, fg_color="#FFFFFF")
        button_frame.pack()
        
        def confirm():
            result['confirmed'] = True
            confirm_window.destroy()
            
        # Botones
        confirm_button = ctk.CTkButton(
            button_frame,
            text="Confirmar",
            command=confirm
        )
        confirm_button.pack(side="left", padx=5)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=confirm_window.destroy
        )
        cancel_button.pack(side="left", padx=5)
        
        # Esperar a que se cierre la ventana
        confirm_window.wait_window()
        return result['confirmed']

class SessionManager:
    _session_data = {}
    
    @classmethod
    def set_session(cls, token, user_data):
        cls._session_data = {
            'token': token,
            'user': user_data
        }
    
    @classmethod
    def clear_session(cls):
        cls._session_data = {}
    
    @classmethod
    def get_token(cls):
        return cls._session_data.get('token')
    
    @classmethod
    def get_user_data(cls):
        return cls._session_data.get('user')

class DataValidator:
    @staticmethod
    def validate_required_fields(data, required_fields):
        missing_fields = []
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)
        return missing_fields
        
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    @staticmethod
    def validate_phone(phone):
        import re
        pattern = r'^\+?[0-9]{9,12}$'
        return re.match(pattern, phone) is not None
        
    @staticmethod
    def validate_password(password):
        import re
        # Mínimo 8 caracteres, al menos una letra mayúscula, una minúscula y un número
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
        return re.match(pattern, password) is not None

class DateTimeHelper:
    @staticmethod
    def format_date(date_string, format='%Y-%m-%d %H:%M:%S'):
        try:
            date = datetime.strptime(date_string, format)
            return date.strftime('%d/%m/%Y %H:%M')
        except:
            return date_string
            
    @staticmethod
    def get_current_datetime():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    @staticmethod
    def get_current_date():
        return datetime.now().strftime('%Y-%m-%d')
        
    @staticmethod
    def get_current_time():
        return datetime.now().strftime('%H:%M:%S')

# Establecer referencia del SessionManager para APIHandler
APIHandler._session_manager_ref = SessionManager

def create_default_icons():
    """Crea los íconos por defecto si no existen"""
    # Asegurarse de que la carpeta de íconos exista
    # os.makedirs(ICONS_DIR, exist_ok=True)
    
    # Lista de íconos a crear
    icons = {
        'add.png': (255, 255, 255),  # Blanco
        'edit.png': (0, 0, 255),     # Azul
        'delete.png': (255, 0, 0),   # Rojo
        'status.png': (0, 255, 0),   # Verde
        'password.png': (128, 0, 128), # Púrpura
        'search.png': (0, 128, 128)   # Turquesa
    }
    
    for icon_name, color in icons.items():
        # icon_path = os.path.join(ICONS_DIR, icon_name)
        icon_path = os.path.join(os.path.dirname(__file__), '../../assets/images/icons', icon_name)
        if not os.path.exists(icon_path):
            # Crear una imagen de 20x20 píxeles
            img = Image.new('RGB', (20, 20), color)
            draw = ImageDraw.Draw(img)
            
            # Dibujar un círculo simple
            draw.ellipse([2, 2, 18, 18], fill=color)
            
            # Guardar la imagen
            img.save(icon_path)
            print(f"Ícono creado: {icon_path}")