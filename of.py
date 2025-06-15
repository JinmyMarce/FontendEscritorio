import customtkinter as ctk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import os

# -------- CONFIGURACIÓN GLOBAL --------
ctk.set_appearance_mode("000000")

# -------- VENTANA PRINCIPAL --------
ventana = ctk.CTk()
ventana.title("Inicio de Sesión - FRESATERRA")
ventana.geometry("300x400")
ventana.resizable(True, True)
ventana.configure(fg_color="#000000")  # Establecer el color de fondo de la ventana

# -------- CARGAR FUENTE QUICKSAND (DESPUÉS de crear la ventana) --------
fuente_path = os.path.join(os.getcwd(), "Quicksand-Regular.ttf")
try:
    font_quicksand_regular = tkFont.Font(family="Quicksand", size=12)
except:
    print("La fuente Quicksand no se encontró. Asegúrate de que el archivo 'Quicksand-Regular.ttf' esté en la misma carpeta.")

# -------- CENTRAR VENTANA --------
ventana.update_idletasks()
ancho = 300
alto = 400
x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
y = (ventana.winfo_screenheight() // 2) - (alto // 2)
ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

# -------- CONTENEDOR PRINCIPAL --------
frame = ctk.CTkFrame(ventana, fg_color="#000000", corner_radius=10)  # Fondo oscuro igual a la ventana
frame.pack(expand=True, fill="both", padx=10, pady=10)

# -------- IMAGEN DE FRESAS --------
try:
    # Cargar la imagen de fresas
    imagen_fresas_pil = Image.open("imagen/logoBlanco.png")
    # Redimensionar la imagen
    nuevo_ancho = 150
    nuevo_alto = int(imagen_fresas_pil.height * (nuevo_ancho / imagen_fresas_pil.width))
    imagen_fresas_resized = imagen_fresas_pil.resize((nuevo_ancho, nuevo_alto))
    imagen_fresas_tk = ImageTk.PhotoImage(imagen_fresas_resized)
    fresas_label = ctk.CTkLabel(frame, image=imagen_fresas_tk, text="", bg_color="white") # Fondo oscuro para la etiqueta
    fresas_label.pack(pady=(5, 5))
    fresas_label.imagen = imagen_fresas_tk
except FileNotFoundError:
    print("Error: No se encontró el archivo de imagen 'imagen/logoBlanco.png'.")

# -------- TÍTULO --------
titulo = ctk.CTkLabel(frame, text="Inicio de sesión", text_color="white", fg_color="#3A6B5D",
                            font=("Quicksand", 16, "bold"), corner_radius=8, width=250, height=35)
titulo.pack(pady=(8, 8))

# -------- SUBTÍTULO --------
subtitulo = ctk.CTkLabel(frame, text="Bienvenido, inicie sesión con su correo\nelectrónico y contraseña",
                                     text_color="#D3D3D3", font=("Quicksand", 10), fg_color="#000000", justify="center")
subtitulo.pack(pady=(0, 12))

# -------- CAMPOS DE ENTRADA --------
correo = ctk.CTkEntry(frame, placeholder_text="Correo electrónico", width=260, height=36,
                                    corner_radius=10, font=("Quicksand", 12), fg_color="#4A4A4A", text_color="white", placeholder_text_color="#A9A9A9")
correo.pack(pady=6)

# -------- CONTRASEÑA --------
contrasena = ctk.CTkEntry(frame, placeholder_text="Contraseña", width=260, height=36,
                                     corner_radius=10, show="*", font=("Quicksand", 12), fg_color="#4A4A4A", text_color="white", placeholder_text_color="#A9A9A9")
contrasena.pack(pady=6)

# -------- BOTÓN DE INICIAR SESIÓN --------
btn_login = ctk.CTkButton(frame, text="Iniciar Sesión", width=260, height=40,
                                     corner_radius=20, fg_color="#3E526B", hover_color="#3D593D",
                                     font=("Quicksand", 13, "bold"))
btn_login.pack(pady=15)

# -------- INICIAR LOOP --------
ventana.mainloop()