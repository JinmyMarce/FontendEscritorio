#!/usr/bin/env python3
"""
Script de demostración para mostrar la interfaz de estadísticas con datos simulados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import customtkinter as ctk
from src.interfaces.management.statistics_management import EstadisticasVentas

# Simular datos de ejemplo
def simular_datos_demo():
    """Simula datos de ejemplo para la demostración"""
    return {
        'total_ventas': {
            'valor': 15750.50,
            'formato': 'currency',
            'crecimiento': 12.5
        },
        'total_pedidos': {
            'valor': 42,
            'formato': 'number',
            'crecimiento': 8.3
        },
        'ticket_promedio': {
            'valor': 375.25,
            'formato': 'currency'
        },
        'conversion_rate': {
            'valor': 3.2,
            'formato': 'percentage'
        }
    }

class EstadisticasDemo(EstadisticasVentas):
    """Versión demo de EstadisticasVentas con datos simulados"""
    
    def cargar_kpis(self, fecha_inicio, fecha_fin):
        """Override para usar datos simulados"""
        print(f"Simulando KPIs para período: {fecha_inicio} a {fecha_fin}")
        self.kpis_data = simular_datos_demo()
        self.actualizar_widgets_kpis()

def main():
    """Función principal para la demostración"""
    # Configurar tema
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    
    # Crear ventana principal
    root = ctk.CTk()
    root.title("Demo - Estadísticas de Ventas con Soles Peruanos")
    root.geometry("1200x800")
    
    # Crear interfaz de estadísticas con datos simulados
    app = EstadisticasDemo(root)
    
    # Ejecutar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
