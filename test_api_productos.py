#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de prueba específico para la conexión con API de productos
en la gestión de categorías.

Funcionalidades a probar:
1. Conexión con API real de productos
2. Filtrado de productos por categoría
3. Manejo de diferentes estructuras de respuesta API
4. Fallback a datos de ejemplo cuando API falla
"""

import customtkinter as ctk
import sys
import os

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.interfaces.management.categories_management import GestionCategoriasFrame

class TestAPIProductosApp:
    def __init__(self):
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Crear ventana principal
        self.root = ctk.CTk()
        self.root.title("Test API - Productos de Categorías")
        self.root.geometry("1300x900")
        
        # Configurar grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Marco principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Título de la prueba
        title = ctk.CTkLabel(
            main_frame,
            text="🔗 Test Conexión API - Productos de Categorías",
            font=("Quicksand", 24, "bold"),
            text_color="#2E6B5C"
        )
        title.grid(row=0, column=0, pady=20)
        
        # Instrucciones
        instructions_frame = ctk.CTkFrame(main_frame, fg_color="#E3F2FD", corner_radius=10)
        instructions_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        instructions = ctk.CTkLabel(
            instructions_frame,
            text=(
                "🔗 FUNCIONALIDAD API IMPLEMENTADA:\n\n"
                "📡 Conexión real con API de productos:\n"
                "   • Endpoint específico: /admin/products?category_id={id}\n"
                "   • Fallback: /admin/products (todos) + filtrado local\n"
                "   • Manejo de diferentes estructuras de respuesta\n\n"
                "🔍 Procesamiento inteligente:\n"
                "   • Normalización de campos (nombre/name, precio/price, etc.)\n"
                "   • Múltiples formas de relación categoría-producto\n"
                "   • Filtrado robusto por ID de categoría\n\n"
                "📊 Estadísticas en tiempo real:\n"
                "   • Conteo real de productos desde API\n"
                "   • Cálculo de valor total del inventario\n"
                "   • Indicadores cuando no coinciden datos API/local\n\n"
                "🛡️ Manejo de errores:\n"
                "   • Fallback automático a datos de ejemplo\n"
                "   • Debug logs para diagnóstico\n"
                "   • Mensajes informativos para el usuario\n\n"
                "💡 CÓMO PROBAR:\n"
                "• Haz clic en números con 🔍 en 'N° Productos'\n"
                "• Observa la consola para logs de API\n"
                "• Compara datos reales vs ejemplos\n"
                "• Prueba con diferentes categorías"
            ),
            font=("Quicksand", 11),
            text_color="#1565C0",
            justify="left"
        )
        instructions.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Frame de gestión de categorías
        self.categorias_frame = GestionCategoriasFrame(main_frame)
        self.categorias_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
    
    def run(self):
        print("🚀 Iniciando test de conexión API para productos...")
        print("="*70)
        print("🔗 FUNCIONALIDADES DE API IMPLEMENTADAS:")
        print("="*70)
        print("📡 Conexión con API real:")
        print("   ✓ Endpoint específico por categoría")
        print("   ✓ Fallback a todos los productos + filtrado")
        print("   ✓ Normalización de campos de diferentes APIs")
        print("   ✓ Manejo de múltiples estructuras de respuesta")
        print("")
        print("🔍 Procesamiento de datos:")
        print("   ✓ Filtrado inteligente por ID de categoría")
        print("   ✓ Mapeo de campos (name->nombre, price->precio, etc.)")
        print("   ✓ Detección de relaciones categoria_id/category_id/id_categoria")
        print("   ✓ Validación y limpieza de datos")
        print("")
        print("📊 Estadísticas dinámicas:")
        print("   ✓ Conteo real desde API")
        print("   ✓ Cálculo de valor total de inventario")
        print("   ✓ Detección de inconsistencias datos locales/API")
        print("")
        print("🛡️ Manejo de errores:")
        print("   ✓ Fallback graceful a datos de ejemplo")
        print("   ✓ Logs detallados para debugging")
        print("   ✓ Mensajes informativos al usuario")
        print("")
        
        # Verificar entorno y configuración
        if os.environ.get('WAYLAND_DISPLAY') or os.environ.get('XDG_SESSION_TYPE') == 'wayland':
            print("🐧 Entorno: Linux con Wayland")
        else:
            print("🖥️ Entorno: X11 o Windows")
            
        # Verificar si hay token de sesión
        try:
            from src.shared.utils import SessionManager
            token = SessionManager.get_token()
            if token:
                print("🔑 Token de sesión: Disponible")
                print("   → La API usará autenticación con Bearer token")
            else:
                print("🔒 Token de sesión: No disponible")
                print("   → La API intentará sin autenticación (puede fallar)")
        except:
            print("⚠️ No se pudo verificar token de sesión")
        
        print("\n" + "="*70)
        print("🎯 INSTRUCCIONES DE PRUEBA:")
        print("="*70)
        print("1. Busca categorías con productos (números con 🔍)")
        print("2. Haz clic en 'N° Productos' para abrir modal")
        print("3. Observa los logs en la consola:")
        print("   • 'Cargando productos para categoría ID: X'")
        print("   • 'Intentando URL específica: ...'")
        print("   • 'Productos encontrados en API: X'")
        print("   • 'Productos filtrados para categoría X: Y'")
        print("4. Compara datos mostrados:")
        print("   • Si son datos reales: verás IDs/precios de la API")
        print("   • Si son ejemplos: verás datos predefinidos")
        print("5. Verifica estadísticas en el footer del modal")
        print("6. Prueba con diferentes categorías")
        print("="*70)
        
        self.root.mainloop()

if __name__ == "__main__":
    app = TestAPIProductosApp()
    app.run()
