import os
import json
import tkinter as tk
from tkinter import scrolledtext, filedialog

# Configuración de la ruta para TCL (ajústala según corresponda)
os.environ['TCL_LIBRARY'] = r"C:\Users\panda\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"

# Ruta base y carga del archivo JSON con las definiciones de tokens
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "tabla_contenidos.json")


def cargar_tabla_simbolos():
    with open(JSON_PATH, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


tabla_simbolos = cargar_tabla_simbolos()

# Extraer listas definidas en el JSON
palabras_reservadas = set(item["token"] for item in tabla_simbolos["palabras_reservadas"])
operadores = set(
    tabla_simbolos["operadores_aritmeticos"] +
    tabla_simbolos["operadores_asignacion"] +
    tabla_simbolos["operadores_comparacion"] +
    tabla_simbolos.get("operadores_logicos", [])
)
simbolos_puntuacion = set(tabla_simbolos["simbolos_puntuacion"])


# Función de tokenización manual (AFD) sin uso de expresiones regulares
def tokenizar(codigo):
    tokens = []
    i = 0
    while i < len(codigo):
        c = codigo[i]
        # Saltar espacios y saltos de línea
        if c.isspace():
            i += 1
            continue
        # Identificadores y palabras reservadas: inician con letra o guión bajo
        if c.isalpha() or c == '_':
            token = c
            i += 1
            while i < len(codigo) and (codigo[i].isalnum() or codigo[i] == '_'):
                token += codigo[i]
                i += 1
            if token in palabras_reservadas:
                token_type = "PALABRA_RESERVADA"
            else:
                token_type = "IDENTIFICADOR"
            tokens.append((token, token_type))
            continue
        # Números: enteros o decimales
        elif c.isdigit():
            token = c
            i += 1
            has_dot = False
            while i < len(codigo) and (codigo[i].isdigit() or (codigo[i] == '.' and not has_dot)):
                if codigo[i] == '.':
                    has_dot = True
                token += codigo[i]
                i += 1
            tokens.append((token, "NUMERO"))
            continue
        # Operadores y símbolos de puntuación
        else:
            # Primero se intenta reconocer tokens de dos caracteres (por ejemplo, "==", "<=", "&&", etc.)
            if i + 1 < len(codigo):
                dos_chars = codigo[i:i + 2]
                if dos_chars in operadores:
                    tokens.append((dos_chars, "OPERADOR"))
                    i += 2
                    continue
            # Si no es de dos caracteres, se evalúa el carácter actual
            if c in operadores:
                tokens.append((c, "OPERADOR"))
                i += 1
                continue
            elif c in simbolos_puntuacion:
                tokens.append((c, "SIMBOLO"))
                i += 1
                continue
            else:
                # Si el carácter no coincide con ningún patrón, se marca como error
                tokens.append((c, "ERROR"))
                i += 1
    return tokens


# Función para resaltar la sintaxis en el área de código usando la tokenización manual
def resaltar_sintaxis(event=None):
    txt_codigo.tag_remove("reservada", "1.0", tk.END)
    txt_codigo.tag_remove("operador", "1.0", tk.END)
    txt_codigo.tag_remove("simbolo", "1.0", tk.END)

    codigo = txt_codigo.get("1.0", tk.END)
    tokens = tokenizar(codigo)
    # Para cada token encontrado, se busca su posición en el widget y se le asigna el color según su tipo.
    for token, tipo in tokens:
        index = txt_codigo.search(token, "1.0", tk.END)
        if index:
            end_index = f"{index}+{len(token)}c"
            if tipo == "PALABRA_RESERVADA":
                txt_codigo.tag_add("reservada", index, end_index)
            elif tipo == "OPERADOR":
                txt_codigo.tag_add("operador", index, end_index)
            elif tipo == "SIMBOLO":
                txt_codigo.tag_add("simbolo", index, end_index)


# Función de compilación: tokeniza el código, clasifica cada token y muestra el resultado y errores
def compilar(text_widget):
    txt_errores.config(state="normal")
    txt_errores.delete("1.0", tk.END)

    codigo = text_widget.get("1.0", tk.END)
    tokens = tokenizar(codigo)
    errores = []
    reconocidos = []

    for token, tipo in tokens:
        if tipo == "ERROR":
            errores.append(f"Token desconocido: {token}")
        else:
            reconocidos.append(f"{tipo}: {token}")

    if errores:
        for error in errores:
            txt_errores.insert(tk.END, error + "\n")
    else:
        txt_errores.insert(tk.END, "Compilación exitosa\n")

    if reconocidos:
        txt_errores.insert(tk.END, "Tokens reconocidos:\n" + "\n".join(reconocidos) + "\n")

    txt_errores.config(state="disabled")


# Función para cargar un archivo de texto y mostrar su contenido en el editor
def cargar_archivo(text_widget):
    file_path = filedialog.askopenfilename(
        title="Selecciona un archivo",
        filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
    )
    if file_path:
        with open(file_path, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
        text_widget.delete("1.0", tk.END)
        text_widget.insert(tk.END, contenido)
        resaltar_sintaxis()


# Configuración de la interfaz gráfica con Tkinter
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
