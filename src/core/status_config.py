# -*- coding: utf-8 -*-
"""
Configuración de Estados del Sistema
Este archivo centraliza todos los estados utilizados en la aplicación para mantener
consistencia entre frontend y backend según el flujo de estados definido.
"""

# ========================================
# ESTADOS DE PEDIDOS
# ========================================
class EstadosPedido:
    PENDIENTE = 'pendiente'      # Esperando que el usuario pague
    CONFIRMADO = 'confirmado'    # Pago exitoso, listo para procesar
    PREPARANDO = 'preparando'    # Preparando el pedido para ser enviado
    EN_CAMINO = 'en_camino'      # El pedido en camino de ser completado
    ENTREGADO = 'entregado'      # Completado exitosamente
    CANCELADO = 'cancelado'      # Cancelado sin opción a reanudar

    @classmethod
    def get_all(cls):
        return [cls.PENDIENTE, cls.CONFIRMADO, cls.PREPARANDO, cls.EN_CAMINO, cls.ENTREGADO, cls.CANCELADO]
    
    @classmethod
    def get_labels(cls):
        return {
            cls.PENDIENTE: 'Pendiente',
            cls.CONFIRMADO: 'Confirmado',
            cls.PREPARANDO: 'Preparando',
            cls.EN_CAMINO: 'En Camino',
            cls.ENTREGADO: 'Entregado',
            cls.CANCELADO: 'Cancelado'
        }

    @classmethod
    def get_colors(cls):
        return {
            cls.PENDIENTE: '#FFA000',   # Naranja - Esperando acción
            cls.CONFIRMADO: '#1976D2',  # Azul - Confirmado
            cls.PREPARANDO: '#7B1FA2',  # Púrpura - En proceso
            cls.EN_CAMINO: '#FF6F00',   # Naranja oscuro - En tránsito
            cls.ENTREGADO: '#2E7D32',   # Verde - Exitoso
            cls.CANCELADO: '#C62828'    # Rojo - Cancelado
        }

# ========================================
# ESTADOS DE PAGOS
# ========================================
class EstadosPago:
    PENDIENTE = 'pendiente'     # Esperando confirmación del pago
    COMPLETADO = 'completado'   # Pago exitoso
    CANCELADO = 'cancelado'     # Cancelado sin opción a reanudar

    @classmethod
    def get_all(cls):
        return [cls.PENDIENTE, cls.COMPLETADO, cls.CANCELADO]
    
    @classmethod
    def get_labels(cls):
        return {
            cls.PENDIENTE: 'Pendiente',
            cls.COMPLETADO: 'Completado',
            cls.CANCELADO: 'Cancelado'
        }

    @classmethod
    def get_colors(cls):
        return {
            cls.PENDIENTE: '#FFA000',   # Naranja - Esperando pago
            cls.COMPLETADO: '#2E7D32',  # Verde - Pago exitoso
            cls.CANCELADO: '#C62828'    # Rojo - Pago cancelado
        }

# ========================================
# ESTADOS DE ENVÍOS
# ========================================
class EstadosEnvio:
    PENDIENTE = 'pendiente'     # Esperando que el usuario pague
    CONFIRMADO = 'confirmado'   # Listo para enviar (pago confirmado)
    PREPARANDO = 'preparando'   # Preparando el envío para ir en camino
    EN_CAMINO = 'en_camino'     # El envío está en camino al destino
    ENTREGADO = 'entregado'     # Completado exitosamente
    CANCELADO = 'cancelado'     # Cancelado sin opción a reanudar

    @classmethod
    def get_all(cls):
        return [cls.PENDIENTE, cls.CONFIRMADO, cls.PREPARANDO, cls.EN_CAMINO, cls.ENTREGADO, cls.CANCELADO]
    
    @classmethod
    def get_labels(cls):
        return {
            cls.PENDIENTE: 'Pendiente',
            cls.CONFIRMADO: 'Confirmado',
            cls.PREPARANDO: 'Preparando',
            cls.EN_CAMINO: 'En Camino',
            cls.ENTREGADO: 'Entregado',
            cls.CANCELADO: 'Cancelado'
        }

    @classmethod
    def get_colors(cls):
        return {
            cls.PENDIENTE: '#FFA000',   # Naranja - Esperando pago
            cls.CONFIRMADO: '#1976D2',  # Azul - Listo para envío
            cls.PREPARANDO: '#7B1FA2',  # Púrpura - Preparando envío
            cls.EN_CAMINO: '#FF6F00',   # Naranja oscuro - En tránsito
            cls.ENTREGADO: '#2E7D32',   # Verde - Entregado
            cls.CANCELADO: '#C62828'    # Rojo - Cancelado
        }

