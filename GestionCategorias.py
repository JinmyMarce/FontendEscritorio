import customtkinter as ctk
from tkinter import ttk
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry

class GestionCategoriasFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        # Título
        titulo = ctk.CTkLabel(self, text="Gestión de Categorías", 
                            font=("Quicksand", 24, "bold"))
        titulo.pack(pady=20)

        # Frame para el formulario
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(pady=20, padx=20, fill="x")

        # ID Categoría (autoincremental, solo lectura)
        ctk.CTkLabel(form_frame, text="ID Categoría:", 
                    font=("Quicksand", 12)).pack(pady=(10,0))
        self.id_entry = ctk.CTkEntry(form_frame, state="disabled", 
                                   font=("Quicksand", 12))
        self.id_entry.pack(pady=(5,10), padx=20, fill="x")

        # Nombre
        ctk.CTkLabel(form_frame, text="Nombre:", 
                    font=("Quicksand", 12)).pack(pady=(10,0))
        self.nombre_entry = ctk.CTkEntry(form_frame, 
                                       font=("Quicksand", 12))
        self.nombre_entry.pack(pady=(5,10), padx=20, fill="x")

        # Descripción
        ctk.CTkLabel(form_frame, text="Descripción:", 
                    font=("Quicksand", 12)).pack(pady=(10,0))
        self.descripcion_text = ctk.CTkTextbox(form_frame, height=100, 
                                             font=("Quicksand", 12))
        self.descripcion_text.pack(pady=(5,10), padx=20, fill="x")

        # Fecha de Creación
        ctk.CTkLabel(form_frame, text="Fecha de Creación:", 
                    font=("Quicksand", 12)).pack(pady=(10,0))
        # Usamos un frame para contener el DateEntry ya que no es un widget de customtkinter
        fecha_frame = ctk.CTkFrame(form_frame)
        fecha_frame.pack(pady=(5,10), padx=20, fill="x")
        self.fecha_entry = DateEntry(fecha_frame, width=20, 
                                   background='darkgreen', 
                                   foreground='white', 
                                   borderwidth=2)
        self.fecha_entry.pack(fill="x", padx=2, pady=2)

        # Botones
        botones_frame = ctk.CTkFrame(self)
        botones_frame.pack(pady=20, fill="x")

        # Botón Guardar
        self.guardar_btn = ctk.CTkButton(botones_frame, 
                                       text="Guardar Categoría",
                                       command=self.guardar_categoria,
                                       font=("Quicksand", 12),
                                       fg_color="#2E6B5C",
                                       hover_color="#24544A")
        self.guardar_btn.pack(side="left", padx=10)

        # Botón Limpiar
        self.limpiar_btn = ctk.CTkButton(botones_frame, 
                                        text="Limpiar Campos",
                                        command=self.limpiar_campos,
                                        font=("Quicksand", 12),
                                        fg_color="#6B2E2E",
                                        hover_color="#542424")
        self.limpiar_btn.pack(side="left", padx=10)

        # Tabla de categorías
        self.setup_tabla()
        self.cargar_categorias()

    def setup_tabla(self):
        # Frame para la tabla
        tabla_frame = ctk.CTkFrame(self)
        tabla_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Crear la tabla
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview",
                       background="#ffffff",
                       foreground="#000000",
                       rowheight=25,
                       fieldbackground="#ffffff")
        style.configure("Treeview.Heading",
                       background="#2E6B5C",
                       foreground="white",
                       relief="flat")

        self.tabla = ttk.Treeview(tabla_frame, columns=("ID", "Nombre", "Descripción", "Fecha"), show='headings')
        
        # Configurar columnas
        self.tabla.heading("ID", text="ID")
        self.tabla.heading("Nombre", text="Nombre")
        self.tabla.heading("Descripción", text="Descripción")
        self.tabla.heading("Fecha", text="Fecha de Creación")
        
        self.tabla.column("ID", width=50)
        self.tabla.column("Nombre", width=150)
        self.tabla.column("Descripción", width=300)
        self.tabla.column("Fecha", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tabla_frame, orient="vertical", command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)
        
        self.tabla.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Evento de selección
        self.tabla.bind('<<TreeviewSelect>>', self.on_select)

    def guardar_categoria(self):
        nombre = self.nombre_entry.get()
        descripcion = self.descripcion_text.get("1.0", "end-1c")
        fecha = self.fecha_entry.get_date()
        
        if not nombre:
            # Aquí podrías mostrar un mensaje de error
            return
        
        try:
            conn = sqlite3.connect('sistema.db')
            cursor = conn.cursor()
            
            # Crear la tabla si no existe
            cursor.execute('''CREATE TABLE IF NOT EXISTS categorias
                            (id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
                             nombre TEXT NOT NULL,
                             descripcion TEXT,
                             fecha_creacion DATE)''')
            
            # Insertar nueva categoría
            cursor.execute('''INSERT INTO categorias (nombre, descripcion, fecha_creacion)
                            VALUES (?, ?, ?)''', (nombre, descripcion, fecha))
            
            conn.commit()
            self.limpiar_campos()
            self.cargar_categorias()
            
        except sqlite3.Error as e:
            print(f"Error al guardar la categoría: {e}")
        finally:
            conn.close()

    def cargar_categorias(self):
        # Limpiar tabla actual
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        try:
            conn = sqlite3.connect('sistema.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categorias")
            categorias = cursor.fetchall()
            
            for categoria in categorias:
                self.tabla.insert("", "end", values=categoria)
                
        except sqlite3.Error as e:
            print(f"Error al cargar las categorías: {e}")
        finally:
            conn.close()

    def limpiar_campos(self):
        self.nombre_entry.delete(0, "end")
        self.descripcion_text.delete("1.0", "end")
        self.fecha_entry.set_date(datetime.now())
        self.id_entry.configure(state="normal")
        self.id_entry.delete(0, "end")
        self.id_entry.configure(state="disabled")

    def on_select(self, event):
        selected_item = self.tabla.selection()[0]
        categoria = self.tabla.item(selected_item)['values']
        
        # Llenar los campos con los datos seleccionados
        self.id_entry.configure(state="normal")
        self.id_entry.delete(0, "end")
        self.id_entry.insert(0, categoria[0])
        self.id_entry.configure(state="disabled")
        
        self.nombre_entry.delete(0, "end")
        self.nombre_entry.insert(0, categoria[1])
        
        self.descripcion_text.delete("1.0", "end")
        self.descripcion_text.insert("1.0", categoria[2])
        
        # Convertir la fecha string a objeto datetime
        fecha = datetime.strptime(categoria[3], '%Y-%m-%d')
        self.fecha_entry.set_date(fecha) 