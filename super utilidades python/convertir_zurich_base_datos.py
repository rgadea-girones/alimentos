import os

def buscar_archivos_csv(directorio):
    archivos_csv = []
    for root, dirs, files in os.walk(directorio):
        for file in files:
            if file.endswith(".csv"):
                archivos_csv.append(os.path.join(root, file))
    return archivos_csv

directorio = "I:/nuevas_investigaciones_alimentos_2024/EXCELS_zurich_DCM"
archivos_csv = buscar_archivos_csv(directorio)
# print(archivos_csv)

archivos_csv_sin_header = [archivo for archivo in archivos_csv if "header" not in archivo]
print(archivos_csv_sin_header)