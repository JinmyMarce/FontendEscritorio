import customtkinter as ctk
import os
from PIL import Image
from src.interfaces.management.inventory_management import GestionInventario
from src.interfaces.management.orders_management import GestionPedidos
from src.interfaces.management.clients_management import GestionClientes
from src.interfaces.management.notifications_management import GestionNotificaciones
from src.interfaces.management.payments_management import GestionPagos
from src.shared.image_handler import ImageHandler
import tkinter.messagebox as messagebox
from src.core.config import ORDERS_ENDPOINTS
from src.shared.utils import APIHandler, SessionManager

# Configuración de la UI
UI_CONFIG = {
    'PRIMARY_COLOR': '#2E6B5C',
    'HIGHLIGHT_COLOR': '#1D4A3C',
    'SECONDARY_COLOR': '#557A46',
    'ACCENT_COLOR': '#7A9D54',
    'BG_COLOR': '#F5F5F5'
}

class DashboardApp(ctk.CTkFrame):
    def __init__(self, parent, on_logout=None):
        super().__init__(parent)
        self.parent = parent
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        try:
            # Configuración del tema
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("green")
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Frame principal con color de fondo
            self.main_frame = ctk.CTkFrame(self, fg_color=UI_CONFIG['BG_COLOR'])
            self.main_frame.pack(fill="both", expand=True)
            
            # Frame de la barra lateral con esquinas redondeadas
            self.sidebar = ctk.CTkFrame(self.main_frame, fg_color=UI_CONFIG['PRIMARY_COLOR'], width=250, corner_radius=15)
            self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
            self.sidebar.pack_propagate(False)
            
            # Frame para el contenido con esquinas redondeadas
            self.content = ctk.CTkFrame(self.main_frame, fg_color="#FFFFFF", corner_radius=15)
            self.content.pack(side="right", fill="both", expand=True, padx=(0,10), pady=10)
            
            # Logo
            try:
                logo = self.image_handler.get_image("logoBlanco.png", (200, 200))
                if logo:
                    self.logo_label = ctk.CTkLabel(self.sidebar, image=logo, text="")
                    self.logo_label.pack(pady=20)
                else:
                    self.logo_label = ctk.CTkLabel(
                        self.sidebar,
                        text="Sistema de\nAdministración",
                        font=("Quicksand", 24, "bold"),
                        text_color="white"
                    )
                    self.logo_label.pack(pady=20)
            except Exception as e:
                print(f"Error al cargar el logo: {str(e)}")
                self.logo_label = ctk.CTkLabel(
                    self.sidebar,
                    text="Sistema de\nAdministración",
                    font=("Quicksand", 24, "bold"),
                    text_color="white"
                )
                self.logo_label.pack(pady=20)
            
            # Separador
            separator = ctk.CTkFrame(self.sidebar, height=2, fg_color="white")
            separator.pack(fill="x", padx=20, pady=10)
            
            # Botones de navegación con mejor estilo
            self.nav_buttons = []
            self.current_module = None
            
            self.add_nav_button("🏠 Inicio", self.mostrar_inicio)
            self.add_nav_button("📦 Inventario", self.mostrar_inventario)
            self.add_nav_button("🛒 Pedidos", self.mostrar_pedidos)
            self.add_nav_button("👥 Clientes", self.mostrar_clientes)
            self.add_nav_button("🔔 Notificaciones", self.mostrar_notificaciones)
            self.add_nav_button("💰 Pagos", self.mostrar_pagos)
            
            # Botón de cerrar sesión
            self.add_nav_button("🚪 Cerrar Sesión", self.cerrar_sesion)
            
            # Mostrar inicio por defecto
            self.mostrar_inicio()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar dashboard: {str(e)}")
            
    def add_nav_button(self, text, command, icon=""):
        try:
            button = ctk.CTkButton(
                self.sidebar,
                text=f"{icon} {text}",
                command=command,
                fg_color="transparent",
                text_color="white",
                hover_color=UI_CONFIG['HIGHLIGHT_COLOR'],
                anchor="w",
                height=40,
                corner_radius=10,
                font=("Quicksand", 14)
            )
            button.pack(fill="x", padx=10, pady=5)
            self.nav_buttons.append(button)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear botón de navegación: {str(e)}")
            
    def clear_content(self):
        try:
            for widget in self.content.winfo_children():
                widget.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al limpiar contenido: {str(e)}")
            
    def mostrar_inicio(self):
        try:
            self.clear_content()
            
            # Frame de bienvenida con esquinas redondeadas
            welcome_frame = ctk.CTkFrame(self.content, fg_color="#FFFFFF", corner_radius=15)
            welcome_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Logo grande en el centro
            try:
                logo = self.image_handler.get_image("logo.png", (400, 400))
                if logo:
                    self.home_logo_label = ctk.CTkLabel(welcome_frame, image=logo, text="")
                    self.home_logo_label.pack(pady=30)
            except Exception as e:
                print(f"Error al cargar el logo del inicio: {str(e)}")
            
            # Título de bienvenida con mejor estilo
            ctk.CTkLabel(
                welcome_frame,
                text="¡Bienvenido al Sistema de Administración!",
                font=("Quicksand", 32, "bold"),
                text_color=UI_CONFIG['PRIMARY_COLOR']
            ).pack(pady=20)
            
            # Descripción con mejor estilo
            ctk.CTkLabel(
                welcome_frame,
                text="Seleccione una opción del menú para comenzar:",
                font=("Quicksand", 18)
            ).pack(pady=10)
            
            # Grid de opciones con mejor estilo
            grid_frame = ctk.CTkFrame(welcome_frame, fg_color="#FFFFFF")
            grid_frame.pack(pady=30)
            
            # Configurar grid
            grid_frame.grid_columnconfigure(0, weight=1)
            grid_frame.grid_columnconfigure(1, weight=1)
            
            # Opciones del dashboard
            options = [
                {
                    "icon": "📦",
                    "title": "Gestión de Inventario",
                    "desc": "Administre su inventario de productos",
                    "command": self.mostrar_inventario
                },
                {
                    "icon": "🛒",
                    "title": "Gestión de Pedidos",
                    "desc": "Administre los pedidos de sus clientes",
                    "command": self.mostrar_pedidos
                },
                {
                    "icon": "👥",
                    "title": "Gestión de Clientes",
                    "desc": "Administre la información de sus clientes",
                    "command": self.mostrar_clientes
                },
                {
                    "icon": "🔔",
                    "title": "Notificaciones",
                    "desc": "Gestione las notificaciones del sistema",
                    "command": self.mostrar_notificaciones
                },
                {
                    "icon": "💰",
                    "title": "Gestión de Pagos",
                    "desc": "Administre los pagos y transacciones",
                    "command": self.mostrar_pagos
                }
            ]
            
            for i, opt in enumerate(options):
                # Frame de la opción con sombra y hover
                option_frame = ctk.CTkFrame(grid_frame, fg_color="#FFFFFF", corner_radius=10)
                option_frame.grid(row=i//2, column=i%2, padx=15, pady=15, sticky="nsew")
                
                # Icono
                ctk.CTkLabel(
                    option_frame,
                    text=opt["icon"],
                    font=("Segoe UI Emoji", 32)
                ).pack(pady=(20, 10))
                
                # Título
                ctk.CTkLabel(
                    option_frame,
                    text=opt["title"],
                    font=("Quicksand", 18, "bold"),
                    text_color=UI_CONFIG['PRIMARY_COLOR']
                ).pack(pady=(0, 10))
                
                # Descripción
                ctk.CTkLabel(
                    option_frame,
                    text=opt["desc"],
                    font=("Quicksand", 14),
                    wraplength=250
                ).pack(pady=(0, 20))
                
                # Botón
                ctk.CTkButton(
                    option_frame,
                    text="Ir",
                    command=opt["command"],
                    fg_color=UI_CONFIG['PRIMARY_COLOR'],
                    hover_color=UI_CONFIG['HIGHLIGHT_COLOR'],
                    width=120,
                    height=35,
                    corner_radius=8,
                    font=("Quicksand", 14)
                ).pack(pady=(0, 20))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar inicio: {str(e)}")
            
    def mostrar_inventario(self):
        try:
            self.clear_content()
            self.current_module = GestionInventario(self.content)
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar inventario: {str(e)}")
            
    def mostrar_pedidos(self):
        try:
            self.clear_content()
            self.current_module = GestionPedidos(self.content)
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar pedidos: {str(e)}")
            
    def mostrar_clientes(self):
        try:
            self.clear_content()
            self.current_module = GestionClientes(self.content)
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar clientes: {str(e)}")
            
    def mostrar_notificaciones(self):
        try:
            self.clear_content()
            self.current_module = GestionNotificaciones(self.content)
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar notificaciones: {str(e)}")
            
    def mostrar_pagos(self):
        try:
            self.clear_content()
            self.current_module = GestionPagos(self.content)
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar pagos: {str(e)}")
            
    def cerrar_sesion(self):
        try:
            if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar sesión?"):
                if self.on_logout is not None:
                    self.on_logout()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cerrar sesión: {str(e)}")

def obtener_pedido_completo_backend(pedido_id):
    try:
        url = ORDERS_ENDPOINTS['detail'].format(id=pedido_id)
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = APIHandler.make_request('get', url, headers=headers)
        if response.get('status_code') == 200:
            return response.get('data')
    except Exception as e:
        print(f"Error al obtener pedido completo: {e}")
    return None
