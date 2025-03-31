import os

os.environ['TCL_LIBRARY'] = r"C:\Users\panda\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"

import os
import json
import tkinter as tk
from tkinter import scrolledtext, filedialog
import re

# Obtener la ruta del archivo JSON en el mismo directorio que el script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "tabla_contenidos.json")


# Cargar el archivo JSON con los tokens desde la ruta general
def cargar_tabla_simbolos():
    with open(JSON_PATH, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


tabla_simbolos = cargar_tabla_simbolos()

# Extraer listas de palabras reservadas, operadores y símbolos de puntuación
palabras_reservadas = [item["token"] for item in tabla_simbolos["palabras_reservadas"]]
operadores = tabla_simbolos["operadores_aritmeticos"] + tabla_simbolos["operadores_asignacion"] + tabla_simbolos[
    "operadores_comparacion"]
simbolos_puntuacion = tabla_simbolos["simbolos_puntuacion"]


# Función para resaltar palabras en el código
def resaltar_sintaxis(event=None):
    txt_codigo.tag_remove("reservada", "1.0", tk.END)
    txt_codigo.tag_remove("operador", "1.0", tk.END)
    txt_codigo.tag_remove("simbolo", "1.0", tk.END)

    texto = txt_codigo.get("1.0", tk.END)
    palabras = texto.split()

    index = "1.0"
    for palabra in palabras:
        inicio = txt_codigo.search(palabra, index, stopindex=tk.END)
        if inicio:
            fin = f"{inicio}+{len(palabra)}c"
            if palabra in palabras_reservadas:
                txt_codigo.tag_add("reservada", inicio, fin)
            elif palabra in operadores:
                txt_codigo.tag_add("operador", inicio, fin)
            elif palabra in simbolos_puntuacion:
                txt_codigo.tag_add("simbolo", inicio, fin)
            index = fin


# Función para cargar un archivo de texto en el área de código
def cargar_archivo(text_widget):
    filename = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
    if filename:
        with open(filename, "r", encoding="utf-8") as f:
            contenido = f.read()
            text_widget.delete("1.0", tk.END)
            text_widget.insert(tk.END, contenido)
        resaltar_sintaxis()


# Función de compilación que tokeniza y muestra errores
def compilar(text_widget):
    txt_errores.config(state="normal")
    txt_errores.delete("1.0", tk.END)

    codigo = text_widget.get("1.0", tk.END)
    tokens = codigo.split()
    errores = []

    for token in tokens:
        if token in palabras_reservadas or token in operadores or token in simbolos_puntuacion:
            continue
        elif re.match(r'^[a-zA-Z_]\w*$', token):  # identificador válido
            continue
        elif token.isdigit():  # números
            continue
        else:
            errores.append(f"Token desconocido: {token}")

    if errores:
        for error in errores:
            txt_errores.insert(tk.END, error + "\n")
    else:
        txt_errores.insert(tk.END, "Compilación exitosa")

    txt_errores.config(state="disabled")


# Configuración de la ventana principal
root = tk.Tk()
root.title("VLAD.io")

menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Cargar archivo", command=lambda: cargar_archivo(txt_codigo))
menu_bar.add_cascade(label="Archivo", menu=file_menu)
root.config(menu=menu_bar)

lbl_codigo = tk.Label(root, text="Código:")
lbl_codigo.pack(padx=5, pady=5)

txt_codigo = scrolledtext.ScrolledText(root, width=80, height=20, font=("Consolas", 12))
txt_codigo.pack(padx=5, pady=5)

txt_codigo.tag_configure("reservada", foreground="blue")
txt_codigo.tag_configure("operador", foreground="red")
txt_codigo.tag_configure("simbolo", foreground="purple")

txt_codigo.bind("<KeyRelease>", resaltar_sintaxis)

btn_compilar = tk.Button(root, text="Compilar", command=lambda: compilar(txt_codigo))
btn_compilar.pack(padx=5, pady=5)

lbl_errores = tk.Label(root, text="Errores:")
lbl_errores.pack(padx=5, pady=5)

txt_errores = scrolledtext.ScrolledText(root, width=80, height=10, fg="red", font=("Consolas", 12), state="disabled")
txt_errores.pack(padx=5, pady=5)

root.mainloop()