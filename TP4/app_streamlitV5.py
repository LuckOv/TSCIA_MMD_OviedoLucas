import streamlit as st
import pandas as pd
import csv
import os
import json
import tempfile
from pathlib import Path
from funcionesCSV_v3 import (
    csv_a_diccionarios, agregar_registro, borrar_por_indice, modificar_interactivo,
    json_a_diccionarios, agregar_registro_json, borrar_por_indice_json, modificar_interactivo_json
)

# Configuración de la página
st.set_page_config(
    page_title="Gestor de Archivos CSV/JSON",
    page_icon="📊",
    layout="wide"
)

def determinar_formato(archivo):
    """Determina si el archivo es CSV o JSON por su extensión"""
    if archivo.lower().endswith('.json'):
        return 'json'
    elif archivo.lower().endswith('.csv'):
        return 'csv'
    else:
        return None

# Inicializar estado de sesión
if 'archivo_actual' not in st.session_state:
    st.session_state.archivo_actual = None
if 'datos' not in st.session_state:
    st.session_state.datos = []
if 'campos' not in st.session_state:
    st.session_state.campos = []
if 'formato_actual' not in st.session_state:
    st.session_state.formato_actual = None
if 'directorio_guardado' not in st.session_state:
    st.session_state.directorio_guardado = os.getcwd()

