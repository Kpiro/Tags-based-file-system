import datetime
import io
from queue import Empty, Queue
import threading
import zipfile
from client import Client
import pandas as pd
import streamlit as st

# region MAIN
# -------------------------------------------------------------- MAIN --------------------------------------------------------------
# Interfaz gráfica
st.set_page_config(page_title="Sistema de Archivos basado en Etiquetas", layout="centered")
st.title("📁 Sistema de Archivos basado en Etiquetas")
st.markdown("### Gestiona tus archivos con etiquetas.")

# region VARIABLES
# -------------------------------------------------------------- VARIABLES ----------------------------------------------------------
# Inicializar todas las variables de estado necesarias
if "start_page" not in st.session_state:
    st.session_state.update({
        "start_page": True,
        "server_connected": False,
        "client": None,
        "options_menu": True,
        "mostrar_uploader": False,
        "add_tags_to_files": False,
        "delete_files_by_query": False,
        "delete_tags_from_files": False,
        "list_files_by_query": False,
        "show_all_files": False,
        "download": False,
        "download2": False,
        "make_dir": False
    })

# region INICIAR CONEXIÓN
# -------------------------------------------------------------- INICIAR CONEXIÓN --------------------------------------------------------
if "client" not in st.session_state or st.session_state.client is None:
    st.session_state.client = Client()
    st.session_state.server_connected = st.session_state.client.is_connected

# region Menú de opciones
# -------------------------------------------------------------- Menú de opciones --------------------------------------------------------

if st.session_state.options_menu:
    st.markdown("### Menú de Opciones:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📂 Agregar Archivos con Etiquetas"):
            st.session_state.mostrar_uploader = True
            st.session_state.options_menu = False
            st.rerun()
        if st.button("🏷️ Agregar Etiquetas a Archivos por Consulta"):
            st.session_state.add_tags_to_files = True
            st.session_state.options_menu = False
            st.rerun()
        if st.button("🗑️ Eliminar Archivos por Consulta"):
            st.session_state.delete_files_by_query = True
            st.session_state.options_menu = False
            st.rerun()
        
    with col2:
        if st.button("❌ Eliminar Etiquetas de Archivos"):
            st.session_state.delete_tags_from_files = True
            st.session_state.options_menu = False
            st.rerun()

        if st.button("📃 Listar Archivos por Consulta"):
            st.session_state.list_files_by_query = True
            st.session_state.options_menu = False
            st.rerun()

        if st.button("🗂️🔍 Mostrar todos los Archivos"):
            st.session_state.show_all_files = True
            st.session_state.options_menu = False
            st.rerun()

    # Mostrar mensaje de éxito si existe
    if "success_message" in st.session_state:
        st.success(st.session_state.success_message)
        del st.session_state.success_message  # Limpiar el mensaje después de mostrar

    # Mostrar resultados de búsqueda si existen
    if "query_results" in st.session_state:
        results = st.session_state.query_results
        st.success(f"🔍 {len(results['resultados'])} resultados encontrados para: {results['query']}")
        
        # Mostrar resultados en una tabla
        if results["resultados"]:
            st.table(pd.DataFrame({
                "Archivo": [f["nombre"] for f in results["resultados"]]
                # ,"Etiquetas": [", ".join(f["tags"]) for f in results["resultados"]]
            }))
        else:
            st.info("No se encontraron archivos que coincidan con la consulta")
        
        del st.session_state.query_results  # Limpiar resultados después de mostrar

