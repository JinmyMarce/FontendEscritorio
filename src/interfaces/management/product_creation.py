import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
from src.core.config import INVENTORY_ENDPOINTS
from src.shared.utils import APIHandler
import os

# --- Ventana emergente personalizada ---
def mostrar_alerta(titulo, mensaje, tipo="info"):
    colores = {
        "info": {"bg": "#E0F7FA", "fg": "#00796B", "icon": "ℹ️"},
        "error": {"bg": "#FFEBEE", "fg": "#C62828", "icon": "❌"},
        "success": {"bg": "#E8F5E9", "fg": "#2E7D32", "icon": "✔️"},
        "warning": {"bg": "#FFF8E1", "fg": "#FF8F00", "icon": "⚠️"}
    }
    c = colores.get(tipo, colores["info"])
    win = ctk.CTkToplevel()
    win.title(titulo)
    win.geometry("360x160")
    win.resizable(False, False)
    win.configure(fg_color=c["bg"])
    win.grab_set()
    # Icono y mensaje
    icon_label = ctk.CTkLabel(win, text=c["icon"], font=("Segoe UI Emoji", 38), text_color=c["fg"], fg_color=c["bg"])
    icon_label.pack(pady=(18, 0))
    msg_label = ctk.CTkLabel(win, text=mensaje, font=("Quicksand", 13), text_color=c["fg"], fg_color=c["bg"])
    msg_label.pack(pady=(8, 8), padx=20)
    # Botón cerrar
    ctk.CTkButton(win, text="Aceptar", command=win.destroy, fg_color=c["fg"], hover_color="#444", text_color="white", width=120, height=36, corner_radius=16, font=("Quicksand", 12, "bold")).pack(pady=(0, 18))
    win.after(7000, win.destroy)  # autocerrar tras 7s
    win.mainloop() if not hasattr(ctk, '_running_mainloop') else None

class CrearProductoFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white")
        self.pack(expand=True, fill="both", padx=10, pady=10)
        
        # -------- CONTENEDOR PRINCIPAL --------
        self.frame = ctk.CTkFrame(self, fg_color="white", corner_radius=10)
        self.frame.pack(expand=True, fill="both", padx=10, pady=10)

        # -------- LOGO --------
        try:
            img = Image.open(os.path.join("..", "..", "..", "assets", "images", "logoBlanco.png"))
            img = img.resize((150, int(img.height * (150 / img.width))))
            self.logo = ImageTk.PhotoImage(img)
            logo_label = ctk.CTkLabel(self.frame, image=self.logo, text="", bg_color="white")
            logo_label.pack(pady=(5, 5))
        except:
            print("Logo no encontrado.")

        # -------- TÍTULO --------
        ctk.CTkLabel(self.frame, text="Crear Producto", text_color="white", fg_color="#2E6B5C",
                    font=("Quicksand", 16, "bold"), corner_radius=8, width=250, height=35).pack(pady=(8, 8))

        # -------- ENTRADAS --------
        labels = {
            "nombre": "Nombre",
            "descripcion": "Descripción",
            "precio": "Precio",
            "peso": "Peso",
        }

        self.entradas = {}
        for key, text in labels.items():
            self.entradas[key] = ctk.CTkEntry(self.frame, placeholder_text=text, width=280, height=36,
                                        corner_radius=10, font=("Quicksand", 12))
            self.entradas[key].pack(pady=5)

        # -------- COMBOBOX DE CATEGORÍAS (se llenará desde API) --------
        self.categoria_var = ctk.StringVar(value="Cargando categorías...")
        self.combo_categoria = ctk.CTkOptionMenu(self.frame, variable=self.categoria_var, 
                                               values=["Cargando categorías..."], width=280, height=36,
                                               corner_radius=10, font=("Quicksand", 12))
        self.combo_categoria.pack(pady=5)

        # -------- Variable global para categorías completas --------
        self.categorias_completas = []

        # -------- BOTÓN PARA ELEGIR IMAGEN --------
        self.ruta_imagen = None

        self.btn_imagen = ctk.CTkButton(
            self.frame, text="🖼️ Seleccionar Imagen", command=self.seleccionar_imagen,
            fg_color="#43A047", hover_color="#357a38", text_color="white",
            font=("Quicksand", 13, "bold"), corner_radius=18, width=200, height=38, border_width=0
        )
        self.btn_imagen.pack(pady=(10, 4))

        # -------- BOTÓN GUARDAR --------
        self.btn_guardar = ctk.CTkButton(
            self.frame, text="💾 Guardar Producto", command=self.guardar_producto,
            fg_color="#1976D2", hover_color="#0D47A1", text_color="white",
            font=("Quicksand", 14, "bold"), corner_radius=18, width=220, height=42, border_width=0
        )
        self.btn_guardar.pack(pady=16)

        # Cargar categorías al inicio
        self.cargar_categorias()

    def cargar_categorias(self):
        url_categorias = INVENTORY_ENDPOINTS['categories']
        try:
            response = APIHandler.make_request('get', url_categorias)
            if response['status_code'] == 200:
                json_data = response['data']
                # Detectar si el JSON tiene la lista dentro de "data" o si es la lista directamente
                categorias = json_data.get('data', json_data) if isinstance(json_data, dict) else json_data
                self.categorias_completas = categorias
                self.combo_categoria.configure(values=[c['nombre'] for c in categorias])
                self.categoria_var.set(categorias[0]['nombre'] if categorias else "Sin categorías")
            else:
                self.combo_categoria.configure(values=["Error al cargar"])
        except Exception as e:
            self.combo_categoria.configure(values=["Error al cargar"])
            self.categoria_var.set("Error al cargar")

    def seleccionar_imagen(self):
        self.ruta_imagen = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png")])
        if self.ruta_imagen:
            mostrar_alerta("Imagen seleccionada", f"Archivo: {os.path.basename(self.ruta_imagen)}", tipo="info")

    def guardar_producto(self):
        url_api = INVENTORY_ENDPOINTS['register']

        if not self.ruta_imagen:
            mostrar_alerta("Error", "Debes seleccionar una imagen.", tipo="error")
            return

        nombre_seleccionado = self.categoria_var.get()

        # Buscar el id_categoria que corresponde al nombre seleccionado
        id_categoria = None
        for cat in self.categorias_completas:
            if cat['nombre'] == nombre_seleccionado:
                id_categoria = cat['id_categoria']
                break

        if id_categoria is None:
            mostrar_alerta("Error", "Categoría inválida seleccionada.", tipo="error")
            return

        data = {
            "nombre": self.entradas["nombre"].get(),
            "descripcion": self.entradas["descripcion"].get(),
            "precio": self.entradas["precio"].get(),
            "peso": self.entradas["peso"].get(),
            "categorias_id_categoria": str(id_categoria)
        }

        for campo, valor in data.items():
            if not valor.strip():
                mostrar_alerta("Campo vacío", f"El campo '{campo}' es obligatorio.", tipo="warning")
                return

        try:
            with open(self.ruta_imagen, 'rb') as img:
                files = {'imagen': img}
                response = APIHandler.make_request('post', url_api, data=data, files=files)

            if hasattr(response, 'status_code'):
                code = response.status_code
                content = getattr(response, 'text', '')
            else:
                code = response.get('status_code', 0)
                content = response.get('text', '')

            if code == 201:
                mostrar_alerta("Éxito", "Producto creado correctamente.", tipo="success")
                # Limpiar campos después de guardar
                for entrada in self.entradas.values():
                    entrada.delete(0, 'end')
                self.ruta_imagen = None
            else:
                try:
                    resultado = response.json() if hasattr(response, 'json') else response.get('data', {})
                    errores = resultado.get("errors", resultado.get("message", "Error desconocido"))
                    mostrar_alerta("Error", str(errores), tipo="error")
                except Exception:
                    mostrar_alerta("Error", "La respuesta de la API no es un JSON válido.", tipo="error")

        except Exception as e:
            mostrar_alerta("Error", f"No se pudo crear el producto: {str(e)}", tipo="error")

