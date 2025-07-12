import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
import json
import os
from datetime import datetime
from src.core.config import INVENTORY_MANAGEMENT_ENDPOINTS, UI_CONFIG
from src.shared.utils import APIHandler, UIHelper, SessionManager, DataValidator, DateTimeHelper
from src.interfaces.management.products_management import ProductsSection
from src.interfaces.management.categories_management import GestionCategoriasFrame
from src.interfaces.management.stock_management import StockManagementSection
from PIL import Image, ImageTk
from src.shared.image_handler import ImageHandler

class GestionInventario(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            
            # Configurar layout responsivo con grid
            self.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            
            # Configurar grid del parent para que se expanda
            if hasattr(parent, 'grid_rowconfigure'):
                parent.grid_rowconfigure(0, weight=1)
                parent.grid_columnconfigure(0, weight=1)
            
            # Configurar grid interno
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(2, weight=1)  # El contenido principal se expande
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Inicializar manejador de imágenes
            self.image_handler = ImageHandler()
            
            # Variables de datos (solo las que aún se usan en este módulo principal)
            self.inventario = []
            
            # Variable para rastrear la sección actual
            self.seccion_actual = "productos"  # productos, categorias, stock
            
            self.crear_interfaz_principal()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar gestión de inventario: {str(e)}")
            
    def crear_interfaz_principal(self):
        """Crear la interfaz principal con navegación por pestañas"""
        try:
            # Frame superior con título
            top_frame = ctk.CTkFrame(self, fg_color="transparent")
            top_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 20))
            
            # Título con icono
            title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            title_frame.pack(side="left")
            
            # Cargar y mostrar icono de inventario
            icon = self.image_handler.load_image("inventory.png", (32, 32))
            if icon:
                ctk.CTkLabel(
                    title_frame,
                    image=icon,
                    text=""
                ).pack(side="left", padx=(0, 10))
                
            ctk.CTkLabel(
                title_frame,
                text="Gestión de Inventario",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left")
            
            # Frame de navegación con pestañas
            nav_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            nav_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 20))
            
            # Botones de navegación
            buttons_frame = ctk.CTkFrame(nav_frame, fg_color="transparent")
            buttons_frame.pack(fill="x", padx=20, pady=15)
            
            # Botón Productos
            self.btn_productos = ctk.CTkButton(
                buttons_frame,
                text="📦 Productos",
                command=lambda: self.cambiar_seccion("productos"),
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=150,
                height=35,
                font=("Quicksand", 14, "bold")
            )
            self.btn_productos.pack(side="left", padx=5)
            
            # Botón Categorías
            self.btn_categorias = ctk.CTkButton(
                buttons_frame,
                text="🏷️ Categorías",
                command=lambda: self.cambiar_seccion("categorias"),
                fg_color="#4A934A",
                hover_color="#367832",
                width=150,
                height=35,
                font=("Quicksand", 14, "bold")
            )
            self.btn_categorias.pack(side="left", padx=5)
            
            # Botón Stock
            self.btn_stock = ctk.CTkButton(
                buttons_frame,
                text="📊 Control de Stock",
                command=lambda: self.cambiar_seccion("stock"),
                fg_color="#367832",
                hover_color="#2D5A27",
                width=150,
                height=35,
                font=("Quicksand", 14, "bold")
            )
            self.btn_stock.pack(side="left", padx=5)
            
            # Frame de contenido principal (aquí se cargarán las diferentes secciones)
            self.content_frame = ctk.CTkFrame(self, fg_color="#F5F5F5")
            self.content_frame.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
            self.content_frame.grid_columnconfigure(0, weight=1)
            self.content_frame.grid_rowconfigure(0, weight=1)
            
            # Cargar la sección por defecto
            self.cambiar_seccion("productos")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear interfaz principal: {str(e)}")
            
    def cambiar_seccion(self, seccion):
        """Cambiar entre las diferentes secciones del inventario"""
        try:
            # Actualizar variable de sección actual
            self.seccion_actual = seccion
            
            # Actualizar colores de botones para mostrar el activo
            self.actualizar_botones_navegacion()
            
            # Limpiar frame de contenido
            for widget in self.content_frame.winfo_children():
                widget.destroy()
                
            # Cargar la sección correspondiente
            if seccion == "productos":
                self.crear_seccion_productos()
            elif seccion == "categorias":
                self.crear_seccion_categorias()
            elif seccion == "stock":
                self.crear_seccion_stock()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cambiar sección: {str(e)}")
            
    def actualizar_botones_navegacion(self):
        """Actualizar colores de botones según la sección activa"""
        # Reset todos los botones a color inactivo
        self.btn_productos.configure(fg_color="#6B6B6B", hover_color="#5A5A5A")
        self.btn_categorias.configure(fg_color="#6B6B6B", hover_color="#5A5A5A")
        self.btn_stock.configure(fg_color="#6B6B6B", hover_color="#5A5A5A")
        
        # Destacar botón activo
        if self.seccion_actual == "productos":
            self.btn_productos.configure(fg_color="#2E6B5C", hover_color="#1D4A3C")
        elif self.seccion_actual == "categorias":
            self.btn_categorias.configure(fg_color="#4A934A", hover_color="#367832")
        elif self.seccion_actual == "stock":
            self.btn_stock.configure(fg_color="#367832", hover_color="#2D5A27")
            
    def crear_seccion_productos(self):
        """Crear la sección de gestión de productos usando el componente modular"""
        try:
            # Crear y configurar la sección de productos modular
            self.productos_section = ProductsSection(self.content_frame)
            self.productos_section.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear sección de productos: {str(e)}")
            
    def crear_seccion_categorias(self):
        """Crear la sección de gestión de categorías usando el componente modular"""
        try:
            # Crear y configurar la sección de categorías modular
            self.categorias_section = GestionCategoriasFrame(self.content_frame)
            self.categorias_section.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear sección de categorías: {str(e)}")
            
    def crear_seccion_stock(self):
        """Crear la sección de control de stock usando el componente modular"""
        try:
            # Crear y configurar la sección de stock modular
            self.stock_section = StockManagementSection(self.content_frame)
            self.stock_section.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear sección de stock: {str(e)}")


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1000x650")
    frame = GestionInventario(app)
    app.mainloop()
