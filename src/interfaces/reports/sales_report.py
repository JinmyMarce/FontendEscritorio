import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from src.core.config import REPORTS_ENDPOINTS, UI_CONFIG
from src.shared.utils import APIHandler, UIHelper, SessionManager, DataValidator, DateTimeHelper
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

# API endpoint
API_REPORTS_URL = REPORTS_ENDPOINTS['sales']

# UI Setup
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class ReporteVenta(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="#FFFFFF")
        
        # Datos de ejemplo
        self.ventas = [
            {
                "fecha": "2024-03-01",
                "producto": "Fresa Fresca",
                "cantidad": 50,
                "total": 2299.50
            },
            {
                "fecha": "2024-03-02",
                "producto": "Mermelada de Fresa",
                "cantidad": 30,
                "total": 1065.00
            },
            {
                "fecha": "2024-03-03",
                "producto": "Jugo de Fresa",
                "cantidad": 40,
                "total": 1000.00
            },
            {
                "fecha": "2024-03-04",
                "producto": "Fresa Fresca",
                "cantidad": 45,
                "total": 2069.55
            },
            {
                "fecha": "2024-03-05",
                "producto": "Mermelada de Fresa",
                "cantidad": 25,
                "total": 887.50
            }
        ]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame superior con título y filtros
        top_frame = ctk.CTkFrame(self, fg_color="#FFFFFF")
        top_frame.pack(fill="x", padx=20, pady=10)
        
        # Título
        ctk.CTkLabel(
            top_frame,
            text="Reportes de Ventas",
            font=("Quicksand", 24, "bold"),
            text_color="#2E6B5C"
        ).pack(side="left")
        
        # Frame de filtros
        filter_frame = ctk.CTkFrame(top_frame, fg_color="#FFFFFF")
        filter_frame.pack(side="right")
        
        # Filtro por período
        ctk.CTkLabel(
            filter_frame,
            text="Período:",
            font=("Quicksand", 12)
        ).pack(side="left", padx=(0, 5))
        
        self.periodo_var = ctk.StringVar(value="Última semana")
        periodos = ["Última semana", "Último mes", "Último año"]
        
        def actualizar_periodo(periodo):
            self.cargar_datos()
            self.actualizar_graficos()
        
        periodo_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=periodos,
            variable=self.periodo_var,
            command=actualizar_periodo
        )
        periodo_menu.pack(side="left", padx=5)
        
        # Frame de contenido principal
        self.content_frame = ctk.CTkFrame(self, fg_color="white")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Frame para gráficos
        graficos_frame = ctk.CTkFrame(self.content_frame)
        graficos_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Gráfico de ventas por día
        self.fig_ventas, self.ax_ventas = plt.subplots(figsize=(8, 4))
        self.canvas_ventas = FigureCanvasTkAgg(self.fig_ventas, master=graficos_frame)
        self.canvas_ventas.get_tk_widget().pack(side="left", fill="both", expand=True)
        
        # Gráfico de productos más vendidos
        self.fig_productos, self.ax_productos = plt.subplots(figsize=(8, 4))
        self.canvas_productos = FigureCanvasTkAgg(self.fig_productos, master=graficos_frame)
        self.canvas_productos.get_tk_widget().pack(side="right", fill="both", expand=True)
        
        # Frame para tabla
        tabla_frame = ctk.CTkFrame(self.content_frame)
        tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabla de ventas
        columns = ("Fecha", "Producto", "Cantidad", "Total")
        self.tabla = ttk.Treeview(tabla_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar tabla y scrollbar
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Frame para resumen
        resumen_frame = ctk.CTkFrame(self.content_frame)
        resumen_frame.pack(fill="x", padx=10, pady=10)
        
        # Labels para totales
        self.total_ventas_label = ctk.CTkLabel(
            resumen_frame,
            text="Total de ventas: $0.00",
            font=("Quicksand", 16, "bold")
        )
        self.total_ventas_label.pack(side="left", padx=20)
        
        self.total_productos_label = ctk.CTkLabel(
            resumen_frame,
            text="Total de productos: 0",
            font=("Quicksand", 16, "bold")
        )
        self.total_productos_label.pack(side="right", padx=20)
        
        # Cargar datos iniciales
        self.cargar_datos()
        self.actualizar_graficos()
        
    def cargar_datos(self):
        # Simular llamada a API
        print("GET /reports/api/v1/sales/")
        
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Insertar ventas
        total_ventas = 0
        total_productos = 0
        
        for venta in self.ventas:
            self.tabla.insert("", "end", values=(
                venta["fecha"],
                venta["producto"],
                venta["cantidad"],
                f"${venta['total']:.2f}"
            ))
            
            total_ventas += venta["total"]
            total_productos += venta["cantidad"]
        
        # Actualizar totales
        self.total_ventas_label.configure(text=f"Total de ventas: ${total_ventas:.2f}")
        self.total_productos_label.configure(text=f"Total de productos: {total_productos}")
    
    def actualizar_graficos(self):
        # Limpiar gráficos
        self.ax_ventas.clear()
        self.ax_productos.clear()
        
        # Datos para gráfico de ventas por día
        fechas = [venta["fecha"] for venta in self.ventas]
        totales = [venta["total"] for venta in self.ventas]
        
        self.ax_ventas.bar(fechas, totales, color="#2E6B5C")
        self.ax_ventas.set_title("Ventas por día")
        self.ax_ventas.set_xlabel("Fecha")
        self.ax_ventas.set_ylabel("Total ($)")
        plt.setp(self.ax_ventas.xaxis.get_majorticklabels(), rotation=45)
        
        # Datos para gráfico de productos más vendidos
        productos = {}
        for venta in self.ventas:
            if venta["producto"] not in productos:
                productos[venta["producto"]] = 0
            productos[venta["producto"]] += venta["cantidad"]
        
        nombres = list(productos.keys())
        cantidades = list(productos.values())
        
        self.ax_productos.pie(cantidades, labels=nombres, autopct='%1.1f%%', colors=["#2E6B5C", "#3F4F2A", "#5C8374"])
        self.ax_productos.set_title("Productos más vendidos")
        
        # Ajustar layout y actualizar
        self.fig_ventas.tight_layout()
        self.fig_productos.tight_layout()
        self.canvas_ventas.draw()
        self.canvas_productos.draw()

    def cargar_ventas(self):
        token = SessionManager.get_token()
        headers = {'Authorization': f'Bearer {token}'} if token else {}
        response = APIHandler.make_request('get', API_REPORTS_URL, headers=headers)
        if response['status_code'] == 200:
            self.ventas = response['data']
        else:
            self.ventas = []

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1000x800")
    frame = ReporteVenta(app)
    app.mainloop()
