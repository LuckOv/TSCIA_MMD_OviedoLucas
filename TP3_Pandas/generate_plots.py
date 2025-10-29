import pandas as pd
import matplotlib.pyplot as plt
import itertools
import matplotlib.ticker as mtick

# Cargar datos
productos = pd.read_csv('productos.csv')
rubros = pd.read_csv('rubros.csv')
clientes = pd.read_csv('clientes.csv')
facturas_encabezados = pd.read_csv('facturas_encabezados_simulados.csv')
facturas_detalles = pd.read_csv('facturas_detalles_simulados.csv')
ventas = pd.read_csv('ventas_simuladas.csv')

# Unificar datos
ventas_clientes = pd.merge(ventas, facturas_encabezados, on='id_factura', how='left')
ventas_clientes = pd.merge(ventas_clientes, clientes, on='id_cliente', how='left')
ventas_clientes = ventas_clientes.rename(columns={'nombre': 'nombre_cliente', 'monto': 'total_venta'})

# Plot 1: Ranking de clientes
ranking_clientes = ventas_clientes.groupby('nombre_cliente')['total_venta'].sum().reset_index()
ranking_clientes = ranking_clientes.sort_values(by='total_venta', ascending=False)
num_clientes = len(ranking_clientes)
base_colors = plt.cm.tab20.colors
colors = list(itertools.islice(itertools.cycle(base_colors), num_clientes))
plt.figure(figsize=(14, 6))
plt.bar(ranking_clientes['nombre_cliente'], ranking_clientes['total_venta'], color=colors)
plt.xticks(rotation=45, ha='right')
plt.ylabel('Total de Ventas ($)')
plt.title('Ranking de Clientes por Total de Ventas')
formatter = mtick.StrMethodFormatter('${x:,.0f}')
plt.gca().yaxis.set_major_formatter(formatter)
plt.tight_layout()
plt.savefig('ranking_clientes.png')
plt.close()

# Plot 2: Ventas mensuales
ventas_clientes['fecha'] = pd.to_datetime(ventas_clientes['fecha'], format='%d/%m/%Y')
ventas_por_mes = ventas_clientes.groupby(ventas_clientes['fecha'].dt.to_period('M'))['total_venta'].sum().reset_index(name='total_venta')
ventas_por_mes.set_index('fecha', inplace=True)
ventas_por_mes['total_venta'].plot(kind='line', figsize=(10,5))
plt.title('Ventas mensuales')
plt.ylabel('Total Facturado (ARS)')
plt.grid(True)
formatter = mtick.StrMethodFormatter('${x:,.0f}')
plt.gca().yaxis.set_major_formatter(formatter)
plt.savefig('ventas_mensuales.png')
plt.close()

# Plot 3: Ventas semanales septiembre
septiembre_ventas = ventas_clientes[ventas_clientes['fecha'].dt.month == 9].copy()
ventas_semanales_septiembre = septiembre_ventas.groupby(septiembre_ventas['fecha'].dt.isocalendar().week)['total_venta'].sum().reset_index()
plt.figure(figsize=(10, 6))
plt.plot(ventas_semanales_septiembre['week'], ventas_semanales_septiembre['total_venta'], marker='o', linestyle='-')
plt.xlabel('Semana de Septiembre')
plt.ylabel('Total de Ventas (ARS)')
plt.title('Ventas Semanales en Septiembre')
plt.grid(True)
plt.xticks(ventas_semanales_septiembre['week'])
formatter = mtick.StrMethodFormatter('${x:,.0f}')
plt.gca().yaxis.set_major_formatter(formatter)
plt.tight_layout()
plt.savefig('ventas_semanales_septiembre.png')
plt.close()

