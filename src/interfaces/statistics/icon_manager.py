"""
Manejador de iconos para estadísticas
"""
import os
from tkinter import PhotoImage
import customtkinter as ctk
from PIL import Image


class StatisticsIconManager:
    """Gestor de iconos para la interfaz de estadísticas"""
    
    def __init__(self):
        self.icons_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
            "assets", "icons", "statistics"
        )
        self.icon_cache = {}
    
    def get_icon_path(self, icon_name, extension="png"):
        """Obtiene la ruta completa de un icono"""
        return os.path.join(self.icons_path, f"{icon_name}.{extension}")
    
    def load_icon(self, icon_name, size=(32, 32), color=None):
        """
        Carga un icono desde archivos PNG
        
        Args:
            icon_name (str): Nombre del archivo de icono sin extensión
            size (tuple): Tamaño del icono (ancho, alto)
            color (str): Color para aplicar al icono (opcional, no usado con PNG)
        
        Returns:
            CTkImage: Objeto de imagen para customtkinter
        """
        try:
            cache_key = f"{icon_name}_{size[0]}x{size[1]}"
            
            if cache_key in self.icon_cache:
                return self.icon_cache[cache_key]
            
            # Buscar archivo PNG
            png_path = self.get_icon_path(icon_name, "png")
            
            if os.path.exists(png_path):
                # Cargar imagen PNG
                image = Image.open(png_path)
                # Redimensionar si es necesario
                if image.size != size:
                    image = image.resize(size, Image.Resampling.LANCZOS)
            else:
                # Crear icono de respaldo
                print(f"Archivo no encontrado: {png_path}")
                image = self._create_fallback_icon(icon_name, size, color)
            
            # Crear CTkImage
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=size)
            
            # Guardar en caché
            self.icon_cache[cache_key] = ctk_image
            
            return ctk_image
            
        except Exception as e:
            print(f"Error al cargar icono {icon_name}: {str(e)}")
            return self._create_fallback_icon("default", size, color)
    
    def _create_fallback_icon(self, icon_name, size=(32, 32), color=None):
        """Crea un icono de respaldo usando PIL"""
        try:
            from PIL import Image, ImageDraw
            
            # Color por defecto si no se especifica
            if not color:
                color = "#16A34A"
            
            # Crear imagen
            image = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Convertir color hex a RGB
            color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
            
            # Dibujar según el tipo de icono
            if icon_name == "sales":
                self._draw_sales_icon(draw, size, color_rgb)
            elif icon_name == "orders":
                self._draw_orders_icon(draw, size, color_rgb)
            elif icon_name == "target":
                self._draw_target_icon(draw, size, color_rgb)
            elif icon_name == "conversion":
                self._draw_conversion_icon(draw, size, color_rgb)
            else:
                self._draw_default_icon(draw, size, color_rgb)
            
            return image
            
        except ImportError:
            # Si PIL no está disponible, usar icono de texto simple
            return self._create_text_icon(icon_name, size)
    
    def _draw_sales_icon(self, draw, size, color):
        """Dibuja un icono de ventas (billete/dinero)"""
        w, h = size
        margin = w // 8
        
        # Rectángulo principal (billete)
        draw.rectangle([margin, margin*2, w-margin, h-margin*2], 
                      outline=color, width=2)
        
        # Círculo central
        center_x, center_y = w//2, h//2
        radius = min(w, h) // 6
        draw.ellipse([center_x-radius, center_y-radius, 
                     center_x+radius, center_y+radius], 
                     outline=color, width=2)
    
    def _draw_orders_icon(self, draw, size, color):
        """Dibuja un icono de pedidos (caja)"""
        w, h = size
        margin = w // 6
        
        # Caja principal
        draw.rectangle([margin, margin*2, w-margin, h-margin], 
                      outline=color, width=2)
        
        # Tapa de la caja
        draw.rectangle([margin-2, margin, w-margin+2, margin*3], 
                      outline=color, width=2)
        
        # Líneas de la caja
        draw.line([w//2, margin*2, w//2, h-margin], fill=color, width=1)
    
    def _draw_target_icon(self, draw, size, color):
        """Dibuja un icono de objetivo (diana)"""
        w, h = size
        center_x, center_y = w//2, h//2
        
        # Círculos concéntricos
        for i in range(3, 0, -1):
            radius = (min(w, h) // 2 - 4) * i // 3
            draw.ellipse([center_x-radius, center_y-radius,
                         center_x+radius, center_y+radius],
                        outline=color, width=2)
        
        # Punto central
        draw.ellipse([center_x-2, center_y-2, center_x+2, center_y+2],
                    fill=color)
    
    def _draw_conversion_icon(self, draw, size, color):
        """Dibuja un icono de conversión (gráfico)"""
        w, h = size
        margin = w // 8
        
        # Línea de tendencia
        points = [
            (margin, h-margin),
            (w//4, h-margin*3),
            (w//2, h-margin*2),
            (w*3//4, h-margin*4),
            (w-margin, h-margin*5)
        ]
        
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=color, width=2)
        
        # Puntos en la línea
        for point in points:
            draw.ellipse([point[0]-2, point[1]-2, point[0]+2, point[1]+2],
                        fill=color)
    
    def _draw_default_icon(self, draw, size, color):
        """Dibuja un icono por defecto"""
        w, h = size
        margin = w // 4
        draw.rectangle([margin, margin, w-margin, h-margin], 
                      outline=color, width=2)
    
    def _create_text_icon(self, icon_name, size):
        """Crea un icono de texto simple como respaldo final"""
        from PIL import Image, ImageDraw, ImageFont
        
        image = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Texto simple según el tipo
        text_map = {
            'sales': '$',
            'orders': '📦',
            'target': '🎯',
            'conversion': '📊'
        }
        
        text = text_map.get(icon_name, '?')
        
        try:
            # Intentar usar una fuente más grande
            font_size = min(size) // 2
            # font = ImageFont.truetype("arial.ttf", font_size)
            # Por ahora usar fuente por defecto
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # Centrar texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        draw.text((x, y), text, fill="#16A34A", font=font)
        
        return image

# Instancia global del gestor de iconos
icon_manager = StatisticsIconManager()
