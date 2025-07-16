#!/usr/bin/env python3
"""
Script para verificar que los botones se movieron correctamente al header
"""

import customtkinter as ctk
from src.interfaces.statistics.components.analysis_panel import AnalysisPanel

# Configurar CustomTkinter
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

class TestBotonesHeader(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Test - Botones en Header")
        self.geometry("800x600")
        
        # Crear el panel de análisis
        self.analysis_panel = AnalysisPanel(self)
        self.analysis_panel.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Simular datos de prueba para mostrar un gráfico
        test_data = {
            'title': 'Test Chart',
            'labels': ['Producto A', 'Producto B', 'Producto C'],
            'datasets': [{
                'data': [150, 80, 30],
                'backgroundColor': ['#FFD700', '#C0C0C0', '#CD7F32']
            }],
            'chart_type': 'bar'
        }
        
        # Actualizar el gráfico para probar los botones
        self.after(500, lambda: self.analysis_panel.update_chart("productos_vendidos", test_data))
        
        print("✅ Verificaciones a realizar:")
        print("1. Los botones 'Detalle' y 'PNG' deben aparecer en el header derecho")
        print("2. Los botones deben ser pequeños (70x28 px)")
        print("3. No debe haber botones cortados debajo del gráfico")
        print("4. El layout debe verse limpio y organizado")

if __name__ == "__main__":
    app = TestBotonesHeader()
    app.mainloop()