# region Agregar Archivos con Etiquetas
# ---------------------------------------- Agregar Archivos con Etiquetas ---------------------------------
if st.session_state.mostrar_uploader:
    st.header("📂 Agregar Archivos con Etiquetas")
    uploaded_files = st.file_uploader("Selecciona uno o más archivos", accept_multiple_files=True)
    uploaded_files_names = [file.name for file in uploaded_files]
    files = ','.join(uploaded_files_names) 
    
    # Campo para ingresar etiquetas
    tags_input = st.text_input("🏷️Ingresa las etiquetas (separadas por comas):")
    
    # Botones de acción
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Subir archivos"):
            if uploaded_files and tags_input:
                # Procesar la subida de archivos
                st.session_state.client.add_files_to_tags(files, tags_input)
                
                st.session_state.success_message = (f"✅Archivos {uploaded_files_names} agregados exitosamente con las etiquetas "
                                                    f"[{tags_input}].")
                st.session_state.options_menu = True
                st.session_state.mostrar_uploader = False
                st.rerun()
            else:
                st.error("Debes seleccionar al menos un archivo y agregar etiquetas")
    
    with col2:
        if st.button("Volver al menú principal"):
            st.session_state.options_menu = True
            st.session_state.mostrar_uploader = False
            st.rerun()

# region Agregar Etiquetas
# -------------------------------------------------------------- Agregar Etiquetas --------------------------------------------------------
elif st.session_state.add_tags_to_files:
    st.header("🏷️ Agregar Etiquetas a Archivos por Consulta")
    
    with st.form("add_tags_form"):
        # Input para la consulta de búsqueda
        query = st.text_input("Consulta de búsqueda (separadas por comas):")
        
        # Input para las nuevas etiquetas
        new_tags = st.text_input("Etiquetas a agregar (separadas por comas):")
        
        # Botones de acción
        col1, col2 = st.columns([1, 3])
        with col1:
            submit_btn = st.form_submit_button("Agregar Etiquetas")
        with col2:
            cancel_btn = st.form_submit_button("Cancelar")
        
        if submit_btn:
            if query and new_tags:
                # Convertir a lista de tags
                
                st.session_state.client.add_tags_to_file_by_query(query, new_tags)
                
                # Guardar mensaje de éxito en session_state
                st.session_state.success_message = (
                    f"✅Etiquetas [{new_tags}] agregadas exitosamente a los archivos "
                    f"que coinciden con: [{query}]"
                )
                st.session_state.options_menu = True
                st.session_state.add_tags_to_files = False
                st.rerun()
            else:
                st.error("Debes completar ambos campos para continuar")
        
        if cancel_btn:
            st.session_state.options_menu = True
            st.session_state.add_tags_to_files = False
            st.rerun()

# region Eliminar Archivos
# ------------------------------------------------- Eliminar Archivos -------------------------------------------
elif st.session_state.delete_files_by_query:
    st.header("🗑️ Eliminar Archivos por Consulta")
    
    with st.form("delete_files_form"):
        query = st.text_input("Consulta de eliminación (separada por comas):")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit_btn = st.form_submit_button("Eliminar Archivos")
        with col2:
            cancel_btn = st.form_submit_button("Cancelar")

        if submit_btn:
            if query:
                # Guardar mensaje de éxito en session_state
                st.session_state.client.delete_files_by_query(query)
                st.session_state.success_message = (
                    f"✅ Archivos eliminados exitosamente para la consulta: {query}"
                )
                
                # Limpiar estados y volver al menú
                st.session_state.options_menu = True
                st.session_state.delete_files_by_query = False
                st.rerun()
            else:
                st.error("Debes ingresar una consulta válida")

        if cancel_btn:
            st.session_state.options_menu = True
            st.session_state.delete_files_by_query = False
            st.rerun()

# region Eliminar Etiquetas 
# -------------------------------------------------------------- Eliminar Etiquetas --------------------------------------------------------
elif st.session_state.delete_tags_from_files:
    st.header("❌ Eliminar Etiquetas de Archivos")
    
    with st.form("delete_tags_form"):
        query = st.text_input("Consulta de búsqueda (separada por comas):")
        tags_to_delete = st.text_input("Etiquetas a eliminar (separadas por comas):")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit_btn = st.form_submit_button("Eliminar Etiquetas")
        with col2:
            cancel_btn = st.form_submit_button("Cancelar")

        if submit_btn:
            if query and tags_to_delete:
                tags_list = [tag.strip() for tag in tags_to_delete.split(",")]
                response = st.session_state.client.delete_tags_from_files(query, tags_to_delete)

                # Guardar mensaje de éxito
                st.session_state.success_message = (
                    response
                )
                
                st.session_state.options_menu = True
                st.session_state.delete_tags_from_files = False
                st.rerun()
            else:
                st.error("Debes completar ambos campos para continuar")

        if cancel_btn:
            st.session_state.options_menu = True
            st.session_state.delete_tags_from_files = False
            st.rerun()

