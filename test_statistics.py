#!/usr/bin/env python3
"""
Script de prueba para la interfaz de estadísticas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import customtkinter as ctk
from src.interfaces.management.statistics_management import EstadisticasVentas
from src.shared.utils import SessionManager

def main():
    """Función principal para probar la interfaz de estadísticas"""
    # Configurar tema
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")
    
    # Crear ventana principal
    root = ctk.CTk()
    root.title("Prueba - Estadísticas de Ventas")
    root.geometry("1200x800")
    
    # Simular token de sesión (opcional para pruebas)
    # SessionManager.save_token("test_token")
    
    # Crear interfaz de estadísticas
    app = EstadisticasVentas(root)
    
    # Ejecutar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
