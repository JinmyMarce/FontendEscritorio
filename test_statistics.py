#!/usr/bin/env python3
"""
Script de prueba para la nueva estructura modular de estadísticas

Mejoras implementadas:
- 📊 Estructura modular con componentes separados
- 🎨 Iconos modernos y profesionales para KPIs
- 🎨 Colores mejorados y más profesionales
- 💰 Formato de moneda en soles peruanos (S/.)
- 🔄 Botón de actualizar con estado de carga
- 📱 Diseño responsivo y moderno
- 🏗️ Arquitectura limpia con separación de responsabilidades

Componentes:
- StatisticsControls: Controles de filtros y acciones
- KPIGrid: Grid de tarjetas KPI
- KPICard: Tarjetas individuales para cada KPI
- StatisticsService: Servicio de datos
- StatisticsMain: Interfaz principal
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import customtkinter as ctk
from src.interfaces.statistics import EstadisticasVentas

def main():
    """Función principal para probar la interfaz modular"""
    # Configurar tema
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    
    # Crear ventana principal
    root = ctk.CTk()
    root.title("Estadísticas de Ventas - Paleta Verde Profesional")
    root.geometry("1200x800")
    
    print("🚀 Iniciando interfaz de estadísticas con nueva paleta verde...")
    print("✨ Mejoras implementadas:")
    print("   🎨 Paleta de colores verde principal con rojo suave")
    print("   💰 Iconos coloridos SIN cuadros de fondo")
    print("   📊 Iconos modernos: 💰 📦 🎯 📈")
    print("   💱 Formato de moneda en soles (S/.)")
    print("   🏗️ Estructura completamente modular")
    print("   🎯 Colores de crecimiento diferenciados")
    print("   ✨ Diseño limpio y profesional")
    
    # Crear interfaz de estadísticas modular
    app = EstadisticasVentas(root)
    
    # Ejecutar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
