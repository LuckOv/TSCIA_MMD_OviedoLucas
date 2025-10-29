# main.py
from funcionesCSV_v3 import (
    csv_a_diccionarios, agregar_registro, borrar_por_indice, modificar_interactivo,
    json_a_diccionarios, agregar_registro_json, borrar_por_indice_json, modificar_interactivo_json
)
import os
import csv
import json

def determinar_formato(archivo):
    """Determina si el archivo es CSV o JSON por su extensión"""
    if archivo.lower().endswith('.json'):
        return 'json'
    elif archivo.lower().endswith('.csv'):
        return 'csv'
    else:
        return None

def mostrar_menu(archivos_cargados):
    """Muestra el menú principal actualizado"""
    print("\n" + "="*50)
    print("GESTOR DE ARCHIVOS CSV/JSON")
    print("="*50)
    if archivos_cargados:
        print("Archivos cargados:")
        for i, (archivo, formato) in enumerate(archivos_cargados.items(), 1):
            print(f"  {i}. {archivo} ({formato.upper()})")
    else:
        print("Archivos cargados: Ninguno")
    print("="*50)
    print("1. Cargar archivos (CSV/JSON)")
    print("2. Leer y mostrar registros")
    print("3. Agregar nuevo registro")
    print("4. Borrar registro")
    print("5. Modificar registro")
    print("6. Salir")
    print("="*50)

def mostrar_registros_como_tabla(registros, archivo):
    """Muestra los registros como una tabla en la terminal"""
    if not registros:
        print(f"No hay registros en '{archivo}'")
        return

    # Obtener las claves (columnas) del primer registro
    if registros:
        columnas = list(registros[0].keys())
    else:
        return

    # Calcular anchos de columna
    anchos = {}
    for col in columnas:
        anchos[col] = max(len(col), max(len(str(registro.get(col, ''))) for registro in registros))

    # Función para imprimir línea separadora
    def imprimir_linea():
        print("+" + "+".join("-" * (anchos[col] + 2) for col in columnas) + "+")

    # Imprimir encabezado
    imprimir_linea()
    print("|" + "|".join(f" {col:<{anchos[col]}} " for col in columnas) + "|")
    imprimir_linea()

    # Imprimir registros
    for registro in registros:
        fila = "|" + "|".join(f" {str(registro.get(col, '')):<{anchos[col]}} " for col in columnas) + "|"
        print(fila)

    imprimir_linea()
    print(f"Total de registros: {len(registros)}")

def pedir_datos_registro(campos, archivo_actual, localidades_data=None):
    """Pide los datos para un nuevo registro basado en los campos del archivo"""
    print(f"\nIngrese los datos del nuevo registro:")
    registro = {}

    # Cargar localidades si es necesario
    if localidades_data is None and 'id_localidad' in campos:
        localidades_data = csv_a_diccionarios('localidades.csv')

    for campo in campos:
        if campo.lower().startswith('id_') and campo != 'id_localidad':
            # Asignar ID automáticamente usando len() + 1
            registros_existentes = csv_a_diccionarios(archivo_actual) if os.path.exists(archivo_actual) else []
            nuevo_id = len(registros_existentes) + 1
            registro[campo] = str(nuevo_id)
            print(f"{campo}: {nuevo_id} (asignado automáticamente)")
        elif campo == 'id_localidad' and localidades_data:
            # Seleccionar localidad por nombre
            registro[campo] = seleccionar_localidad(localidades_data)
        else:
            valor = input(f"{campo}: ").strip()
            registro[campo] = valor

    return registro

def seleccionar_localidad(localidades_data):
    """Permite seleccionar una localidad por nombre y retorna su ID"""
    print("\nSeleccione una localidad:")
    for i, loc in enumerate(localidades_data, 1):
        print(f"{i}. {loc['nombre_localidad']} (ID: {loc['id_localidad']})")

    while True:
        try:
            opcion = int(input("\nIngrese el número de la localidad: "))
            if 1 <= opcion <= len(localidades_data):
                localidad_seleccionada = localidades_data[opcion - 1]
                print(f"Seleccionada: {localidad_seleccionada['nombre_localidad']}")
                return localidad_seleccionada['id_localidad']
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingrese un número válido")

