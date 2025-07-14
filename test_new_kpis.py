#!/usr/bin/env python3
"""
Script de prueba para verificar los nuevos KPIs con la estructura mejorada
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from src.interfaces.statistics.components.kpi_grid import KPIGrid

def test_new_kpi_structure():
    """Prueba la nueva estructura de KPIs"""
    
    # Datos de ejemplo con la nueva estructura de respuesta
    new_kpi_data = {
        "total_ventas": {
            "valor": "508.00",
            "formato": "currency",
            "crecimiento": {
                "porcentaje": 1000,
                "tendencia": "positiva",
                "valor_anterior": "39.00",
                "diferencia_absoluta": 469
            }
        },
        "total_pedidos": {
            "valor": 10,
            "formato": "number",
            "crecimiento": {
                "porcentaje": 400,
                "tendencia": "positiva",
                "valor_anterior": 2,
                "diferencia_absoluta": 8
            }
        },
        "ticket_promedio": {
            "valor": 50.8,
            "formato": "currency",
            "crecimiento": {
                "porcentaje": 160.51,
                "tendencia": "positiva",
                "valor_anterior": 19.5,
                "diferencia_absoluta": 31.3
            }
        },
        "conversion_rate": {
            "valor": 12.5,
            "formato": "percentage",
            "contexto": {
                "carritos_creados": 8,
                "pedidos_completados": 1,
                "descripcion": "De 8 carritos, 1 se convirtieron en pedidos"
            }
        }
    }
    
    # Configurar interfaz
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    
    root = ctk.CTk()
    root.title("Prueba KPIs Mejorados")
    root.geometry("1000x400")
    root.configure(fg_color="#F8FAFC")
    
    # Frame principal
    main_frame = ctk.CTkFrame(root, fg_color="#FFFFFF", corner_radius=15)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Título
    title_label = ctk.CTkLabel(
        main_frame,
        text="🧪 Prueba de KPIs con Nueva Estructura",
        font=("Arial", 24, "bold"),
        text_color="#16A34A"
    )
    title_label.pack(pady=(20, 30))
    
    # Grid de KPIs
    kpi_grid = KPIGrid(main_frame)
    kpi_grid.pack(fill="x", padx=30, pady=(0, 30))
    
    # Botón para cargar datos de prueba
    def load_test_data():
        print("📊 Cargando datos de prueba...")
        kpi_grid.update_kpi_data(new_kpi_data)
        print("✅ Datos cargados exitosamente!")
    
    test_button = ctk.CTkButton(
        main_frame,
        text="Cargar Datos de Prueba",
        command=load_test_data,
        font=("Arial", 14, "bold"),
        fg_color="#16A34A",
        hover_color="#15803D",
        height=40,
        width=200
    )
    test_button.pack(pady=(0, 20))
    
    # Información de los datos
    info_text = """
    📋 Datos de Prueba:
    • Total Ventas: S/. 508.00 (+1000% crecimiento!)
    • Total Pedidos: 10 (+400% crecimiento)
    • Ticket Promedio: S/. 50.80 (+160.51% crecimiento)
    • Tasa de Conversión: 12.5% (contexto: 1 de 8 carritos)
    """
    
    info_label = ctk.CTkLabel(
        main_frame,
        text=info_text,
        font=("Arial", 12),
        text_color="#6B7280",
        justify="left"
    )
    info_label.pack(pady=(0, 20))
    
    # Cargar datos automáticamente
    root.after(1000, load_test_data)  # Cargar después de 1 segundo
    
    print("🚀 Iniciando prueba de KPIs mejorados...")
    root.mainloop()

if __name__ == "__main__":
    test_new_kpi_structure()