# ========================================
# FLUJO DE ESTADOS SINCRONIZADOS
# ========================================
class FlujoEstados:
    """
    Define cómo cambian los estados de forma sincronizada según el flujo de negocio
    """
    
    # Situación exitosa - Se pagó exitosamente el pedido
    FLUJO_EXITOSO = {
        'inicial': {
            'pedido': EstadosPedido.PENDIENTE,
            'pago': EstadosPago.PENDIENTE,
            'envio': EstadosEnvio.PENDIENTE
        },
        'pago_completado': {
            'pedido': EstadosPedido.CONFIRMADO,
            'pago': EstadosPago.COMPLETADO,
            'envio': EstadosEnvio.CONFIRMADO
        },
        'preparando': {
            'pedido': EstadosPedido.PREPARANDO,
            'pago': EstadosPago.COMPLETADO,
            'envio': EstadosEnvio.PREPARANDO
        },
        'en_camino': {
            'pedido': EstadosPedido.EN_CAMINO,
            'pago': EstadosPago.COMPLETADO,
            'envio': EstadosEnvio.EN_CAMINO
        },
        'entregado': {
            'pedido': EstadosPedido.ENTREGADO,
            'pago': EstadosPago.COMPLETADO,
            'envio': EstadosEnvio.ENTREGADO
        }
    }
    
    # Situación cancelada
    FLUJO_CANCELADO = {
        'cancelado': {
            'pedido': EstadosPedido.CANCELADO,
            'pago': EstadosPago.CANCELADO,
            'envio': EstadosEnvio.CANCELADO
        }
    }

    @classmethod
    def get_estados_sincronizados(cls, etapa):
        """
        Obtiene los estados sincronizados para una etapa específica
        """
        if etapa in cls.FLUJO_EXITOSO:
            return cls.FLUJO_EXITOSO[etapa]
        elif etapa in cls.FLUJO_CANCELADO:
            return cls.FLUJO_CANCELADO[etapa]
        else:
            return None

# ========================================
# MENSAJES SEGÚN ESTADOS
# ========================================
class MensajesEstado:
    """
    Mensajes a mostrar en el frontend según el estado del pedido
    """
    
    MENSAJES_PEDIDO = {
        EstadosPedido.PENDIENTE: "Tu pedido aún no ha sido pagado",
        EstadosPedido.CONFIRMADO: "Tu pedido está confirmado, se realizarán los preparativos para el envío",
        EstadosPedido.PREPARANDO: "Tu pedido se está preparando para el envío",
        EstadosPedido.EN_CAMINO: "Tu pedido está en camino",
        EstadosPedido.ENTREGADO: "Tu pedido ha sido entregado exitosamente",
        EstadosPedido.CANCELADO: "Tu pedido ha sido cancelado"
    }

    @classmethod
    def get_mensaje(cls, estado):
        return cls.MENSAJES_PEDIDO.get(estado, "Estado desconocido")

# ========================================
# TRANSICIONES VÁLIDAS DE ESTADOS
# ========================================
class TransicionesEstado:
    """
    Define qué transiciones de estados son válidas para evitar cambios incorrectos
    """
    
    TRANSICIONES_PEDIDO = {
        EstadosPedido.PENDIENTE: [EstadosPedido.CONFIRMADO, EstadosPedido.CANCELADO],
        EstadosPedido.CONFIRMADO: [EstadosPedido.PREPARANDO, EstadosPedido.CANCELADO],
        EstadosPedido.PREPARANDO: [EstadosPedido.EN_CAMINO, EstadosPedido.CANCELADO],
        EstadosPedido.EN_CAMINO: [EstadosPedido.ENTREGADO],
        EstadosPedido.ENTREGADO: [],  # Estado final
        EstadosPedido.CANCELADO: []   # Estado final
    }

    @classmethod
    def es_transicion_valida(cls, estado_actual, estado_nuevo):
        """
        Verifica si una transición de estado es válida
        """
        transiciones_permitidas = cls.TRANSICIONES_PEDIDO.get(estado_actual, [])
        return estado_nuevo in transiciones_permitidas

    @classmethod
    def get_estados_siguientes(cls, estado_actual):
        """
        Obtiene los estados a los que se puede transicionar desde el estado actual
        """
        return cls.TRANSICIONES_PEDIDO.get(estado_actual, [])

