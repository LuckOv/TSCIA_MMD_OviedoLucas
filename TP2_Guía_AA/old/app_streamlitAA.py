import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import warnings

# Configuración para suprimir warnings
warnings.filterwarnings('ignore')

# Configuración de la página
st.set_page_config(
    page_title="Predicción de Abandono Estudiantil",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎓 Predicción de Abandono Estudiantil - Instituto Tecnológico Beltrán")

# Sidebar para navegación
st.sidebar.title("Navegación")
app_mode = st.sidebar.selectbox(
    "Selecciona una sección:",
    ["🏠 Inicio", "📊 Análisis Exploratorio", "🤖 Entrenar Modelo", "📝 Predecir Abandono", "📈 Exploración Avanzada"]
)

# Función para cargar datos
@st.cache_data
def load_data(uploaded_file):
    """Cargar datos desde archivo Excel o CSV"""
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Formato de archivo no soportado. Use .xlsx o .csv")
            return None
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return None

# Función para entrenar modelo
def train_model(df, max_depth=None, min_samples_split=5, min_samples_leaf=2):
    """Entrenar modelo de predicción de abandono"""
    try:
        # Verificar que existe la columna objetivo
        if 'EstadoFinal' not in df.columns:
            st.error("El dataset debe contener la columna 'EstadoFinal'")
            return None, None, None, None, None, None, None
        
        # Codificar variable objetivo
        df_processed = df.copy()
        df_processed['EstadoFinal'] = df_processed['EstadoFinal'].map({'Continúa': 0, 'Abandonó': 1})
        
        # Codificar variables categóricas
        label_encoders = {}
        categorical_columns = ['genero', 'carrera', 'trabaja/NoTrabaja', 'ActividadesExtracurriculares(Estudio)']
        
        for col in categorical_columns:
            if col in df_processed.columns:
                le = LabelEncoder()
                df_processed[col] = le.fit_transform(df_processed[col].astype(str))
                label_encoders[col] = le
        
        # Preparar características y variable objetivo
        X = df_processed.drop('EstadoFinal', axis=1)
        y = df_processed['EstadoFinal']
        
        # División train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Entrenar modelo optimizado
        arbol_optimizado = DecisionTreeClassifier(
            criterion='entropy',
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=42
        )
        
        arbol_optimizado.fit(X_train, y_train)
        
        return arbol_optimizado, X_train, X_test, y_train, y_test, label_encoders, X.columns
        
    except Exception as e:
        st.error(f"Error en el entrenamiento: {e}")
        return None, None, None, None, None, None, None

# Página de Inicio
if app_mode == "🏠 Inicio":
    st.header("Bienvenido al Sistema de Predicción de Abandono Estudiantil")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 📋 Descripción del Sistema
        
        Esta aplicación permite:
        
        - **📊 Análisis Exploratorio**: Visualizar y analizar los datos de estudiantes
        - **🤖 Entrenamiento de Modelos**: Crear modelos predictivos de abandono estudiantil
        - **📝 Predicciones**: Evaluar estudiantes individuales o en lote
        - **📈 Exploración Avanzada**: Análisis interactivo de datos
        
        ### 🎯 Características Principales
        
        - Modelo de Árbol de Decisión optimizado
        - Interfaz intuitiva para ingreso de datos
        - Visualización del árbol de decisión
        - Análisis de riesgo individualizado
        - Recomendaciones de intervención
        """)
    
    with col2:
        st.markdown("""
        <div style='text-align: center'>
            <h3>🎓</h3>
            <p><strong>Sistema de Predicción</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("""
        **📁 Formatos soportados:**
        - Excel (.xlsx)
        - CSV (.csv)
        
        **🎓 Variables requeridas:**
        - EstadoFinal (Continúa/Abandonó)
        - Datos académicos y demográficos
        """)

# Página de Análisis Exploratorio
elif app_mode == "📊 Análisis Exploratorio":
    st.header("📊 Análisis Exploratorio de Datos")
    
    uploaded_file = st.file_uploader(
        "Carga tu archivo de datos", 
        type=['xlsx', 'csv'],
        help="Sube el archivo con los datos de los estudiantes"
    )
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        if df is not None:
            # Mostrar información general
            st.subheader("📈 Información General del Dataset")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Estudiantes", len(df))
            
            with col2:
                if 'EstadoFinal' in df.columns:
                    abandonos = sum(df['EstadoFinal'] == 'Abandonó')
                    st.metric("Estudiantes que Abandonan", abandonos)
            
            with col3:
                if 'EstadoFinal' in df.columns:
                    continuan = sum(df['EstadoFinal'] == 'Continúa')
                    st.metric("Estudiantes que Continúan", continuan)
            
            with col4:
                if 'EstadoFinal' in df.columns:
                    tasa_abandono = (sum(df['EstadoFinal'] == 'Abandonó') / len(df)) * 100
                    st.metric("Tasa de Abandono", f"{tasa_abandono:.1f}%")
            
            # Pestañas para diferentes vistas
            tab1, tab2, tab3 = st.tabs(["📋 Vista de Datos", "📊 Estadísticas", "📈 Visualizaciones"])
            
            with tab1:
                st.subheader("Primeros registros del dataset")
                st.dataframe(df.head(10), use_container_width=True)
                
                st.subheader("Información de columnas")
                col_info = pd.DataFrame({
                    'Columna': df.columns,
                    'Tipo': df.dtypes,
                    'Valores Únicos': [df[col].nunique() for col in df.columns],
                    'Valores Nulos': [df[col].isnull().sum() for col in df.columns]
                })
                st.dataframe(col_info, use_container_width=True)
            
            with tab2:
                st.subheader("Estadísticas Descriptivas")
                st.dataframe(df.describe(), use_container_width=True)
                
                # Estadísticas por carrera si existe
                if 'carrera' in df.columns and 'EstadoFinal' in df.columns:
                    st.subheader("Tasa de Abandono por Carrera")
                    abandono_carrera = df.groupby('carrera')['EstadoFinal'].apply(
                        lambda x: (x == 'Abandonó').mean() * 100
                    ).round(1).sort_values(ascending=False)
                    st.dataframe(abandono_carrera, use_container_width=True)
            
            with tab3:
                st.subheader("Visualizaciones")
                
                # Gráfico de distribución de abandono
                if 'EstadoFinal' in df.columns:
                    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
                    
                    # Pie chart
                    counts = df['EstadoFinal'].value_counts()
                    ax[0].pie(counts.values, labels=counts.index, autopct='%1.1f%%', startangle=90,
                             colors=['#66b3ff', '#ff6666'])
                    ax[0].set_title('Distribución de Estado Final')
                    
                    # Bar plot
                    counts.plot(kind='bar', ax=ax[1], color=['#66b3ff', '#ff6666'])
                    ax[1].set_title('Conteo por Estado Final')
                    ax[1].set_ylabel('Cantidad de Estudiantes')
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                
                # Distribución de promedio si existe
                if 'PromedioPrimerCuatrimestre' in df.columns and 'EstadoFinal' in df.columns:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    continuan_data = df[df['EstadoFinal'] == 'Continúa']['PromedioPrimerCuatrimestre']
                    abandonaron_data = df[df['EstadoFinal'] == 'Abandonó']['PromedioPrimerCuatrimestre']
                    
                    ax.hist(continuan_data, alpha=0.7, label='Continúa', bins=15, color='#66b3ff')
                    ax.hist(abandonaron_data, alpha=0.7, label='Abandonó', bins=15, color='#ff6666')
                    
                    ax.set_xlabel('Promedio Primer Cuatrimestre')
                    ax.set_ylabel('Frecuencia')
                    ax.set_title('Distribución de Promedios por Estado Final')
                    ax.legend()
                    
                    st.pyplot(fig)

# Página de Entrenamiento del Modelo
elif app_mode == "🤖 Entrenar Modelo":
    st.header("🤖 Entrenamiento del Modelo Predictivo")
    
    uploaded_file = st.file_uploader(
        "Carga el archivo de entrenamiento", 
        type=['xlsx', 'csv'],
        key="train_file"
    )
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        if df is not None:
            st.success(f"✅ Dataset cargado: {len(df)} estudiantes")
            
            # Mostrar vista previa
            with st.expander("🔍 Vista previa del dataset"):
                st.dataframe(df.head(), use_container_width=True)
            
            # Verificar columna objetivo
            if 'EstadoFinal' not in df.columns:
                st.error("❌ El dataset debe contener la columna 'EstadoFinal'")
            else:
                # Configuración de hiperparámetros
                st.subheader("⚙️ Configuración del Modelo")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    max_depth = st.selectbox("Profundidad máxima", [3, 4, 5, 6, 7, None], index=2)
                
                with col2:
                    min_samples_split = st.selectbox("Mínimo samples para dividir", [2, 5, 10, 15], index=1)
                
                with col3:
                    min_samples_leaf = st.selectbox("Mínimo samples en hoja", [1, 2, 5, 10], index=1)
                
                # Botón para entrenar modelo
                if st.button("🚀 Entrenar Modelo", type="primary"):
                    with st.spinner("Entrenando modelo..."):
                        modelo, X_train, X_test, y_train, y_test, label_encoders, feature_columns = train_model(
                            df, max_depth, min_samples_split, min_samples_leaf
                        )
                    
                    if modelo is not None:
                        # Realizar predicciones
                        y_pred = modelo.predict(X_test)
                        precision = accuracy_score(y_test, y_pred)
                        
                        st.success("✅ Modelo entrenado exitosamente!")
                        
                        # Métricas del modelo
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Precisión del Modelo", f"{precision*100:.1f}%")
                        
                        with col2:
                            st.metric("Profundidad del Árbol", modelo.get_depth())
                        
                        with col3:
                            st.metric("Hojas del Árbol", modelo.get_n_leaves())
                        
                        # Matriz de confusión
                        st.subheader("📊 Matriz de Confusión")
                        cm = confusion_matrix(y_test, y_pred)
                        
                        fig, ax = plt.subplots(figsize=(6, 4))
                        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                                   xticklabels=['Continúa', 'Abandona'],
                                   yticklabels=['Continúa', 'Abandona'])
                        ax.set_xlabel('Predicción')
                        ax.set_ylabel('Real')
                        ax.set_title('Matriz de Confusión')
                        st.pyplot(fig)
                        
                        # Reporte de clasificación
                        st.subheader("📋 Reporte de Clasificación")
                        reporte = classification_report(y_test, y_pred, target_names=['Continúa', 'Abandona'])
                        st.text(reporte)
                        
                        # Visualización del árbol
                        st.subheader("🌳 Visualización del Árbol de Decisión")
                        
                        nombres_legibles = {
                            'edad': 'Edad',
                            'genero': 'Género', 
                            'carrera': 'Carrera',
                            'PromedioPrimerCuatrimestre': 'Promedio 1er Cuatrimestre',
                            'CantMateriasAprobadasPrimerCuatrimestre': 'Materias Aprobadas',
                            'CantMateriasDesaprobadasPrimerCuatrimestre': 'Materias Desaprobadas',
                            'AsistenciaPromedio(%)': 'Asistencia Promedio (%)',
                            'trabaja/NoTrabaja': 'Trabaja',
                            'DistanciaDomicilioAlInstituto(Kms)': 'Distancia al Instituto (Km)',
                            'ActividadesExtracurriculares(Estudio)': 'Actividades Extracurriculares'
                        }
                        
                        feature_names_legibles = [nombres_legibles.get(col, col) for col in feature_columns]
                        
                        fig, ax = plt.subplots(figsize=(20, 12))
                        plot_tree(modelo, 
                                feature_names=feature_names_legibles,
                                class_names=['Continúa', 'Abandona'],
                                filled=True,
                                rounded=True,
                                fontsize=10,
                                proportion=True,
                                ax=ax)
                        
                        ax.set_title(f"Árbol de Decisión - Precisión: {precision*100:.1f}%", fontsize=16)
                        st.pyplot(fig)
                        
                        # Importancia de características
                        st.subheader("📈 Importancia de Características")
                        importancia = pd.DataFrame({
                            'Característica': feature_names_legibles,
                            'Importancia': modelo.feature_importances_
                        }).sort_values('Importancia', ascending=False)
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.barplot(data=importancia, x='Importancia', y='Característica', ax=ax, palette='viridis')
                        ax.set_title('Importancia de Características en el Modelo')
                        st.pyplot(fig)
                        
                        # Guardar información en session state
                        st.session_state['modelo'] = modelo
                        st.session_state['label_encoders'] = label_encoders
                        st.session_state['feature_columns'] = feature_columns
                        st.session_state['precision'] = precision
                        st.session_state['feature_names_legibles'] = feature_names_legibles
                        
                        st.success("🎯 Modelo listo para realizar predicciones!")

