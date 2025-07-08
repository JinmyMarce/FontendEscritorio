"""
Servicio para gestión de notificaciones con integración a la API
"""
import requests
import json
from datetime import datetime
from src.shared.utils import APIHandler
from src.core.config import NOTIFICATIONS_ENDPOINTS


class NotificationsService:
    """Servicio para manejar notificaciones a través de la API"""
    
    @staticmethod
    def get_all_notifications():
        """Obtener todas las notificaciones del administrador"""
        try:
            response = APIHandler.make_request('get', NOTIFICATIONS_ENDPOINTS['list'])
            
            if response.get('status_code') == 200:
                data = response.get('data', {})
                notifications = data.get('datos', [])
                
                # Formatear notificaciones para la tabla
                formatted_notifications = []
                for notif in notifications:
                    # Determinar estado basado en read_at
                    estado = 'Leído' if notif.get('read_at') and notif.get('read_at') != 'null' else 'No leído'
                    
                    # Extraer datos del mensaje
                    mensaje_data = notif.get('mensaje', {})
                    data_field = notif.get('data', {})
                    
                    formatted_notifications.append({
                        'id': notif.get('id_notificacion'),
                        'tipo': data_field.get('tipo_mensaje') or mensaje_data.get('tipo', 'campanita'),
                        'contenido': data_field.get('contenido_mensaje') or mensaje_data.get('contenido', 'Sin contenido'),
                        'asunto': data_field.get('asunto') or mensaje_data.get('asunto', 'Sin asunto'),
                        'estado': estado,
                        'fecha': NotificationsService._format_date(notif.get('fecha_creacion')),
                        'usuario': notif.get('usuario', {}).get('nombre', 'Usuario desconocido'),
                        'usuario_id': notif.get('usuario', {}).get('id_usuario'),
                        'prioridad': data_field.get('prioridad') or mensaje_data.get('prioridad', 'normal'),
                        'read_at': notif.get('read_at'),
                        'type': notif.get('type', 'campanita'),
                        'data': data_field
                    })
                
                return {
                    'success': True,
                    'notifications': formatted_notifications,
                    'pagination': data.get('pagination', {})
                }
            else:
                return {
                    'success': False,
                    'error': response.get('data', {}).get('error', 'Error al obtener notificaciones')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
    
    @staticmethod
    def get_users_list():
        """Obtener lista de usuarios registrados"""
        try:
            response = APIHandler.make_request('get', NOTIFICATIONS_ENDPOINTS['users_list'])
            
            if response.get('status_code') == 200:
                data = response.get('data', {})
                users = data.get('usuarios', [])
                
                # Formatear usuarios
                formatted_users = []
                for user in users:
                    formatted_users.append({
                        'id': user.get('id_usuario'),
                        'nombre': f"{user.get('nombre', '')} {user.get('apellidos', '')}".strip(),
                        'email': user.get('email'),
                        'telefono': user.get('telefono', ''),
                        'estado': user.get('estado', 'activo')
                    })
                
                return {
                    'success': True,
                    'users': formatted_users
                }
            else:
                return {
                    'success': False,
                    'error': response.get('data', {}).get('error', 'Error al obtener usuarios')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
    
    @staticmethod
    def send_notification_to_user(user_id, asunto, contenido, tipo='campanita_email', prioridad='normal'):
        """
        Enviar notificación a un usuario específico
        
        Args:
            user_id (int): ID del usuario
            asunto (str): Asunto de la notificación
            contenido (str): Contenido del mensaje
            tipo (str): Tipo de notificación ('campanita', 'email', 'campanita_email')
            prioridad (str): Prioridad ('baja', 'normal', 'alta', 'urgente')
        """
        try:
            # Determinar el endpoint según el tipo
            if tipo == 'campanita':
                endpoint = NOTIFICATIONS_ENDPOINTS['send_campanita']
            elif tipo == 'email':
                endpoint = NOTIFICATIONS_ENDPOINTS['send_email']
            else:  # campanita_email por defecto
                endpoint = NOTIFICATIONS_ENDPOINTS['send_campanita_email']
            
            data = {
                'user_id': user_id,
                'asunto': asunto,
                'contenido': contenido,
                'prioridad': prioridad
            }
            
            response = APIHandler.make_request('post', endpoint, data=data)
            
            if response.get('status_code') in [200, 201]:
                return {
                    'success': True,
                    'message': 'Notificación enviada correctamente',
                    'notification_id': response.get('data', {}).get('notificacion_id')
                }
            else:
                return {
                    'success': False,
                    'error': response.get('data', {}).get('error', 'Error al enviar notificación')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
    
    @staticmethod
    def send_notification_to_all_users(asunto, contenido, prioridad='normal'):
        """
        Enviar notificación campanita a todos los usuarios registrados
        
        Args:
            asunto (str): Asunto de la notificación
            contenido (str): Contenido del mensaje
            prioridad (str): Prioridad ('baja', 'normal', 'alta', 'urgente')
        """
        try:
            data = {
                'todos_los_usuarios': True,
                'tipo_mensaje': 'campanita',
                'asunto': asunto,
                'contenido_mensaje': contenido,
                'prioridad': prioridad
            }
            
            response = APIHandler.make_request('post', NOTIFICATIONS_ENDPOINTS['send'], data=data)
            
            if response.get('status_code') in [200, 201]:
                result_data = response.get('data', {})
                return {
                    'success': True,
                    'message': result_data.get('mensaje', 'Notificaciones enviadas correctamente'),
                    'total_sent': result_data.get('total_notificaciones', 0),
                    'notification_ids': result_data.get('notificacion_ids', [])
                }
            else:
                return {
                    'success': False,
                    'error': response.get('data', {}).get('error', 'Error al enviar notificaciones')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
    
    @staticmethod
    def delete_notification(notification_id):
        """Eliminar una notificación"""
        try:
            endpoint = NOTIFICATIONS_ENDPOINTS['delete'].format(id=notification_id)
            response = APIHandler.make_request('delete', endpoint)
            
            if response.get('status_code') == 200:
                return {
                    'success': True,
                    'message': 'Notificación eliminada correctamente'
                }
            else:
                return {
                    'success': False,
                    'error': response.get('data', {}).get('error', 'Error al eliminar notificación')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
    
    @staticmethod
    def get_users_count():
        """Obtener conteo de usuarios activos"""
        try:
            response = APIHandler.make_request('get', NOTIFICATIONS_ENDPOINTS['users_count'])
            
            if response.get('status_code') == 200:
                data = response.get('data', {})
                return {
                    'success': True,
                    'total_users': data.get('total_usuarios', 0),
                    'message': data.get('mensaje', '')
                }
            else:
                return {
                    'success': False,
                    'error': response.get('data', {}).get('error', 'Error al obtener conteo')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error de conexión: {str(e)}'
            }
    
    @staticmethod
    def _format_date(date_string):
        """Formatear fecha para mostrar en la tabla"""
        try:
            if not date_string:
                return "Sin fecha"
            
            # Intentar parsear diferentes formatos de fecha
            formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ']
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(date_string.replace('T', ' ').replace('Z', ''), fmt.replace('T', ' ').replace('Z', ''))
                    return dt.strftime('%d/%m/%Y %H:%M')
                except ValueError:
                    continue
            
            return date_string  # Si no se puede parsear, devolver tal como está
            
        except Exception:
            return "Fecha inválida"
    
    @staticmethod
    def mark_notification_as_read(notification_id):
        """Marcar una notificación como leída"""
        try:
            # Preparar datos para marcar como leída
            data = {
                'estado': 'leida'
            }
            
            # URL del endpoint para actualizar estado
            url = f"{NOTIFICATIONS_ENDPOINTS['list']}/{notification_id}"
            
            response = APIHandler.make_request('patch', url, data)
            
            if response.get('status_code') == 200:
                return {
                    'success': True,
                    'message': 'Notificación marcada como leída exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': response.get('data', {}).get('message', 'Error al actualizar notificación')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al marcar notificación como leída: {str(e)}'
            }
    
    @staticmethod
    def mark_notification_as_unread(notification_id):
        """Marcar una notificación como no leída"""
        try:
            # Preparar datos para marcar como no leída
            data = {
                'estado': 'no_leida'
            }
            
            # URL del endpoint para actualizar estado
            url = f"{NOTIFICATIONS_ENDPOINTS['list']}/{notification_id}"
            
            response = APIHandler.make_request('patch', url, data)
            
            if response.get('status_code') == 200:
                return {
                    'success': True,
                    'message': 'Notificación marcada como no leída exitosamente'
                }
            else:
                return {
                    'success': False,
                    'error': response.get('data', {}).get('message', 'Error al actualizar notificación')
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al marcar notificación como no leída: {str(e)}'
            }
