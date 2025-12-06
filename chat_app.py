import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

# --- CONEXIÓN A FIREBASE USANDO st.secrets ---

# 1. Obtener la configuración general de la sección [firebase]
firebase_secrets = st.secrets.get("firebase", {})

# 2. Intentamos obtener la clave renombrada para evitar el error de cache/lectura.
FIREBASE_URL = firebase_secrets.get("https://chat-e752f-default-rtdb.europe-west1.firebasedatabase.app/")

# Validar que la clave exista
if not FIREBASE_URL:
    # Si la clave 'db_url_final' no se encuentra, mostramos un error claro.
    st.error("Error: La clave 'db_url_final' no se encuentra en st.secrets['firebase']. Vuelve a revisar la configuración de secretos.")
    st.stop()
    
# Si Firebase aún no está inicializado, lo hacemos.
if not firebase_admin._apps:
    try:
        # Crea las credenciales a partir de los secretos
        # Usamos el diccionario completo, excluyendo la URL que ya extrajimos
        cred_data = {
            "type": firebase_secrets.get("type"),
            "project_id": firebase_secrets.get("project_id"),
            "private_key_id": firebase_secrets.get("private_key_id"),
            # Reemplaza los escapes de línea (\n) por la forma correcta antes de usar
            "private_key": firebase_secrets.get("private_key").replace('\\n', '\n'),
            "client_email": firebase_secrets.get("client_email"),
            "client_id": firebase_secrets.get("client_id"),
            "auth_uri": firebase_secrets.get("auth_uri"),
            "token_uri": firebase_secrets.get("token_uri"),
            "auth_provider_x509_cert_url": firebase_secrets.get("auth_provider_x509_cert_url"),
            "client_x509_cert_url": firebase_secrets.get("client_x509_cert_url"),
            "universe_domain": firebase_secrets.get("universe_domain")
        }
        
        # Carga las credenciales
        cred = credentials.Certificate(cred_data)

        # Inicializa la app de Firebase
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_URL
        })
        st.success("Conexión a Firebase exitosa. ¡Listo para trabajar!")
        
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")
        st.stop()

# --- EJEMPLO DE USO (Muestra el estado de la conexión) ---
st.title("Aplicación Conectada a Firebase")
st.write(f"Conectado a la URL: **{FIREBASE_URL}**")

# Referencia a la base de datos (Ejemplo)
try:
    ref = db.reference('/')
    st.write("Estructura de la base de datos (raíz):")
    st.json(ref.get())
except Exception as e:
    st.warning(f"No se pudo leer la raíz de la BD (es normal si está vacía, pero verifica las reglas): {e}")