#  ---------------------------------------------- Sección Listar Archivos ---------------------------------------------
elif st.session_state.list_files_by_query:
    st.header("📃 Listar Archivos por Consulta")
    
    with st.form("list_files_form"):
        query = st.text_input("Consulta de búsqueda (separada por comas):")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submit_btn = st.form_submit_button("Buscar Archivos")
        with col2:
            cancel_btn = st.form_submit_button("Cancelar")

        if submit_btn:
            if query:
                files = st.session_state.client.list_files_by_query(query)
                results_list = [ {"nombre": file} for file in files]
                fake_results = [
                    {"nombre": "foto1.jpg", "tags": ["@casa", "@familia"]},
                    {"nombre": "vacaciones.pdf", "tags": ["@playa", "@viaje"]}
                ]
                
                st.session_state.query_results = {
                    "query": query,
                    "resultados": results_list
                }
                
                st.session_state.options_menu = True
                st.session_state.list_files_by_query = False
                st.rerun()
            else:
                st.error("Debes ingresar una consulta válida")

        if cancel_btn:
            st.session_state.options_menu = True
            st.session_state.list_files_by_query = False
            st.rerun()

# -------------------------------------------------------------- Sección Mostrar Todos los Archivos --------------------------------------------------------
elif st.session_state.show_all_files:
    st.header("🗂️🔍 Todos los Archivos")

    # Inicializar cesta en session_state
    if 'cesta_descargas' not in st.session_state:
        st.session_state.cesta_descargas = []
    
    try:
        # Simular datos de ejemplo (reemplazar con tu lógica real)
        files, tags_list = st.session_state.client.show_all_files()
        all_files = [{"nombre": file, "tags": tags} for file, tags in zip(files, tags_list)]
        
        if not all_files:
            st.info("📭 No hay archivos almacenados en el sistema")
        else:
            # Mostrar estadísticas
            total_archivos = len(all_files)
            # total_tamano = sum(float(f["size"][:-2]) for f in all_files)
            total_tamano = 5
            cols = st.columns(3)
            cols[0].metric("📦 Archivos totales", total_archivos)
            cols[1].metric("📦 Tamaño total", f"{total_tamano:.1f} MB")
            cols[2].metric("🏷️ Etiquetas únicas", 5)  # Valor hardcodeado temporal
            
            # Mostrar tabla con detalles
            df = pd.DataFrame({
                "Archivo": [f["nombre"] for f in all_files],
                "Etiquetas": [", ".join(f["tags"]) for f in all_files]
                # ,
                # "Tamaño": [f["size"] for f in all_files],
                # "Última modificación": ["2024-02-15", "2024-01-30", "2024-02-01"]  # Datos de ejemplo
            })
            
            st.dataframe(df, use_container_width=True)

            # Sección de descarga -------------------------
            st.subheader("📥 Descargar Archivos")
            
            # Input para query de descarga
            query_descarga = st.text_input(
                "Ingresa tu consulta de búsqueda:",
                placeholder="Ejemplo: escuela, universidad",
                help="Busca archivos usando criterios tags"
            )
            
            # Botón de descarga (simulado - necesitarías implementar la lógica de filtrado)
            if st.button("⏬ Descargar resultados", type="primary"):
                if query_descarga:
                    response = st.session_state.client.download_files(query_descarga)
                    if response == 'OK':
                        st.success("✅ Todos los archivos se descargaron satisfactoriamente.")
                    else:
                        st.error(f"❌ {response}")
                else:
                    st.error("Debes completar el campo.")
                    
    except Exception as e:
        st.error(f"Error al cargar archivos: {str(e)}")
    
    # Botón para volver
    if st.button("🔙 Volver al menú principal"):
        st.session_state.options_menu = True
        st.session_state.show_all_files = False
        st.rerun()