# Plot 4: Ventas por rubro (pie chart)
detalle_rubro = pd.merge(facturas_detalles, productos, on='id_producto')
detalle_rubro = pd.merge(detalle_rubro, rubros, on='id_rubro')
detalle_rubro['importe'] = detalle_rubro['cantidad'] * detalle_rubro['precio']
ventas_por_rubro_importe = detalle_rubro.groupby('nombre_rubro')['importe'].sum().reset_index()
plt.figure(figsize=(8, 8))
plt.pie(ventas_por_rubro_importe['importe'], labels=ventas_por_rubro_importe['nombre_rubro'], autopct='%1.1f%%', startangle=140)
plt.title('Porcentaje de Ventas por Rubro')
plt.axis('equal')
plt.savefig('ventas_por_rubro.png')
plt.close()

# Plot 5: Ranking productos
detalle_con_precio = pd.merge(facturas_detalles, productos, on='id_producto')
detalle_con_precio['importe'] = detalle_con_precio['cantidad'] * detalle_con_precio['precio']
ranking_productos = detalle_con_precio.groupby('descripcion')['importe'].sum().reset_index()
ranking_productos = ranking_productos.sort_values(by='importe', ascending=False)
num_productos = len(ranking_productos)
colors = list(itertools.islice(itertools.cycle(base_colors), num_productos))
plt.figure(figsize=(14, 7))
plt.bar(ranking_productos['descripcion'], ranking_productos['importe'], color=colors)
plt.xticks(rotation=90, ha='right')
plt.xlabel('Producto')
plt.ylabel('Total Facturado (ARS)')
plt.title('Ranking de Productos por Total Facturado')
plt.grid(axis='y')
formatter = mtick.StrMethodFormatter('${x:,.0f}')
plt.gca().yaxis.set_major_formatter(formatter)
plt.tight_layout()
plt.savefig('ranking_productos.png')
plt.close()

# Plot 6: Matriz BCG
detalle = pd.merge(facturas_detalles, productos, on='id_producto')
detalle = pd.merge(detalle, facturas_encabezados[['id_factura', 'fecha']], left_on='id_facturaENC', right_on='id_factura', how='left')
detalle = detalle.drop(columns=['id_factura'])
detalle['fecha'] = pd.to_datetime(detalle['fecha'], format='%d/%m/%Y')
detalle['mes'] = detalle['fecha'].dt.to_period('M')
detalle['importe'] = detalle['cantidad'] * detalle['precio_unitario']
ingresos_mes = detalle.groupby(['descripcion', 'mes'])['importe'].sum().reset_index()
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
plt.figure(figsize=(12, 7))
for quadrant, color in zip(pivot['cuadrante'].unique(), pivot['color'].unique()):
    subset = pivot[pivot['cuadrante'] == quadrant]
    plt.scatter(subset['crecimiento'] * 100, subset['ingresos_totales'] / 1_000_000, s=300, alpha=0.7, color=color, label=quadrant)
for i, producto in enumerate(pivot.index):
    plt.text(pivot['crecimiento'].iloc[i] * 100, pivot['ingresos_totales'].iloc[i] / 1_000_000, producto, fontsize=8, ha='center')
plt.axhline(y=avg_income / 1_000_000, color='gray', linestyle='--')
plt.axvline(x=avg_growth * 100, color='gray', linestyle='--')
plt.text(avg_growth * 100, (pivot['ingresos_totales'].max() + avg_income) / 2 / 1_000_000, 'Estrellas', fontsize=12, ha='left', va='center', color='green')
plt.text(avg_growth * 100, (pivot['ingresos_totales'].min() + avg_income) / 2 / 1_000_000, 'Interrogantes', fontsize=12, ha='left', va='center', color='orange')
plt.text((pivot['crecimiento'].max() + avg_growth) / 2 * 100, avg_income / 1_000_000, 'Vacas Lecheras', fontsize=12, ha='center', va='bottom', color='blue')
plt.text((pivot['crecimiento'].min() + avg_growth) / 2 * 100, avg_income / 1_000_000, 'Perros', fontsize=12, ha='center', va='bottom', color='red')
plt.xlabel('Crecimiento mensual (%)')
plt.ylabel('Ingresos totales (millones $)')
plt.title('Matriz BCG por Producto')
plt.grid(True)
plt.legend(title='Cuadrante')
plt.tight_layout()
plt.savefig('matriz_bcg.png')
plt.close()

print("Plots generated successfully!")