def cargar_archivo(uploaded_file=None, nombre_archivo=None):
    """Carga un archivo CSV o JSON - CORREGIDA"""
    try:
        if uploaded_file is not None:
            # Leer el archivo subido
            formato = determinar_formato(uploaded_file.name)
            if formato is None:
                st.error("Formato no soportado. Use .csv o .json")
                return False
            
            nombre = uploaded_file.name
            
            # Guardar como archivo local
            with open(nombre, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            st.session_state.archivo_actual = nombre
            st.session_state.formato_actual = formato
            
            # Cargar datos según el formato
            if formato == 'csv':
                st.session_state.datos = csv_a_diccionarios(nombre)
            else:  # json
                datos_json = json_a_diccionarios(nombre)
                # Asegurarse de que los datos JSON sean una lista
                if isinstance(datos_json, list):
                    st.session_state.datos = datos_json
                else:
                    st.error("El archivo JSON no tiene el formato correcto. Debe contener una lista de objetos.")
                    return False
            
            # Obtener campos del primer registro si hay datos
            if st.session_state.datos and len(st.session_state.datos) > 0:
                st.session_state.campos = list(st.session_state.datos[0].keys())
            else:
                st.session_state.campos = []
            
            st.success(f"Archivo '{nombre}' cargado exitosamente! ({len(st.session_state.datos)} registros)")
            return True
        
        elif nombre_archivo:
            # Verificar si el archivo existe
            if not os.path.exists(nombre_archivo):
                st.error(f"El archivo '{nombre_archivo}' no existe en el directorio actual.")
                st.info(f"Archivos disponibles: {[f for f in os.listdir('.') if f.endswith(('.csv', '.json'))]}")
                return False
            
            formato = determinar_formato(nombre_archivo)
            if formato is None:
                st.error("Formato no soportado. Use .csv o .json")
                return False
            
            st.session_state.archivo_actual = nombre_archivo
            st.session_state.formato_actual = formato
            
            # Cargar datos según el formato
            if formato == 'csv':
                st.session_state.datos = csv_a_diccionarios(nombre_archivo)
            else:  # json
                datos_json = json_a_diccionarios(nombre_archivo)
                # Asegurarse de que los datos JSON sean una lista
                if isinstance(datos_json, list):
                    st.session_state.datos = datos_json
                else:
                    st.error("El archivo JSON no tiene el formato correcto. Debe contener una lista de objetos.")
                    return False
            
            # Obtener campos del primer registro si hay datos
            if st.session_state.datos and len(st.session_state.datos) > 0:
                st.session_state.campos = list(st.session_state.datos[0].keys())
            else:
                st.session_state.campos = []
            
            st.success(f"Archivo '{nombre_archivo}' cargado exitosamente! ({len(st.session_state.datos)} registros)")
            return True
            
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return False

def mostrar_registros():
    """Muestra los registros en una tabla - MEJORADA"""
    if not st.session_state.datos:
        st.info("No hay registros para mostrar")
        return
    
    # Crear DataFrame
    df = pd.DataFrame(st.session_state.datos)
    
    # Mostrar información sobre los datos
    st.write(f"**Total de registros:** {len(st.session_state.datos)}")
    
    # Mostrar tabla
    st.dataframe(df, use_container_width=True)
    
    # Mostrar estadísticas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de registros", len(st.session_state.datos))
    with col2:
        st.metric("Campos", len(st.session_state.campos))
    with col3:
        st.metric("Archivo", st.session_state.archivo_actual)
    with col4:
        st.metric("Formato", st.session_state.formato_actual.upper())

def crear_nuevo_archivo(nombre_archivo, campos, formato):
    """Crea un nuevo archivo CSV o JSON"""
    try:
        # Asegurar extensión correcta
        if not nombre_archivo.endswith(f'.{formato}'):
            nombre_archivo += f'.{formato}'
        
        if formato == 'csv':
            # Crear archivo CSV con encabezados
            with open(nombre_archivo, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=campos)
                writer.writeheader()
        else:  # json
            # Crear archivo JSON vacío
            with open(nombre_archivo, 'w', encoding='utf-8') as file:
                json.dump([], file, indent=4, ensure_ascii=False)
        
        st.session_state.archivo_actual = nombre_archivo
        st.session_state.formato_actual = formato
        st.session_state.datos = []
        st.session_state.campos = campos
        
        st.success(f"Archivo '{nombre_archivo}' creado exitosamente!")
        return True
    except Exception as e:
        st.error(f"Error al crear archivo: {e}")
        return False

def obtener_directorios_disponibles():
    """Obtiene una lista de directorios disponibles para guardar archivos"""
    directorios = []
    
    # Directorio actual
    directorios.append(("Directorio actual", os.getcwd()))
    
    # Directorio de documentos del usuario
    documentos_path = Path.home() / "Documents"
    if documentos_path.exists():
        directorios.append(("Documentos", str(documentos_path)))
    
    # Directorio de escritorio
    escritorio_path = Path.home() / "Desktop"
    if escritorio_path.exists():
        directorios.append(("Escritorio", str(escritorio_path)))
    
    # Directorio de descargas
    descargas_path = Path.home() / "Downloads"
    if descargas_path.exists():
        directorios.append(("Descargas", str(descargas_path)))
    
    return directorios

def guardar_cambios_interfaz():
    """Interfaz para guardar cambios en el archivo actual o en uno nuevo"""
    st.subheader("💾 Guardar Cambios")
    
    if not st.session_state.datos:
        st.warning("No hay datos para guardar")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Guardar en archivo actual**")
        st.info(f"Archivo actual: {st.session_state.archivo_actual}")
        if st.button("💾 Guardar en archivo actual", use_container_width=True):
            guardar_archivo_actual()
    
    with col2:
        st.write("**Guardar como nuevo archivo**")
        
        # Selección de directorio
        st.write("**Seleccionar ubicación:**")
        directorios = obtener_directorios_disponibles()
        
        opciones_directorios = [f"{nombre} ({ruta})" for nombre, ruta in directorios]
        directorio_seleccionado = st.selectbox(
            "Ubicación para guardar:",
            options=opciones_directorios,
            index=0,
            key="selector_directorio"
        )
        
        # Obtener la ruta del directorio seleccionado
        directorio_ruta = directorios[opciones_directorios.index(directorio_seleccionado)][1]
        st.session_state.directorio_guardado = directorio_ruta
        
        # Mostrar ruta seleccionada
        st.info(f"**Directorio seleccionado:** `{directorio_ruta}`")
        
        # Campo para nombre personalizado
        nombre_base = f"copia_{st.session_state.archivo_actual}"
        nombre_personalizado = st.text_input(
            "Nombre del archivo:",
            value=nombre_base,
            help="Puedes cambiar el nombre del archivo"
        )
        
        formato_nuevo = st.selectbox(
            "Formato:", 
            ["csv", "json"], 
            index=0 if st.session_state.formato_actual == "csv" else 1,
            key="formato_guardar"
        )
        
        # Mostrar ruta completa previa
        ruta_completa = os.path.join(directorio_ruta, nombre_personalizado)
        if not ruta_completa.endswith(f'.{formato_nuevo}'):
            ruta_completa += f'.{formato_nuevo}'
        
        st.info(f"**Se guardará en:** `{ruta_completa}`")
        
        if st.button("💾 Guardar como nuevo archivo", use_container_width=True):
            if nombre_personalizado:
                guardar_como_nuevo_archivo(nombre_personalizado, formato_nuevo, directorio_ruta)
            else:
                st.error("Debe ingresar un nombre para el nuevo archivo")

def guardar_archivo_actual():
    """Guarda los cambios en el archivo actual"""
    try:
        if st.session_state.formato_actual == 'csv':
            # Guardar como CSV
            with open(st.session_state.archivo_actual, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=st.session_state.campos)
                writer.writeheader()
                writer.writerows(st.session_state.datos)
        else:  # json
            # Guardar como JSON
            with open(st.session_state.archivo_actual, 'w', encoding='utf-8') as file:
                json.dump(st.session_state.datos, file, indent=4, ensure_ascii=False)
        
        st.success(f"Cambios guardados exitosamente en '{st.session_state.archivo_actual}'")
        return True
    except Exception as e:
        st.error(f"Error al guardar cambios: {e}")
        return False

def guardar_como_nuevo_archivo(nombre_archivo, formato, directorio=None):
    """Guarda los datos actuales en un nuevo archivo en la ubicación especificada"""
    try:
        # Usar directorio por defecto si no se especifica
        if directorio is None:
            directorio = st.session_state.directorio_guardado
        
        # Asegurar extensión correcta
        if not nombre_archivo.endswith(f'.{formato}'):
            nombre_archivo += f'.{formato}'
        
        # Construir ruta completa
        ruta_completa = os.path.join(directorio, nombre_archivo)
        
        # Verificar si el archivo ya existe
        if os.path.exists(ruta_completa):
            st.warning(f"El archivo '{ruta_completa}' ya existe. Se sobrescribirá.")
        
        if formato == 'csv':
            # Guardar como CSV
            with open(ruta_completa, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=st.session_state.campos)
                writer.writeheader()
                writer.writerows(st.session_state.datos)
        else:  # json
            # Guardar como JSON
            with open(ruta_completa, 'w', encoding='utf-8') as file:
                json.dump(st.session_state.datos, file, indent=4, ensure_ascii=False)
        
        st.success(f"Datos guardados exitosamente en '{ruta_completa}'")
        
        # Ofrecer opción para descargar el archivo
        with open(ruta_completa, "rb") as file:
            btn = st.download_button(
                label="📥 Descargar archivo",
                data=file,
                file_name=nombre_archivo,
                mime="text/csv" if formato == "csv" else "application/json",
                use_container_width=True
            )
        
        return True
    except Exception as e:
        st.error(f"Error al guardar archivo: {e}")
        return False

def agregar_registro_interfaz():
    """Interfaz para agregar nuevo registro"""
    st.subheader("➕ Agregar Nuevo Registro")
    
    if not st.session_state.campos:
        st.warning("No hay campos definidos. Primero carga un archivo existente o crea uno nuevo.")
        return
    
    with st.form("form_agregar_registro"):
        registro = {}
        cols = st.columns(2)
        
        for i, campo in enumerate(st.session_state.campos):
            with cols[i % 2]:
                registro[campo] = st.text_input(f"{campo}", key=f"add_{campo}")
        
        submitted = st.form_submit_button("Agregar Registro")
        
        if submitted:
            if all(registro.values()):
                if st.session_state.formato_actual == 'csv':
                    resultado = agregar_registro(st.session_state.archivo_actual, registro)
                else:  # json
                    resultado = agregar_registro_json(st.session_state.archivo_actual, registro)
                
                if resultado:
                    # Actualizar datos
                    if st.session_state.formato_actual == 'csv':
                        st.session_state.datos = csv_a_diccionarios(st.session_state.archivo_actual)
                    else:  # json
                        st.session_state.datos = json_a_diccionarios(st.session_state.archivo_actual)
                    st.rerun()
            else:
                st.error("Todos los campos son obligatorios")

def borrar_registro_interfaz():
    """Interfaz para borrar registros"""
    st.subheader("🗑️ Borrar Registro")
    
    if not st.session_state.datos:
        st.warning("No hay registros para borrar")
        return
    
    # Mostrar registros con selección
    df = pd.DataFrame(st.session_state.datos)
    
    # Agregar columna de selección
    df_seleccion = df.copy()
    df_seleccion['Seleccionar'] = False
    
    # Crear editor de datos para selección
    edited_df = st.data_editor(
        df_seleccion,
        column_config={
            "Seleccionar": st.column_config.CheckboxColumn(
                "Seleccionar",
                help="Selecciona los registros a borrar",
                default=False,
            )
        },
        disabled=df.columns.tolist(),
        use_container_width=True
    )
    
    # Contar registros seleccionados
    registros_seleccionados = edited_df[edited_df['Seleccionar'] == True]
    
    if not registros_seleccionados.empty:
        st.warning(f"Se borrarán {len(registros_seleccionados)} registros")
        
        if st.button("Confirmar Borrado", type="primary"):
            # Obtener índices de los registros seleccionados
            indices = []
            for idx in registros_seleccionados.index:
                indices.append(idx)
            
            # Borrar registros según el formato
            if st.session_state.formato_actual == 'csv':
                borrados = borrar_por_indice(st.session_state.archivo_actual, indices)
            else:  # json
                borrados = borrar_por_indice_json(st.session_state.archivo_actual, indices)
            
            if borrados > 0:
                st.success(f"Se borraron {borrados} registros exitosamente!")
                # Actualizar datos
                if st.session_state.formato_actual == 'csv':
                    st.session_state.datos = csv_a_diccionarios(st.session_state.archivo_actual)
                else:  # json
                    st.session_state.datos = json_a_diccionarios(st.session_state.archivo_actual)
                st.rerun()

def modificar_registro_interfaz():
    """Interfaz para modificar registros"""
    st.subheader("✏️ Modificar Registro")
    
    if not st.session_state.datos:
        st.warning("No hay registros para modificar")
        return
    
    # Seleccionar registro
    opciones = [f"Registro {i+1}: {str(registro)[:50]}..." for i, registro in enumerate(st.session_state.datos)]
    registro_seleccionado = st.selectbox("Selecciona el registro a modificar:", opciones)
    
    if registro_seleccionado:
        indice = opciones.index(registro_seleccionado)
        registro_actual = st.session_state.datos[indice]
        
        st.write("**Registro seleccionado:**")
        st.json(registro_actual)
        
        # Formulario para modificación
        with st.form("form_modificar_registro"):
            st.write("**Nuevos valores:**")
            nuevo_registro = {}
            cols = st.columns(2)
            
            for i, campo in enumerate(st.session_state.campos):
                with cols[i % 2]:
                    valor_actual = registro_actual.get(campo, '')
                    nuevo_registro[campo] = st.text_input(f"{campo}", value=valor_actual, key=f"mod_{campo}_{indice}")
            
            submitted = st.form_submit_button("Actualizar Registro")
            
            if submitted:
                # Aplicar cambios según el formato
                if st.session_state.formato_actual == 'csv':
                    # Para CSV: leer, modificar y escribir
                    with open(st.session_state.archivo_actual, 'r', encoding='utf-8') as file:
                        reader = csv.DictReader(file)
                        encabezados = reader.fieldnames
                        registros = list(reader)
                    
                    registros[indice] = nuevo_registro
                    
                    with open(st.session_state.archivo_actual, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.DictWriter(file, fieldnames=encabezados)
                        writer.writeheader()
                        writer.writerows(registros)
                else:  # json
                    # Para JSON: leer, modificar y escribir
                    datos = json_a_diccionarios(st.session_state.archivo_actual)
                    datos[indice] = nuevo_registro
                    
                    with open(st.session_state.archivo_actual, 'w', encoding='utf-8') as file:
                        json.dump(datos, file, indent=4, ensure_ascii=False)
                
                st.success("Registro modificado exitosamente!")
                # Actualizar datos
                if st.session_state.formato_actual == 'csv':
                    st.session_state.datos = csv_a_diccionarios(st.session_state.archivo_actual)
                else:  # json
                    st.session_state.datos = json_a_diccionarios(st.session_state.archivo_actual)
                st.rerun()

# Interfaz principal
st.title("📊 Gestor de Archivos CSV/JSON")
st.markdown("---")

# Sidebar para carga de archivos
with st.sidebar:
    st.header("📁 Gestión de Archivos")
    
    # Opción 1: Subir archivo existente
    st.subheader("Cargar Archivo Existente")
    uploaded_file = st.file_uploader("Sube un archivo CSV o JSON", type=['csv', 'json'])
    
    if uploaded_file is not None:
        if st.button("Cargar Archivo Subido"):
            cargar_archivo(uploaded_file=uploaded_file)
    
    # Opción 2: Cargar archivo local
    st.subheader("Cargar Archivo Local")
    
    # Mostrar archivos disponibles
    archivos_disponibles = [f for f in os.listdir('.') if f.endswith('.csv') or f.endswith('.json')]
    if archivos_disponibles:
        archivo_seleccionado = st.selectbox("Selecciona un archivo:", archivos_disponibles)
        if st.button("Cargar Archivo Local"):
            cargar_archivo(nombre_archivo=archivo_seleccionado)
    else:
        st.info("No hay archivos CSV o JSON en el directorio actual")
    
    # Mostrar directorio actual para debug
    st.info(f"Directorio actual: {os.getcwd()}")
    
    # Opción 3: Crear nuevo archivo
    st.subheader("Crear Nuevo Archivo")
    nuevo_nombre = st.text_input("Nombre del nuevo archivo:")
    formato_nuevo = st.selectbox("Formato:", ["csv", "json"])
    campos_nuevo = st.text_input("Campos (separados por coma):", placeholder="ej: id,nombre,edad")
    
    if st.button("Crear Nuevo Archivo"):
        if nuevo_nombre and campos_nuevo:
            campos_lista = [campo.strip() for campo in campos_nuevo.split(',')]
            crear_nuevo_archivo(nuevo_nombre, campos_lista, formato_nuevo)
        else:
            st.error("Debe ingresar nombre y campos para crear un nuevo archivo")
    
    st.markdown("---")
    # Información del archivo actual
    if st.session_state.archivo_actual:
        st.success(f"**Archivo actual:** {st.session_state.archivo_actual}")
        st.info(f"**Formato:** {st.session_state.formato_actual.upper()}")
        st.info(f"**Registros:** {len(st.session_state.datos)}")
        st.info(f"**Campos:** {', '.join(st.session_state.campos)}")
    else:
        st.warning("No hay archivo cargado")

# Contenido principal
if st.session_state.archivo_actual:
    # Pestañas para diferentes operaciones
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Ver Registros", 
        "➕ Agregar", 
        "✏️ Modificar", 
        "🗑️ Borrar",
        "💾 Guardar"  # Nueva pestaña para guardar cambios
    ])
    
    with tab1:
        mostrar_registros()
    
    with tab2:
        agregar_registro_interfaz()
    
    with tab3:
        modificar_registro_interfaz()
    
    with tab4:
        borrar_registro_interfaz()
    
    with tab5:
        guardar_cambios_interfaz()

