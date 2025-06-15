import customtkinter as ctk
import tkinter.messagebox as messagebox
from tkinter import ttk
import json
import os
from datetime import datetime
from config import INVENTORY_ENDPOINTS, UI_CONFIG
from utils import APIHandler, UIHelper, SessionManager, DataValidator, DateTimeHelper
from crearProduct import abrir_ventana_crear_producto
from PIL import Image, ImageTk
from image_handler import ImageHandler

class GestionInventario(ctk.CTkFrame):
    def __init__(self, parent):
        try:
            super().__init__(parent)
            self.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(
                self,
                text="Gestión de Inventario",
                font=("Quicksand", 24, "bold"),
                text_color="#2E6B5C"
            ).pack(pady=(0, 20))
            
            # Frame superior para botones de acción
            action_frame = ctk.CTkFrame(self)
            action_frame.pack(fill="x", pady=(0, 20))
            
            # Botones de acción
            ctk.CTkButton(
                action_frame,
                text="Nuevo Producto",
                command=self.nuevo_producto,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C"
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                action_frame,
                text="Editar Producto",
                command=self.editar_producto,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C"
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                action_frame,
                text="Eliminar Producto",
                command=self.eliminar_producto,
                fg_color="#E64A19",
                hover_color="#BF360C"
            ).pack(side="left", padx=5)
            
            # Frame de búsqueda
            search_frame = ctk.CTkFrame(self)
            search_frame.pack(fill="x", pady=(0, 20))
            
            ctk.CTkLabel(
                search_frame,
                text="Buscar:",
                font=("Quicksand", 12)
            ).pack(side="left", padx=(0, 10))
            
            self.search_var = ctk.StringVar()
            self.search_var.trace("w", self.filtrar_productos)
            
            search_entry = ctk.CTkEntry(
                search_frame,
                textvariable=self.search_var,
                width=300
            )
            search_entry.pack(side="left")
            
            # Crear tabla
            self.crear_tabla()
            self.actualizar_tabla()
            
            self.image_handler = ImageHandler()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar gestión de inventario: {str(e)}")
            
    def cargar_datos_ejemplo(self):
        try:
            # Intentar cargar datos desde archivo
            if os.path.exists("datos/inventario.json"):
                with open("datos/inventario.json", "r", encoding="utf-8") as f:
                    self.productos = json.load(f)
            else:
                # Datos de ejemplo
                self.productos = [
                    {
                        "id": 1,
                        "codigo": "P001",
                        "nombre": "Laptop HP Pavilion",
                        "categoria": "Computadoras",
                        "precio": 899.99,
                        "stock": 15
                    },
                    {
                        "id": 2,
                        "codigo": "P002",
                        "nombre": "Monitor Dell 27\"",
                        "categoria": "Monitores",
                        "precio": 299.99,
                        "stock": 25
                    },
                    {
                        "id": 3,
                        "codigo": "P003",
                        "nombre": "Teclado Mecánico RGB",
                        "categoria": "Periféricos",
                        "precio": 79.99,
                        "stock": 50
                    }
                ]
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos de ejemplo: {str(e)}")
            
    def crear_tabla(self):
        try:
            # Frame para la tabla
            table_frame = ctk.CTkFrame(self)
            table_frame.pack(fill="both", expand=True)
            
            # Crear Treeview
            columns = ("codigo", "nombre", "categoria", "precio", "stock")
            self.tabla = ttk.Treeview(table_frame, columns=columns, show="headings")
            
            # Configurar columnas
            self.tabla.heading("codigo", text="Código")
            self.tabla.heading("nombre", text="Nombre")
            self.tabla.heading("categoria", text="Categoría")
            self.tabla.heading("precio", text="Precio")
            self.tabla.heading("stock", text="Stock")
            
            # Configurar anchos de columna
            self.tabla.column("codigo", width=100)
            self.tabla.column("nombre", width=300)
            self.tabla.column("categoria", width=150)
            self.tabla.column("precio", width=100)
            self.tabla.column("stock", width=100)
            
            # Scrollbars
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tabla.yview)
            hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tabla.xview)
            self.tabla.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Imagen de fondo
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                logo_path = os.path.join(current_dir, "imagen", "logo.png")
                if os.path.exists(logo_path):
                    # Mantener referencia a la imagen
                    self.bg_logo_image = Image.open(logo_path)
                    self.bg_logo = ctk.CTkImage(
                        light_image=self.bg_logo_image,
                        dark_image=self.bg_logo_image,
                        size=(100, 100)
                    )
                    self.bg_logo_label = ctk.CTkLabel(table_frame, image=self.bg_logo, text="")
                    self.bg_logo_label.place(relx=0.5, rely=0.5, anchor="center")
            except Exception as e:
                print(f"Error al cargar el logo: {str(e)}")
            
            # Empaquetar elementos
            self.tabla.pack(fill="both", expand=True)
            vsb.pack(side="right", fill="y")
            hsb.pack(side="bottom", fill="x")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear tabla: {str(e)}")
            
    def actualizar_tabla(self, filtro=""):
        try:
            # Limpiar tabla
            for item in self.tabla.get_children():
                self.tabla.delete(item)
                
            # Filtrar y mostrar productos
            for producto in self.productos:
                if (filtro.lower() in producto["nombre"].lower() or 
                    filtro.lower() in producto["codigo"].lower() or
                    filtro.lower() in producto["categoria"].lower()):
                    self.tabla.insert("", "end", values=(
                        producto["codigo"],
                        producto["nombre"],
                        producto["categoria"],
                        f"${producto['precio']:.2f}",
                        producto["stock"]
                    ))
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar tabla: {str(e)}")
            
    def filtrar_productos(self, *args):
        try:
            self.actualizar_tabla(self.search_var.get())
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar productos: {str(e)}")
            
    def nuevo_producto(self):
        try:
            # Abrir la ventana de crear producto
            ventana = abrir_ventana_crear_producto()
            ventana.mainloop()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear nuevo producto: {str(e)}")
            
    def editar_producto(self):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un producto para editar")
                return
                
            # Obtener producto seleccionado
            item = self.tabla.item(seleccion[0])
            producto_id = item["values"][0]
            producto = next((p for p in self.productos if p["id"] == producto_id), None)
            
            if producto:
                # Mostrar diálogo de edición
                dialog = ProductDialog(self, "Editar Producto", producto)
                if dialog.result:
                    # Actualizar producto
                    producto.update(dialog.result)
                    self.actualizar_tabla()
                    self.guardar_datos()
                    messagebox.showinfo("Éxito", "Producto actualizado correctamente")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar producto: {str(e)}")
            
    def eliminar_producto(self):
        try:
            # Obtener selección
            seleccion = self.tabla.selection()
            if not seleccion:
                messagebox.showwarning("Advertencia", "Por favor seleccione un producto para eliminar")
                return
                
            # Confirmar eliminación
            if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar el producto seleccionado?"):
                # Obtener producto seleccionado
                item = self.tabla.item(seleccion[0])
                producto_id = item["values"][0]
                
                # Eliminar producto
                self.productos = [p for p in self.productos if p["id"] != producto_id]
                self.actualizar_tabla()
                self.guardar_datos()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar producto: {str(e)}")
            
    def guardar_datos(self):
        try:
            # Crear directorio si no existe
            os.makedirs("datos", exist_ok=True)
            
            # Guardar datos en archivo
            with open("datos/inventario.json", "w", encoding="utf-8") as f:
                json.dump(self.productos, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
class ProductDialog:
    def __init__(self, parent, title, producto=None):
        try:
            self.result = None
            
            # Crear ventana de diálogo
            self.dialog = ctk.CTkToplevel(parent)
            self.dialog.title(title)
            self.dialog.geometry("400x500")
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
            
            # Campos del formulario
            campos = [
                ("Código", "codigo"),
                ("Nombre", "nombre"),
                ("Categoría", "categoria"),
                ("Precio", "precio"),
                ("Stock", "stock")
            ]
            
            self.entries = {}
            
            for i, (label, field) in enumerate(campos):
                # Label
                ctk.CTkLabel(
                    self.dialog,
                    text=label,
                    font=("Quicksand", 12)
                ).pack(pady=(20 if i == 0 else 10, 0))
                
                # Entry
                entry = ctk.CTkEntry(self.dialog, width=300)
                entry.pack()
                self.entries[field] = entry
                
                # Valor inicial si es edición
                if producto:
                    entry.insert(0, str(producto[field]))
                    
            # Botones
            button_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
            button_frame.pack(pady=20)
            
            ctk.CTkButton(
                button_frame,
                text="Guardar",
                command=self.guardar,
                fg_color="#2E6B5C",
                hover_color="#1D4A3C"
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                button_frame,
                text="Cancelar",
                command=self.cancelar,
                fg_color="#E64A19",
                hover_color="#BF360C"
            ).pack(side="left", padx=5)
            
            # Esperar a que se cierre el diálogo
            parent.wait_window(self.dialog)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear diálogo: {str(e)}")
            self.dialog.destroy()
            
    def guardar(self):
        try:
            # Validar campos
            for field, entry in self.entries.items():
                if not entry.get().strip():
                    messagebox.showwarning("Advertencia", f"El campo {field} es requerido")
                    return
                    
            # Validar precio y stock como números
            try:
                precio = float(self.entries["precio"].get())
                stock = int(self.entries["stock"].get())
                if precio < 0 or stock < 0:
                    raise ValueError("Los valores deben ser positivos")
            except ValueError as e:
                messagebox.showwarning("Advertencia", "Precio y stock deben ser números válidos y positivos")
                return
                
            # Guardar resultado
            self.result = {
                "codigo": self.entries["codigo"].get().strip(),
                "nombre": self.entries["nombre"].get().strip(),
                "categoria": self.entries["categoria"].get().strip(),
                "precio": precio,
                "stock": stock
            }
            
            # Cerrar diálogo
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar datos: {str(e)}")
            
    def cancelar(self):
        self.dialog.destroy()

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("1000x650")
    frame = GestionInventario(app)
    app.mainloop()
