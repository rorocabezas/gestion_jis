import streamlit as st
import requests
import json
import informe
import dtes
import depositos
import carga


# Agregar una variable de estado para el estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = None

BASE_URL = 'https://apijis.com/login_users/token'

def obtener_usuarios(rut, contrasena):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': '',
        'username': rut,
        'password': contrasena,
        'scope': '',
        'client_id': '',
        'client_secret': ''
    }
    response = requests.post(BASE_URL,headers=headers, data= data)
    if response.status_code == 200:
        return response.json()
    else:
        return []
    
def validar_credenciales(rut, contrasena):
    usuarios = obtener_usuarios(rut, contrasena)
    if str(usuarios['rut']) == rut:
        return usuarios
    else:
        return None


def main():    
    if st.session_state.authenticated is None:        
        with st.form(key='my_form'):
            st.title("Inicio de Sesión")
            # Campos de entrada para RUT y Contraseña
            rut = st.text_input("RUT")
            contrasena = st.text_input("Contraseña", type="password")
            # Botón para iniciar sesión
            login_clicked = st.form_submit_button("Iniciar sesión")

        if login_clicked:
            if rut and contrasena:
                usuario = obtener_usuarios(rut, contrasena)
                if usuario is not None and "access_token" in usuario:
                    st.success("Inicio de sesión exitoso!")
                    st.write(f"Bienvenido, {usuario['rol_id']}")                    
                    st.session_state.authenticated = True
                    st.experimental_rerun() 
                else:
                    #st.session_state.authentication_status = False
                    st.session_state.authenticated = False
                    st.error("Credenciales inválidas. Inténtalo de nuevo o contáctanos.")

    elif st.session_state.authenticated:
        menu_option = None
        st.sidebar.title("Menú")
        menu_option = st.sidebar.selectbox("Selecciona un informe", ["Informe de ventas", "Informe de abonados", "Informe de depositos", "Cargas"])        

        try:
            if menu_option == "Informe de ventas":
                informe.main(authenticated=st.session_state.authenticated)  
            elif menu_option == "Informe de abonados":
                dtes.main(authenticated=st.session_state.authenticated)
    
            elif menu_option == "Informe de depositos":
                depositos.main(authenticated=st.session_state.authenticated)  

            elif menu_option == "Cargas":
                carga.main(authenticated=st.session_state.authenticated)

        except Exception as e:
            st.success("Por favor inicia sesión primero")
            st.error(e)
            st.session_state.authenticated = False
            st.experimental_rerun()

        
if __name__ == "__main__":
    main()
