import streamlit as st
import requests
import time
import pandas as pd
import matplotlib.pyplot as plt
import random

# Configuración del backend y URL base
BACKEND_URL = "https://analiticadidactica.net"


def close_attempt():
    """
    Llama al endpoint para cerrar el intento activo.
    """
    questionnaire_id = st.session_state.get("id_questionnaire")  # ID del cuestionario    
    jwt_token = st.session_state.get("jwt_token")

    if not jwt_token or not questionnaire_id:
        st.error("No se puede cerrar el intento. Faltan datos.")
        return

    url = f"{BACKEND_URL}/attempts/close/{questionnaire_id}"
    headers = {"Authorization": f"Bearer {jwt_token}"}

    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            st.success(data.get("message", "El intento se cerró exitosamente."))
            st.session_state.clear()
            st.rerun()  # Recargar la página
        else:
            st.error(response.json().get("detail", "Error al cerrar el intento."))
    except requests.RequestException as e:
        st.error(f"Error al conectar con el servidor: {e}")

def resumen_cuestionario():
    
    # Extraer datos
    ejs_data = st.session_state['ejs_data']

    #st.write(ejs_data)
    
    # Procesar datos
    total_ejs = len(ejs_data)
    resolved = sum(1 for tag, data in ejs_data.items() if data['already_answered'])
    correct = sum(1 for tag, data in ejs_data.items() if data['already_answered'] and data['was_correct'])
    incorrect = resolved - correct
    pending = total_ejs - resolved

    # Crear DataFrame para mostrar en tabla
    table_data = pd.DataFrame(
        [
            {"Tag": tag, 
            "Estado": "Correcto" if data['was_correct'] else "Incorrecto" if data['already_answered'] else "Pendiente"}
            for tag, data in ejs_data.items()
        ]
    )

    # Layout de Streamlit
    st.title("Resultados")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Ejercicios", total_ejs, border=True)
    col2.metric("Resueltos Correctamente", correct, border=True)
    col3.metric("Pendientes", pending, border=True)

    resolved = correct + incorrect

    if pending > 0 and resolved > 0:

        if correct > 0 and incorrect > 0:
            fig, ax = plt.subplots()
            ax.pie(
                [correct, incorrect, pending],
                labels=["Correctos", "Incorrectos", "Pendientes"],
                autopct='%1.1f%%',
                colors=["#4CAF50", "#FF5722", "#FFC107"]
            )
        elif correct > 0:  # correctos y pendientes
            fig, ax = plt.subplots()
            ax.pie(
                [correct, pending],
                labels=["Correctos", "Pendientes"],
                autopct='%1.1f%%',
                colors=["#4CAF50", "#FFC107"]
            )
        elif incorrect > 0:
            fig, ax = plt.subplots()
            ax.pie(
                [incorrect, pending],
                labels=["Incorrectos", "Pendientes"],
                autopct='%1.1f%%',
                colors=["#FF5722", "#FFC107"]
            )
        
        ax.axis("equal")  # Asegurar que el gráfico sea circular
        st.pyplot(fig)

    elif resolved > 0:
        if correct > 0 and incorrect > 0:
            fig, ax = plt.subplots()
            ax.pie(
                [correct, incorrect],
                labels=["Correctos", "Incorrectos"],
                autopct='%1.1f%%',
                colors=["#4CAF50", "#FF5722"]
            )
        elif correct > 0:  # correctos y pendientes
            fig, ax = plt.subplots()
            ax.pie(
                [correct],
                labels=["Correctos"],
                autopct='%1.1f%%',
                colors=["#4CAF50"]
            )
        elif incorrect > 0:
            fig, ax = plt.subplots()
            ax.pie(
                [incorrect],
                labels=["Incorrectos"],
                autopct='%1.1f%%',
                colors=["#FF5722"]
            )
        
        ax.axis("equal")  # Asegurar que el gráfico sea circular
        st.pyplot(fig)
        

    st.markdown("---")

    # Botón para cerrar el intento
    col1, col2, col3 = st.columns([2, 2, 1])  # Centrar el botón en la columna central
    with col2:
        if st.button("Concluir cuestionario", type="primary"):
            close_attempt()

