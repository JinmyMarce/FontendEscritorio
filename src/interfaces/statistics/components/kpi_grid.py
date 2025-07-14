"""
Componente KPI Grid para mostrar múltiples KPIs
"""
import customtkinter as ctk
from .kpi_card import KPICard


class KPIGrid(ctk.CTkFrame):
    """Componente que contiene y organiza múltiples tarjetas KPI"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.kpi_cards = {}
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz del grid de KPIs"""
        try:
            # Configurar grid
            for i in range(4):
                self.grid_columnconfigure(i, weight=1)
            
            # Definir configuración de KPIs con paleta profesional
            # Paleta: Verde principal, Azul para datos importantes, Amarillo/Naranja para métricas especiales
            self.kpis_config = [
                {
                    'key': 'total_ventas',
                    'title': 'Total Ventas',
                    'icon_name': 'sales',
                    'color': '#16A34A',  # Verde principal - Ventas (más importante)
                    'row': 0,
                    'col': 0
                },
                {
                    'key': 'total_pedidos',
                    'title': 'Total Pedidos',
                    'icon_name': 'orders',
                    'color': '#2563EB',  # Azul profesional - Datos operativos
                    'row': 0,
                    'col': 1
                },
                {
                    'key': 'ticket_promedio',
                    'title': 'Ticket Promedio',
                    'icon_name': 'target',
                    'color': '#F59E0B',  # Amarillo/Naranja - Métricas de análisis
                    'row': 0,
                    'col': 2
                },
                {
                    'key': 'conversion_rate',
                    'title': 'Tasa de Conversión',
                    'icon_name': 'conversion',
                    'color': '#7C3AED',  # Púrpura - Métricas de rendimiento
                    'row': 0,
                    'col': 3
                }
            ]
            
            # Crear tarjetas KPI
            self.create_kpi_cards()
            
        except Exception as e:
            print(f"Error al configurar KPI grid: {str(e)}")
    
    def create_kpi_cards(self):
        """Crea las tarjetas KPI"""
        try:
            for kpi_config in self.kpis_config:
                kpi_card = KPICard(
                    self,
                    title=kpi_config['title'],
                    icon_name=kpi_config['icon_name'],
                    color=kpi_config['color']
                )
                
                kpi_card.grid(
                    row=kpi_config['row'],
                    column=kpi_config['col'],
                    padx=10,
                    pady=10,
                    sticky="ew"
                )
                
                self.kpi_cards[kpi_config['key']] = kpi_card
                
        except Exception as e:
            print(f"Error al crear tarjetas KPI: {str(e)}")
    
    def update_kpi_data(self, kpi_data):
        """Actualiza todos los KPIs con nuevos datos"""
        try:
            for kpi_key, card in self.kpi_cards.items():
                if kpi_key in kpi_data:
                    data = kpi_data[kpi_key]
                    
                    # Actualizar valor
                    valor = data.get('valor', 0)
                    formato = data.get('formato', 'number')
                    card.update_value(valor, formato)
                    
                    # Manejar información de crecimiento o contexto
                    if 'crecimiento' in data:
                        # Datos con información de crecimiento
                        card.update_growth(data['crecimiento'])
                    elif 'contexto' in data:
                        # Datos con información contextual (como conversion_rate)
                        card.update_context(data['contexto'])
                    else:
                        # Sin información adicional
                        card.clear_growth()
                else:
                    # Sin datos
                    card.set_error("Sin datos")
                    
        except Exception as e:
            print(f"Error al actualizar KPIs: {str(e)}")
            # En caso de error, mostrar mensaje en todas las tarjetas
            for card in self.kpi_cards.values():
                card.set_error("Error al cargar")
    
    def set_loading_state(self):
        """Establece todas las tarjetas en estado de carga"""
        for card in self.kpi_cards.values():
            card.set_loading()
    
    def set_fallback_data(self):
        """Establece datos de fallback (ceros) para todas las tarjetas"""
        fallback_data = {
            'total_ventas': {
                'valor': 0,
                'formato': 'currency',
                'crecimiento': 0
            },
            'total_pedidos': {
                'valor': 0,
                'formato': 'number',
                'crecimiento': 0
            },
            'ticket_promedio': {
                'valor': 0,
                'formato': 'currency'
            },
            'conversion_rate': {
                'valor': 0,
                'formato': 'percentage'
            }
        }
        self.update_kpi_data(fallback_data)
    
    def get_kpi_card(self, kpi_key):
        """Obtiene una tarjeta KPI específica"""
        return self.kpi_cards.get(kpi_key)
