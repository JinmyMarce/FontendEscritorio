import customtkinter as ctk
from PIL import Image, ImageTk
import os
import tkinter.messagebox as messagebox
from customtkinter import CTkImage
import json
import base64

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
            # Limpiar widgets existentes de forma segura
            self.cleanup_widgets()
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
            
            # Checkbox para recordar credenciales
            self.remember_var = ctk.BooleanVar()
            self.remember_checkbox = ctk.CTkCheckBox(
                self.main_frame,
                text="Recordar credenciales",
                variable=self.remember_var,
                font=("Quicksand", 12),
                text_color="#2E6B5C",
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                border_color="#2E6B5C"
            )
            self.remember_checkbox.pack(pady=(10, 5))
            
            # Cargar credenciales guardadas si existen
            self.load_saved_credentials()
            
            # Frame para botones adicionales
            button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
            button_frame.pack(pady=(5, 10))
            
            # Botón para limpiar credenciales guardadas
            self.clear_credentials_button = ctk.CTkButton(
                button_frame,
                text="Limpiar guardadas",
                width=120, height=28,
                corner_radius=15,
                fg_color="#6B6B6B",
                hover_color="#5A5A5A",
                font=("Quicksand", 10),
                command=self.clear_credentials_action
            )
            self.clear_credentials_button.pack(side="left", padx=5)
            
            # Botón para verificar credenciales guardadas
            self.check_credentials_button = ctk.CTkButton(
                button_frame,
                text="Ver guardadas",
                width=120, height=28,
                corner_radius=15,
                fg_color="#4A934A",
                hover_color="#367832",
                font=("Quicksand", 10),
                command=self.show_saved_credentials_info
            )
            self.check_credentials_button.pack(side="left", padx=5)
            
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
                    # Verificar que el widget aún existe antes de ocultar spinner
                    if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
                        self.hide_spinner()
                        messagebox.showwarning("Advertencia", "Por favor complete todos los campos")
                    return
                
                from src.core.config import AUTH_ENDPOINTS
                from src.shared.utils import APIHandler
                data = {"email": email, "password": password}
                print(f"Intentando login con: {data}")
                response = APIHandler.make_request('post', AUTH_ENDPOINTS['login'], data=data)
                print(f"Respuesta de la API: {response}")
                
                # Verificar que el widget aún existe antes de continuar
                if not (hasattr(self, 'main_frame') and self.main_frame.winfo_exists()):
                    return
                
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
                    
                    # Manejar el guardado de credenciales
                    if self.remember_var.get():
                        # Guardar credenciales si está marcado
                        self.save_credentials(email, password)
                    else:
                        # Eliminar credenciales guardadas si está desmarcado
                        self.clear_saved_credentials()
                    
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
                # Verificar que el widget aún existe antes de ocultar spinner
                if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
                    self.hide_spinner()
                    messagebox.showerror("Error", f"Error en el inicio de sesión: {str(e)}")
        
        # Mostrar spinner de carga y lanzar hilo solo si el widget existe
        if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
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
        # Verificar que el canvas aún existe y el spinner está corriendo
        if not self.spinner_running or not hasattr(self, 'spinner_canvas'):
            return
        try:
            if not self.spinner_canvas.winfo_exists():
                return
        except Exception:
            return
            
        self.spinner_canvas.delete("all")
        # Dibuja un arco circular animado
        extent = 270  # Arco de 270 grados
        self.spinner_canvas.create_oval(6, 6, 42, 42, outline="#E0E0E0", width=5)  # Fondo gris claro
        self.spinner_canvas.create_arc(6, 6, 42, 42, start=self.spinner_angle, extent=extent, style="arc", outline="#2E6B5C", width=5)
        self.spinner_angle = (self.spinner_angle + 12) % 360
        
        # Verificar nuevamente antes de programar la siguiente animación
        if self.spinner_running and hasattr(self, 'spinner_canvas'):
            try:
                if self.spinner_canvas.winfo_exists():
                    self.spinner_canvas.after(40, self.animate_spinner)
            except Exception:
                pass  # Ignorar errores si el widget ya no existe

    def hide_spinner(self):
        self.spinner_running = False
        # Destruir widgets de spinner de forma segura
        for attr in ['spinner_overlay', 'spinner_shadow', 'spinner_frame', 'spinner_canvas']:
            if hasattr(self, attr):
                widget = getattr(self, attr)
                try:
                    if widget and widget.winfo_exists():
                        widget.destroy()
                except Exception:
                    pass  # Ignorar errores de destrucción
                finally:
                    if hasattr(self, attr):
                        delattr(self, attr)

    # Eliminado: no se permite registro en este sistema
    def show_register(self):
        pass

    def show_login(self):
        try:
            if hasattr(self, 'main_frame') and self.main_frame.winfo_exists():
                self.cleanup_widgets()
            self.create_widgets()
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar el login: {str(e)}")

    def cleanup_widgets(self):
        """Limpia widgets de forma segura para evitar errores de Tcl"""
        # Detener spinner si está corriendo
        if hasattr(self, 'spinner_running'):
            self.spinner_running = False
        
        # Destruir widgets de spinner primero
        self.hide_spinner()
        
        # Destruir main_frame y sus hijos de forma segura
        if hasattr(self, 'main_frame'):
            try:
                if self.main_frame.winfo_exists():
                    # Destruir widgets hijos primero
                    for child in self.main_frame.winfo_children():
                        try:
                            if child.winfo_exists():
                                child.destroy()
                        except Exception:
                            pass
                    # Luego destruir el frame principal
                    self.main_frame.destroy()
            except Exception:
                pass  # Ignorar errores de destrucción
            finally:
                if hasattr(self, 'main_frame'):
                    delattr(self, 'main_frame')

    # Manejo seguro del cierre de la app
    def safe_close(self):
        try:
            # Limpiar recursos antes de cerrar
            self.cleanup_widgets()
            if hasattr(self, 'parent') and self.parent.winfo_exists():
                self.parent.destroy()
        except Exception as e:
            import traceback
            print("Error al cerrar la aplicación:", e)
            traceback.print_exc()
    
    def __del__(self):
        """Destructor para limpieza de recursos"""
        try:
            self.cleanup_widgets()
        except Exception:
            pass  # Ignorar errores en el destructor
    
    def get_credentials_file_path(self):
        """Obtener la ruta del archivo de credenciales"""
        try:
            # Crear directorio de datos si no existe
            app_data_dir = os.path.join(os.path.expanduser("~"), ".fresaterra_admin")
            os.makedirs(app_data_dir, exist_ok=True)
            return os.path.join(app_data_dir, "credentials.dat")
        except Exception:
            # Fallback a directorio local
            return os.path.join(os.path.dirname(__file__), "credentials.dat")
    
    def simple_encrypt(self, text):
        """Cifrado simple usando base64 (no es seguro para producción)"""
        try:
            # Agregar un salt simple
            salt = "fresaterra_admin_2024"
            combined = f"{salt}:{text}:{salt}"
            encoded = base64.b64encode(combined.encode('utf-8')).decode('utf-8')
            return encoded
        except Exception:
            return None
    
    def simple_decrypt(self, encoded_text):
        """Descifrado simple usando base64"""
        try:
            decoded = base64.b64decode(encoded_text.encode('utf-8')).decode('utf-8')
            salt = "fresaterra_admin_2024"
            if decoded.startswith(f"{salt}:") and decoded.endswith(f":{salt}"):
                # Extraer el texto original
                return decoded[len(salt)+1:-len(salt)-1]
            return None
        except Exception:
            return None
    
    def save_credentials(self, email, password):
        """Guardar credenciales de forma cifrada"""
        try:
            credentials_file = self.get_credentials_file_path()
            
            # Cifrar credenciales
            encrypted_email = self.simple_encrypt(email)
            encrypted_password = self.simple_encrypt(password)
            
            if encrypted_email and encrypted_password:
                credentials_data = {
                    "email": encrypted_email,
                    "password": encrypted_password,
                    "remember": True
                }
                
                with open(credentials_file, 'w', encoding='utf-8') as f:
                    json.dump(credentials_data, f)
                
                print("Credenciales guardadas exitosamente")
            
        except Exception as e:
            print(f"Error al guardar credenciales: {str(e)}")
    
    def load_saved_credentials(self):
        """Cargar credenciales guardadas"""
        try:
            credentials_file = self.get_credentials_file_path()
            
            if not os.path.exists(credentials_file):
                return
            
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials_data = json.load(f)
            
            if credentials_data.get("remember", False):
                # Descifrar credenciales
                email = self.simple_decrypt(credentials_data.get("email", ""))
                password = self.simple_decrypt(credentials_data.get("password", ""))
                
                if email and password:
                    # Llenar los campos
                    self.email_entry.delete(0, 'end')
                    self.email_entry.insert(0, email)
                    self.password_entry.delete(0, 'end')
                    self.password_entry.insert(0, password)
                    
                    # Marcar el checkbox
                    self.remember_var.set(True)
                    
                    print("Credenciales cargadas exitosamente")
        
        except Exception as e:
            print(f"Error al cargar credenciales: {str(e)}")
    
    def clear_saved_credentials(self):
        """Eliminar credenciales guardadas"""
        try:
            credentials_file = self.get_credentials_file_path()
            if os.path.exists(credentials_file):
                os.remove(credentials_file)
                print("Credenciales eliminadas")
        except Exception as e:
            print(f"Error al eliminar credenciales: {str(e)}")
    
    def clear_credentials_action(self):
        """Acción para limpiar credenciales guardadas"""
        try:
            result = messagebox.askyesno(
                "Confirmar", 
                "¿Está seguro de que desea eliminar las credenciales guardadas?",
                icon='question'
            )
            if result:
                self.clear_saved_credentials()
                # Limpiar campos actuales
                self.email_entry.delete(0, 'end')
                self.password_entry.delete(0, 'end')
                self.remember_var.set(False)
                messagebox.showinfo("Éxito", "Credenciales eliminadas correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar credenciales: {str(e)}")
    
    def show_saved_credentials_info(self):
        """Mostrar información sobre las credenciales guardadas"""
        try:
            credentials_file = self.get_credentials_file_path()
            
            if not os.path.exists(credentials_file):
                messagebox.showinfo("Información", "No hay credenciales guardadas")
                return
            
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials_data = json.load(f)
            
            if credentials_data.get("remember", False):
                email = self.simple_decrypt(credentials_data.get("email", ""))
                if email:
                    # Mostrar solo parte del email por seguridad
                    if '@' in email:
                        username, domain = email.split('@', 1)
                        masked_email = f"{username[:2]}{'*' * (len(username) - 2)}@{domain}"
                    else:
                        masked_email = f"{email[:2]}{'*' * (len(email) - 2)}"
                    
                    messagebox.showinfo(
                        "Credenciales Guardadas", 
                        f"Usuario guardado: {masked_email}\n\n" +
                        "Las credenciales se cargarán automáticamente al iniciar la aplicación."
                    )
                else:
                    messagebox.showwarning("Advertencia", "Las credenciales guardadas están corruptas")
            else:
                messagebox.showinfo("Información", "No hay credenciales guardadas")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar credenciales: {str(e)}")
    
    def toggle_password_visibility(self):
        """Alternar visibilidad de la contraseña"""
        try:
            if self.password_entry.cget("show") == "*":
                self.password_entry.configure(show="")
                self.toggle_password_button.configure(text="🙈")
            else:
                self.password_entry.configure(show="*")
                self.toggle_password_button.configure(text="👁️")
        except Exception as e:
            print(f"Error al alternar visibilidad: {str(e)}")
