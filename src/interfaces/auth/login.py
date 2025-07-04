import customtkinter as ctk
from PIL import Image, ImageTk
import os
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
            logo_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "assets", "images", "logoBlanco.png")
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
            # Permitir login con Enter solo en los campos de entrada
            self.email_entry.bind('<Return>', lambda event: self.login())
            self.password_entry.bind('<Return>', lambda event: self.login())
            # Eliminar botón de registro
            # (No se agrega self.register_button)
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la interfaz: {str(e)}")

    def login(self):
        import threading
        def do_login():
            try:
                email = self.email_entry.get().strip()
                password = self.password_entry.get().strip()
                # Validar campos vacíos
                if not email or not password:
                    self.hide_spinner()
                    messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
                    return
                from src.core.config import AUTH_ENDPOINTS
                from src.shared.utils import APIHandler
                data = {"email": email, "password": password}
                print(f"Intentando login con: {data}")
                response = APIHandler.make_request('post', AUTH_ENDPOINTS['login'], data=data)
                print(f"Respuesta de la API: {response}")
                self.hide_spinner()
                if response['status_code'] == 200 and 'token' in response['data']:
                    token = response['data']['token']
                    user = response['data'].get('user', {})
                    # Validar si el usuario es administrador (acepta 'admin' o 'administrador')
                    rol_nombre = user.get('rol', '')
                    if not rol_nombre and 'role' in user and isinstance(user['role'], dict):
                        rol_nombre = user['role'].get('nombre', '')
                    if rol_nombre.lower() not in ['administrador']:
                        messagebox.showerror("Acceso denegado", "Acceso denegado: solo administradores pueden ingresar.")
                        print("Acceso denegado: solo administradores pueden ingresar.")
                        return
                    from src.shared.utils import SessionManager
                    SessionManager.set_session(token, user)
                    if self.on_login_success:
                        self.on_login_success(user)
                else:
                    error_msg = None
                    if isinstance(response['data'], dict):
                        # Prioridad: error de acceso denegado
                        if 'error' in response['data'] and 'acceso denegado' in response['data']['error'].lower():
                            error_msg = response['data']['error']
                            messagebox.showerror("Acceso denegado", error_msg)
                            print(f"Acceso denegado: {error_msg}")
                            return
                        # Otro mensaje de error de la API
                        error_msg = response['data'].get('message') or response['data'].get('error')
                    if not error_msg:
                        error_msg = 'Credenciales incorrectas'
                    messagebox.showerror("Error", f"Login fallido: {error_msg}")
                    print(f"Login fallido: {error_msg}")
            except Exception as e:
                import traceback
                print("Error en el inicio de sesión:", e)
                traceback.print_exc()
                self.hide_spinner()
                messagebox.showerror("Error", f"Error en el inicio de sesión: {str(e)}")
        # Mostrar spinner de carga y lanzar hilo
        self.show_spinner()
        threading.Thread(target=do_login, daemon=True).start()

    def show_spinner(self):
        # Overlay "semiransparente" simulado con gris oscuro
        self.spinner_overlay = ctk.CTkFrame(self.main_frame, fg_color="#222222", corner_radius=0)
        self.spinner_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        # Sombra (simulada con otro frame detrás)
        self.spinner_shadow = ctk.CTkFrame(self.spinner_overlay, fg_color="#B0B0B0", corner_radius=18)
        self.spinner_shadow.place(relx=0.5, rely=0.5, anchor="center", x=6, y=6)
        # Cuadro central con borde
        self.spinner_frame = ctk.CTkFrame(self.spinner_overlay, fg_color="#FFFFFF", corner_radius=18, border_width=2, border_color="#2E6B5C")
        self.spinner_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.spinner_frame.lift()
        # Canvas para spinner circular
        self.spinner_canvas = ctk.CTkCanvas(self.spinner_frame, width=48, height=48, bg="#FFFFFF", highlightthickness=0)
        self.spinner_canvas.pack(pady=(22, 8))
        # Texto estilizado
        self.spinner_label = ctk.CTkLabel(self.spinner_frame, text="Cargando...", font=("Quicksand", 15, "bold"), text_color="#2E6B5C")
        self.spinner_label.pack(padx=30, pady=(0, 18))
        self.spinner_running = True
        self.spinner_angle = 0
        self.animate_spinner()

    def animate_spinner(self):
        if not hasattr(self, 'spinner_canvas') or not self.spinner_running:
            return
        self.spinner_canvas.delete("all")
        # Dibuja un arco circular animado
        extent = 270  # Arco de 270 grados
        self.spinner_canvas.create_oval(6, 6, 42, 42, outline="#E0E0E0", width=5)  # Fondo gris claro
        self.spinner_canvas.create_arc(6, 6, 42, 42, start=self.spinner_angle, extent=extent, style="arc", outline="#2E6B5C", width=5)
        self.spinner_angle = (self.spinner_angle + 12) % 360
        self.spinner_canvas.after(40, self.animate_spinner)

    def hide_spinner(self):
        self.spinner_running = False
        if hasattr(self, 'spinner_overlay'):
            self.spinner_overlay.destroy()
        if hasattr(self, 'spinner_shadow'):
            self.spinner_shadow.destroy()
        if hasattr(self, 'spinner_frame'):
            self.spinner_frame.destroy()

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
