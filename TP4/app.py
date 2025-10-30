import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import itertools
import io
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import base64

# Set pandas option for float format
pd.set_option('display.float_format', '{:,.2f}'.format)

# Function to load data
def load_data(productos, rubros, clientes, facturas_encabezados, facturas_detalles, ventas):
    # Merge data as in notebook
    ventas_clientes = pd.merge(ventas, facturas_encabezados, on='id_factura', how='left')
    ventas_clientes = pd.merge(ventas_clientes, clientes, on='id_cliente', how='left')
    ventas_clientes = ventas_clientes.rename(columns={'nombre': 'nombre_cliente', 'monto': 'total_venta'})

    # Convert fecha
    ventas_clientes['fecha'] = pd.to_datetime(ventas_clientes['fecha'], format='%d/%m/%Y')

    # Merge detalles with productos
    detalle = pd.merge(facturas_detalles, productos, on='id_producto')
    detalle['importe'] = detalle['cantidad'] * detalle['precio']

    return ventas_clientes, detalle

# Function for ranking clientes
def plot_ranking_clientes(ventas_clientes):
    ranking_clientes = ventas_clientes.groupby('nombre_cliente')['total_venta'].sum().reset_index()
    ranking_clientes = ranking_clientes.sort_values(by='total_venta', ascending=False)

    num_clientes = len(ranking_clientes)
    base_colors = plt.cm.tab20.colors
    colors = list(itertools.islice(itertools.cycle(base_colors), num_clientes))

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(ranking_clientes['nombre_cliente'], ranking_clientes['total_venta'], color=colors)
    ax.set_xticklabels(ranking_clientes['nombre_cliente'], rotation=45, ha='right')
    ax.set_ylabel('Total de Ventas ($)')
    ax.set_title('Ranking de Clientes por Total de Ventas')

    formatter = mtick.StrMethodFormatter('${x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)

    return fig

# Function for ventas mensuales
def plot_ventas_mensuales(ventas_clientes):
    ventas_por_mes = ventas_clientes.groupby(ventas_clientes['fecha'].dt.to_period('M'))['total_venta'].sum().reset_index(name='total_venta')
    ventas_por_mes.set_index('fecha', inplace=True)

    fig, ax = plt.subplots(figsize=(10, 5))
    ventas_por_mes['total_venta'].plot(kind='line', ax=ax)
    ax.set_title('Ventas mensuales')
    ax.set_ylabel('Total Facturado (ARS)')
    ax.grid(True)

    formatter = mtick.StrMethodFormatter('${x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)

    return fig

# Function for ventas semanales septiembre
def plot_ventas_semanales_septiembre(ventas_clientes):
    septiembre_ventas = ventas_clientes[ventas_clientes['fecha'].dt.month == 9].copy()
    ventas_semanales_septiembre = septiembre_ventas.groupby(septiembre_ventas['fecha'].dt.isocalendar().week)['total_venta'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ventas_semanales_septiembre['week'], ventas_semanales_septiembre['total_venta'], marker='o', linestyle='-')
    ax.set_xlabel('Semana de Septiembre')
    ax.set_ylabel('Total de Ventas (ARS)')
    ax.set_title('Ventas Semanales en Septiembre')
    ax.grid(True)
    ax.set_xticks(ventas_semanales_septiembre['week'])

    formatter = mtick.StrMethodFormatter('${x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)

    return fig

# Function for ventas por rubro
def plot_ventas_por_rubro(detalle, rubros):
    detalle_rubro = pd.merge(detalle, rubros, on='id_rubro')
    ventas_por_rubro_importe = detalle_rubro.groupby('nombre_rubro')['importe'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(ventas_por_rubro_importe['importe'], labels=ventas_por_rubro_importe['nombre_rubro'], autopct='%1.1f%%', startangle=140)
    ax.set_title('Porcentaje de Ventas por Rubro')
    ax.axis('equal')

    return fig

# Function for ranking productos
def plot_ranking_productos(detalle):
    ranking_productos = detalle.groupby('descripcion')['importe'].sum().reset_index()
    ranking_productos = ranking_productos.sort_values(by='importe', ascending=False)

    num_productos = len(ranking_productos)
    base_colors = plt.cm.tab20.colors
    colors = list(itertools.islice(itertools.cycle(base_colors), num_productos))

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(ranking_productos['descripcion'], ranking_productos['importe'], color=colors)
    ax.set_xticklabels(ranking_productos['descripcion'], rotation=90, ha='right')
    ax.set_xlabel('Producto')
    ax.set_ylabel('Total Facturado (ARS)')
    ax.set_title('Ranking de Productos por Total Facturado')
    ax.grid(axis='y')

    formatter = mtick.StrMethodFormatter('${x:,.0f}')
    ax.yaxis.set_major_formatter(formatter)

    return fig

# Function for BCG matrix
def plot_bcg_matrix(detalle, facturas_encabezados):
    detalle_bcg = pd.merge(detalle, facturas_encabezados[['id_factura', 'fecha']], left_on='id_facturaENC', right_on='id_factura', how='left')
    detalle_bcg = detalle_bcg.drop(columns=['id_factura'])  # Drop redundant
    detalle_bcg['fecha'] = pd.to_datetime(detalle_bcg['fecha'], format='%d/%m/%Y')
    detalle_bcg['mes'] = detalle_bcg['fecha'].dt.to_period('M')

    ingresos_mes = detalle_bcg.groupby(['descripcion', 'mes'])['importe'].sum().reset_index()
    pivot = ingresos_mes.pivot(index='descripcion', columns='mes', values='importe').fillna(0)
    pivot.columns = pivot.columns.astype(str)

    pivot['ingresos_totales'] = pivot.sum(axis=1)
    pivot['crecimiento'] = 0.0

    for index, row in pivot.iterrows():
        monthly_sales = row.drop('ingresos_totales')
        monthly_sales = monthly_sales[monthly_sales > 0]
        if len(monthly_sales) >= 2:
            last_month_sales = monthly_sales.iloc[-1]
            second_last_month_sales = monthly_sales.iloc[-2]
            pivot.loc[index, 'crecimiento'] = last_month_sales / (second_last_month_sales + 1e-6) - 1

    avg_income = pivot['ingresos_totales'].mean()
    avg_growth = pivot['crecimiento'].mean()

    def assign_quadrant(row):
        if row['crecimiento'] > avg_growth and row['ingresos_totales'] > avg_income:
            return 'Estrellas', 'green'
        elif row['crecimiento'] <= avg_growth and row['ingresos_totales'] > avg_income:
            return 'Vacas Lecheras', 'blue'
        elif row['crecimiento'] > avg_growth and row['ingresos_totales'] <= avg_income:
            return 'Interrogantes', 'orange'
        else:
            return 'Perros', 'red'

    pivot[['cuadrante', 'color']] = pivot.apply(assign_quadrant, axis=1, result_type='expand')

    fig, ax = plt.subplots(figsize=(12, 7))
    for quadrant, color in zip(pivot['cuadrante'].unique(), pivot['color'].unique()):
        subset = pivot[pivot['cuadrante'] == quadrant]
        ax.scatter(subset['crecimiento'] * 100, subset['ingresos_totales'] / 1_000_000, s=300, alpha=0.7, color=color, label=quadrant)

    for i, producto in enumerate(pivot.index):
        ax.text(pivot['crecimiento'].iloc[i] * 100, pivot['ingresos_totales'].iloc[i] / 1_000_000, producto, fontsize=8, ha='center')

    ax.axhline(y=avg_income / 1_000_000, color='gray', linestyle='--')
    ax.axvline(x=avg_growth * 100, color='gray', linestyle='--')

    ax.text(avg_growth * 100, (pivot['ingresos_totales'].max() + avg_income) / 2 / 1_000_000, 'Estrellas', fontsize=12, ha='left', va='center', color='green')
    ax.text(avg_growth * 100, (pivot['ingresos_totales'].min() + avg_income) / 2 / 1_000_000, 'Interrogantes', fontsize=12, ha='left', va='center', color='orange')
    ax.text((pivot['crecimiento'].max() + avg_growth) / 2 * 100, avg_income / 1_000_000, 'Vacas Lecheras', fontsize=12, ha='center', va='bottom', color='blue')
    ax.text((pivot['crecimiento'].min() + avg_growth) / 2 * 100, avg_income / 1_000_000, 'Perros', fontsize=12, ha='center', va='bottom', color='red')

    ax.set_xlabel('Crecimiento mensual (%)')
    ax.set_ylabel('Ingresos totales (millones $)')
    ax.set_title('Matriz BCG por Producto')
    ax.grid(True)
    ax.legend(title='Cuadrante')

    return fig

# Function to generate CSV
def generate_csv(data, filename):
    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

# Function to generate JSON
def generate_json(data, filename):
    json_str = data.to_json(orient='records')
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

# Function to generate PDF with all plots
def generate_pdf_report(filtered_ventas, filtered_detalle, rubros, facturas_encabezados, months, rubro, cliente, filename):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Informe de Ventas", styles['Title']))
    story.append(Spacer(1, 12))

    # Summary stats
    total_ventas = filtered_ventas['total_venta'].sum()
    story.append(Paragraph(f"Total de Ventas: ${total_ventas:,.2f}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Ranking clientes
    ranking_clientes = filtered_ventas.groupby('nombre_cliente')['total_venta'].sum().reset_index().sort_values(by='total_venta', ascending=False).head(5)
    story.append(Paragraph("Top 5 Clientes:", styles['Heading2']))
    for _, row in ranking_clientes.iterrows():
        story.append(Paragraph(f"{row['nombre_cliente']}: ${row['total_venta']:,.2f}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Ranking productos
    ranking_productos = filtered_detalle.groupby('descripcion')['importe'].sum().reset_index().sort_values(by='importe', ascending=False).head(5)
    story.append(Paragraph("Top 5 Productos:", styles['Heading2']))
    for _, row in ranking_productos.iterrows():
        story.append(Paragraph(f"{row['descripcion']}: ${row['importe']:,.2f}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Add all plots
    plots = [
        ("Ranking de Clientes por Total de Ventas", plot_ranking_clientes, [filtered_ventas]),
        ("Ventas Mensuales", plot_ventas_mensuales, [filtered_ventas]),
    ]

    if 9 in months:
        plots.append(("Ventas Semanales en Septiembre", plot_ventas_semanales_septiembre, [filtered_ventas]))

    plots.extend([
        ("Porcentaje de Ventas por Rubro", plot_ventas_por_rubro, [filtered_detalle, rubros]),
        ("Ranking de Productos por Total Facturado", plot_ranking_productos, [filtered_detalle]),
        ("Matriz BCG por Producto", plot_bcg_matrix, [filtered_detalle, facturas_encabezados])
    ])

    for title, plot_func, args in plots:
        story.append(Paragraph(title, styles['Heading2']))
        story.append(Spacer(1, 6))  # Reduce space
        fig = plot_func(*args)
        img_buffer = io.BytesIO()
        fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
        img_buffer.seek(0)
        img_data = img_buffer.getvalue()
        img = Image(io.BytesIO(img_data), width=350, height=250)  # Smaller size
        story.append(img)
        story.append(Spacer(1, 6))  # Reduce space
        plt.close(fig)

    if cliente:
        # Add client historical plot
        cliente_data = filtered_ventas[filtered_ventas['nombre_cliente'] == cliente]
        if not cliente_data.empty:
            cliente_data = cliente_data.groupby(cliente_data['fecha'].dt.to_period('M'))['total_venta'].sum().reset_index()
            cliente_data.set_index('fecha', inplace=True)

            fig = plt.figure(figsize=(8, 6))
            ax = fig.add_subplot(111)
            cliente_data['total_venta'].plot(kind='line', ax=ax, marker='o')
            ax.set_title(f'Histórico de Gasto de {cliente}')
            ax.set_ylabel('Total Gasto (ARS)')
            ax.grid(True)
            formatter = mtick.StrMethodFormatter('${x:,.0f}')
            ax.yaxis.set_major_formatter(formatter)

            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
            img_buffer.seek(0)
            img_data = img_buffer.getvalue()
            img = Image(io.BytesIO(img_data), width=350, height=250)
            story.append(Paragraph(f'Histórico de Gasto de {cliente}', styles['Heading2']))
            story.append(Spacer(1, 6))
            story.append(img)
            story.append(Spacer(1, 6))
            plt.close(fig)

    # If rubro selected, add products table
    if rubro != "Todos":
        story.append(Paragraph(f"Productos del Rubro: {rubro}", styles['Heading2']))
        rubro_id = rubros[rubros['nombre_rubro'] == rubro]['id_rubro'].values[0]
        productos_rubro = productos[productos['id_rubro'] == rubro_id]
        ventas_productos = filtered_detalle.groupby('descripcion')['importe'].sum().reset_index().sort_values(by='importe', ascending=False)
        # Simple table
        data = [['Producto', 'Ventas']] + ventas_productos[['descripcion', 'importe']].values.tolist()
        from reportlab.platypus import Table, TableStyle
        table = Table(data)
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), 'lightgrey'), ('GRID', (0, 0), (-1, -1), 1, 'black')]))
        story.append(table)
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download {filename}</a>'
    return href

# Streamlit app
st.title("Análisis de Ventas - TP3")

st.header("Cargar Datos")
productos_file = st.file_uploader("Cargar productos.csv", type="csv")
rubros_file = st.file_uploader("Cargar rubros.csv", type="csv")
clientes_file = st.file_uploader("Cargar clientes.csv", type="csv")
facturas_encabezados_file = st.file_uploader("Cargar facturas_encabezados_simulados.csv", type="csv")
facturas_detalles_file = st.file_uploader("Cargar facturas_detalles_simulados.csv", type="csv")
ventas_file = st.file_uploader("Cargar ventas_simuladas.csv", type="csv")

if all([productos_file, rubros_file, clientes_file, facturas_encabezados_file, facturas_detalles_file, ventas_file]):
    productos = pd.read_csv(productos_file)
    rubros = pd.read_csv(rubros_file)
    clientes = pd.read_csv(clientes_file)
    facturas_encabezados = pd.read_csv(facturas_encabezados_file)
    facturas_detalles = pd.read_csv(facturas_detalles_file)
    ventas = pd.read_csv(ventas_file)

    ventas_clientes, detalle = load_data(productos, rubros, clientes, facturas_encabezados, facturas_detalles, ventas)

    # Filtros
    st.header("Filtros")
    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.selectbox("Seleccionar Año", options=sorted(ventas_clientes['fecha'].dt.year.unique()), index=0)
    with col2:
        months = st.multiselect("Seleccionar Meses", options=range(1, 13), default=list(range(1, 13)))
    with col3:
        rubro = st.selectbox("Seleccionar Rubro", options=["Todos"] + list(rubros['nombre_rubro'].unique()))

    # Filtrar datos
    filtered_ventas = ventas_clientes[(ventas_clientes['fecha'].dt.year == year) & (ventas_clientes['fecha'].dt.month.isin(months))]
    filtered_detalle = detalle.copy()
    if rubro != "Todos":
        rubro_id = rubros[rubros['nombre_rubro'] == rubro]['id_rubro'].values[0]
        filtered_detalle = filtered_detalle[filtered_detalle['id_rubro'] == rubro_id]

    st.header("Gráficos")

    st.subheader("Ranking de Clientes por Total de Ventas")
    fig1 = plot_ranking_clientes(filtered_ventas)
    st.pyplot(fig1)

    st.subheader("Ventas Mensuales")
    fig2 = plot_ventas_mensuales(filtered_ventas)
    st.pyplot(fig2)

    st.subheader("Ventas Semanales en Septiembre")
    if 9 in months:
        fig3 = plot_ventas_semanales_septiembre(filtered_ventas)
        st.pyplot(fig3)
    else:
        st.info("Septiembre no está seleccionado en los filtros.")

    st.subheader("Porcentaje de Ventas por Rubro")
    fig4 = plot_ventas_por_rubro(filtered_detalle, rubros)
    st.pyplot(fig4)

    st.subheader("Ranking de Productos por Total Facturado")
    fig5 = plot_ranking_productos(filtered_detalle)
    st.pyplot(fig5)

    st.subheader("Matriz BCG por Producto")
    fig6 = plot_bcg_matrix(filtered_detalle, facturas_encabezados)
    st.pyplot(fig6)

    # Productos por rubro
    if rubro != "Todos":
        st.subheader(f"Productos del Rubro: {rubro}")
        productos_rubro = productos[productos['id_rubro'] == rubro_id]
        ventas_productos = filtered_detalle.groupby('descripcion')['importe'].sum().reset_index().sort_values(by='importe', ascending=False)
        st.dataframe(ventas_productos)

    # Histórico de gasto de cliente específico
    st.subheader("Histórico de Gasto de Cliente Específico")
    cliente = st.selectbox("Seleccionar Cliente", options=ventas_clientes['nombre_cliente'].unique())
    if cliente:
        cliente_data = ventas_clientes[ventas_clientes['nombre_cliente'] == cliente]
        cliente_data = cliente_data.groupby(cliente_data['fecha'].dt.to_period('M'))['total_venta'].sum().reset_index()
        cliente_data.set_index('fecha', inplace=True)

        fig, ax = plt.subplots(figsize=(10, 5))
        cliente_data['total_venta'].plot(kind='line', ax=ax, marker='o')
        ax.set_title(f'Histórico de Gasto de {cliente}')
        ax.set_ylabel('Total Gasto (ARS)')
        ax.grid(True)

        formatter = mtick.StrMethodFormatter('${x:,.0f}')
        ax.yaxis.set_major_formatter(formatter)

        st.pyplot(fig)
        cliente_fig = fig

    st.header("Descargas de Informes")

    st.subheader("Descargar Ranking de Clientes (CSV)")
    st.markdown(generate_csv(filtered_ventas.groupby('nombre_cliente')['total_venta'].sum().reset_index().sort_values(by='total_venta', ascending=False), "ranking_clientes.csv"), unsafe_allow_html=True)

    st.subheader("Descargar Ranking de Clientes (JSON)")
    st.markdown(generate_json(filtered_ventas.groupby('nombre_cliente')['total_venta'].sum().reset_index().sort_values(by='total_venta', ascending=False), "ranking_clientes.json"), unsafe_allow_html=True)

    st.subheader("Descargar Ranking de Productos (CSV)")
    st.markdown(generate_csv(filtered_detalle.groupby('descripcion')['importe'].sum().reset_index().sort_values(by='importe', ascending=False), "ranking_productos.csv"), unsafe_allow_html=True)

    st.subheader("Descargar Ranking de Productos (JSON)")
    st.markdown(generate_json(filtered_detalle.groupby('descripcion')['importe'].sum().reset_index().sort_values(by='importe', ascending=False), "ranking_productos.json"), unsafe_allow_html=True)

    st.subheader("Descargar Informe PDF")
    st.markdown(generate_pdf_report(filtered_ventas, filtered_detalle, rubros, facturas_encabezados, months, rubro, cliente, "informe_ventas.pdf"), unsafe_allow_html=True)

else:
    st.info("Por favor, carga todos los archivos CSV para continuar.")