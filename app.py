from flask import Flask, request, render_template, send_file, jsonify
import pandas as pd
import time
import random
import threading
import os

app = Flask(__name__)

# Ruta del archivo de entrada (Asegurate de que exista en el servidor)
file_path = "CABA_Enriquecido.xlsx"
output_path = "/tmp/CABA_Resultado_Sin_Index.xlsx"  # Guardamos en /tmp para que persista durante la sesión

# Función para generar el Excel después de 10 segundos
def generar_excel(user_number):
    time.sleep(10)  # Espera 10 segundos

    if not os.path.exists(file_path):
        print("Error: El archivo de entrada no existe.")
        return

    # Cargar el archivo Excel
    df = pd.read_excel(file_path)

    # Seleccionar 4000 filas aleatorias del archivo
    df_sampled = df.sample(n=min(4000, len(df)), random_state=random.randint(1, 10000))

    # Listas de nombres argentinos y parentescos
    nombres_argentinos = [
        "Juan", "María", "Carlos", "Sofía", "Martín", "Lucía", "Joaquín", "Valentina",
        "Gonzalo", "Camila", "Federico", "Florencia", "Leandro", "Agustina"
    ]
    parentescos = ["HIJO/A", "CÓNYUGE", "SOBRINO/A", "PADRE/MADRE", "TÍO/A", "PRIMO/A"]

    # Función para obtener un apellido de la columna "Nombre"
    def get_apellido(nombre):
        if pd.notna(nombre):
            return nombre.split()[-1]  # Tomamos el último elemento del nombre como apellido
        return "Pérez"  # Default si no hay nombre

    # Agregar las nuevas columnas con familiares y nombres aleatorios
    df_sampled["Familiar 1"] = [random.choice(parentescos) for _ in range(len(df_sampled))]
    df_sampled["Nombre 1"] = [random.choice(nombres_argentinos) + " " + get_apellido(nombre) for nombre in df_sampled.iloc[:, 1]]
    df_sampled["Familiar 2"] = [random.choice(parentescos) for _ in range(len(df_sampled))]
    df_sampled["Nombre 2"] = [random.choice(nombres_argentinos) + " " + get_apellido(nombre) for nombre in df_sampled.iloc[:, 1]]

    # Guardar el archivo en /tmp para evitar problemas de almacenamiento en Render
    df_sampled.to_excel(output_path, index=False)
    print("Archivo generado correctamente en:", output_path)

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

    # Ejecutar la generación del archivo en un hilo separado
    thread = threading.Thread(target=generar_excel, args=(int(user_number),))
    thread.start()

    return jsonify({"message": "Proceso iniciado. Espere 10 segundos.", "success": True})

# Ruta para descargar el archivo
@app.route('/descargar')
def descargar():
    if not os.path.exists(output_path):
        return jsonify({"error": "El archivo no existe. Intente generar el archivo primero."}), 404
    
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
