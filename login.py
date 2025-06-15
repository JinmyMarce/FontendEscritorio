import customtkinter as ctk
from PIL import Image, ImageTk
import os
from dashboard import DashboardApp
import tkinter.messagebox as messagebox

class LoginApp:
    def __init__(self):
        # Configuración de la ventana
        self.window = ctk.CTk()
        self.window.title("Login - Sistema de Administración")
        self.window.geometry("400x600")
        self.window.resizable(False, False)  # Evitar problemas de redimensionamiento
        
        # Configuración del tema antes de crear widgets
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Centrar ventana
        self.center_window(400, 600)
        
        # Crear widgets
        self.create_widgets()
        
    def center_window(self, width, height):
        """Centra una ventana en la pantalla"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        try:
            # Frame principal con color de fondo
            self.main_frame = ctk.CTkFrame(self.window, fg_color="#ffffff")
            self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Logo
            logo_path = os.path.join(os.path.dirname(__file__), "imagen", "logoBlanco.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                # Calcular tamaño manteniendo proporción
                width = 150
                ratio = width / logo_img.width
                height = int(logo_img.height * ratio)
                logo_img = logo_img.resize((width, height), Image.Resampling.LANCZOS)
                self.logo = ImageTk.PhotoImage(logo_img)
                logo_label = ctk.CTkLabel(self.main_frame, image=self.logo, text="")
                logo_label.pack(pady=(20, 20))
            else:
                # Título alternativo si no hay logo
                ctk.CTkLabel(
                    self.main_frame,
                    text="Sistema de\nAdministración",
                    font=("Quicksand", 24, "bold"),
                    text_color="#2E6B5C"
                ).pack(pady=(20, 20))
            
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
            
            # Enlace para registro
            self.register_button = ctk.CTkButton(
                self.main_frame,
                text="¿No tienes cuenta? Regístrate",
                fg_color="transparent",
                hover_color="transparent",
                font=("Quicksand", 12),
                text_color="#2E6B5C",
                command=self.show_register)
            self.register_button.pack(pady=10)
            
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
            
            if email == "admin" and password == "admin":
                # Ocultar ventana de login
                self.window.withdraw()
                
                try:
                    # Crear nueva ventana para el dashboard
                    dashboard_window = ctk.CTk()
                    dashboard_window.title("Dashboard - Sistema de Administración")
                    dashboard_window.geometry("1280x720")
                    dashboard_window.resizable(True, True)
                    
                    # Centrar la ventana del dashboard
                    screen_width = dashboard_window.winfo_screenwidth()
                    screen_height = dashboard_window.winfo_screenheight()
                    x = (screen_width - 1280) // 2
                    y = (screen_height - 720) // 2
                    dashboard_window.geometry(f"1280x720+{x}+{y}")
                    
                    # Crear instancia del dashboard
                    dashboard = DashboardApp(dashboard_window)
                    
                    # Función para cerrar sesión
                    def logout():
                        try:
                            dashboard_window.destroy()
                            self.window.deiconify()
                            self.email_entry.delete(0, 'end')
                            self.password_entry.delete(0, 'end')
                            self.email_entry.focus()
                        except Exception as e:
                            messagebox.showerror("Error", f"Error al cerrar sesión: {str(e)}")
                    
                    # Asignar función de logout
                    dashboard_window.protocol("WM_DELETE_WINDOW", logout)
                    
                    # Iniciar el dashboard
                    dashboard_window.mainloop()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error al cargar el dashboard: {str(e)}")
                    self.window.deiconify()
            else:
                messagebox.showerror("Error", "Credenciales incorrectas")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error en el inicio de sesión: {str(e)}")
            
    def show_register(self):
        try:
            # Ocultar elementos de login
            for widget in self.main_frame.winfo_children():
                widget.pack_forget()
                
            # Título de registro
            titulo = ctk.CTkLabel(
                self.main_frame, 
                text="Registro de Usuario",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C")
            titulo.pack(pady=(0, 20))
            
            # Campos del formulario
            campos = {
                "nombre": "Nombre completo",
                "email": "Email",
                "password": "Contraseña",
                "confirm_password": "Confirmar contraseña"
            }
            
            entries = {}
            for key, placeholder in campos.items():
                entry = ctk.CTkEntry(
                    self.main_frame,
                    placeholder_text=placeholder,
                    width=260, height=36,
                    corner_radius=10,
                    font=("Quicksand", 12),
                    show="*" if "password" in key else "")
                entry.pack(pady=6)
                entries[key] = entry
                
            def register():
                try:
                    # Validar campos vacíos
                    if not all(entry.get().strip() for entry in entries.values()):
                        messagebox.showwarning("Advertencia", "Todos los campos son requeridos")
                        return
                        
                    if entries["password"].get() != entries["confirm_password"].get():
                        messagebox.showwarning("Advertencia", "Las contraseñas no coinciden")
                        return
                        
                    # Simular registro exitoso
                    messagebox.showinfo("Éxito", "Usuario registrado correctamente")
                    
                    # Volver al login
                    self.show_login()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Error en el registro: {str(e)}")
                
            # Botón de registro
            ctk.CTkButton(
                self.main_frame,
                text="Registrarse",
                width=260, height=40,
                corner_radius=20,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                font=("Quicksand", 13, "bold"),
                command=register).pack(pady=15)
                
            # Enlace para volver al login
            ctk.CTkButton(
                self.main_frame,
                text="¿Ya tienes cuenta? Inicia sesión",
                fg_color="transparent",
                hover_color="transparent",
                font=("Quicksand", 12),
                text_color="#2E6B5C",
                command=self.show_login).pack(pady=10)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar el registro: {str(e)}")
            self.show_login()
            
    def show_login(self):
        try:
            # Limpiar frame
            for widget in self.main_frame.winfo_children():
                widget.destroy()
                
            # Recrear widgets de login
            self.create_widgets()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar el login: {str(e)}")
            
    def run(self):
        try:
            self.window.mainloop()
        except Exception as e:
            messagebox.showerror("Error", f"Error en la aplicación: {str(e)}")

if __name__ == "__main__":
    try:
        app = LoginApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar la aplicación: {str(e)}")
