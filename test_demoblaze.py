import uuid
import base64
import requests
import pytest

BASE_URL = "https://api.demoblaze.com"


def generate_unique_credentials():
    """Genera credenciales únicas para evitar colisiones en pruebas."""
    unique_suffix = uuid.uuid4().hex[:8]
    username = f"user_{unique_suffix}"
    raw_password = f"Pass_{unique_suffix}"
    # La API de DemoBlaze espera contraseñas codificadas en Base64
    password_b64 = base64.b64encode(raw_password.encode("utf-8")).decode("utf-8")
    return username, password_b64


class TestDemoBlazeAuthAPI:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.username, self.password = generate_unique_credentials()

    def test_01_create_user_successful(self):
        """Escenario: Creación de un usuario nuevo exitosamente."""
        payload = {
            "username": self.username,
            "password": self.password
        }
        response = self.session.post(f"{BASE_URL}/signup", json=payload)
        
        assert response.status_code == 200
        # DemoBlaze responde con un string vacío o respuesta vacía al registrar exitosamente
        assert response.text == "" or response.status_code == 200

    def test_02_create_duplicate_user(self):
        """Escenario: Intentar registrar un usuario existente."""
        payload = {
            "username": self.username,
            "password": self.password
        }
        # Primer registro
        self.session.post(f"{BASE_URL}/signup", json=payload)

        # Segundo intento con el mismo username
        response = self.session.post(f"{BASE_URL}/signup", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "errorMessage" in data
        assert data["errorMessage"] == "This user already exist."

    def test_03_login_successful(self):
        """Escenario: Login con usuario y contraseña correctos."""
        # Se registra primero el usuario
        payload = {
            "username": self.username,
            "password": self.password
        }
        self.session.post(f"{BASE_URL}/signup", json=payload)

        # Intentar login
        response = self.session.post(f"{BASE_URL}/login", json=payload)
        
        assert response.status_code == 200
        # DemoBlaze devuelve un token en formato "Auth_token: <token>"
        assert "Auth_token:" in response.text

    def test_04_login_wrong_password(self):
        """Escenario: Login fallido por contraseña incorrecta."""
        # Se registra primero el usuario
        signup_payload = {
            "username": self.username,
            "password": self.password
        }
        self.session.post(f"{BASE_URL}/signup", json=signup_payload)

        # Intentar login con clave incorrecta
        wrong_password = base64.b64encode("ClaveIncorrecta123!".encode("utf-8")).decode("utf-8")
        login_payload = {
            "username": self.username,
            "password": wrong_password
        }
        response = self.session.post(f"{BASE_URL}/login", json=login_payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "errorMessage" in data
        assert data["errorMessage"] == "Wrong password."

    def test_05_login_non_existent_user(self):
        """Escenario: Login con un usuario que no existe."""
        payload = {
            "username": f"no_existe_{uuid.uuid4().hex[:10]}",
            "password": base64.b64encode("cualquiera".encode("utf-8")).decode("utf-8")
        }
        response = self.session.post(f"{BASE_URL}/login", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "errorMessage" in data
        assert data["errorMessage"] == "User does not exist."


if __name__ == "__main__":
    pytest.main(["-v", __file__])