# ========================================
# CONFIGURACIÓN PARA FILTROS DE UI
# ========================================
class FiltrosUI:
    """
    Configuración para filtros y opciones de la interfaz de usuario
    """
    
    OPCIONES_FILTRO_PEDIDOS = ["Todos"] + EstadosPedido.get_all()
    OPCIONES_FILTRO_PAGOS = ["Todos"] + EstadosPago.get_all()
    OPCIONES_FILTRO_ENVIOS = ["Todos"] + EstadosEnvio.get_all()

# ========================================
# ESTADOS DEPRECADOS (PARA MIGRACIÓN)
# ========================================
class EstadosDeprecados:
    """
    Mapeo de estados antiguos a nuevos para facilitar la migración
    """
    
    MAPEO_PEDIDOS = {
        'enviado': EstadosPedido.EN_CAMINO,
        'abandonado': EstadosPedido.CANCELADO,
        'completado': EstadosPedido.ENTREGADO,
        'en_proceso': EstadosPedido.PREPARANDO,
        'rechazado': EstadosPedido.CANCELADO
    }

    @classmethod
    def migrar_estado(cls, estado_antiguo):
        """
        Convierte un estado antiguo al nuevo formato
        """
        return cls.MAPEO_PEDIDOS.get(estado_antiguo, estado_antiguo)

# ========================================
# UTILIDADES
# ========================================
def validar_estado_pedido(estado):
    """Valida si un estado de pedido es válido"""
    return estado in EstadosPedido.get_all()

def validar_estado_pago(estado):
    """Valida si un estado de pago es válido"""
    return estado in EstadosPago.get_all()

def validar_estado_envio(estado):
    """Valida si un estado de envío es válido"""
    return estado in EstadosEnvio.get_all()

def obtener_color_estado(tipo, estado):
    """
    Obtiene el color asociado a un estado según el tipo (pedido, pago, envio)
    """
    if tipo == 'pedido':
        return EstadosPedido.get_colors().get(estado, '#666666')
    elif tipo == 'pago':
        return EstadosPago.get_colors().get(estado, '#666666')
    elif tipo == 'envio':
        return EstadosEnvio.get_colors().get(estado, '#666666')
    else:
        return '#666666'

def obtener_label_estado(tipo, estado):
    """
    Obtiene la etiqueta legible de un estado según el tipo
    """
    if tipo == 'pedido':
        return EstadosPedido.get_labels().get(estado, estado.capitalize())
    elif tipo == 'pago':
        return EstadosPago.get_labels().get(estado, estado.capitalize())
    elif tipo == 'envio':
        return EstadosEnvio.get_labels().get(estado, estado.capitalize())
    else:
        return estado.capitalize()

# ========================================
# SINCRONIZACIÓN DE ESTADOS
# ========================================
def sincronizar_estado_envio(estado_pedido):
    """
    Determina qué estado de envío corresponde a un estado de pedido
    para mantener la sincronización entre ambos.
    """
    # Mapeo directo entre estados de pedido y envío
    mapeo_estados = {
        EstadosPedido.PENDIENTE: EstadosEnvio.PENDIENTE,
        EstadosPedido.CONFIRMADO: EstadosEnvio.CONFIRMADO,
        EstadosPedido.PREPARANDO: EstadosEnvio.PREPARANDO,
        EstadosPedido.EN_CAMINO: EstadosEnvio.EN_CAMINO,
        EstadosPedido.ENTREGADO: EstadosEnvio.ENTREGADO,
        EstadosPedido.CANCELADO: EstadosEnvio.CANCELADO
    }
    
    return mapeo_estados.get(estado_pedido, estado_pedido)

def get_estado_sincronizado_por_etapa(etapa):
    """
    Obtiene los estados sincronizados para una etapa específica del flujo
    """
    return FlujoEstados.get_estados_sincronizados(etapa)
