from flask import Flask, request, render_template, send_file, jsonify
import pandas as pd
import time
import random
import threading

app = Flask(__name__)

# Ruta del archivo de entrada
file_path = "CABA_Enriquecido.xlsx"
output_path = "CABA_Resultado_Sin_Index.xlsx"

# Función para generar el Excel después de 3:30 horas
def generar_excel(user_number):
    time.sleep(12600)  # 3 horas y 30 minutos

    # Cargar el archivo Excel
    df = pd.read_excel(file_path)

    # Seleccionar 4000 filas aleatorias del archivo
    df_sampled = df.sample(n=4000, random_state=random.randint(1, 10000))

    # Listas de nombres argentinos y parentescos
    nombres_argentinos = [
        "Juan", "María", "Carlos", "Sofía", "Martín", "Lucía", "Joaquín", "Valentina",
        "Gonzalo", "Camila", "Federico", "Florencia", "Leandro", "Agustina"
    ]
    parentescos = ["HIJO/A", "CONYUGE", "SOBRINO/A", "PADRE/MADRE", "TÍO/A", "PRIMO/A"]

    # Función para obtener un apellido de la columna "Nombre" (suponiendo que está en la segunda columna)
    def get_apellido(nombre):
        if pd.notna(nombre):
            return nombre.split()[-1]  # Tomamos el último elemento del nombre como apellido
        return "Pérez"  # Default en caso de que no haya un nombre

    # Agregar las nuevas columnas con familiares y nombres aleatorios
    df_sampled["Familiar 1"] = [random.choice(parentescos) for _ in range(len(df_sampled))]
    df_sampled["Nombre 1"] = [random.choice(nombres_argentinos) + " " + get_apellido(nombre) for nombre in df_sampled.iloc[:, 1]]
    df_sampled["Familiar 2"] = [random.choice(parentescos) for _ in range(len(df_sampled))]
    df_sampled["Nombre 2"] = [random.choice(nombres_argentinos) + " " + get_apellido(nombre) for nombre in df_sampled.iloc[:, 1]]

    # Guardar el archivo con el resultado final sin índice de numeración en la primera columna
    df_sampled.to_excel(output_path, index=False)

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

    return jsonify({"message": "Proceso iniciado. Espere 3 horas y 30 minutos.", "success": True})

# Ruta para descargar el archivo después de 3:30 horas
@app.route('/descargar')
def descargar():
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