def iniciar_cuestionario():
    """
    Página de bienvenida para iniciar el cuestionario.
    """
    st.title("¡Bienvenido!")
    st.write(f"Hola, **{st.session_state.get('name', 'Usuario')}**.")
    
    id_questionnaire = st.session_state['id_questionnaire']
    jwt_token = st.session_state.get('jwt_token')

    # Verificar o crear un intento
    initialize_questionnaire()

    # Verificar el estado del intento
    attempt_status = st.session_state.get("attempt_status")
    if attempt_status not in ["activo", "creado"]:
        st.error("No se pudo iniciar el intento. Por favor, inténtalo de nuevo.")
        return

    # Obtener los datos de las respuestas del cuestionario
    res = get_questionnaire_responses_data(jwt_token, id_questionnaire)
    if not res or "responses_data" not in res:
        st.error("No se pudo obtener la información del cuestionario.")
        return

    # Procesar los datos de las respuestas
    for tag in res['responses_data'].keys():
        if tag not in st.session_state["ejs_data"].keys():
            if not res['responses_data'][tag]['already_answered']:
                icon = "🔘"
                already_answered = False    
                was_correct = False
            elif res['responses_data'][tag]['was_correct']:
                icon = "✅"
                already_answered = True
                was_correct = True                
            else:
                icon = "❌"
                already_answered = True
                was_correct = False

            st.session_state["ejs_data"][tag] = {
                'icon': icon,
                'question': None,
                'already_answered': already_answered,
                'was_correct': was_correct
            }

    # Crear columnas para centrar el botón
    col1, col2, col3 = st.columns([1, 4, 10])

    with col2:  # Botón centrado en la columna del medio
        if st.button("Iniciar cuestionario", type="primary"):
            st.success(f"Tienes un intento activo. ID del intento: {st.session_state.get('attempt_id')}")
            st.rerun()



def get_questionnaire_responses_data(jwt_token, questionnaire_id):
    """
    Llama al endpoint para obtener la información de las respuestas del estudiante al cuestionario activo.

    Args:
        jwt_token (str): Token JWT del usuario autenticado.
        questionnaire_id (int): ID del cuestionario.

    Returns:
        dict: Respuesta del servidor con el estado de cada respuesta en el intento activo.
    """
    url = f"{BACKEND_URL}/attempts/responses/{questionnaire_id}"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return {
                "responses_data": data.get("responses"),
                "message": "Datos obtenidos correctamente."
            }
        else:
            return {
                "detail": response.json().get("detail", "Error desconocido."),
                "status_code": response.status_code,
            }

    except requests.RequestException as e:
        return {"detail": "No se pudo conectar con el servidor.", "error": str(e)}

def check_or_create_attempt(jwt_token, questionnaire_id):
    """
    Llama al endpoint para verificar o crear un intento para un cuestionario.

    Args:
        jwt_token (str): Token JWT del usuario autenticado.
        questionnaire_id (int): ID del cuestionario.

    Returns:
        dict: Respuesta del servidor con el estado del intento (activo o creado) o un mensaje de error.
    """
    url = f"{BACKEND_URL}/attempts/check_or_create"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }
    payload = {"questionnaire_id": questionnaire_id}

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return {
                "attempt_id": data.get("attempt_id"),
                "status": data.get("status"),
                "message": data.get("message"),
            }
        else:
            return {
                "detail": response.json().get("detail", "Error desconocido."),
                "status_code": response.status_code,
            }

    except requests.RequestException as e:
        return {"detail": "No se pudo conectar con el servidor.", "error": str(e)}


# Uso de la función en el flujo del frontend
def initialize_questionnaire():
    jwt_token = st.session_state.get("jwt_token")
    questionnaire_id = st.session_state.get("id_questionnaire")  # ID del cuestionario
    #questionnaire_id = 3  # ID fijo del cuestionario (puede ajustarse dinámicamente)

    if not jwt_token:
        st.error("No estás autenticado.")
        return

    #st.info("Verificando ...")
    attempt_response = check_or_create_attempt(jwt_token, questionnaire_id)

    # Procesar la respuesta
    if "attempt_id" in attempt_response:
        if attempt_response["status"] == "activo":
            #st.success(f"Tienes un intento activo. ID del intento: {attempt_response['attempt_id']}")
            # Configurar el estado para redirigir al cuestionario
            st.session_state["attempt_id"] = attempt_response["attempt_id"]
            st.session_state["attempt_status"] = "activo"
        elif attempt_response["status"] == "creado":
            #st.success(f"Nuevo intento creado. ID del intento: {attempt_response['attempt_id']}")
            # Configurar el estado para iniciar el cuestionario
            st.session_state["attempt_id"] = attempt_response["attempt_id"]
            st.session_state["attempt_status"] = "creado"
    else:
        # Mostrar errores si los hay
        if "detail" in attempt_response:
            st.error(f"Error: {attempt_response['detail']}")
        else:
            st.error("Ocurrió un error inesperado.")


