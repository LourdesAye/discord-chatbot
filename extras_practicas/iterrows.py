import pandas as pd

# Crear un DataFrame de ejemplo
data = {'nombre': ['Alice', 'Bob', 'Charlie'],
        'edad': [25, 30, 22],
        'ciudad': ['New York', 'London', 'Paris']}
df = pd.DataFrame(data)

print(df)
# Iterar sobre las filas usando iterrows() que devuelve una tupla (index,serie)
for index, row in df.iterrows():
    print(f"Índice: {index}, Nombre: {row['nombre']}, Edad: {row['edad']}, Ciudad: {row['ciudad']}")
    # una serie puede parecerse a un diccionario en términos de acceder a los valores por clave (nombre de columna),
    # pero no es un diccionario estándar de Python. 