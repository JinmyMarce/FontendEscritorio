#!/usr/bin/env python3
"""
Script de prueba para los gráficos modernos y compactos
"""

import sys
import os
import json

# Agregar directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
from datetime import datetime, timedelta

# Importar componentes
from src.interfaces.statistics.components.charts_manager import ChartsManager
from src.interfaces.statistics.statistics_service import StatisticsService

class TestModernCharts:
    def __init__(self):
        # Configurar customtkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("Prueba de Gráficos Modernos")
        self.root.geometry("900x700")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de prueba"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color="#FFFFFF")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text="🧪 Prueba de Gráficos Modernos",
            font=("Arial", 24, "bold"),
            text_color="#1F2937"
        )
        title_label.pack(pady=(20, 10))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="Vista compacta con tarjetas optimizadas",
            font=("Arial", 14),
            text_color="#6B7280"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # ChartsManager
        self.charts_manager = ChartsManager(main_frame)
        self.charts_manager.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame de controles
        controls_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(10, 20))
        
        # Botón para cargar datos de prueba
        test_button = ctk.CTkButton(
            controls_frame,
            text="🔄 Cargar Datos de Prueba",
            command=self.load_test_data,
            font=("Arial", 12),
            fg_color="#16A34A",
            hover_color="#15803D"
        )
        test_button.pack(side="left", padx=(0, 10))
        
        # Botón para limpiar
        clear_button = ctk.CTkButton(
            controls_frame,
            text="🧹 Limpiar",
            command=self.clear_charts,
            font=("Arial", 12),
            fg_color="#DC2626",
            hover_color="#B91C1C"
        )
        clear_button.pack(side="left")
        
        # Cargar datos iniciales
        self.load_test_data()
    
    def load_test_data(self):
        """Carga datos de prueba para los gráficos"""
        print("🧪 Cargando datos de prueba para gráficos modernos...")
        
        # Datos simulados
        test_data = {
            "ventas_diarias": {
                "labels": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
                "datasets": [{
                    "label": "Ventas",
                    "data": [1200, 1900, 1500, 2200, 2800, 3100, 2400],
                    "borderColor": "#16A34A",
                    "backgroundColor": "#16A34A"
                }]
            },
            "ventas_mensuales": {
                "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun"],
                "datasets": [{
                    "label": "2024",
                    "data": [15000, 18000, 22000, 19000, 25000, 28000],
                    "borderColor": "#2563EB",
                    "backgroundColor": "#2563EB"
                }]
            },
            "productos_vendidos": {
                "labels": ["Producto A", "Producto B", "Producto C", "Producto D"],
                "datasets": [{
                    "label": "Unidades",
                    "data": [150, 120, 98, 87],
                    "borderColor": "#F59E0B",
                    "backgroundColor": "#F59E0B"
                }]
            },
            "estados_pedidos": {
                "labels": ["Completado", "Pendiente", "Cancelado", "En Proceso"],
                "datasets": [{
                    "label": "Pedidos",
                    "data": [65, 20, 5, 10],
                    "backgroundColor": ["#16A34A", "#F59E0B", "#DC2626", "#2563EB"]
                }]
            }
        }
        
        # Simular período
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Actualizar ChartsManager
        self.charts_manager.update_period(
            fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin.strftime("%Y-%m-%d")
        )
        
        # Cargar datos directamente en las tarjetas
        for chart_type, data in test_data.items():
            self.charts_manager.charts_data[chart_type] = data
            self.charts_manager.charts_grid.update_chart_preview(chart_type, data)
        
        # Actualizar estado
        self.charts_manager.set_loading_status(False, "✅ Datos de prueba cargados")
        
        print("✅ Datos de prueba cargados exitosamente")
    
    def clear_charts(self):
        """Limpia los gráficos"""
        print("🧹 Limpiando gráficos...")
        
        # Limpiar datos
        self.charts_manager.charts_data.clear()
        
        # Recrear las tarjetas
        for chart_type, card in self.charts_manager.charts_grid.chart_cards.items():
            # Destruir canvas actual si existe
            for widget in card.chart_frame.winfo_children():
                widget.destroy()
            
            # Restaurar placeholder
            placeholder = ctk.CTkLabel(
                card.chart_frame,
                text="🔄 Cargando...",
                font=("Arial", 11),
                text_color="#9CA3AF"
            )
            placeholder.pack(expand=True)
            card.placeholder_label = placeholder
        
        # Actualizar estado
        self.charts_manager.set_loading_status(False, "🧹 Gráficos limpiados")
        
        print("✅ Gráficos limpiados")
    
    def run(self):
        """Ejecuta la prueba"""
        print("🚀 Iniciando prueba de gráficos modernos...")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        test = TestModernCharts()
        test.run()
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