else:
    # Pantalla de bienvenida cuando no hay archivo cargado
    st.markdown("""
    ## 👋 ¡Bienvenido al Gestor de Archivos CSV/JSON!
    
    ### Para comenzar:
    1. **Carga un archivo existente** (CSV o JSON) usando las opciones en la barra lateral, o
    2. **Crea un nuevo archivo** especificando nombre, formato y campos
    
    ### Funcionalidades disponibles:
    - 📋 **Ver y explorar** registros en formato tabla
    - ➕ **Agregar** nuevos registros
    - ✏️ **Modificar** registros existentes  
    - 🗑️ **Borrar** registros seleccionados
    - 💾 **Guardar** cambios en archivos
    
    ### Formatos soportados:
    - **CSV** (Comma Separated Values)
    - **JSON** (JavaScript Object Notation)
    
    ### Instrucciones:
    - Usa la barra lateral para gestionar archivos
    - Una vez cargado un archivo, podrás acceder a todas las funcionalidades
    """)
    
    # Mostrar archivos disponibles localmente
    archivos_disponibles = [f for f in os.listdir('.') if f.endswith('.csv') or f.endswith('.json')]
    if archivos_disponibles:
        st.subheader("Archivos disponibles localmente:")
        for archivo in archivos_disponibles:
            formato = determinar_formato(archivo)
            st.write(f"- `{archivo}` ({formato.upper()})")

# Footer
st.markdown("---")
st.caption("Gestor de Archivos CSV/JSON - Desarrollado con Streamlit")