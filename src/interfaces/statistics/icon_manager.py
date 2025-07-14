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
            "assets", "images", "icons"
        )
        self.icon_cache = {}
        print(f"🔧 IconManager iniciado. Ruta de iconos: {self.icons_path}")
        
    def clear_cache(self):
        """Limpia el cache de iconos"""
        self.icon_cache.clear()
        print("🧹 Cache de iconos limpiado")
    
    def get_icon_path(self, icon_name, extension="png"):
        """Obtiene la ruta completa de un icono"""
        return os.path.join(self.icons_path, f"{icon_name}.{extension}")
    
    def load_icon(self, icon_name, size=(32, 32), color=None):
        """
        Carga un icono desde archivos PNG o SVG
        
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
                print(f"📦 Usando icono desde cache: {icon_name}")
                return self.icon_cache[cache_key]
            
            # Intentar cargar SVG primero, luego PNG
            svg_path = self.get_icon_path(icon_name, "svg")
            png_path = self.get_icon_path(icon_name, "png")
            
            image = None
            
            if os.path.exists(svg_path):
                # Cargar SVG usando cairosvg y PIL
                try:
                    import cairosvg
                    from io import BytesIO
                    
                    print(f"📦 Cargando SVG: {svg_path}")
                    
                    # Convertir SVG a PNG en memoria
                    png_data = cairosvg.svg2png(
                        url=svg_path,
                        output_width=size[0],
                        output_height=size[1]
                    )
                    
                    # Cargar desde bytes
                    image = Image.open(BytesIO(png_data))
                    print(f"✅ SVG cargado exitosamente: {icon_name}")
                    
                except ImportError:
                    print("❌ cairosvg no está instalado, intentando con PNG...")
                    image = None
                except Exception as e:
                    print(f"❌ Error al cargar SVG {svg_path}: {str(e)}")
                    image = None
            else:
                print(f"❌ Archivo SVG no encontrado: {svg_path}")
            
            if image is None and os.path.exists(png_path):
                # Cargar imagen PNG
                print(f"📦 Cargando PNG: {png_path}")
                image = Image.open(png_path)
                # Redimensionar si es necesario
                if image.size != size:
                    image = image.resize(size, Image.Resampling.LANCZOS)
                print(f"✅ PNG cargado exitosamente: {icon_name}")
                    
            if image is None:
                # Crear icono de respaldo
                print(f"⚠️ Creando icono de fallback para: {icon_name}")
                image = self._create_fallback_icon(icon_name, size, color)
            
            # Crear CTkImage
            ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=size)
            
            # Guardar en caché
            self.icon_cache[cache_key] = ctk_image
            
            return ctk_image
            
        except Exception as e:
            print(f"💥 Error crítico al cargar icono {icon_name}: {str(e)}")
            import traceback
            traceback.print_exc()
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
            elif icon_name == "statistics":
                self._draw_statistics_icon(draw, size, color_rgb)
            elif icon_name.startswith("growth_"):
                self._draw_growth_icon(draw, size, color_rgb, icon_name)
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
    
    def _draw_statistics_icon(self, draw, size, color):
        """Dibuja un icono de estadísticas (gráfico de barras con tendencia)"""
        w, h = size
        margin = w // 8
        
        # Gráfico de barras
        bar_width = max(2, w // 12)
        bar_spacing = max(1, w // 16)
        bar_count = 4
        
        # Alturas de las barras (creciente)
        bar_heights = [h//4, h//3, h//2.2, h//1.8]
        
        start_x = margin + 2
        for i in range(bar_count):
            x = start_x + i * (bar_width + bar_spacing)
            y = h - margin - bar_heights[i]
            
            # Barra
            draw.rectangle([x, y, x + bar_width, h - margin], 
                          fill=color, outline=color)
        
        # Línea de tendencia ascendente
        trend_points = [
            (start_x + bar_width//2, h - margin - bar_heights[0]//2),
            (start_x + bar_width//2 + (bar_width + bar_spacing), h - margin - bar_heights[1]//2),
            (start_x + bar_width//2 + 2*(bar_width + bar_spacing), h - margin - bar_heights[2]//2),
            (start_x + bar_width//2 + 3*(bar_width + bar_spacing), h - margin - bar_heights[3]//2)
        ]
        
        # Dibujar línea de tendencia en rojo suave
        trend_color = (239, 68, 68)  # Color diferente para la tendencia
        for i in range(len(trend_points)-1):
            draw.line([trend_points[i], trend_points[i+1]], fill=trend_color, width=2)
        
        # Puntos en la línea
        for point in trend_points:
            draw.ellipse([point[0]-2, point[1]-2, point[0]+2, point[1]+2], fill=trend_color)

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
            'conversion': '📊',
            'statistics': '📈',
            'growth_arrow_up': '↗️',
            'growth_arrow_down': '↘️',
            'growth_trend_up': '📈',
            'growth_trend_down': '📉',
            'growth_rocket': '🚀',
            'growth_fire': '🔥',
            'growth_neutral': '➡️'
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
    
    def _draw_growth_icon(self, draw, size, color, icon_name):
        """Dibuja iconos de crecimiento"""
        w, h = size
        center_x, center_y = w//2, h//2
        
        if icon_name == "growth_arrow_up":
            # Flecha hacia arriba
            points = [
                (center_x, h//4),  # Punta
                (center_x - w//4, center_y),  # Izquierda
                (center_x - w//8, center_y),  # Base izquierda
                (center_x - w//8, h*3//4),  # Abajo izquierda
                (center_x + w//8, h*3//4),  # Abajo derecha
                (center_x + w//8, center_y),  # Base derecha
                (center_x + w//4, center_y),  # Derecha
            ]
            draw.polygon(points, fill=color)
            
        elif icon_name == "growth_arrow_down":
            # Flecha hacia abajo
            points = [
                (center_x, h*3//4),  # Punta
                (center_x - w//4, center_y),  # Izquierda
                (center_x - w//8, center_y),  # Base izquierda
                (center_x - w//8, h//4),  # Arriba izquierda
                (center_x + w//8, h//4),  # Arriba derecha
                (center_x + w//8, center_y),  # Base derecha
                (center_x + w//4, center_y),  # Derecha
            ]
            draw.polygon(points, fill=color)
            
        elif icon_name == "growth_trend_up":
            # Línea de tendencia ascendente
            points = [
                (w//8, h*3//4),
                (w*3//8, h//2),
                (w*5//8, h*3//8),
                (w*7//8, h//4)
            ]
            for i in range(len(points)-1):
                draw.line([points[i], points[i+1]], fill=color, width=3)
            # Puntos
            for point in points:
                draw.ellipse([point[0]-2, point[1]-2, point[0]+2, point[1]+2], fill=color)
                
        elif icon_name == "growth_trend_down":
            # Línea de tendencia descendente
            points = [
                (w//8, h//4),
                (w*3//8, h*3//8),
                (w*5//8, h//2),
                (w*7//8, h*3//4)
            ]
            for i in range(len(points)-1):
                draw.line([points[i], points[i+1]], fill=color, width=3)
            # Puntos
            for point in points:
                draw.ellipse([point[0]-2, point[1]-2, point[0]+2, point[1]+2], fill=color)
                
        elif icon_name == "growth_rocket":
            # Cohete simple
            # Cuerpo del cohete
            draw.ellipse([center_x-w//6, center_y-h//3, center_x+w//6, center_y+h//3], fill=color)
            # Punta
            draw.polygon([
                (center_x, center_y-h//3),
                (center_x-w//8, center_y-h//4),
                (center_x+w//8, center_y-h//4)
            ], fill=color)
            # Llamas
            flame_color = (255, 140, 0)  # Naranja
            draw.polygon([
                (center_x, center_y+h//3),
                (center_x-w//8, center_y+h//2),
                (center_x+w//8, center_y+h//2)
            ], fill=flame_color)
            
        elif icon_name == "growth_fire":
            # Fuego simple
            # Llama principal
            flame_points = [
                (center_x, center_y-h//3),  # Punta
                (center_x-w//6, center_y-h//6),
                (center_x-w//8, center_y+h//6),
                (center_x, center_y+h//4),
                (center_x+w//8, center_y+h//6),
                (center_x+w//6, center_y-h//6),
            ]
            draw.polygon(flame_points, fill=color)
            
        elif icon_name == "growth_neutral":
            # Línea horizontal (sin cambio)
            draw.line([w//4, center_y, w*3//4, center_y], fill=color, width=3)
            draw.ellipse([w//4-2, center_y-2, w//4+2, center_y+2], fill=color)
            draw.ellipse([w*3//4-2, center_y-2, w*3//4+2, center_y+2], fill=color)
            
        else:
            # Icono por defecto para crecimiento
            self._draw_default_icon(draw, size, color)

# Instancia global del gestor de iconos
icon_manager = StatisticsIconManager()
