import streamlit as st
from auth import page_login, page_logout
from content import resumen_cuestionario, muestra_ejercicio_opcion_multiple, iniciar_cuestionario # initialize_questionnaire, get_questionnaire_responses_data
import logging

# Configuración inicial del logger
logging.basicConfig(level=logging.INFO)

# ID fijo del cuestionario
id_questionnaire = st.session_state['id_questionnaire'] = 3

# Variables de estado inicial
if 'jwt_token' not in st.session_state:
    st.session_state['jwt_token'] = ""

if 'email' not in st.session_state:
    st.session_state['email'] = None

if 'name' not in st.session_state:
    st.session_state['name'] = None

if 'attempt_active' not in st.session_state:
    st.session_state['attempt_active'] = False

if 'attempt_status' not in st.session_state:
    st.session_state['attempt_status'] = None

if 'role' not in st.session_state:
    st.session_state['role'] = None

if 'ejs_data' not in st.session_state:
    st.session_state['ejs_data'] = {}


def ej1():    
    muestra_ejercicio_opcion_multiple(tag='conj_num', questionnaire_id=id_questionnaire)

def ej2():
    muestra_ejercicio_opcion_multiple(tag='conj_num_cmplx', questionnaire_id=id_questionnaire)

def ej3():
    muestra_ejercicio_opcion_multiple(tag='prod_not_bin_cuad', questionnaire_id=id_questionnaire)

def ej4():
    muestra_ejercicio_opcion_multiple(tag='prod_not_bin_cub', questionnaire_id=id_questionnaire)

def ej5():
    muestra_ejercicio_opcion_multiple(tag='prod_num_cmplx', questionnaire_id=id_questionnaire)

def ej6():
    muestra_ejercicio_opcion_multiple(tag='div_num_cmplx', questionnaire_id=id_questionnaire)

def ej7():
    muestra_ejercicio_opcion_multiple(tag='fact_trin', questionnaire_id=id_questionnaire)

def ej8():
    muestra_ejercicio_opcion_multiple(tag='fact_dif_cub', questionnaire_id=id_questionnaire)

def ej9():
    muestra_ejercicio_opcion_multiple(tag='simpl_exp_alg', questionnaire_id=id_questionnaire)

def ej10():
    muestra_ejercicio_opcion_multiple(tag='alg_pol_coef_princ', questionnaire_id=id_questionnaire)

def ej11():
    muestra_ejercicio_opcion_multiple(tag='dist_puntos', questionnaire_id=id_questionnaire)

def ej12():
    muestra_ejercicio_opcion_multiple(tag='ec_recta_punto_pend', questionnaire_id=id_questionnaire)

def ej13():
    muestra_ejercicio_opcion_multiple(tag='ec_recta_paralela_punto', questionnaire_id=id_questionnaire)

def ej14():
    muestra_ejercicio_opcion_multiple(tag='vert_parab', questionnaire_id=id_questionnaire)

def ej15():
    muestra_ejercicio_opcion_multiple(tag='parab_eje_hor_foco', questionnaire_id=id_questionnaire)

def ej16():
    muestra_ejercicio_opcion_multiple(tag='parab_vert_pto_foco', questionnaire_id=id_questionnaire)

def ej17():
    muestra_ejercicio_opcion_multiple(tag='ec_circ_centr_rad', questionnaire_id=id_questionnaire)

def ej18():
    muestra_ejercicio_opcion_multiple(tag='centro_circ_ecn', questionnaire_id=id_questionnaire)

def ej19():
    muestra_ejercicio_opcion_multiple(tag='circ_ecn_radio', questionnaire_id=id_questionnaire)

def ej20():
    muestra_ejercicio_opcion_multiple(tag='diam_enc_circ', questionnaire_id=id_questionnaire)

def ej21():
    muestra_ejercicio_opcion_multiple(tag='tan_60_deg', questionnaire_id=id_questionnaire)

def ej22():
    muestra_ejercicio_opcion_multiple(tag='sin_from_tan', questionnaire_id=id_questionnaire)

def ej23():
    muestra_ejercicio_opcion_multiple(tag='ang_cos_0', questionnaire_id=id_questionnaire)

def ej24():
    muestra_ejercicio_opcion_multiple(tag='ident_trig', questionnaire_id=id_questionnaire)

def ej25():
    muestra_ejercicio_opcion_multiple(tag='ident_trig_csc_sin', questionnaire_id=id_questionnaire)

def ej26():
    muestra_ejercicio_opcion_multiple(tag='exp_eq', questionnaire_id=id_questionnaire)

def ej27():
    muestra_ejercicio_opcion_multiple(tag='ident_trig_basica', questionnaire_id=id_questionnaire)

def ej28():
    muestra_ejercicio_opcion_multiple(tag='trig_aplic_1', questionnaire_id=id_questionnaire)

def ej29():
    muestra_ejercicio_opcion_multiple(tag='trig_aplic_2', questionnaire_id=id_questionnaire)