# # -------------------------------------------------------------- Descargar Archivos --------------------------------------------------------
# elif st.session_state.download:
#     # Sección de descarga
#     st.subheader("📥 Descargar Archivos")
    
#     # Input para query de descarga
#     query_descarga = st.text_input(
#         "Ingresa tu consulta de búsqueda:",
#         placeholder="Ejemplo: escuela, universidad",
#         help="Busca archivos usando criterios tags"
#     )
    
#     col1, col2 = st.columns([1,1])
#     with col1:
#         # Botón de descarga (simulado - necesitarías implementar la lógica de filtrado)
#         if st.button("⏬ Descargar resultados", type="primary"):
#             if query_descarga:
#                 file_content_list, file_name_list = st.session_state.client.download_files(query_descarga)
#                 # Crear archivo ZIP (simulación)
#                 zip_buffer = io.BytesIO()
#                 with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
#                     for archivo, name in zip(file_content_list, file_name_list):
#                         zip_file.writestr(name, archivo)
                
#                 zip_buffer.seek(0)
#                 st.download_button(
#                     label="⬇️ Descargar ZIP",
#                     data=zip_buffer,
#                     file_name="tag_based_file_system_downloads.zip",
#                     mime="application/zip"
#                 )
#             else:
#                 st.error("Debes completar el campo.")
#     with col2:
#         # Botón para volver
#         if st.button("🔙 Volver al menú principal"):
#             st.session_state.options_menu = True
#             st.session_state.download = False
#             st.rerun()
# # -------------------------------------------------------------- Sección Mostrar Todos los Archivos --------------------------------------------------------
# elif st.session_state.show_all_files:
#     st.header("🗂️🔍 Todos los Archivos")
    
#     # Inicializar cesta en session_state
#     if 'cesta_descargas' not in st.session_state:
#         st.session_state.cesta_descargas = []
#     if 'seleccionados' not in st.session_state:
#         st.session_state.seleccionados = set()
    
#     try:
#         # Datos de ejemplo (simular tu lógica real)
#         file_content_list, file_size_list = st.session_state.client.download_files()
#         files, tags_list = st.session_state.client.show_all_files()
#         all_files = [{"nombre": file, "tags": tags} for file, tags in zip(files, tags_list)]
#         all_files_ = [
#             {"nombre": "informe.pdf", "tags": ["@trabajo", "@importante"], "size": "2MB", "ruta": "/fake/path/informe.pdf"},
#             {"nombre": "vacaciones.jpg", "tags": ["@playa", "@familia"], "size": "4.5MB", "ruta": "/fake/path/vacaciones.jpg"},
#             {"nombre": "contrato.docx", "tags": ["@legal", "@urgente"], "size": "1.2MB", "ruta": "/fake/path/contrato.docx"}
#         ]
        
#         if not all_files:
#             st.info("📭 No hay archivos almacenados en el sistema")
#         else:
#             # Mostrar estadísticas
#             total_archivos = len(all_files)
#             # total_tamano = sum(float(f["size"][:-2]) for f in all_files)
#             total_tamano = 5
            
#             cols = st.columns(3)
#             cols[0].metric("📦 Archivos totales", total_archivos)
#             cols[1].metric("📦 Tamaño total", f"{total_tamano:.1f} MB")
#             cols[2].metric("🏷️ Etiquetas únicas", 5)  # Valor hardcodeado temporal
            
#             # Sincronizar selección actual
#             current_selection = {f["nombre"] for f in st.session_state.cesta_descargas}
            
#             # Crear DataFrame con selección actualizada
#             df = pd.DataFrame({
#                 "Archivo": [f["nombre"] for f in all_files],
#                 "Etiquetas": [", ".join(f["tags"]) for f in all_files],
#                 # "Tamaño": [f["size"] for f in all_files],
#                 "Seleccionar": [f["nombre"] in current_selection for f in all_files]
#             })
            
