import os
from PIL import Image, ImageTk

class ImageHandler:
    def __init__(self):
        self.image_cache = {}
        self.image_path = "imagen"
        
        # Crear directorio de imágenes si no existe
        if not os.path.exists(self.image_path):
            os.makedirs(self.image_path)
            
    def load_image(self, filename, size=None):
        """
        Carga una imagen y la redimensiona si es necesario.
        Si la imagen no existe, devuelve None.
        """
        try:
            # Verificar si la imagen está en caché
            cache_key = f"{filename}_{size}"
            if cache_key in self.image_cache:
                return self.image_cache[cache_key]
            
            # Ruta completa de la imagen
            image_path = os.path.join(self.image_path, filename)
            
            # Verificar si el archivo existe
            if not os.path.exists(image_path):
                return None
                
            # Cargar imagen
            image = Image.open(image_path)
            
            # Redimensionar si es necesario
            if size:
                image = image.resize(size, Image.Resampling.LANCZOS)
                
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Guardar en caché
            self.image_cache[cache_key] = photo
            
            return photo
            
        except Exception as e:
            print(f"Error al cargar imagen {filename}: {str(e)}")
            return None
            
    def clear_cache(self):
        """Limpia la caché de imágenes"""
        self.image_cache.clear() 