def ej30():
    muestra_ejercicio_opcion_multiple(tag='trig_apl_3', questionnaire_id=id_questionnaire)

# Página condicional según el estado
if not st.session_state.get('jwt_token'):
    # Estado 1: Usuario no autenticado, solo se muestra la página de login
    pages = [st.Page(page_login, title="Inicio de Sesión", icon=":material/login:")]
elif st.session_state.get('jwt_token') and not st.session_state.get('attempt_status'):
    # Estado 2: Usuario autenticado pero no se ha revisado el estado del intento
    pages = [st.Page(iniciar_cuestionario, title="Iniciar Cuestionario", icon=":material/edit:")]
else:    

    # Estado 3: Usuario autenticado y con intento activo o creado
    pages = {
        '✏️ Cuestionario': [            
            st.Page(ej1, title="Ejercicio 1", icon=st.session_state["ejs_data"]['conj_num']['icon']),
            st.Page(ej2, title="Ejercicio 2", icon=st.session_state["ejs_data"]['conj_num_cmplx']['icon']),
            st.Page(ej3, title="Ejercicio 3", icon=st.session_state["ejs_data"]['prod_not_bin_cuad']['icon']),
            st.Page(ej4, title="Ejercicio 4", icon=st.session_state["ejs_data"]['prod_not_bin_cub']['icon']),
            st.Page(ej5, title="Ejercicio 5", icon=st.session_state["ejs_data"]['prod_num_cmplx']['icon']),
            st.Page(ej6, title="Ejercicio 6", icon=st.session_state["ejs_data"]['div_num_cmplx']['icon']),
            st.Page(ej7, title="Ejercicio 7", icon=st.session_state["ejs_data"]['fact_trin']['icon']),
            st.Page(ej8, title="Ejercicio 8", icon=st.session_state["ejs_data"]['fact_dif_cub']['icon']),
            st.Page(ej9, title="Ejercicio 9", icon=st.session_state["ejs_data"]['simpl_exp_alg']['icon']),
            st.Page(ej10, title="Ejercicio 10", icon=st.session_state["ejs_data"]['alg_pol_coef_princ']['icon']),
            st.Page(ej11, title="Ejercicio 11", icon=st.session_state["ejs_data"]['dist_puntos']['icon']),
            st.Page(ej12, title="Ejercicio 12", icon=st.session_state["ejs_data"]['ec_recta_punto_pend']['icon']),
            st.Page(ej13, title="Ejercicio 13", icon=st.session_state["ejs_data"]['ec_recta_paralela_punto']['icon']),
            st.Page(ej14, title="Ejercicio 14", icon=st.session_state["ejs_data"]['vert_parab']['icon']),
            st.Page(ej15, title="Ejercicio 15", icon=st.session_state["ejs_data"]['parab_eje_hor_foco']['icon']),
            st.Page(ej16, title="Ejercicio 16", icon=st.session_state["ejs_data"]['parab_vert_pto_foco']['icon']),
            st.Page(ej17, title="Ejercicio 17", icon=st.session_state["ejs_data"]['ec_circ_centr_rad']['icon']),
            st.Page(ej18, title="Ejercicio 18", icon=st.session_state["ejs_data"]['centro_circ_ecn']['icon']),
            st.Page(ej19, title="Ejercicio 19", icon=st.session_state["ejs_data"]['circ_ecn_radio']['icon']),
            st.Page(ej20, title="Ejercicio 20", icon=st.session_state["ejs_data"]['diam_enc_circ']['icon']),
            st.Page(ej21, title="Ejercicio 21", icon=st.session_state["ejs_data"]['tan_60_deg']['icon']),
            st.Page(ej22, title="Ejercicio 22", icon=st.session_state["ejs_data"]['sin_from_tan']['icon']),
            st.Page(ej23, title="Ejercicio 23", icon=st.session_state["ejs_data"]['ang_cos_0']['icon']),
            st.Page(ej24, title="Ejercicio 24", icon=st.session_state["ejs_data"]['ident_trig']['icon']),
            st.Page(ej25, title="Ejercicio 25", icon=st.session_state["ejs_data"]['ident_trig_csc_sin']['icon']),
            st.Page(ej26, title="Ejercicio 26", icon=st.session_state["ejs_data"]['exp_eq']['icon']),
            st.Page(ej27, title="Ejercicio 27", icon=st.session_state["ejs_data"]['ident_trig_basica']['icon']),
            st.Page(ej28, title="Ejercicio 28", icon=st.session_state["ejs_data"]['trig_aplic_1']['icon']),
            st.Page(ej29, title="Ejercicio 29", icon=st.session_state["ejs_data"]['trig_aplic_2']['icon']),
            st.Page(ej30, title="Ejercicio 30", icon=st.session_state["ejs_data"]['trig_apl_3']['icon'])
        ],
        '📋 Resultados': [
            st.Page(resumen_cuestionario, title="Resumen", icon="📈")
        ]
    }

pg = st.navigation(pages)
pg.run()


