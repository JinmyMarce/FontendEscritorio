import customtkinter as ctk
from config import UI_CONFIG, APP_CONFIG
from utils import SessionManager, UIHelper, create_default_icons
from login import LoginApp
from dashboard import DashboardApp

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
        self.window.geometry(f"{APP_CONFIG['WINDOW_SIZE']['width']}x{APP_CONFIG['WINDOW_SIZE']['height']}")
        self.window.minsize(
            APP_CONFIG['MIN_WINDOW_SIZE']['width'],
            APP_CONFIG['MIN_WINDOW_SIZE']['height']
        )
        
        # Centrar ventana
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (APP_CONFIG['WINDOW_SIZE']['width'] // 2)
        y = (self.window.winfo_screenheight() // 2) - (APP_CONFIG['WINDOW_SIZE']['height'] // 2)
        self.window.geometry(f"+{x}+{y}")
        
        # Variables de estado
        self.current_frame = None
        
        # Iniciar aplicación
        self.show_login()
        
    def show_login(self):
        # Limpiar frame actual
        if self.current_frame:
            self.current_frame.destroy()
            
        # Crear frame de login
        self.current_frame = LoginApp(
            parent=self.window,
            on_login_success=self.show_dashboard
        )
        
    def show_dashboard(self, user_data):
        # Limpiar frame actual
        if self.current_frame:
            self.current_frame.destroy()
            
        # Crear frame del dashboard
        self.current_frame = DashboardApp(
            parent=self.window,
            on_logout=self.show_login
        )
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = MainApp()
    app.run() 