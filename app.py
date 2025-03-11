from flask import Flask, request, render_template, send_file, jsonify
import pandas as pd
import time
import random
import threading
import os

app = Flask(__name__)

# Ruta del archivo de entrada (asegúrate de subirlo en Render)
file_path = "CABA_Enriquecido.xlsx"
output_path = "/tmp/CABA_Resultado_Sin_Index.xlsx"

# Función para generar el Excel
def generar_excel(user_number):
    print("🟢 Iniciando generación de archivo...")
    start_time = time.time()  # Guardamos el tiempo de inicio

    # Simulación de espera (puede tardar más de 10s dependiendo del tamaño del archivo)
    time.sleep(30)  # Ahora esperamos 30 segundos antes de generar el archivo

    if not os.path.exists(file_path):
        print("🔴 ERROR: El archivo de entrada no existe en el servidor.")
        return

    print("🟢 Cargando archivo de entrada...")

    try:
        df = pd.read_excel(file_path)

        # Seleccionar 4000 filas aleatorias del archivo
        df_sampled = df.sample(n=min(4000, len(df)), random_state=random.randint(1, 10000))

        # Listas de nombres argentinos y parentescos
        nombres_argentinos = ["Juan", "María", "Carlos", "Sofía", "Martín", "Lucía"]
        parentescos = ["HIJO/A", "CÓNYUGE", "SOBRINO/A", "PADRE/MADRE", "TÍO/A", "PRIMO/A"]

        # Función para obtener un apellido
        def get_apellido(nombre):
            if pd.notna(nombre):
                return nombre.split()[-1]  # Última palabra como apellido
            return "Pérez"

        # Agregar columnas de familiares
        df_sampled["Familiar 1"] = [random.choice(parentescos) for _ in range(len(df_sampled))]
        df_sampled["Nombre 1"] = [random.choice(nombres_argentinos) + " " + get_apellido(nombre) for nombre in df_sampled.iloc[:, 1]]
        df_sampled["Familiar 2"] = [random.choice(parentescos) for _ in range(len(df_sampled))]
        df_sampled["Nombre 2"] = [random.choice(nombres_argentinos) + " " + get_apellido(nombre) for nombre in df_sampled.iloc[:, 1]]

        # Guardamos en /tmp/
        df_sampled.to_excel(output_path, index=False)

        end_time = time.time()  # Tiempo final
        print(f"✅ Archivo generado en {round(end_time - start_time, 2)} segundos")
        print(f"✅ Archivo guardado en: {output_path}")

    except Exception as e:
        print(f"🔴 ERROR al procesar el archivo: {e}")

# Ruta para iniciar el procesamiento
@app.route('/procesar', methods=['POST'])
def procesar():
    user_number = request.form.get('numero')

    if not user_number or not user_number.isdigit() or not (1000000 <= int(user_number) <= 99999999):
        return jsonify({"error": "Debe ingresar un número válido de 7 u 8 cifras."})

    print(f"🟢 Proceso iniciado por el usuario: {user_number}")

    thread = threading.Thread(target=generar_excel, args=(int(user_number),), daemon=True)
    thread.start()

    return jsonify({"message": "Proceso iniciado. Espere al menos 30 segundos.", "success": True})

# Ruta para descargar el archivo
@app.route('/descargar')
def descargar():
    if not os.path.exists(output_path):
        print("🔴 ERROR: Archivo no encontrado al intentar descargar.")
        return jsonify({"error": "El archivo no existe. Espere unos segundos más y vuelva a intentar."}), 404

    print("🟢 Enviando archivo para descarga...")
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
