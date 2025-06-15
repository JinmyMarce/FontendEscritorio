import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os

# Cargar la fuente personalizada
try:
    import tkinter.font as tkFont
    fuente_path = os.path.join(os.getcwd(), "Quicksand-Regular.ttf")
    tkFont.Font(family="Quicksand", size=12)
except Exception as e:
    print("Error cargando fuente:", e)

# Configuración global
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Función para aplicar estilo base y logo
def aplicar_estilo_base(ventana, ancho=300, alto=350, titulo="Ventana"):
    ventana.title(titulo)
    ventana.geometry(f"{ancho}x{alto}")
    ventana.resizable(True, True)
    
    # Centrar ventana
    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

# Función para crear un frame con imagen del logo
def crear_frame_con_logo(ventana, color_fondo="white"):
    frame = ctk.CTkFrame(ventana, fg_color=color_fondo, corner_radius=10)
    frame.pack(expand=True, fill="both", padx=10, pady=10)

    # Cargar imagen
    ruta_imagen = os.path.join("imagen", "logoBlanco.png")
    try:
        img = Image.open(ruta_imagen)
        img = img.resize((150, int(img.height * (150 / img.width))))
        img_tk = ImageTk.PhotoImage(img)

        logo = ctk.CTkLabel(frame, image=img_tk, text="", bg_color=color_fondo)
        logo.image = img_tk  # Evitar que se elimine la referencia
        logo.pack(pady=(5, 5))
    except FileNotFoundError:
        print(f"No se encontró la imagen: {ruta_imagen}")

    return frame
