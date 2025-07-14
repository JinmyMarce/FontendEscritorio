#!/usr/bin/env python3
"""
Script de prueba para la nueva interfaz de gráficos estadísticos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from src.interfaces.statistics.statistics_main import EstadisticasVentas

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando prueba de gráficos estadísticos...")
    print("📊 Funcionalidades implementadas:")
    print("   ✅ Gráfico de ventas diarias (doble eje Y)")
    print("   ✅ Gráfico de ventas mensuales (barras)")
    print("   ✅ Top productos más vendidos (barras horizontales)")
    print("   ✅ Estados de pedidos (gráfico de pastel)")
    print("   ✅ Integración con API backend")
    print("   ✅ Datos de fallback automáticos")
    print("   ✅ Paleta de colores profesional")
    print("   ✅ Controles interactivos")
    print("   ✅ Sincronización de períodos con KPIs")
    print()
    
    # Configurar customtkinter
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    
    # Crear ventana principal
    root = ctk.CTk()
    root.title("Estadísticas de Ventas - Con Gráficos Profesionales")
    root.geometry("1400x900")
    root.minsize(1200, 700)
    
    try:
        # Crear interfaz de estadísticas
        app = EstadisticasVentas(root)
        
        print("✅ Interfaz cargada exitosamente")
        print("🎯 Funciones disponibles:")
        print("   • Cambiar período en el selector superior")
        print("   • Cambiar tipo de gráfico en el selector de gráficos")
        print("   • Hacer clic en 'Actualizar' para recargar datos")
        print("   • Los gráficos se sincronizan automáticamente con el período de KPIs")
        print()
        print("📈 Tipos de gráficos disponibles:")
        print("   1. ventas_diarias - Tendencia diaria con transacciones")
        print("   2. ventas_mensuales - Evolución mensual") 
        print("   3. productos_vendidos - Top 10 productos")
        print("   4. estados_pedidos - Distribución de estados")
        print()
        print("🔧 Endpoints API utilizados:")
        print("   • KPIs: /api/v1/admin/reports/data/kpis")
        print("   • Gráficos: /api/v1/admin/reports/data/charts")
        print()
        
        # Ejecutar aplicación
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error al ejecutar la aplicación: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("👋 Aplicación cerrada")

if __name__ == "__main__":
    main()
