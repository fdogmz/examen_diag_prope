import streamlit as st
import logging
import requests

# Configuración del backend y URL base
BACKEND_URL = "https://analiticadidactica.net"

#logging.basicConfig(level=logging.INFO)

def page_login():
    jwt_token = st.session_state.get("jwt_token")
    if not jwt_token:
        authenticate()
        handle_auth_callback()
    else:
        if not st.session_state.get('email'):
            user_info = get_user_info(jwt_token)
            if not user_info:
                st.error("Error al obtener información del usuario.")
                st.stop()
            
        st.info(f"Bienvenido/a, {st.session_state.get('name', 'Usuario')} 👋")

# Cerrar sesión
def page_logout():
    jwt_token = st.session_state.get("jwt_token")
    if jwt_token != "":
        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()
    else:        
        st.warning("No estás autenticado.")

def authenticate():
    # Intenta recuperar la URL base del frontend desde el encabezado Referer
    request_headers = st.query_params  # Permite obtener parámetros desde la URL

    frontend_url = "https://ct9pqyv2ovbvkhtlg5vxuk.streamlit.app/"
    #frontend_url = request_headers.get("frontend_url", ["http://localhost:8501"])[0]

    auth_url = f"{BACKEND_URL}/auth/login?frontend_url={frontend_url}"
    st.markdown(f'<a href="{auth_url}" target="_self">Iniciar sesión con Google</a>', unsafe_allow_html=True)


'''
def authenticate():
    auth_url = f"{BACKEND_URL}/auth/login"
    st.markdown(f'<a href="{auth_url}" target="_self">Iniciar sesión con Google</a>', unsafe_allow_html=True)
'''

def handle_auth_callback():
    query_params = st.query_params
    token = query_params.get("token")
    if token and len(token) > 0:
        st.session_state["jwt_token"] = token

        if not st.session_state.get('email'):
            user_info = get_user_info(token)
            if not user_info:
                st.error("Error al obtener información del usuario.")
                st.stop()

        st.rerun()

def get_user_info(jwt_token):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    try:
        response = requests.get(f"{BACKEND_URL}/auth/user-info", headers=headers)
        response.raise_for_status()
        user_data = response.json()
        logging.info(f"Información del usuario recibida: {user_data}")
        st.session_state['email'] = user_data.get("email", "Email no encontrado.")
        st.session_state['name'] = user_data.get("name", "No identificado.")
        st.session_state['role'] = user_data.get("role", "No asignado.")
        return True
    except requests.RequestException as e:
        logging.error(f"Error al obtener información del usuario: {e}")
        st.session_state["jwt_token"] = ""
        st.rerun()
        return False
