import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# --------------------------------------------
# CONFIGURACIÓN DE FIREBASE DESDE SECRETS
# --------------------------------------------

firebase_secrets = st.secrets.get("firebase", {})

# Validar que exista la URL de la base de datos
FIREBASE_URL = firebase_secrets.get("database_url")
if not FIREBASE_URL:
    st.error("Error: La clave 'database_url' no se encuentra en st.secrets['firebase']")
    st.stop()

# Inicializar Firebase solo una vez
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(dict(firebase_secrets))
        firebase_admin.initialize_app(cred, {"databaseURL": FIREBASE_URL})
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")
        st.stop()

# Referencia a la rama 'chat'
ref = db.reference("chat")

# --------------------------------------------
# CONFIG STREAMLIT
# --------------------------------------------

st.set_page_config(layout="wide")
st.title("💬 Chat de Clase (Powered by Streamlit)")

# Nombre del usuario
if "nombre" not in st.session_state:
    st.session_state.nombre = None

if st.session_state.nombre is None:
    st.session_state.nombre = st.text_input(
        "Ingresa tu nombre para comenzar a chatear:", key="user_input"
    )
    if not st.session_state.nombre:
        st.stop()
    else:
        st.success(f"¡Hola, {st.session_state.nombre}! Ya puedes chatear.")

# Contenedor del chat
chat_container = st.container()

# --------------------------------------------
# FUNCIÓN: CARGAR MENSAJES
# --------------------------------------------

def cargar_mensajes():
    """Recupera los mensajes de Firebase y los muestra."""
    results = ref.get()
    mensajes_a_mostrar = []

    if results and isinstance(results, dict):
        mensajes_ordenados = sorted(results.items(), key=lambda x: x[1].get("timestamp", 0))
        for key, data in mensajes_ordenados:
            if "usuario" in data and "texto" in data:
                mensajes_a_mostrar.append(f"**{data['usuario']}**: {data['texto']}")

    with chat_container:
        st.markdown("<hr>", unsafe_allow_html=True)
        for msg in mensajes_a_mostrar[-20:]:
            st.markdown(msg)
        st.markdown("<hr>", unsafe_allow_html=True)

# --------------------------------------------
# FUNCIÓN: ENVIAR MENSAJE
# --------------------------------------------

def enviar_mensaje():
    if st.session_state.message_input:
        nuevo_mensaje = {
            "usuario": st.session_state.nombre,
            "texto": st.session_state.message_input,
            "timestamp": time.time()
        }
        ref.push(nuevo_mensaje)
        st.session_state.message_input = ""
        cargar_mensajes()

# --------------------------------------------
# FORMULARIO DEL CHAT
# --------------------------------------------

with st.form(key="message_form"):
    st.text_input(
        "Escribe tu mensaje:",
        key="message_input",
        placeholder="¡Escribe aquí y presiona Enter o el botón para enviar!"
    )
    st.form_submit_button("Enviar Mensaje", on_click=enviar_mensaje)

# Cargar mensajes al iniciar
cargar_mensajes()

# Recarga automática cada 1 segundo
time.sleep(1)
st.rerun()