# Página de Predicción
elif app_mode == "📝 Predecir Abandono":
    st.header("📝 Predicción de Abandono Estudiantil")
    
    # Verificar si el modelo está entrenado
    if 'modelo' not in st.session_state:
        st.warning("⚠️ Primero debes entrenar el modelo en la sección '🤖 Entrenar Modelo'")
        st.info("Ve a la sección de entrenamiento y carga tu dataset para entrenar el modelo.")
    else:
        modelo = st.session_state['modelo']
        label_encoders = st.session_state['label_encoders']
        feature_columns = st.session_state['feature_columns']
        
        # Opciones de predicción
        pred_mode = st.radio(
            "Selecciona el modo de predicción:",
            ["👤 Predicción Individual", "📊 Predicción por Lote"]
        )
        
        if pred_mode == "👤 Predicción Individual":
            st.subheader("Ingreso de Datos del Estudiante")
            
            with st.form("formulario_estudiante"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 Datos Académicos**")
                    edad = st.number_input("Edad", min_value=15, max_value=100, value=20)
                    promedio = st.number_input("Promedio Primer Cuatrimestre", min_value=0.0, max_value=10.0, value=6.0, step=0.1)
                    materias_aprobadas = st.number_input("Materias Aprobadas", min_value=0, max_value=20, value=4)
                    materias_desaprobadas = st.number_input("Materias Desaprobadas", min_value=0, max_value=20, value=4)
                    asistencia = st.number_input("Asistencia Promedio (%)", min_value=0, max_value=100, value=60)
                
                with col2:
                    st.markdown("**👤 Datos Personales**")
                    distancia = st.number_input("Distancia al Instituto (Km)", min_value=0.0, max_value=200.0, value=50.0, step=1.0)
                    
                    # Campos categóricos con opciones disponibles
                    genero = st.selectbox("Género", ["femenino", "masculino", "otro"])
                    carrera = st.selectbox("Carrera", [
                        "Tecnicatura Superior en Análisis de Sistemas",
                        "Tecnicatura Superior en Diseño Industrial", 
                        "Tecnicatura Superior en Administración",
                        "Tecnicatura Superior en Turismo"
                    ])
                    trabaja = st.selectbox("Trabaja", ["Si", "No"])
                    actividades = st.selectbox("Actividades Extracurriculares", ["Si", "No"])
                
                submitted = st.form_submit_button("🎯 Predecir Abandono", type="primary")
                
                if submitted:
                    # Crear diccionario con datos del estudiante
                    estudiante = {
                        'edad': edad,
                        'PromedioPrimerCuatrimestre': promedio,
                        'CantMateriasAprobadasPrimerCuatrimestre': materias_aprobadas,
                        'CantMateriasDesaprobadasPrimerCuatrimestre': materias_desaprobadas,
                        'AsistenciaPromedio(%)': asistencia,
                        'DistanciaDomicilioAlInstituto(Kms)': distancia,
                        'genero': genero,
                        'carrera': carrera,
                        'trabaja/NoTrabaja': trabaja,
                        'ActividadesExtracurriculares(Estudio)': actividades
                    }
                    
                    # Codificar variables categóricas
                    estudiante_codificado = {}
                    for col, valor in estudiante.items():
                        if col in label_encoders:
                            try:
                                # Verificar si el valor existe en el encoder
                                if valor in label_encoders[col].classes_:
                                    estudiante_codificado[col] = label_encoders[col].transform([valor])[0]
                                else:
                                    # Si no existe, usar el valor más común
                                    estudiante_codificado[col] = 0
                            except:
                                estudiante_codificado[col] = 0
                        else:
                            estudiante_codificado[col] = valor
                    
                    # Convertir a DataFrame
                    df_estudiante = pd.DataFrame([estudiante_codificado])
                    
                    # Asegurarse de que tenemos todas las columnas necesarias
                    for col in feature_columns:
                        if col not in df_estudiante.columns:
                            df_estudiante[col] = 0
                    
                    df_estudiante = df_estudiante[feature_columns]
                    
                    # Realizar predicción
                    try:
                        prediccion = modelo.predict(df_estudiante)[0]
                        probabilidad = modelo.predict_proba(df_estudiante)[0][1]
                        
                        # Mostrar resultados
                        st.subheader("🎯 Resultado de la Predicción")
                        
                        # Tarjetas de métricas
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            estado = "🟢 Continúa" if prediccion == 0 else "🔴 Abandona"
                            st.metric("Predicción", estado)
                        
                        with col2:
                            st.metric("Probabilidad de Abandono", f"{probabilidad*100:.1f}%")
                        
                        with col3:
                            if probabilidad > 0.7:
                                riesgo = "🔴 ALTO"
                                accion = "Intervención urgente"
                            elif probabilidad > 0.3:
                                riesgo = "🟡 MODERADO"
                                accion = "Seguimiento académico"
                            else:
                                riesgo = "🟢 BAJO"
                                accion = "Monitoreo estándar"
                            st.metric("Nivel de Riesgo", riesgo)
                        
                        # Barra de progreso
                        st.progress(float(probabilidad), text=f"Probabilidad de abandono: {probabilidad*100:.1f}%")
                        
                        # Recomendación
                        st.info(f"**📋 Recomendación:** {accion}")
                        
                        # Análisis detallado
                        with st.expander("🔍 Análisis Detallado"):
                            st.write("**Datos del estudiante evaluado:**")
                            for col, valor in estudiante.items():
                                st.write(f"- **{col}:** {valor}")
                            
                            st.write(f"**Probabilidad de continuar:** {(1-probabilidad)*100:.1f}%")
                            
                            if probabilidad > 0.5:
                                st.error("""
                                **🚨 Factores de riesgo identificados:**
                                - El estudiante muestra características asociadas con abandono
                                - Se recomienda intervención temprana
                                - Contactar con el departamento de orientación estudiantil
                                """)
                                
                                # Sugerencias específicas basadas en los datos
                                if asistencia < 70:
                                    st.warning("🔔 **Baja asistencia:** Considerar programa de tutorías")
                                if promedio < 6:
                                    st.warning("🔔 **Bajo promedio:** Sugerir reforzamiento académico")
                                if materias_desaprobadas > materias_aprobadas:
                                    st.warning("🔔 **Alto índice de materias desaprobadas:** Revisión de carga académica")
                            else:
                                st.success("""
                                **✅ Situación favorable:**
                                - El estudiante muestra buen desempeño académico
                                - Continuar con el monitoreo regular
                                - Mantener el apoyo institucional
                                """)
                    
                    except Exception as e:
                        st.error(f"Error en la predicción: {e}")
        
        else:  # Predicción por Lote
            st.subheader("Predicción por Lote")
            
            uploaded_batch = st.file_uploader(
                "Carga archivo con datos de estudiantes para predicción",
                type=['xlsx', 'csv'],
                key="batch_file"
            )
            
            if uploaded_batch is not None:
                df_batch = load_data(uploaded_batch)
                
                if df_batch is not None:
                    st.success(f"✅ Archivo cargado: {len(df_batch)} estudiantes")
                    
                    # Mostrar vista previa
                    st.dataframe(df_batch.head(), use_container_width=True)
                    
                    if st.button("🎯 Predecir Lote Completo", type="primary"):
                        with st.spinner("Realizando predicciones..."):
                            try:
                                # Procesar datos
                                df_processed = df_batch.copy()
                                
                                # Codificar variables categóricas
                                for col in label_encoders:
                                    if col in df_processed.columns:
                                        # Manejar valores nuevos
                                        mask = df_processed[col].isin(label_encoders[col].classes_)
                                        df_processed.loc[mask, col] = label_encoders[col].transform(df_processed.loc[mask, col])
                                        df_processed.loc[~mask, col] = 0  # Valor por defecto para valores nuevos
                                
                                # Asegurar que tenemos todas las columnas necesarias
                                for col in feature_columns:
                                    if col not in df_processed.columns:
                                        df_processed[col] = 0
                                
                                df_processed = df_processed[feature_columns]
                                
                                # Realizar predicciones
                                predicciones = modelo.predict(df_processed)
                                probabilidades = modelo.predict_proba(df_processed)[:, 1]
                                
                                # Crear DataFrame de resultados
                                df_resultados = df_batch.copy()
                                df_resultados['Prediccion_Abandono'] = predicciones
                                df_resultados['Probabilidad_Abandono'] = probabilidades
                                df_resultados['Estado_Predicho'] = df_resultados['Prediccion_Abandono'].map(
                                    {0: 'Continúa', 1: 'Abandona'}
                                )
                                df_resultados['Riesgo'] = df_resultados['Probabilidad_Abandono'].apply(
                                    lambda x: 'ALTO' if x > 0.7 else 'MODERADO' if x > 0.3 else 'BAJO'
                                )
                                
                                # Mostrar resumen
                                st.subheader("📊 Resumen de Predicciones")
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("Total Evaluados", len(df_resultados))
                                
                                with col2:
                                    abandonos_pred = sum(predicciones)
                                    st.metric("Predicen Abandono", abandonos_pred)
                                
                                with col3:
                                    continuan_pred = len(predicciones) - abandonos_pred
                                    st.metric("Predicen Continúan", continuan_pred)
                                
                                with col4:
                                    tasa_pred = (abandonos_pred / len(predicciones)) * 100
                                    st.metric("Tasa Predicha", f"{tasa_pred:.1f}%")
                                
                                # Gráfico de distribución
                                fig, ax = plt.subplots(figsize=(8, 4))
                                df_resultados['Estado_Predicho'].value_counts().plot(
                                    kind='bar', ax=ax, color=['#66b3ff', '#ff6666']
                                )
                                ax.set_title('Distribución de Predicciones')
                                ax.set_ylabel('Cantidad de Estudiantes')
                                st.pyplot(fig)
                                
                                # Mostrar resultados detallados
                                st.subheader("📋 Resultados Detallados")
                                st.dataframe(df_resultados, use_container_width=True)
                                
                                # Descargar resultados
                                csv = df_resultados.to_csv(index=False)
                                st.download_button(
                                    label="📥 Descargar Resultados CSV",
                                    data=csv,
                                    file_name="predicciones_abandono.csv",
                                    mime="text/csv"
                                )
                                
                            except Exception as e:
                                st.error(f"Error en el procesamiento del lote: {e}")

# Página de Exploración Avanzada
elif app_mode == "📈 Exploración Avanzada":
    st.header("📈 Exploración Avanzada de Datos")
    
    uploaded_file = st.file_uploader(
        "Carga tu archivo de datos para análisis avanzado", 
        type=['xlsx', 'csv'],
        key="advanced_file"
    )
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        if df is not None:
            st.success(f"✅ Dataset cargado: {len(df)} registros")
            
            # Análisis de correlación
            st.subheader("🔗 Análisis de Correlación")
            
            # Seleccionar solo columnas numéricas
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_cols) > 1:
                # Calcular matriz de correlación
                corr_matrix = df[numeric_cols].corr()
                
                # Heatmap de correlación
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax, fmt='.2f')
                ax.set_title('Matriz de Correlación')
                st.pyplot(fig)
            
            # Análisis de segmentación
            st.subheader("🎯 Análisis de Segmentación")
            
            if 'EstadoFinal' in df.columns:
                # Selector de variables para segmentación
                var_segmentacion = st.selectbox(
                    "Variable para segmentación:", 
                    [col for col in df.columns if col != 'EstadoFinal'],
                    key="segmentation_var"
                )
                
                if df[var_segmentacion].dtype in ['object', 'category']:
                    # Para variables categóricas
                    st.write(f"**Segmentos encontrados:** {len(df[var_segmentacion].unique())}")
                    
                    # Tasa de abandono por segmento
                    abandono_por_segmento = df.groupby(var_segmentacion)['EstadoFinal'].apply(
                        lambda x: (x == 'Abandonó').mean() * 100
                    ).round(1).sort_values(ascending=False)
                    
                    st.dataframe(abandono_por_segmento, use_container_width=True)
                    
                    # Gráfico
                    fig, ax = plt.subplots(figsize=(10, 6))
                    abandono_por_segmento.sort_values().plot(kind='barh', ax=ax, color='#ff6666')
                    ax.set_title(f'Tasa de Abandono por {var_segmentacion}')
                    ax.set_xlabel('Tasa de Abandono (%)')
                    st.pyplot(fig)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("""
**🎓 Sistema de Predicción de Abandono Estudiantil**

Desarrollado para el Instituto Tecnológico Beltrán

📧 Contacto: soporte@institutobeltran.edu
""")

# Información adicional en el sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Consejos de uso:")
st.sidebar.markdown("""
1. **Comienza** cargando tus datos en Análisis Exploratorio
2. **Entrena** el modelo con diferentes parámetros
3. **Realiza predicciones** individuales o por lote
4. **Exporta** los resultados para su análisis
""")

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-medium {
        color: #ffa500;
        font-weight: bold;
    }
    .risk-low {
        color: #00cc96;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)