def obtener_campos_desde_archivo(archivo, formato):
    """Obtiene los campos (encabezados) de un archivo existente"""
    try:
        if formato == 'csv':
            with open(archivo, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return reader.fieldnames
        else:  # json
            datos = json_a_diccionarios(archivo)
            if datos and len(datos) > 0:
                return list(datos[0].keys())
            return None
    except:
        return None

def cargar_archivos():
    """Permite al usuario cargar múltiples archivos CSV o JSON"""
    print("\n📁 CARGAR ARCHIVOS CSV/JSON")
    print("Ingrese los nombres de los archivos separados por coma")
    print("Ejemplo: clientes.csv, productos.csv, localidades.csv")

    archivos_input = input("Archivos: ").strip()

    if not archivos_input:
        print("No se ingresaron archivos")
        return {}

    nombres_archivos = [nombre.strip() for nombre in archivos_input.split(',')]
    archivos_cargados = {}

    for archivo in nombres_archivos:
        formato = determinar_formato(archivo)
        if formato is None:
            print(f"Formato no soportado para '{archivo}'. Use .csv o .json")
            continue

        if not os.path.exists(archivo):
            crear = input(f"El archivo '{archivo}' no existe. ¿Crearlo? (s/n): ").strip().lower()
            if crear == 's':
                try:
                    with open(archivo, 'w', encoding='utf-8') as f:
                        if formato == 'json':
                            json.dump([], f)
                        # Para CSV se crea vacío
                    print(f"Archivo '{archivo}' creado exitosamente")
                    archivos_cargados[archivo] = formato
                except Exception as e:
                    print(f"Error al crear archivo '{archivo}': {e}")
            else:
                print(f"Archivo '{archivo}' omitido")
        else:
            print(f"Archivo '{archivo}' cargado exitosamente")
            archivos_cargados[archivo] = formato

    return archivos_cargados

def verificar_archivos_cargados(archivos_cargados):
    """Verifica si hay archivos cargados"""
    if not archivos_cargados:
        print("\n❌ Error: Primero debe cargar archivos (Opción 1)")
        return False, None
    return True, archivos_cargados

def seleccionar_archivo(archivos_cargados, operacion):
    """Permite al usuario seleccionar un archivo de los cargados"""
    if len(archivos_cargados) == 1:
        archivo_seleccionado = list(archivos_cargados.keys())[0]
        formato_seleccionado = archivos_cargados[archivo_seleccionado]
        print(f"Archivo seleccionado automáticamente: {archivo_seleccionado}")
        return archivo_seleccionado, formato_seleccionado

    print(f"\nSeleccione el archivo para {operacion}:")
    for i, (archivo, formato) in enumerate(archivos_cargados.items(), 1):
        print(f"{i}. {archivo} ({formato.upper()})")

    while True:
        try:
            opcion = int(input("\nIngrese el número del archivo: "))
            if 1 <= opcion <= len(archivos_cargados):
                archivo_seleccionado = list(archivos_cargados.keys())[opcion - 1]
                formato_seleccionado = archivos_cargados[archivo_seleccionado]
                print(f"Seleccionado: {archivo_seleccionado}")
                return archivo_seleccionado, formato_seleccionado
            else:
                print("Opción inválida")
        except ValueError:
            print("Por favor ingrese un número válido")

def opciones_guardado():
    """Permite elegir entre sobrescribir o crear nuevo archivo"""
    print("\nOpciones de guardado:")
    print("1. Sobrescribir archivo actual")
    print("2. Crear nuevo archivo")

    while True:
        try:
            opcion = input("Seleccione opción (1-2): ").strip()
            if opcion == "1":
                return "sobrescribir"
            elif opcion == "2":
                nuevo_nombre = input("Ingrese el nombre del nuevo archivo: ").strip()
                return "nuevo", nuevo_nombre
            else:
                print("Opción inválida")
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Función principal actualizada"""
    archivos_cargados = {}

    while True:
        mostrar_menu(archivos_cargados)

        try:
            opcion = input("\nSeleccione una opción (1-6): ").strip()

            match opcion:
                case "1":
                    nuevos_archivos = cargar_archivos()
                    archivos_cargados.update(nuevos_archivos)

                case "2":
                    ok, _ = verificar_archivos_cargados(archivos_cargados)
                    if not ok:
                        continue

                    archivo_actual, formato_actual = seleccionar_archivo(archivos_cargados, "mostrar registros")

                    print(f"\n Leyendo archivo '{archivo_actual}'...")
                    try:
                        if formato_actual == 'csv':
                            registros = csv_a_diccionarios(archivo_actual)
                        else:  # json
                            registros = json_a_diccionarios(archivo_actual)
                        mostrar_registros_como_tabla(registros, archivo_actual)
                    except Exception as e:
                        print(f" Error al leer el archivo: {e}")

                case "3":
                    ok, _ = verificar_archivos_cargados(archivos_cargados)
                    if not ok:
                        continue

                    archivo_actual, formato_actual = seleccionar_archivo(archivos_cargados, "agregar registro")

                    print(f"\n AGREGAR NUEVO REGISTRO A '{archivo_actual}'")
                    try:
                        campos = obtener_campos_desde_archivo(archivo_actual, formato_actual)
                        if campos is None:
                            campos_input = input("Ingrese los nombres de los campos separados por coma: ").strip()
                            campos = [campo.strip() for campo in campos_input.split(',')]

                        # Cargar localidades si es necesario
                        localidades_data = None
                        if 'id_localidad' in campos:
                            localidades_data = csv_a_diccionarios('localidades.csv')

                        datos_registro = pedir_datos_registro(campos, archivo_actual, localidades_data)

                        # Elegir opción de guardado
                        opcion_guardado = opciones_guardado()

                        if opcion_guardado == "sobrescribir":
                            archivo_destino = archivo_actual
                        else:
                            archivo_destino = opcion_guardado[1]
                            # Determinar formato del nuevo archivo
                            formato_destino = determinar_formato(archivo_destino)
                            if formato_destino != formato_actual:
                                print("El formato del nuevo archivo debe ser el mismo que el original")
                                continue
                            # Copiar archivo original al nuevo
                            import shutil
                            shutil.copy2(archivo_actual, archivo_destino)

                        if formato_actual == 'csv':
                            if all(datos_registro.values()):
                                agregar_registro(archivo_destino, datos_registro)
                            else:
                                print(" Todos los campos son obligatorios")
                        else:  # json
                            agregar_registro_json(archivo_destino, datos_registro)
                    except Exception as e:
                        print(f" Error al agregar registro: {e}")

                case "4":
                    ok, _ = verificar_archivos_cargados(archivos_cargados)
                    if not ok:
                        continue

                    archivo_actual, formato_actual = seleccionar_archivo(archivos_cargados, "borrar registro")

                    print(f"\n BORRAR REGISTRO DE '{archivo_actual}'")
                    try:
                        if formato_actual == 'csv':
                            registros = csv_a_diccionarios(archivo_actual)
                        else:
                            registros = json_a_diccionarios(archivo_actual)

                        if not registros:
                            print(" No hay registros para borrar")
                            continue

                        mostrar_registros_como_tabla(registros, archivo_actual)

                        try:
                            indice = int(input("\nIngrese el número del registro a borrar (1, 2, 3...): ")) - 1

                            if 0 <= indice < len(registros):
                                registro_a_borrar = registros[indice]
                                print(f"\nRegistro seleccionado para borrar:")
                                for campo, valor in registro_a_borrar.items():
                                    print(f"  {campo}: {valor}")

                                confirmacion = input("¿Está seguro de borrar este registro? (s/n): ").strip().lower()

                                if confirmacion == 's':
                                    # Elegir opción de guardado
                                    opcion_guardado = opciones_guardado()

                                    if opcion_guardado == "sobrescribir":
                                        archivo_destino = archivo_actual
                                    else:
                                        archivo_destino = opcion_guardado[1]
                                        # Copiar archivo original al nuevo
                                        import shutil
                                        shutil.copy2(archivo_actual, archivo_destino)

                                    if formato_actual == 'csv':
                                        borrados = borrar_por_indice(archivo_destino, indice)
                                    else:
                                        borrados = borrar_por_indice_json(archivo_destino, indice)
                                    print(f" Se borró {borrados} registro(s)")
                                else:
                                    print(" Operación cancelada")
                            else:
                                print(" Número de registro inválido")
                        except ValueError:
                            print(" Por favor ingrese un número válido")
                    except Exception as e:
                        print(f" Error al borrar registro: {e}")

                case "5":
                    ok, _ = verificar_archivos_cargados(archivos_cargados)
                    if not ok:
                        continue

                    archivo_actual, formato_actual = seleccionar_archivo(archivos_cargados, "modificar registro")

                    print(f"\n MODIFICAR REGISTRO EN '{archivo_actual}'")
                    try:
                        # Elegir opción de guardado primero
                        opcion_guardado = opciones_guardado()

                        if opcion_guardado == "sobrescribir":
                            archivo_destino = archivo_actual
                        else:
                            archivo_destino = opcion_guardado[1]
                            # Copiar archivo original al nuevo
                            import shutil
                            shutil.copy2(archivo_actual, archivo_destino)

                        if formato_actual == 'csv':
                            modificar_interactivo(archivo_destino)
                        else:
                            modificar_interactivo_json(archivo_destino)
                    except Exception as e:
                        print(f" Error al modificar registro: {e}")

                case "6":
                    print("\n ¡Gracias por usar el sistema! ¡Hasta pronto!")
                    break

                case _:
                    print(" Opción no válida. Por favor, seleccione 1-6.")

        except KeyboardInterrupt:
            print("\n\n Programa interrumpido por el usuario")
            break
        except Exception as e:
            print(f" Error inesperado: {e}")

if __name__ == "__main__":
    main()