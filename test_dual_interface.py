#!/usr/bin/env python3
"""
Script de prueba para la nueva interfaz dual de estadísticas
"""

import sys
import os
import json

# Agregar directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import customtkinter as ctk
from datetime import datetime, timedelta

# Importar componentes
from src.interfaces.statistics.components.dual_panel_manager import DualPanelManager
from src.interfaces.statistics.statistics_service import StatisticsService

class TestDualInterface:
    def __init__(self):
        # Configurar customtkinter
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("green")
        
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("Nueva Interfaz Dual - Análisis y Reportes")
        self.root.geometry("1400x800")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de prueba"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color="#F1F5F9")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header de prueba
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 15))
        
        # Título principal
        title_label = ctk.CTkLabel(
            header_frame,
            text="🚀 Nueva Interfaz Dual de Estadísticas",
            font=("Arial", 26, "bold"),
            text_color="#1F2937"
        )
        title_label.pack(side="left")
        
        # Controles de prueba
        controls_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        controls_frame.pack(side="right")
        
        # Botón para cargar datos de prueba
        test_button = ctk.CTkButton(
            controls_frame,
            text="🔄 Cargar Datos de Prueba",
            command=self.load_test_data,
            font=("Arial", 12),
            fg_color="#16A34A",
            hover_color="#15803D",
            width=150
        )
        test_button.pack(side="left", padx=(0, 10))
        
        # Botón para cambiar gráfico
        switch_button = ctk.CTkButton(
            controls_frame,
            text="🔀 Cambiar Gráfico",
            command=self.switch_chart,
            font=("Arial", 12),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            width=130
        )
        switch_button.pack(side="left")
        
        # Manager dual
        self.dual_manager = DualPanelManager(main_frame)
        self.dual_manager.pack(fill="both", expand=True)
        
        # Cargar datos iniciales
        self.load_test_data()
    
    def load_test_data(self):
        """Carga datos de prueba"""
        print("🧪 Cargando datos de prueba para interfaz dual...")
        
        # Simular período
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=30)
        
        # Actualizar período
        self.dual_manager.update_period(
            fecha_inicio.strftime("%Y-%m-%d"),
            fecha_fin.strftime("%Y-%m-%d")
        )
        
        print("✅ Datos de prueba cargados")
    
    def switch_chart(self):
        """Cambia entre tipos de gráficos para probar la navegación"""
        chart_types = ["ventas_diarias", "ventas_mensuales", "productos_vendidos", "estados_pedidos"]
        current = self.dual_manager.get_current_chart_type()
        
        try:
            current_index = chart_types.index(current)
            next_index = (current_index + 1) % len(chart_types)
            next_chart = chart_types[next_index]
            
            # Simular click en navegación
            self.dual_manager.chart_navigation.select_chart(next_chart)
            
            print(f"🔀 Cambiado a: {next_chart}")
            
        except ValueError:
            # Si no encuentra el current, usar el primero
            self.dual_manager.chart_navigation.select_chart(chart_types[0])
    
    def run(self):
        """Ejecuta la prueba"""
        print("🚀 Iniciando prueba de interfaz dual...")
        self.root.mainloop()

if __name__ == "__main__":
    try:
        test = TestDualInterface()
        test.run()
    except Exception as e:
        print(f"❌ Error en la prueba: {str(e)}")
        import traceback
        traceback.print_exc()
