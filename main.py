import customtkinter as ctk
import sys
import os

# Añadir el directorio src al path para los imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import UI_CONFIG, APP_CONFIG
from src.shared.utils import SessionManager, UIHelper, create_default_icons
from src.interfaces.auth.login import LoginApp
from src.interfaces.dashboard.dashboard import DashboardApp

class MainApp:
    def __init__(self):
        # Crear íconos por defecto si no existen
        create_default_icons()
        
        # Configuración global de CustomTkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Crear ventana principal
        self.window = ctk.CTk()
        self.window.title(APP_CONFIG['APP_NAME'])
        # Forzar tamaño de login al iniciar
        self.window.geometry("400x520")
        self.window.resizable(False, False)
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.window.winfo_screenheight() // 2) - (520 // 2)
        self.window.geometry(f"400x520+{x}+{y}")
        # Forzar que la ventana esté al frente al iniciar
        self.window.lift()
        self.window.attributes('-topmost', True)
        self.window.after(500, lambda: self.window.attributes('-topmost', False))
        
        # Variables de estado
        self.current_frame = None
        
        # Iniciar aplicación
        self.show_login()
        
    def show_login(self):
        # Limpiar frame actual
        if self.current_frame:
            self.current_frame.destroy()
        # Cambiar tamaño y centrar ventana para el login
        self.window.update_idletasks()
        width, height = 400, 520
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.resizable(False, False)
        # Crear frame de login
        self.current_frame = LoginApp(
            parent=self.window,
            on_login_success=self.show_dashboard
        )
        
    def show_dashboard(self, user_data):
        # Limpiar frame actual
        if self.current_frame:
            self.current_frame.destroy()
        # Cambiar tamaño de ventana para el dashboard y centrar antes de mostrar el frame
        self.window.update_idletasks()
        width, height = 1100, 700
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.resizable(True, True)
        # Crear frame del dashboard SOLO después de centrar y redimensionar
        self.current_frame = DashboardApp(
            parent=self.window,
            on_logout=self.show_login
        )
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run()
