import os
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

class ApiClient:
    def __init__(self):
        self.base_url = os.getenv("API_URL")
        self.token = None
        print("API_URL cargada:", self.base_url)

    def login(self, username, password):
        url = f"{self.base_url}/login"
        headers = {'Content-Type': 'application/json'}
        data = {"email": username, "password": password}
        try:
            response = requests.post(url, json=data, headers=headers)
            print("Código de estado:", response.status_code)
            print("Respuesta de la API:", response.text)
            if response.status_code == 200:
                self.token = response.json().get("token")
                return True
            elif response.status_code == 404:
                print("[ERROR] La URL no existe o el endpoint está mal configurado. Verifica la URL en el .env y que el backend esté corriendo.")
            elif response.status_code == 401:
                print("[ERROR] Credenciales incorrectas. Verifica el email y la contraseña.")
            elif response.status_code == 500:
                print("[ERROR] Error interno del servidor. Revisa el backend. Mensaje:", response.text)
            else:
                print(f"[ERROR] Código de estado inesperado: {response.status_code}. Respuesta: {response.text}")
        except requests.exceptions.ConnectionError:
            print("[ERROR] No se pudo conectar con el backend. ¿Está el servidor corriendo y la URL es correcta?")
        except Exception as e:
            print(f"[ERROR] Excepción inesperada: {str(e)}")
        return False

    def get_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.get_headers())
        return response

    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data, headers=self.get_headers())
        return response

    def put(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = requests.put(url, json=data, headers=self.get_headers())
        return response

    def delete(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(url, headers=self.get_headers())
        return response

    def get_usuarios(self):
        url = f"{self.base_url}/usuarios"
        response = requests.get(url, headers=self.get_headers())
        return response.json()

    def crear_usuario(self, data):
        url = f"{self.base_url}/usuarios"
        response = requests.post(url, json=data, headers=self.get_headers())
        return response.json()

    def editar_usuario(self, user_id, data):
        url = f"{self.base_url}/usuarios/{user_id}"
        response = requests.put(url, json=data, headers=self.get_headers())
        return response.json()

    def eliminar_usuario(self, user_id):
        url = f"{self.base_url}/usuarios/{user_id}"
        response = requests.delete(url, headers=self.get_headers())
        return response.json()

    # Puedes agregar métodos similares para productos, ventas, reportes, etc.