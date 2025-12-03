import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import os

FIREBASE_URL = "https://chat-e752f-default-rtdb.europe-west1.firebasedatabase.app/"
cred = credentials.Certificate(st.secrets["firebase"]["service_account"])

if not firebase_admin._apps:
    if not os.path.exists(CREDENTIAL_PATH):
        st.error(f"Error Crítico: No se encontró el archivo de credenciales de Firebase en '{CREDENTIAL_PATH}'.")
        st.error("Asegúrate de haber descargado 'serviceAccountKey.json' de Firebase y de tenerlo en esta carpeta.")
        st.stop() 
        
    try:
        cred = credentials.Certificate(CREDENTIAL_PATH)
        firebase_admin.initialize_app(cred, {
            'databaseURL': FIREBASE_URL
        })
        ref = db.reference('chat') 
    except Exception as e:
        st.error(f"Error al inicializar Firebase. Revisa tu URL o archivo JSON: {e}")
        st.stop()
else:
   
    ref = db.reference('chat')




st.set_page_config(layout="wide")
st.title("💬 Chat de Clase (Powered by Streamlit)")

if 'nombre' not in st.session_state:
    st.session_state.nombre = None

if st.session_state.nombre is None:
    st.session_state.nombre = st.text_input("Ingresa tu nombre para comenzar a chatear:", key="user_input")
    if st.session_state.nombre:
        st.success(f"¡Hola, {st.session_state.nombre}! Ya puedes chatear.")
    st.stop() 



chat_container = st.container()

def cargar_mensajes():
    """Recupera los mensajes de Firebase y los muestra."""
    results = ref.get()
    mensajes_a_mostrar = []
    
    if results and isinstance(results, dict):
       
        mensajes_ordenados = sorted(results.items(), key=lambda x: x[1].get('timestamp', 0))
        
        for key, data in mensajes_ordenados:
            if 'usuario' in data and 'texto' in data:
                mensajes_a_mostrar.append(f"**{data['usuario']}**: {data['texto']}")
            
    
    with chat_container:
        st.markdown("<hr>", unsafe_allow_html=True)
        for msg in mensajes_a_mostrar[-20:]:
            st.markdown(msg)
        st.markdown("<hr>", unsafe_allow_html=True)

def enviar_mensaje():
    """Recoge el texto y lo envía a Firebase."""
    if st.session_state.message_input:
        nuevo_mensaje = {
            'usuario': st.session_state.nombre,
            'texto': st.session_state.message_input,
            'timestamp': time.time()
        }
       
        ref.push(nuevo_mensaje)
        
   
        st.session_state.message_input = ""
      
        cargar_mensajes()

with st.form(key='message_form', clear_on_submit=False):
    st.text_input(
        "Escribe tu mensaje:", 
        key='message_input',
        placeholder="¡Escribe aquí y presiona Enter o el botón para enviar!",
    )
    st.form_submit_button(
        label='Enviar Mensaje', 
        on_click=enviar_mensaje
    )

cargar_mensajes()
time.sleep(1) 
st.rerun()