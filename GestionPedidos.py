import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
from config import ORDERS_ENDPOINTS, UI_CONFIG
from utils import APIHandler, UIHelper, SessionManager, DataValidator, DateTimeHelper
import json
import os
from datetime import datetime, timedelta
import random
from PIL import Image, ImageTk
from image_handler import ImageHandler

# --- COLORES ---
PRIMARY_COLOR = "#3A6B5D"
ACCENT_COLOR = "#EC0617"
SECONDARY_COLOR = "#3E526B"
HIGHLIGHT_COLOR = "#3F4F2A"
TEXT_COLOR = "#000000"

# --- CONFIGURACIÓN DE UI ---
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# --- FUNCIONES DE API ---
API_BASE = "http://localhost/shipping/api/v1/"  # Cambiar por la URL real

def obtener_pedidos():
    try:
        response = requests.get(API_BASE)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Error al obtener pedidos:", e)
    return []

def actualizar_estado(pedido_id, nuevo_estado):
    try:
        response = requests.put(f"{API_BASE}{pedido_id}/", json={"estado": nuevo_estado})
        return response.status_code == 200
    except Exception as e:
        print("Error al actualizar:", e)
    return False

# --- CLASE PRINCIPAL DE INTERFAZ ---
class GestionPedidos(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Configurar tema
            self.configure(fg_color="#F5F5F5")
            
            # Datos de ejemplo
            self.pedidos = self.cargar_datos_ejemplo()
            
            # Frame superior
            top_frame = ctk.CTkFrame(self, fg_color="transparent")
            top_frame.pack(fill="x", pady=(0, 20))
            
            # Título con icono
            title_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
            title_frame.pack(side="left")
            
            try:
                # Cargar y redimensionar icono
                icon = Image.open("imagen/pedidos.png")
                icon = icon.resize((32, 32))
                self.icon_image = ImageTk.PhotoImage(icon)
                ctk.CTkLabel(
                    title_frame,
                    image=self.icon_image,
                    text=""
                ).pack(side="left", padx=(0, 10))
            except:
                pass
                
            ctk.CTkLabel(
                title_frame,
                text="Gestión de Pedidos",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(side="left")
            
            # Frame para búsqueda y filtros
            search_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            search_frame.pack(fill="x", pady=(0, 20))
            
            # Búsqueda
            search_label = ctk.CTkLabel(
                search_frame,
                text="🔍",
                font=("Quicksand", 16)
            )
            search_label.pack(side="left", padx=(15, 5))
            
            self.search_var = ctk.StringVar()
            self.search_var.trace("w", self.filtrar_tabla)
            search_entry = ctk.CTkEntry(
                search_frame,
                textvariable=self.search_var,
                width=300,
                placeholder_text="Buscar por ID, cliente o estado...",
                border_width=0,
                fg_color="#F5F5F5"
            )
            search_entry.pack(side="left", padx=5, pady=10)
            
            # Separador
            ctk.CTkFrame(
                search_frame,
                width=1,
                height=30,
                fg_color="#E0E0E0"
            ).pack(side="left", padx=15)
            
            # Filtro de estado
            ctk.CTkLabel(
                search_frame,
                text="Estado:",
                font=("Quicksand", 12)
            ).pack(side="left", padx=5)
            
            self.estado_var = ctk.StringVar(value="Todos")
            self.estado_var.trace("w", self.filtrar_tabla)
            estado_menu = ctk.CTkOptionMenu(
                search_frame,
                values=["Todos", "Pendiente", "En Proceso", "Enviado", "Entregado", "Cancelado"],
                variable=self.estado_var,
                width=120,
                fg_color="#2E6B5C",
                button_color="#1D4A3C",
                button_hover_color="#153A2C",
                dropdown_fg_color="#FFFFFF",
                dropdown_hover_color="#F5F5F5",
                dropdown_text_color="#2E6B5C"
            )
            estado_menu.pack(side="left", padx=5, pady=10)
            
            # Botones de acción
            action_frame = ctk.CTkFrame(search_frame, fg_color="transparent")
            action_frame.pack(side="right", padx=15)
            
            # Botón nuevo pedido
            ctk.CTkButton(
                action_frame,
                text="➕ Nuevo Pedido",
                command=self.nuevo_pedido,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=120
            ).pack(side="left", padx=5)
            
            # Botón actualizar estado
            ctk.CTkButton(
                action_frame,
                text="🔄 Actualizar Estado",
                command=self.actualizar_estado,
                fg_color="#FFA000",
                hover_color="#F57C00",
                width=150
            ).pack(side="left", padx=5)
            
            # Tabla con estilo
            style = ttk.Style()
            style.configure(
                "Treeview",
                background="#FFFFFF",
                foreground="#2E6B5C",
                rowheight=30,
                fieldbackground="#FFFFFF",
                borderwidth=0
            )
            style.configure(
                "Treeview.Heading",
                background="#F5F5F5",
                foreground="#2E6B5C",
                relief="flat",
                font=("Quicksand", 10, "bold")
            )
            style.map(
                "Treeview.Heading",
                background=[("active", "#E0E0E0")]
            )
            
            # Frame para tabla
            table_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=10)
            table_frame.pack(fill="both", expand=True)
            
            # Tabla
            columns = (
                "id_pedido", "cliente", "monto_total", 
                "estado", "fecha_creacion", "metodo_pago"
            )
            
            self.tabla = ttk.Treeview(
                table_frame,
                columns=columns,
                show="headings",
                selectmode="browse",
                style="Treeview"
            )
            
            # Configurar columnas
            self.tabla.heading("id_pedido", text="ID")
            self.tabla.heading("cliente", text="Cliente")
            self.tabla.heading("monto_total", text="Monto Total")
            self.tabla.heading("estado", text="Estado")
            self.tabla.heading("fecha_creacion", text="Fecha Creación")
            self.tabla.heading("metodo_pago", text="Método de Pago")
            
            # Configurar anchos
            self.tabla.column("id_pedido", width=50, anchor="center")
            self.tabla.column("cliente", width=200)
            self.tabla.column("monto_total", width=100, anchor="center")
            self.tabla.column("estado", width=100, anchor="center")
            self.tabla.column("fecha_creacion", width=150, anchor="center")
            self.tabla.column("metodo_pago", width=120, anchor="center")
            
            # Scrollbar personalizado
            scrollbar = ttk.Scrollbar(
                table_frame,
                orient="vertical",
                command=self.tabla.yview
            )
            self.tabla.configure(yscrollcommand=scrollbar.set)
            
            # Empaquetar tabla y scrollbar
            self.tabla.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y", pady=10)
            
            # Cargar datos
            self.cargar_datos()
            
            # Bind doble clic
            self.tabla.bind("<Double-1>", self.ver_detalles)
            
            # Bind tecla Enter
            self.tabla.bind("<Return>", self.ver_detalles)
            
            # Bind tecla Delete
            self.tabla.bind("<Delete>", self.cancelar_pedido)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar: {str(e)}")
            
    def cargar_datos_ejemplo(self):
        return [
            {
                "id_pedido": 1,
                "cliente": "Juan Pérez",
                "monto_total": 150.00,
                "estado": "Pendiente",
                "fecha_creacion": "2024-03-15 10:00:00",
                "metodo_pago": "Tarjeta",
                "items": [
                    {
                        "producto": "Producto 1",
                        "cantidad": 2,
                        "precio": 50.00,
                        "subtotal": 100.00
                    },
                    {
                        "producto": "Producto 2",
                        "cantidad": 1,
                        "precio": 50.00,
                        "subtotal": 50.00
                    }
                ]
            },
            {
                "id_pedido": 2,
                "cliente": "María López",
                "monto_total": 75.50,
                "estado": "Enviado",
                "fecha_creacion": "2024-03-15 11:00:00",
                "metodo_pago": "Efectivo",
                "items": [
                    {
                        "producto": "Producto 3",
                        "cantidad": 1,
                        "precio": 75.50,
                        "subtotal": 75.50
                    }
                ]
            }
        ]
        
    def cargar_datos(self):
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Cargar datos
            for pedido in self.pedidos:
                # Configurar tags para el estado
                tags = (pedido["estado"].lower().replace(" ", "_"),)
                
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        pedido["id_pedido"],
                        pedido["cliente"],
                        f"S/. {pedido['monto_total']:.2f}",
                        pedido["estado"],
                        pedido["fecha_creacion"],
                        pedido["metodo_pago"]
                    ),
                    tags=tags
                )
                
            # Configurar colores de estado
            self.tabla.tag_configure("pendiente", foreground="#FFA000")
            self.tabla.tag_configure("en_proceso", foreground="#1976D2")
            self.tabla.tag_configure("enviado", foreground="#7B1FA2")
            self.tabla.tag_configure("entregado", foreground="#2E7D32")
            self.tabla.tag_configure("cancelado", foreground="#C62828")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            
    def filtrar_tabla(self, *args):
        try:
            # Obtener valores de filtro
            busqueda = self.search_var.get().lower()
            estado = self.estado_var.get()
            
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Filtrar y cargar datos
            for pedido in self.pedidos:
                # Aplicar filtros
                if estado != "Todos" and pedido["estado"] != estado:
                    continue
                    
                if busqueda and not any(
                    busqueda in str(valor).lower()
                    for valor in [
                        str(pedido["id_pedido"]),
                        pedido["cliente"],
                        pedido["estado"]
                    ]
                ):
                    continue
                    
                # Configurar tags para el estado
                tags = (pedido["estado"].lower().replace(" ", "_"),)
                
                # Insertar fila
                self.tabla.insert(
                    "",
                    "end",
                    values=(
                        pedido["id_pedido"],
                        pedido["cliente"],
                        f"S/. {pedido['monto_total']:.2f}",
                        pedido["estado"],
                        pedido["fecha_creacion"],
                        pedido["metodo_pago"]
                    ),
                    tags=tags
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar datos: {str(e)}")
            
    def nuevo_pedido(self):
        try:
            # Ventana de nuevo pedido
            dialog = PedidoDialog(self, "Nuevo Pedido")
            if dialog.result:
                # Agregar nuevo pedido
                nuevo_id = max([p["id_pedido"] for p in self.pedidos], default=0) + 1
                
                self.pedidos.append({
                    "id_pedido": nuevo_id,
                    **dialog.result,
                    "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "estado": "Pendiente"
                })
                
                self.cargar_datos()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Pedido creado correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nuevo pedido: {str(e)}")
            
    def actualizar_estado(self):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
                return
                
            # Obtener pedido seleccionado
            item = self.tabla.item(seleccion[0])
            pedido_id = item["values"][0]
            pedido = next((p for p in self.pedidos if p["id_pedido"] == pedido_id), None)
            
            if pedido:
                # Ventana de actualización de estado
                dialog = EstadoDialog(self, pedido)
                if dialog.result:
                    # Actualizar estado
                    pedido["estado"] = dialog.result
                    self.cargar_datos()
                    self.guardar_datos()
                    messagebox.showinfo("Éxito", "Estado actualizado correctamente")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar estado: {str(e)}")
            
    def cancelar_pedido(self, event=None):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un pedido")
                return
                
            # Obtener pedido seleccionado
            item = self.tabla.item(seleccion[0])
            pedido_id = item["values"][0]
            pedido = next((p for p in self.pedidos if p["id_pedido"] == pedido_id), None)
            
            if pedido:
                # Confirmar cancelación
                if messagebox.askyesno("Confirmar", f"¿Está seguro de cancelar el pedido #{pedido_id}?"):
                    # Cancelar pedido
                    pedido["estado"] = "Cancelado"
                    self.cargar_datos()
                    self.guardar_datos()
                    messagebox.showinfo("Éxito", "Pedido cancelado correctamente")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al cancelar pedido: {str(e)}")

    def guardar_datos(self):
        try:
            # Crear directorio si no existe
            os.makedirs("datos", exist_ok=True)
            
            # Guardar datos en archivo
            with open("datos/pedidos.json", "w", encoding="utf-8") as f:
                json.dump(self.pedidos, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")

    def ver_detalles(self, event):
        try:
            # Obtener item seleccionado
            item = self.tabla.selection()[0]
            pedido_id = self.tabla.item(item)["values"][0]
            pedido = next((p for p in self.pedidos if p["id_pedido"] == pedido_id), None)
            
            if pedido:
                # Mostrar detalles
                DetallesPedidoDialog(self, pedido)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")

class PedidoDialog:
    def __init__(self, parent, title):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("500x600")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Centrar ventana
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text=title,
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Campos del formulario
            campos = [
                ("Cliente", "cliente"),
                ("Método de Pago", "metodo_pago")
            ]
            
            self.entries = {}
            
            for i, (label, field) in enumerate(campos):
                # Label
                ctk.CTkLabel(
                    main_frame,
                    text=label,
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C"
                ).pack(pady=(20 if i == 0 else 10, 0))
                
                if field == "metodo_pago":
                    # Combo box para método de pago
                    self.metodo_pago_var = ctk.StringVar(value="Tarjeta")
                    metodo_pago_menu = ctk.CTkOptionMenu(
                        main_frame,
                        values=["Tarjeta", "Efectivo", "Transferencia"],
                        variable=self.metodo_pago_var,
                        width=300,
                        fg_color="#2E6B5C",
                        button_color="#1D4A3C",
                        button_hover_color="#153A2C",
                        dropdown_fg_color="#FFFFFF",
                        dropdown_hover_color="#F5F5F5",
                        dropdown_text_color="#2E6B5C"
                    )
                    metodo_pago_menu.pack(pady=5)
                    self.entries[field] = self.metodo_pago_var
                else:
                    # Entry para cliente
                    entry = ctk.CTkEntry(
                        main_frame,
                        width=300,
                        placeholder_text=f"Ingrese {label.lower()}...",
                        border_width=0,
                        fg_color="#F5F5F5"
                    )
                    entry.pack(pady=5)
                    self.entries[field] = entry
            
            # Frame para items
            items_frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5")
            items_frame.pack(fill="x", pady=20)
            
            # Título de items
            ctk.CTkLabel(
                items_frame,
                text="Productos",
                font=("Quicksand", 14, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(10, 10))
            
            # Lista de items
            self.items = []
            
            # Botón agregar item
            ctk.CTkButton(
                items_frame,
                text="➕ Agregar Producto",
                command=self.agregar_item,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=200
            ).pack(pady=10)
            
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            
            ctk.CTkButton(
                button_frame,
                text="Guardar",
                command=self.guardar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame,
                text="Cancelar",
                command=self.cancelar,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=120
            ).pack(side="left", padx=5)
            
            # Esperar a que se cierre el diálogo
            parent.wait_window(self.dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
            self.dialog.destroy()
            
    def agregar_item(self):
        try:
            # Ventana de nuevo item
            dialog = ItemDialog(self.dialog)
            if dialog.result:
                # Agregar item
                self.items.append(dialog.result)
                
                # Actualizar lista
                self.actualizar_lista()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al agregar item: {str(e)}")
            
    def actualizar_lista(self):
        try:
            # Limpiar frame de items
            for widget in self.items_frame.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    widget.destroy()
                    
            # Mostrar items
            for i, item in enumerate(self.items):
                frame = ctk.CTkFrame(self.items_frame, fg_color="#FFFFFF")
                frame.pack(fill="x", pady=5, padx=10)
                
                # Producto
                ctk.CTkLabel(
                    frame,
                    text=item["producto"],
                    font=("Quicksand", 12)
                ).pack(side="left", padx=10)
                
                # Cantidad
                ctk.CTkLabel(
                    frame,
                    text=f"Cantidad: {item['cantidad']}",
                    font=("Quicksand", 12)
                ).pack(side="left", padx=10)
                
                # Precio
                ctk.CTkLabel(
                    frame,
                    text=f"S/. {item['precio']:.2f}",
                    font=("Quicksand", 12)
                ).pack(side="left", padx=10)
                
                # Subtotal
                ctk.CTkLabel(
                    frame,
                    text=f"Subtotal: S/. {item['subtotal']:.2f}",
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C"
                ).pack(side="right", padx=10)
                
                # Botón eliminar
                ctk.CTkButton(
                    frame,
                    text="❌",
                    command=lambda idx=i: self.eliminar_item(idx),
                    fg_color="#E64A19",
                    hover_color="#BF360C",
                    width=30
                ).pack(side="right", padx=5)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar lista: {str(e)}")
            
    def eliminar_item(self, idx):
        try:
            # Eliminar item
            self.items.pop(idx)
            
            # Actualizar lista
            self.actualizar_lista()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar item: {str(e)}")
            
    def guardar(self):
        try:
            # Validar campos
            datos = {}
            for field, entry in self.entries.items():
                if isinstance(entry, ctk.StringVar):
                    valor = entry.get()
                else:
                    valor = entry.get().strip()
                if not valor:
                    messagebox.showwarning("Advertencia", f"El campo {field} es requerido")
                    return
                datos[field] = valor
                
            # Validar items
            if not self.items:
                messagebox.showwarning("Advertencia", "Debe agregar al menos un producto")
                return
                
            # Calcular monto total
            monto_total = sum(item["subtotal"] for item in self.items)
            
            # Guardar resultado
            self.result = {
                **datos,
                "monto_total": monto_total,
                "items": self.items
            }
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class ItemDialog:
    def __init__(self, parent):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title("Nuevo Producto")
            self.dialog.geometry("400x300")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Centrar ventana
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text="Nuevo Producto",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Campos del formulario
            campos = [
                ("Producto", "producto"),
                ("Cantidad", "cantidad"),
                ("Precio", "precio")
            ]
            
            self.entries = {}
            
            for i, (label, field) in enumerate(campos):
                # Label
                ctk.CTkLabel(
                    main_frame,
                    text=label,
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C"
                ).pack(pady=(20 if i == 0 else 10, 0))
                
                # Entry
                entry = ctk.CTkEntry(
                    main_frame,
                    width=300,
                    placeholder_text=f"Ingrese {label.lower()}...",
                    border_width=0,
                    fg_color="#F5F5F5"
                )
                entry.pack(pady=5)
                self.entries[field] = entry
                
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            
            ctk.CTkButton(
                button_frame,
                text="Agregar",
                command=self.guardar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame,
                text="Cancelar",
                command=self.cancelar,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=120
            ).pack(side="left", padx=5)
            
            # Esperar a que se cierre el diálogo
            parent.wait_window(self.dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
            self.dialog.destroy()
            
    def guardar(self):
        try:
            # Validar campos
            datos = {}
            for field, entry in self.entries.items():
                valor = entry.get().strip()
                if not valor:
                    messagebox.showwarning("Advertencia", f"El campo {field} es requerido")
                    return
                    
                # Convertir a número si es necesario
                if field in ["cantidad", "precio"]:
                    try:
                        valor = float(valor)
                        if valor <= 0:
                            messagebox.showwarning("Advertencia", f"El {field} debe ser mayor a 0")
                            return
                    except:
                        messagebox.showwarning("Advertencia", f"El {field} debe ser un número válido")
                        return
                        
                datos[field] = valor
                
            # Calcular subtotal
            datos["subtotal"] = datos["cantidad"] * datos["precio"]
            
            # Guardar resultado
            self.result = datos
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class EstadoDialog:
    def __init__(self, parent, pedido):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title("Actualizar Estado")
            self.dialog.geometry("400x200")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Centrar ventana
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text="Actualizar Estado",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Estado actual
            ctk.CTkLabel(
                main_frame,
                text=f"Estado actual: {pedido['estado']}",
                font=("Quicksand", 12),
                text_color="#424242"
            ).pack(pady=(0, 10))
            
            # Nuevo estado
            ctk.CTkLabel(
                main_frame,
                text="Nuevo estado:",
                font=("Quicksand", 12, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(10, 0))
            
            self.estado_var = ctk.StringVar(value=pedido["estado"])
            estado_menu = ctk.CTkOptionMenu(
                main_frame,
                values=["Pendiente", "En Proceso", "Enviado", "Entregado", "Cancelado"],
                variable=self.estado_var,
                width=300,
                fg_color="#2E6B5C",
                button_color="#1D4A3C",
                button_hover_color="#153A2C",
                dropdown_fg_color="#FFFFFF",
                dropdown_hover_color="#F5F5F5",
                dropdown_text_color="#2E6B5C"
            )
            estado_menu.pack(pady=10)
            
            # Botones
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(pady=20)
            
            ctk.CTkButton(
                button_frame,
                text="Actualizar",
                command=self.guardar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=120
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame,
                text="Cancelar",
                command=self.cancelar,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=120
            ).pack(side="left", padx=5)
            
            # Esperar a que se cierre el diálogo
            parent.wait_window(self.dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
            self.dialog.destroy()
            
    def guardar(self):
        try:
            # Guardar resultado
            self.result = self.estado_var.get()
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

class DetallesPedidoDialog:
    def __init__(self, parent, pedido):
        try:
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(f"Detalles del Pedido {pedido['id_pedido']}")
            self.dialog.geometry("600x500")
            self.dialog.resizable(False, False)
            
            # Hacer modal
            self.dialog.transient(parent)
            self.dialog.grab_set()
            
            # Centrar ventana
            self.dialog.update_idletasks()
            width = self.dialog.winfo_width()
            height = self.dialog.winfo_height()
            x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
            self.dialog.geometry(f"{width}x{height}+{x}+{y}")
            
            # Frame principal
            main_frame = ctk.CTkFrame(self.dialog, fg_color="#FFFFFF")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                main_frame,
                text="Detalles del Pedido",
                font=("Quicksand", 20, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Información del pedido
            campos = [
                ("ID", "id_pedido"),
                ("Cliente", "cliente"),
                ("Monto Total", "monto_total"),
                ("Estado", "estado"),
                ("Fecha Creación", "fecha_creacion"),
                ("Método de Pago", "metodo_pago")
            ]
            
            for label, field in campos:
                frame = ctk.CTkFrame(main_frame, fg_color="#F5F5F5")
                frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(
                    frame,
                    text=f"{label}:",
                    font=("Quicksand", 12, "bold"),
                    text_color="#2E6B5C",
                    width=100
                ).pack(side="left", padx=10)
                
                valor = pedido[field]
                if field == "monto_total":
                    valor = f"S/. {valor:.2f}"
                    
                ctk.CTkLabel(
                    frame,
                    text=str(valor),
                    font=("Quicksand", 12),
                    text_color="#424242"
                ).pack(side="left", padx=10)
            
            # Separador
            ctk.CTkFrame(
                main_frame,
                height=1,
                fg_color="#E0E0E0"
            ).pack(fill="x", pady=20)
            
            # Título de items
            ctk.CTkLabel(
                main_frame,
                text="Productos",
                font=("Quicksand", 16, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 10))
            
            # Tabla de items
            columns = ("producto", "cantidad", "precio", "subtotal")
            
            tabla = ttk.Treeview(
                main_frame,
                columns=columns,
                show="headings",
                height=5
            )
            
            # Configurar columnas
            tabla.heading("producto", text="Producto")
            tabla.heading("cantidad", text="Cantidad")
            tabla.heading("precio", text="Precio")
            tabla.heading("subtotal", text="Subtotal")
            
            # Configurar anchos
            tabla.column("producto", width=200)
            tabla.column("cantidad", width=100, anchor="center")
            tabla.column("precio", width=100, anchor="center")
            tabla.column("subtotal", width=100, anchor="center")
            
            # Cargar items
            for item in pedido["items"]:
                tabla.insert(
                    "",
                    "end",
                    values=(
                        item["producto"],
                        item["cantidad"],
                        f"S/. {item['precio']:.2f}",
                        f"S/. {item['subtotal']:.2f}"
                    )
                )
                
            tabla.pack(fill="x", pady=10)
            
            # Frame para botones de acción
            action_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            action_frame.pack(fill="x", pady=20)
            
            # Botón actualizar estado
            ctk.CTkButton(
                action_frame,
                text="Actualizar Estado",
                command=lambda: self.actualizar_estado(pedido),
                fg_color="#2E6B5C",
                hover_color="#1D4A3C",
                width=150
            ).pack(side="left", padx=5)
            
            # Botón cerrar
            ctk.CTkButton(
                action_frame,
                text="Cerrar",
                command=self.dialog.destroy,
                fg_color="#E64A19",
                hover_color="#BF360C",
                width=100
            ).pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar detalles: {str(e)}")
            self.dialog.destroy()
            
    def actualizar_estado(self, pedido):
        try:
            # Obtener referencia al frame padre
            parent = self.dialog.master
            
            # Llamar al método actualizar_estado del frame padre
            parent.actualizar_estado()
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar estado: {str(e)}")

if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = GestionPedidos(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"Error en la aplicación: {str(e)}")
