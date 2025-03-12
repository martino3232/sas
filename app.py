from flask import Flask, request, render_template, send_file, jsonify
import pandas as pd
import time
import random
import threading
import os

app = Flask(__name__, template_folder="templates")

# Obtener el directorio donde está `app.py`
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Definir rutas de archivos usando `BASE_DIR`
file_path = os.path.join(BASE_DIR, "CABA_Enriquecido.xlsx")
output_path = os.path.join(BASE_DIR, "CABA_Resultado_Sin_Index.xlsx")

# Listas de nombres argentinos y parentescos
nombres_argentinos = [
    "Juan", "María", "Carlos", "Sofía", "Martín", "Lucía", "Joaquín", "Valentina",
    "Gonzalo", "Camila", "Federico", "Florencia", "Leandro", "Agustina"
]
parentescos = ["HIJO/A", "CÓNYUGE", "SOBRINO/A", "PADRE/MADRE", "TÍO/A", "PRIMO/A"]

# Función para obtener el apellido (primer elemento del nombre)
def get_apellido(nombre):
    if pd.notna(nombre) and isinstance(nombre, str):
        return nombre.split()[0]  # Tomamos el primer elemento del nombre como apellido
    return "Pérez"  # Default si no hay nombre

# Función para generar el Excel
def generar_excel(user_number):
    print("🟢 Iniciando generación de archivo...")

    # Verificar que el archivo original existe
    if not os.path.exists(file_path):
        print("🔴 ERROR: El archivo de entrada no existe en el servidor.")
        return

    print("🟢 Cargando archivo de entrada...")

    try:
        df = pd.read_excel(file_path)

        # Verificar que haya suficientes filas para tomar 4000
        n_rows = min(4000, len(df))
        df_sampled = df.sample(n=n_rows, random_state=random.randint(1, 10000))

        # **Tomamos la primera columna como nombres**
        col_nombre = df_sampled.columns[0]  # Primera columna es el nombre
        print(f"🟢 Usando la columna '{col_nombre}' para generar apellidos.")

        # **Agregar las columnas de familiares**
        df_sampled["Familiar 1"] = [random.choice(parentescos) for _ in range(n_rows)]
        df_sampled["Nombre 1"] = [random.choice(nombres_argentinos) + " " + get_apellido(nombre) for nombre in df_sampled[col_nombre]]
        df_sampled["Familiar 2"] = [random.choice(parentescos) for _ in range(n_rows)]
        df_sampled["Nombre 2"] = [random.choice(nombres_argentinos) + " " + get_apellido(nombre) for nombre in df_sampled[col_nombre]]

        # Verificar que las columnas nuevas se agregaron
        print(f"📊 Columnas después de agregar familiares: {df_sampled.columns.tolist()}")

        # Guardar el archivo
        df_sampled.to_excel(output_path, index=False)

        print(f"✅ Archivo generado correctamente en: {output_path}")

    except Exception as e:
        print(f"🔴 ERROR al generar el archivo: {e}")

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para iniciar el procesamiento
@app.route('/procesar', methods=['POST'])
def procesar():
    user_number = request.form.get('numero')

    if not user_number or not user_number.isdigit() or not (1000000 <= int(user_number) <= 99999999):
        return jsonify({"error": "Debe ingresar un número válido de 7 u 8 cifras."})

    print(f"🟢 Proceso iniciado por el usuario: {user_number}")

    # Ejecutar la generación del archivo en un hilo separado
    thread = threading.Thread(target=generar_excel, args=(int(user_number),), daemon=True)
    thread.start()

    return jsonify({"message": "Proceso iniciado. Espere 3:00 hs mientras se genera el archivo.", "success": True})

# Ruta para descargar el archivo
@app.route('/descargar')
def descargar():
    print(f"🔍 Intentando descargar desde: {output_path}")

    if not os.path.exists(output_path):
        print("🔴 ERROR: Archivo no encontrado al intentar descargar.")
        return jsonify({"error": "El archivo no existe. Intente generar el archivo primero."}), 404
    
    print("🟢 Enviando archivo para descarga...")
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