def abrir_ventana_crear_producto():
    # -------- CONFIGURACIÓN GLOBAL --------
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")

    # -------- VENTANA PRINCIPAL --------
    ventana = ctk.CTk()
    ventana.title("Crear Producto - FRESATERRA")
    ventana.geometry("400x750")
    ventana.resizable(True, True)

    # -------- CENTRAR VENTANA --------
    ventana.update_idletasks()
    ancho = 400
    alto = 750
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

    # -------- CONTENEDOR PRINCIPAL --------
    frame = ctk.CTkFrame(ventana, fg_color="white", corner_radius=10)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    # -------- LOGO --------
    try:
        img = Image.open("imagen/logoBlanco.png")
        img = img.resize((150, int(img.height * (150 / img.width))))
        logo = ImageTk.PhotoImage(img)
        logo_label = ctk.CTkLabel(frame, image=logo, text="", bg_color="white")
        logo_label.image = logo  # Mantener referencia
        logo_label.pack(pady=(5, 5))
    except:
        print("Logo no encontrado.")

    # -------- TÍTULO --------
    ctk.CTkLabel(frame, text="Crear Producto", text_color="white", fg_color="#2E6B5C",
                font=("Quicksand", 16, "bold"), corner_radius=8, width=250, height=35).pack(pady=(8, 8))

    # -------- ENTRADAS --------
    labels = {
        "nombre": "Nombre",
        "descripcion": "Descripción",
        "precio": "Precio",
        "peso": "Peso",
    }

    entradas = {}
    for key, text in labels.items():
        entradas[key] = ctk.CTkEntry(frame, placeholder_text=text, width=280, height=36,
                                    corner_radius=10, font=("Quicksand", 12))
        entradas[key].pack(pady=5)

    # -------- COMBOBOX DE CATEGORÍAS (se llenará desde API) --------
    categoria_var = ctk.StringVar(value="Cargando categorías...")
    combo_categoria = ctk.CTkOptionMenu(frame, variable=categoria_var, values=["Cargando categorías..."], width=280, height=36,
                                        corner_radius=10, font=("Quicksand", 12))
    combo_categoria.pack(pady=5)

    # -------- Variable global para categorías completas --------
    categorias_completas = []

    # -------- Función para cargar categorías desde API --------
    def cargar_categorias():
        global categorias_completas
        url_categorias = INVENTORY_ENDPOINTS['categories']
        try:
            response = APIHandler.make_request('get', url_categorias)
            if response['status_code'] == 200:
                json_data = response['data']
                # Detectar si el JSON tiene la lista dentro de "data" o si es la lista directamente
                categorias = json_data.get('data', json_data) if isinstance(json_data, dict) else json_data
                categorias_completas = categorias
                combo_categoria.configure(values=[c['nombre'] for c in categorias])
                categoria_var.set(categorias[0]['nombre'] if categorias else "Sin categorías")
            else:
                combo_categoria.configure(values=["Error al cargar"])
        except Exception as e:
            combo_categoria.configure(values=["Error al cargar"])
            categoria_var.set("Error al cargar")

    # Llamar al cargar las categorías al inicio
    cargar_categorias()

    # -------- BOTÓN PARA ELEGIR IMAGEN --------
    ruta_imagen = None

    def seleccionar_imagen():
        global ruta_imagen
        ruta_imagen = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png")])
        if ruta_imagen:
            messagebox.showinfo("Imagen seleccionada", f"Archivo: {os.path.basename(ruta_imagen)}")

    btn_imagen = ctk.CTkButton(frame, text="Seleccionar Imagen", command=seleccionar_imagen,
                                fg_color="#557A46", font=("Quicksand", 12, "bold"))
    btn_imagen.pack(pady=10)

    # -------- ENVIAR A API --------
    def guardar_producto():
        url_api = INVENTORY_ENDPOINTS['register']

        if not ruta_imagen:
            messagebox.showerror("Error", "Debes seleccionar una imagen.")
            return

        nombre_seleccionado = categoria_var.get()

        # Buscar el id_categoria que corresponde al nombre seleccionado
        id_categoria = None
        for cat in categorias_completas:
            if cat['nombre'] == nombre_seleccionado:
                id_categoria = cat['id_categoria']
                break

        if id_categoria is None:
            messagebox.showerror("Error", "Categoría inválida seleccionada.")
            return

        data = {
            "nombre": entradas["nombre"].get(),
            "descripcion": entradas["descripcion"].get(),
            "precio": entradas["precio"].get(),
            "peso": entradas["peso"].get(),
            "categorias_id_categoria": str(id_categoria)
        }

        for campo, valor in data.items():
            if not valor.strip():
                messagebox.showerror("Campo vacío", f"El campo '{campo}' es obligatorio.")
                return

        try:
            with open(ruta_imagen, 'rb') as img:
                files = {'imagen': img}
                response = APIHandler.make_request('post', url_api, data=data, files=files)

            print("Código de respuesta:", response.status_code)
            print("Contenido bruto:", response.text)

            if response.status_code == 201:
                messagebox.showinfo("Éxito", "Producto creado correctamente.")
                ventana.destroy()
            else:
                try:
                    resultado = response.json()
                    errores = resultado.get("errors", resultado.get("message", "Error desconocido"))
                    messagebox.showerror("Error", str(errores))
                except ValueError:
                    messagebox.showerror("Error", "La respuesta de la API no es un JSON válido.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear el producto: {str(e)}")

    btn_guardar = ctk.CTkButton(frame, text="Guardar Producto", width=260, height=40,
                                corner_radius=20, fg_color="#2F405F", hover_color="#1E2C45",
                                font=("Quicksand", 13, "bold"), command=guardar_producto)
    btn_guardar.pack(pady=20)

    return ventana

if __name__ == "__main__":
    ventana = abrir_ventana_crear_producto()
    ventana.mainloop()
