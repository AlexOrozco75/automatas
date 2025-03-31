
import os
os.environ['TCL_LIBRARY'] = r"C:\Users\panda\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"


import os
import json
import tkinter as tk
from tkinter import scrolledtext, filedialog

# Cargar el archivo JSON con los tokens
def cargar_tabla_simbolos():
    with open("tabla_contenidos.json", "r", encoding="utf-8") as archivo:
        return json.load(archivo)

tabla_simbolos = cargar_tabla_simbolos()

# Extraer listas de palabras reservadas y operadores
palabras_reservadas = [item["token"] for item in tabla_simbolos["palabras_reservadas"]]
operadores = tabla_simbolos["operadores_aritmeticos"] + tabla_simbolos["operadores_asignacion"] + tabla_simbolos["operadores_comparacion"]
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

# Configuración de la ventana principal
root = tk.Tk()
root.title("Interfaz de Compilador Escolar")

# Menú de la aplicación
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Cargar archivo", command=lambda: cargar_archivo(txt_codigo))
menu_bar.add_cascade(label="Archivo", menu=file_menu)
root.config(menu=menu_bar)

# Área para escribir el código
lbl_codigo = tk.Label(root, text="Código:")
lbl_codigo.pack(padx=5, pady=5)

txt_codigo = scrolledtext.ScrolledText(root, width=80, height=20, font=("Consolas", 12))
txt_codigo.pack(padx=5, pady=5)

# Configurar colores de resaltado
txt_codigo.tag_configure("reservada", foreground="blue")
txt_codigo.tag_configure("operador", foreground="red")
txt_codigo.tag_configure("simbolo", foreground="purple")

# Detectar cambios en el texto para resaltar automáticamente
txt_codigo.bind("<KeyRelease>", resaltar_sintaxis)

# Botón para compilar
btn_compilar = tk.Button(root, text="Compilar", command=lambda: compilar(txt_codigo))
btn_compilar.pack(padx=5, pady=5)

# Área para mostrar errores
lbl_errores = tk.Label(root, text="Errores:")
lbl_errores.pack(padx=5, pady=5)

txt_errores = scrolledtext.ScrolledText(root, width=80, height=10, fg="red", font=("Consolas", 12))
txt_errores.pack(padx=5, pady=5)

root.mainloop()
