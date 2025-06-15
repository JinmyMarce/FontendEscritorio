import mysql.connector
from mysql.connector import Error
import requests
import json
from datetime import datetime
import customtkinter as ctk
from config import DB_CONFIG, MESSAGES, UI_CONFIG
import re
from tkinter import messagebox
from PIL import Image, ImageDraw
import os

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            return self.connection
        except Error as e:
            print(f"Error conectando a MySQL: {e}")
            return None
            
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

class APIHandler:
    @staticmethod
    def make_request(method, url, data=None, headers=None):
        try:
            # Simular respuesta exitosa para pruebas
            if url.endswith('/login'):
                return {
                    'status_code': 200,
                    'data': {
                        'token': 'test_token',
                        'user': {
                            'id': 1,
                            'name': 'Usuario de Prueba',
                            'email': data.get('email'),
                            'role': 'admin'
                        }
                    }
                }
            return {'status_code': 404, 'error': 'Endpoint no encontrado'}
        except Exception as e:
            return {'status_code': 500, 'error': str(e)}

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
        main_frame = ctk.CTkFrame(error_window)
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
        main_frame = ctk.CTkFrame(success_window)
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
        main_frame = ctk.CTkFrame(warning_window)
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
        main_frame = ctk.CTkFrame(confirm_window)
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
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
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

def create_default_icons():
    """Crea los íconos por defecto si no existen"""
    # Asegurarse de que la carpeta de íconos exista
    os.makedirs(ICONS_DIR, exist_ok=True)
    
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
        icon_path = os.path.join(ICONS_DIR, icon_name)
        if not os.path.exists(icon_path):
            # Crear una imagen de 20x20 píxeles
            img = Image.new('RGB', (20, 20), color)
            draw = ImageDraw.Draw(img)
            
            # Dibujar un círculo simple
            draw.ellipse([2, 2, 18, 18], fill=color)
            
            # Guardar la imagen
            img.save(icon_path)
            print(f"Ícono creado: {icon_path}") 