def get_exercise_and_attemp_info(jwt_token, questionnaire_id, tag="factorizacion"):
    headers = {"Authorization": f"Bearer {jwt_token}"}

    response = requests.get(f"{BACKEND_URL}/opc_mult/random/{questionnaire_id}/{tag}", headers=headers)
    
    if response.status_code == 200:
        exercise = response.json()
        # Permutar las opciones
        random.shuffle(exercise["options"])
        return exercise
        #return response.json()
    else:
        return {"error": f"Error: {response.status_code} - {response.json().get('detail', 'No se encontró el detalle del error')}"}


def get_exercise(jwt_token, tag="factorizacion"):
    headers = {"Authorization": f"Bearer {jwt_token}"}
    response = requests.get(f"{BACKEND_URL}/opc_mult/random/{tag}", headers=headers)
    
    if response.status_code == 200:
        exercise = response.json()
        # Permutar las opciones
        random.shuffle(exercise["options"])
        return exercise        
    else:
        return {"error": f"Error: {response.status_code} - {response.json().get('detail', 'No se encontró el detalle del error')}"}


def validate_answer(exercise_id, selected_indices):
    """
    Valida las respuestas seleccionadas para un ejercicio de opción múltiple.

    Args:
        exercise_id (int): ID del ejercicio a validar.
        selected_indices (list): Lista de índices seleccionados por el usuario.

    Returns:
        dict: Respuesta del backend con el estado de la validación y mensajes.
    """
    url = f"{BACKEND_URL}/opc_mult/{exercise_id}/validate"
    payload = {"selected_indices": selected_indices}
    jwt_token = st.session_state.get("jwt_token")

    if jwt_token:
        headers = {"Authorization": f"Bearer {jwt_token}"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data["valid"]:
                    return {'msg': data["message"], 'status': 0, 'correcto': True}
                else:
                    return {
                        'msg': data["message"],
                        'status': 0,
                        'correcto': False,
                        'missing_correct_indices': data.get("missing_correct_indices", []),
                        'extra_incorrect_indices': data.get("extra_incorrect_indices", [])
                    }
            else:
                return {
                    'msg': f"Error al validar la respuesta: {response.status_code}",
                    'status': 1,
                    'detail': response.json().get("detail", "Sin detalle")
                }
        except requests.RequestException as e:
            return {'status': 1, "msg": f"Error al conectar con el servidor: {e}"}
    else:
        return {'status': 1, "msg": "No estás autenticado."}
    

def register_multiple_choice_response(questionnaire_id, exercise_id, selected_options):
    """
    Registra la respuesta de un usuario para un ejercicio de opción múltiple.

    Args:
        questionnaire_id (int): ID del cuestionario.
        exercise_id (int): ID del ejercicio.
        selected_options (list): Lista de IDs de las opciones seleccionadas por el usuario.

    Returns:
        dict: Respuesta del backend con el estado de la operación y mensajes.
    """
    url = f"{BACKEND_URL}/responses/multiple_choice"
    payload = {
        "questionnaire_id": questionnaire_id,
        "exercise_id": exercise_id,
        "selected_options": selected_options
    }
    jwt_token = st.session_state.get("jwt_token")

    if jwt_token:
        headers = {"Authorization": f"Bearer {jwt_token}"}
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return {
                    'msg': data.get("message", "Respuesta registrada."),
                    'status': 0,
                    'is_correct': data.get("is_correct", False)
                }
            elif response.status_code == 400 and "ya fue respondido" in response.json().get("detail", "").lower():
                return {
                    'msg': "Este ejercicio ya fue respondido en el intento actual.",
                    'status': 1
                }
            else:
                return {
                    'msg': f"Error al registrar la respuesta: {response.status_code}",
                    'status': 1,
                    'detail': response.json().get("detail", "Sin detalle")
                }
        except requests.RequestException as e:
            return {'status': 1, "msg": f"Error al conectar con el servidor: {e}"}
    else:
        return {'status': 1, "msg": "No estás autenticado."}


def muestra_ejercicio_opcion_multiple(tag="factorizacion", questionnaire_id=1):
    """
    Muestra un ejercicio de opción múltiple y permite al usuario registrar su respuesta.
    """
    jwt_token = st.session_state.get("jwt_token")

    # Crear tres columnas para organizar el contenido
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:  # Mensaje de bienvenida en el extremo derecho
        st.write(f"**{st.session_state.get('name', 'Usuario')}**")
    st.markdown("---")        


    if jwt_token:
        # Cargar datos del ejercicio si no están en el estado
        if (st.session_state['ejs_data'].get(tag) is None) or st.session_state['ejs_data'][tag].get('question') is None:
            #exercise = get_exercise(jwt_token, tag)    
            exercise = get_exercise_and_attemp_info(jwt_token, questionnaire_id, tag=tag)
            if "error" in exercise:
                st.error(exercise["error"])
            else:
                if tag in st.session_state['ejs_data'].keys() and 'icon' in st.session_state['ejs_data'][tag].keys():
                    icon = st.session_state['ejs_data'][tag]['icon']
                else:
                    icon = "⭕️"
                st.session_state['ejs_data'][tag] = exercise
                st.session_state['ejs_data'][tag]['icon'] = icon               
            
            
        answered = st.session_state['ejs_data'][tag].get("already_answered", False)
        if st.session_state['ejs_data'].get(tag):
            exercise = st.session_state['ejs_data'][tag]                
            st.subheader(exercise["question"])
            options = exercise.get("options", [])
            options_text = [o['text'] for o in options]
            options_caption = ["$\,$" for o in options]
            multiple_correct = exercise.get("multiple_correct", False)

            with col3:  # Id del ejercicio en el lado izquierdo
                st.write(f"Ej: {exercise['ej_id']}")               

            if not options_text:
                st.warning("No hay opciones disponibles para este ejercicio.")
                return
            
            disabled = answered or st.session_state['ejs_data'][tag].get('already_answered', False)
            
            # Si hay más de una respuesta correcta, usar checkboxes            
            if multiple_correct:
                st.write("**Selecciona todas las respuestas correctas**")
                selected_options = [st.checkbox(opt, key=f"chk_{i}", disabled=disabled) for i, opt in enumerate(options_text)]
                
                st.markdown("---")

                # Centrar el botón usando columnas
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:  # Centrar el botón en la columna del medio                    
                    if disabled:
                        if st.session_state['ejs_data'][tag].get('was_correct', False):
                            st.warning("Tu respuesta ya fue registrada: ✅")
                        else:
                            st.warning("Tu respuesta ya fue registrada: ❌")
                    else: 
                        if st.button("Guardar respuesta", type="primary"):
                            selected_indices = [i for i, selected in enumerate(selected_options) if selected]
                            selected_ids = [options[i]["id"] for i, selected in enumerate(selected_options) if selected]                

                            if not selected_indices:
                                st.warning("Debes seleccionar al menos una opción.")
                            else:
                                # Llamar a register_multiple_choice_response
                                res = register_multiple_choice_response(questionnaire_id, exercise["ej_id"], selected_ids)
                                if res['status'] == 0:
                                    # El mensaje de respuesta del servidor indica "Respuesta registrada correctamente"
                                    if res['msg'].find("registrada") < 0:
                                        st.session_state['ejs_data'][tag]['already_answered'] = True
                                        st.toast("🚫 Ya has respondido este ejercicio")
                                    else:
                                        st.session_state['ejs_data'][tag]['was_correct'] = res.get("is_correct", False)
                                        icon='✅' if res.get("is_correct", False) else '❌'
                                        st.toast('¡Respuesta correcta!'if res.get("is_correct", False) else '¡Respuesta incorrecta!', icon=icon)
                                        st.session_state['ejs_data'][tag]['already_answered'] = True
                                        st.session_state['ejs_data'][tag]['icon'] = icon
                                        time.sleep(1)                                        
                                        st.rerun()
                                else:
                                    st.error(res['msg'])
                                    if "detail" in res:
                                        st.info(res["detail"])

            # Si solo hay una respuesta correcta, usar radio buttons
            else:                
                opcion = st.radio("**Selecciona una opción:**", options_text, captions=options_caption, index=None, disabled=disabled)
                st.markdown("---")

                # Centrar el botón usando columnas
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:  # Centrar el botón en la columna del medio
                    
                    if disabled:
                        if st.session_state['ejs_data'][tag].get('was_correct', False):
                            st.warning("Tu respuesta ya fue registrada: ✅")
                        else:
                            st.warning("Tu respuesta ya fue registrada: ❌")
                    else: 
                        if st.button("Guardar respuesta", type="primary"):
                            if opcion is None:
                                st.warning("Debes seleccionar una opción.")
                            else:
                                selected_index = [options_text.index(opcion)]
                                selected_id = [options[selected_index[0]]["id"]]
                                
                                # Llamar a register_multiple_choice_response
                                res = register_multiple_choice_response(questionnaire_id, exercise["ej_id"], selected_id)
                                if res['status'] == 0:
                                    # Ejercicio ya respondido
                                    if res['msg'].find("registrada") < 0:
                                        st.session_state['ejs_data'][tag]['already_answered'] = True
                                        st.toast("🚫 Ya has respondido este ejercicio")
                                    # Respuesta registrada
                                    else:
                                        st.session_state['ejs_data'][tag]['was_correct'] = res.get("is_correct", False)
                                        icon='✅' if res.get("is_correct", False) else '❌'
                                        st.toast('¡Respuesta correcta!'if res.get("is_correct", False) else '¡Respuesta incorrecta!', icon=icon)
                                        time.sleep(1)
                                        st.session_state['ejs_data'][tag]['already_answered'] = True
                                        st.session_state['ejs_data'][tag]['icon'] = icon
                                        st.rerun()
                                else:
                                    st.error(res['msg'])
                                    if "detail" in res:
                                        st.info(res["detail"])
    else:
        st.warning("No estás autenticado.")    

def muestra_ejercicio(tag="factorizacion"):
    jwt_token = st.session_state.get("jwt_token")

    # Crear tres columnas para organizar el contenido
    col1, col2, col3 = st.columns([1, 1, 1])

    with col3:  # Mensaje de bienvenida en el extremo derecho
        st.write(f"{st.session_state.get('name', 'Usuario')}")
        st.markdown("---")           

    if jwt_token:
        # Cargar datos del ejercicio si no están en el estado
        if st.session_state['ejs_data'].get(tag) is None:
            exercise = get_exercise(jwt_token, tag)
            if "error" in exercise:
                st.error(exercise["error"])
            else:
                st.session_state['ejs_data'][tag] = exercise

        if st.session_state['ejs_data'].get(tag):
            exercise = st.session_state['ejs_data'][tag]
            st.subheader(exercise["question"])
            options = exercise.get("options", [])
            options_text = [o['text'] for o in options]
            options_caption = [f'Opción {i}' for i in range(1, len(options) + 1)]
            multiple_correct = exercise.get("multiple_correct", False)

            if not options_text:
                st.warning("No hay opciones disponibles para este ejercicio.")
                return

            # Si hay más de una respuesta correcta, usar checkboxes
            if multiple_correct:
                st.markdown("---")
                st.write("**Selecciona todas las respuestas correctas**")
                selected_options = [st.checkbox(opt, key=f"chk_{i}") for i, opt in enumerate(options_text)]
                st.markdown("---")

                # Centrar el botón usando columnas
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:  # Centrar el botón en la columna del medio
                    if st.button("Guardar respuesta", type="primary"):
                        selected_indices = [i for i, selected in enumerate(selected_options) if selected]
                        if not selected_indices:
                            st.warning("Debes seleccionar al menos una opción.")
                        else:
                            res = validate_answer(exercise["ej_id"], selected_indices)
                            if res['status'] == 0:
                                st.toast(res['msg'], icon='✅' if res['correcto'] else '❗️')
                            else:
                                st.error(res['msg'])

            # Si solo hay una respuesta correcta, usar radio buttons
            else:
                st.markdown("---")
                opcion = st.radio("**Selecciona una opción:**", options_text, captions=options_caption, index=None)
                st.markdown("---")

                # Centrar el botón usando columnas
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:  # Centrar el botón en la columna del medio
                    if st.button("Guardar respuesta", type="primary"):
                        if opcion is None:
                            st.warning("Debes seleccionar una opción.")
                        else:
                            selected_index = [options_text.index(opcion)]
                            res = validate_answer(exercise["ej_id"], selected_index)
                            if res['status'] == 0:
                                st.toast(res['msg'], icon='✅' if res['msg'] == "¡Respuesta correcta!" else '❗️')
                            else:
                                st.error(res['msg'])
    else:
        st.warning("No estás autenticado.")




# Función para obtener la información de un cuestionario
def get_questionnaire(jwt_token, questionnaire_id):
    """
    Obtiene los datos de un cuestionario desde el servidor.

    Args:
        jwt_token (str): Token JWT del usuario autenticado.
        questionnaire_id (int): ID del cuestionario a obtener.

    Returns:
        dict: Respuesta del servidor con los datos del cuestionario o mensaje de error.
    """
    url = f"{BACKEND_URL}/quizzes/{questionnaire_id}"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
    }

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {"detail": response.json().get("detail", "Error desconocido."), "status_code": response.status_code}

    except requests.RequestException as e:
        return {"detail": "No se pudo conectar con el servidor.", "error": str(e)}


        