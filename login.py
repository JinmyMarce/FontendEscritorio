import customtkinter as ctk
from PIL import Image, ImageTk
import os
from dashboard import DashboardApp
import tkinter.messagebox as messagebox
from customtkinter import CTkImage

class LoginApp(ctk.CTkFrame):
    def __init__(self, parent, on_login_success=None):
        super().__init__(parent)
        self.parent = parent
        self.on_login_success = on_login_success
        # Ajustar tamaño fijo SOLO si parent es una ventana principal
        if hasattr(self.parent, 'geometry') and hasattr(self.parent, 'resizable') and self.parent.winfo_class() in ("Toplevel", "CTk", "Tk"):
            self.parent.geometry("400x520")  # Tamaño compacto y centrado
            self.parent.resizable(False, False)
        self.pack(fill="both", expand=True)
        # Configuración del tema antes de crear widgets
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        # Crear widgets
        self.create_widgets()

    def center_window(self, width, height):
        # Ya no es necesario, el frame se ajusta al parent
        pass

    def create_widgets(self):
        try:
            # Si ya existe main_frame, destrúyelo correctamente
            if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
                self.main_frame.destroy()
            # Frame principal con color de fondo
            self.main_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
            self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            # Logo
            logo_path = os.path.join(os.path.dirname(__file__), "imagen", "logoBlanco.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                width = 250  # Más grande que los inputs
                ratio = width / logo_img.width
                height = int(logo_img.height * ratio)
                logo_img = logo_img.resize((width, height), Image.Resampling.LANCZOS)
                self.logo = CTkImage(light_image=logo_img, dark_image=logo_img, size=(width, height))
                logo_label = ctk.CTkLabel(self.main_frame, image=self.logo, text="", width=width, height=height)
                logo_label.pack(pady=(40, 30))
            else:
                ctk.CTkLabel(
                    self.main_frame,
                    text="Sistema de\nAdministración",
                    font=("Quicksand", 28, "bold"),
                    text_color="#2E6B5C"
                ).pack(pady=(40, 30))
            # Título
            titulo = ctk.CTkLabel(
                self.main_frame, 
                text="Iniciar Sesión",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C")
            titulo.pack(pady=(0, 20))
            # Campo de email
            self.email_entry = ctk.CTkEntry(
                self.main_frame, 
                placeholder_text="Email", 
                width=260, height=36,
                corner_radius=10, 
                font=("Quicksand", 12))
            self.email_entry.pack(pady=6)
            # Campo de contraseña
            self.password_entry = ctk.CTkEntry(
                self.main_frame, 
                placeholder_text="Contraseña", 
                width=260, height=36,
                corner_radius=10, 
                show="*", 
                font=("Quicksand", 12))
            self.password_entry.pack(pady=6)
            # Botón de login
            self.login_button = ctk.CTkButton(
                self.main_frame, 
                text="Iniciar Sesión",
                width=260, height=40,
                corner_radius=20, 
                fg_color="#2E6B5C", 
                hover_color="#1D4A3C",
                font=("Quicksand", 13, "bold"),
                command=self.login)
            self.login_button.pack(pady=15)
            # Eliminar botón de registro
            # (No se agrega self.register_button)
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la interfaz: {str(e)}")

    def login(self):
        try:
            email = self.email_entry.get().strip()
            password = self.password_entry.get().strip()
            # Validar campos vacíos
            if not email or not password:
                messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
                return
            from config import AUTH_ENDPOINTS
            from utils import APIHandler
            data = {"email": email, "password": password}
            print(f"Intentando login con: {data}")
            response = APIHandler.make_request('post', AUTH_ENDPOINTS['login'], data=data)
            print(f"Respuesta de la API: {response}")
            if response['status_code'] == 200 and 'token' in response['data']:
                token = response['data']['token']
                user = response['data'].get('user', {})
                from utils import SessionManager
                SessionManager.set_session(token, user)
                if self.on_login_success:
                    self.on_login_success(user)
            else:
                error_msg = response['data'].get('message', 'Credenciales incorrectas') if isinstance(response['data'], dict) else response['data']
                messagebox.showerror("Error", f"Login fallido: {error_msg}")
                print(f"Login fallido: {error_msg}")
        except Exception as e:
            import traceback
            print("Error en el inicio de sesión:", e)
            traceback.print_exc()
            messagebox.showerror("Error", f"Error en el inicio de sesión: {str(e)}")

    # Eliminado: no se permite registro en este sistema
    def show_register(self):
        pass

    def show_login(self):
        try:
            for widget in self.main_frame.winfo_children():
                widget.destroy()
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar el login: {str(e)}")

    # Manejo seguro del cierre de la app
    def safe_close(self):
        try:
            self.parent.destroy()
        except Exception as e:
            import traceback
            print("Error al cerrar la aplicación:", e)
            traceback.print_exc()
