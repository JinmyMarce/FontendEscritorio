import json
import os

# Lista de usuarios predefinidos
DEFAULT_USERS = [
    {
        "username": "admin",
        "password": "admin123",
        "role": "admin",
        "name": "Administrador"
    },
    {
        "username": "user",
        "password": "user123",
        "role": "user",
        "name": "Usuario Normal"
    }
]

class UserManager:
    def __init__(self):
        self.users_file = "users.json"
        self.load_users()

    def load_users(self):
        if not os.path.exists(self.users_file):
            self.users = DEFAULT_USERS
            self.save_users()
        else:
            try:
                with open(self.users_file, 'r') as f:
                    self.users = json.load(f)
            except:
                self.users = DEFAULT_USERS
                self.save_users()

    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=4)

    def authenticate(self, username, password):
        for user in self.users:
            if user["username"] == username and user["password"] == password:
                return user
        return None

    def register_user(self, username, password, name, role="user"):
        # Verificar si el usuario ya existe
        if any(user["username"] == username for user in self.users):
            return False
        
        # Crear nuevo usuario
        new_user = {
            "username": username,
            "password": password,
            "role": role,
            "name": name
        }
        
        self.users.append(new_user)
        self.save_users()
        return True 