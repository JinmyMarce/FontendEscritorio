import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import pandas as pd
from datetime import datetime, timedelta
from config import UI_CONFIG
from utils import APIHandler, UIHelper, SessionManager, DataValidator, DateTimeHelper

class ReporteUsuario(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(fg_color="#F5F5F5")
        
        # Frame superior
        top_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        top_frame.pack(fill="x", pady=(0, 20))
        
        # Título con icono
        title_frame = ctk.CTkFrame(top_frame, fg_color="#FFFFFF")
        title_frame.pack(side="left", padx=20, pady=20)
        
        ctk.CTkLabel(
            title_frame,
            text="👤 Reporte de Usuario",
            font=("Quicksand", 24, "bold"),
            text_color="#2E6B5C"
        ).pack(side="left")
        
        # Frame de búsqueda
        search_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 20))
        
        # Búsqueda por email
        ctk.CTkLabel(
            search_frame,
            text="Email del usuario:",
            font=("Quicksand", 14)
        ).pack(side="left", padx=(20, 10), pady=20)
        
        self.email_var = ctk.StringVar()
        self.email_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.email_var,
            width=300,
            placeholder_text="Ingrese el email del usuario...",
            border_width=0,
            fg_color="#F5F5F5"
        )
        self.email_entry.pack(side="left", padx=10, pady=20)
        
        # Botón de búsqueda
        search_button = ctk.CTkButton(
            search_frame,
            text="🔍 Buscar",
            command=self.buscar_usuario,
            fg_color="#2E6B5C",
            hover_color="#1D4A3C",
            width=120,
            height=35,
            corner_radius=8,
            font=("Quicksand", 12)
        )
        search_button.pack(side="left", padx=10, pady=20)
        
        # Frame para información del usuario
        self.user_info_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        self.user_info_frame.pack(fill="x", pady=(0, 20))
        
        # Frame para pedidos del usuario
        self.pedidos_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
        self.pedidos_frame.pack(fill="both", expand=True)
        
    def buscar_usuario(self):
        try:
            email = self.email_var.get().strip()
            if not email:
                messagebox.showerror("Error", "Por favor ingrese un email")
                return
                
            # Aquí se haría la llamada a la API para obtener los datos del usuario
            # Por ahora usamos datos de ejemplo
            usuario = {
                "id": 1,
                "nombre": "Juan",
                "apellidos": "Pérez",
                "email": email,
                "telefono": "123456789",
                "fecha_creacion": "2024-01-01",
                "estado": "Activo",
                "rol": "Cliente"
            }
            
            pedidos = [
                {
                    "id": 1,
                    "fecha": "2024-03-01",
                    "total": 150.00,
                    "estado": "Entregado"
                },
                {
                    "id": 2,
                    "fecha": "2024-03-15",
                    "total": 75.50,
                    "estado": "En proceso"
                }
            ]
            
            # Mostrar información del usuario
            self.mostrar_info_usuario(usuario)
            
            # Mostrar pedidos del usuario
            self.mostrar_pedidos(pedidos)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar usuario: {str(e)}")
            
    def mostrar_info_usuario(self, usuario):
        try:
            # Limpiar frame
            for widget in self.user_info_frame.winfo_children():
                widget.destroy()
                
            # Título
            ctk.CTkLabel(
                self.user_info_frame,
                text="Información del Usuario",
                font=("Quicksand", 18, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(20, 10))
            
            # Grid de información
            info_frame = ctk.CTkFrame(self.user_info_frame, fg_color="#FFFFFF")
            info_frame.pack(fill="x", padx=20, pady=(0, 20))
            
            # Configurar grid
            info_frame.grid_columnconfigure(0, weight=1)
            info_frame.grid_columnconfigure(1, weight=1)
            
            # Campos a mostrar
            campos = [
                ("Nombre:", usuario["nombre"]),
                ("Apellidos:", usuario["apellidos"]),
                ("Email:", usuario["email"]),
                ("Teléfono:", usuario["telefono"]),
                ("Fecha de registro:", usuario["fecha_creacion"]),
                ("Estado:", usuario["estado"]),
                ("Rol:", usuario["rol"])
            ]
            
            for i, (label, value) in enumerate(campos):
                # Label
                ctk.CTkLabel(
                    info_frame,
                    text=label,
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C"
                ).grid(row=i, column=0, padx=10, pady=5, sticky="w")
                
                # Valor
                ctk.CTkLabel(
                    info_frame,
                    text=value,
                    font=("Quicksand", 12)
                ).grid(row=i, column=1, padx=10, pady=5, sticky="w")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar información del usuario: {str(e)}")
            
    def mostrar_pedidos(self, pedidos):
        try:
            # Limpiar frame
            for widget in self.pedidos_frame.winfo_children():
                widget.destroy()
                
            # Título
            ctk.CTkLabel(
                self.pedidos_frame,
                text="Historial de Pedidos",
                font=("Quicksand", 18, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(20, 10))
            
            # Crear tabla
            tabla = ttk.Treeview(
                self.pedidos_frame,
                columns=("id", "fecha", "total", "estado"),
                show="headings",
                style="Custom.Treeview"
            )
            
            # Configurar columnas
            tabla.heading("id", text="ID")
            tabla.heading("fecha", text="Fecha")
            tabla.heading("total", text="Total")
            tabla.heading("estado", text="Estado")
            
            tabla.column("id", width=50)
            tabla.column("fecha", width=150)
            tabla.column("total", width=100)
            tabla.column("estado", width=100)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(self.pedidos_frame, orient="vertical", command=tabla.yview)
            tabla.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar tabla y scrollbar
            tabla.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 20))
            scrollbar.pack(side="right", fill="y", pady=(0, 20))
            
            # Insertar datos
            for pedido in pedidos:
                tabla.insert("", "end", values=(
                    pedido["id"],
                    pedido["fecha"],
                    f"${pedido['total']:.2f}",
                    pedido["estado"]
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar pedidos: {str(e)}") 