#             # Mostrar tabla con checkboxes
#             edited_df = st.data_editor(
#                 df,
#                 column_config={
#                     "Seleccionar": st.column_config.CheckboxColumn(
#                         help="Selecciona archivos para descargar",
#                         default=False
#                     )
#                 },
#                 disabled=["Archivo", "Etiquetas"
#                         #   , "Tamaño"
#                         ],
#                 use_container_width=True,
#                 key = "files_editor"
#             )
            
#             # Actualizar cesta basado en selección actual
#             nuevos_seleccionados = set(edited_df[edited_df["Seleccionar"]]["Archivo"].tolist())
            
#             # Detectar cambios en la selección
#             if nuevos_seleccionados != current_selection:
#                 st.session_state.cesta_descargas = [f for f in all_files if f["nombre"] in nuevos_seleccionados]
#                 st.rerun()
            
#             # Mostrar cesta de descargas
#             if st.session_state.cesta_descargas:
#                 st.markdown("---")
#                 st.subheader("🛒 Cesta de Descargas")
                
#                 # Lista de archivos seleccionados
#                 for idx, archivo in enumerate(st.session_state.cesta_descargas, 1):
#                     cols = st.columns([1, 4, 2])
#                     cols[0].write(f"**{idx}.**")
#                     cols[1].write(archivo["nombre"])
                
#                 # Botones de acción para la cesta
#                 col1, col2, col3 = st.columns([2, 2, 6])
#                 with col1:
#                     if st.button("📥 Descargar Todo", type="primary"):
#                         # Crear archivo ZIP (simulación)
#                         zip_buffer = io.BytesIO()
#                         with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
#                             for archivo in st.session_state.cesta_descargas:
#                                 # Aquí deberías agregar la lógica real para obtener el contenido del archivo
#                                 fake_content = f"Contenido simulado de {archivo['nombre']}".encode()
#                                 zip_file.writestr(archivo["nombre"], fake_content)
                        
#                         zip_buffer.seek(0)
#                         st.download_button(
#                             label="⬇️ Descargar ZIP",
#                             data=zip_buffer,
#                             file_name="archivos_seleccionados.zip",
#                             mime="application/zip"
#                         )
                        
#                 with col2:
#                     if st.button("🧹 Vaciar Cesta"):
#                         #  Limpiar cesta y checkboxes
#                         st.session_state.cesta_descargas.clear()
#                         st.session_state.seleccionados.clear()
#                         st.rerun()
            
#     except Exception as e:
#         st.error(f"Error al cargar archivos: {str(e)}")
    
#     # Botón para volver
#     if st.button("🔙 Volver al menú principal"):
#         st.session_state.options_menu = True
#         st.session_state.show_all_files = False
#         st.rerun()

# threading.Thread(target=connect_to_server, daemon=True).start()

# if not is_server_active(st.session_state.server_ip, DEFAULT_SERVER_PORT):
#     st.session_state.start_connection = True

# if st.session_state.get("start_connection", True):
#     st.session_state.start_connection = False
#     result_queue = Queue()
    
#     try:
#         discover_thread = threading.Thread(
#             target=discover_server, 
#             args=(result_queue,), 
#             daemon=True
#         )
#         discover_thread.start()  
        
#         # Hilo para multicast 
#         multicast_thread = threading.Thread(
#             target=send_message_multicast, 
#             daemon=True
#         )
#         multicast_thread.start()
        
#         # Esperar a que el hilo termine con timeout (evita bloqueos)
#         discover_thread.join(timeout=10)  # 10 segundos máximo
        
#         # Obtener el resultado (con timeout para evitar bloqueo)
#         try:
#             st.session_state.server_ip = result_queue.get(timeout=1)
#         except Empty:
#             st.error("No se encontró ningún servidor.")
#             st.session_state.server_ip = None
    
#     except Exception as e:
#         st.error(f"Error al conectar: {str(e)}")
#         st.session_state.server_ip = None