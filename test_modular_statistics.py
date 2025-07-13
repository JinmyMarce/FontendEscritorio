#!/usr/bin/env python3
"""
Script de prueba para la nueva estructura modular de estadísticas
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
    root.title("Estadísticas de Ventas - Estructura Modular")
    root.geometry("1200x800")
    
    # Crear interfaz de estadísticas modular
    app = EstadisticasVentas(root)
    
    # Ejecutar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
