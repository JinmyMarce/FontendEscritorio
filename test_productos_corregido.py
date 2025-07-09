#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Versión corregida y simplificada del módulo de gestión de productos
con funcionalidad de cambio de estado completamente funcional
"""

import customtkinter as ctk
import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.interfaces.management.products_management import ProductsSection

class TestProductosCorregido:
    def __init__(self):
        # Configurar tema
        ctk.set_appearance_mode("light")
        
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("✅ Test Productos - Funcionalidad Corregida")
        self.root.geometry("1400x900")
        
        # Configurar grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Header con instrucciones específicas
        header_frame = ctk.CTkFrame(self.root, fg_color="#2E6B5C", corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        instructions = ctk.CTkLabel(
            header_frame,
            text="🔧 VERSIÓN CORREGIDA - Problemas solucionados:\n" +
                 "✅ Doble modal eliminado (ahora solo abre modal de detalles)\n" +
                 "✅ Combobox de estado implementado correctamente\n" +
                 "✅ Clic en columna de estado para cambiar Activo/Inactivo\n" +
                 "✅ Indicador visual con cursor pointer sobre estado\n" +
                 "✅ Debug habilitado para troubleshooting",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
            justify="left"
        )
        instructions.pack(pady=15)
        
        # Sección de productos corregida
        try:
            self.products_section = ProductsSection(self.root)
            self.products_section.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
            print("✅ ProductsSection inicializado correctamente")
            
        except Exception as e:
            print(f"❌ Error al inicializar ProductsSection: {str(e)}")
            return
        
        # Footer con información de debug
        footer_frame = ctk.CTkFrame(self.root, fg_color="#F8F9FA", corner_radius=10)
        footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        debug_info = ctk.CTkLabel(
            footer_frame,
            text="🐛 Debug: Abra la consola para ver mensajes detallados | " +
                 "Endpoint: /admin/products/{id}/status | Método: PATCH",
            font=ctk.CTkFont(size=12),
            text_color="#2E6B5C"
        )
        debug_info.pack(pady=10)
    
    def run(self):
        print("🚀 Iniciando test corregido de gestión de productos...")
        print("="*60)
        print("📋 Funcionalidades corregidas:")
        print("   ✅ Un solo modal al hacer doble clic")
        print("   ✅ Combobox de estado funcional")
        print("   ✅ Cursor pointer sobre columna de estado")
        print("   ✅ Debug completo habilitado")
        print("="*60)
        self.root.mainloop()

if __name__ == "__main__":
    app = TestProductosCorregido()
    app.run()
