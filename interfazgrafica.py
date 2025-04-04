import os
import json
import tkinter as tk
from tkinter import scrolledtext, filedialog

# Configuración de la ruta para TCL (ajústala según corresponda)
os.environ['TCL_LIBRARY'] = r"C:\Users\panda\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"

# Rutas base y carga del archivo JSON con definiciones de tokens
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "tabla_contenidos.json")

def cargar_tabla_simbolos():
    with open(JSON_PATH, "r", encoding="utf-8") as archivo:
        return json.load(archivo)

tabla_simbolos = cargar_tabla_simbolos()

# Extraer definiciones desde el JSON
palabras_reservadas = set(item["token"] for item in tabla_simbolos["palabras_reservadas"])
operadores = set(
    tabla_simbolos["operadores_aritmeticos"] +
    tabla_simbolos["operadores_asignacion"] +
    tabla_simbolos["operadores_comparacion"] +
    tabla_simbolos.get("operadores_logicos", [])
)
simbolos_puntuacion = set(tabla_simbolos["simbolos_puntuacion"])

# Función de tokenización manual
def tokenizar(codigo):
    tokens = []
    i = 0
    while i < len(codigo):
        c = codigo[i]
        if c.isspace():
            i += 1
            continue
        if c.isalpha() or c == '_':
            token = c
            i += 1
            while i < len(codigo) and (codigo[i].isalnum() or codigo[i] == '_'):
                token += codigo[i]
                i += 1
            if token in palabras_reservadas:
                token_type = "PALABRA_RESERVADA"
            else:
                if token[0] != '_':
                    token_type = "ERROR"
                    token = f"Variable no válida (debe comenzar con '_'): {token}"
                else:
                    token_type = "IDENTIFICADOR"
            tokens.append((token, token_type))
            continue
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
        else:
            if i + 1 < len(codigo):
                dos_chars = codigo[i:i + 2]
                if dos_chars in operadores:
                    tokens.append((dos_chars, "OPERADOR"))
                    i += 2
                    continue
            if c in operadores:
                tokens.append((c, "OPERADOR"))
                i += 1
                continue
            elif c in simbolos_puntuacion:
                tokens.append((c, "SIMBOLO"))
                i += 1
                continue
            else:
                tokens.append((c, "ERROR"))
                i += 1
    return tokens

def resaltar_sintaxis(event=None):
    txt_codigo.tag_remove("reservada", "1.0", tk.END)
    txt_codigo.tag_remove("operador", "1.0", tk.END)
    txt_codigo.tag_remove("simbolo", "1.0", tk.END)
    txt_codigo.tag_remove("error", "1.0", tk.END)

    codigo = txt_codigo.get("1.0", tk.END)
    tokens = tokenizar(codigo)
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
            elif tipo == "ERROR":
                txt_codigo.tag_add("error", index, end_index)

def compilar(text_widget):
    txt_errores.config(state="normal")
    txt_errores.delete("1.0", tk.END)

    codigo = text_widget.get("1.0", tk.END)
    tokens = tokenizar(codigo)
    errores = []

    for token, tipo in tokens:
        if tipo == "ERROR":
            errores.append(token)

    if errores:
        txt_errores.insert(tk.END, "Errores encontrados:\n")
        for error in errores:
            txt_errores.insert(tk.END, error + "\n")
    else:
        txt_errores.insert(tk.END, "Compilación exitosa: No se encontraron errores.\n")

    txt_errores.config(state="disabled")

# Función para cargar archivos en el widget de código
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

# Configuración de la interfaz gráfica (GUI)
root = tk.Tk()
root.title("VLAD.io")

root.configure(bg="#E9F1FA")

frame_principal = tk.Frame(root, bg="#E9F1FA")
frame_principal.pack(padx=20, pady=20, fill="both", expand=True)

frame_codigo = tk.Frame(frame_principal, bg="#E9F1FA")
frame_codigo.pack(fill="both", expand=True)

frame_botones = tk.Frame(frame_principal, bg="#E9F1FA")
frame_botones.pack(fill="x", pady=10)

frame_errores = tk.Frame(frame_principal, bg="#E9F1FA")
frame_errores.pack(fill="both", expand=True)

lbl_codigo = tk.Label(frame_codigo, text="Código:", bg="#E9F1FA", font=("Arial", 14, "bold"), fg="#005A8D")
lbl_codigo.pack(padx=5, pady=5)

txt_codigo = scrolledtext.ScrolledText(frame_codigo, width=80, height=20, font=("Consolas", 12), wrap=tk.WORD)
txt_codigo.pack(padx=5, pady=5)

txt_codigo.tag_configure("reservada", foreground="#1F4B99")  
txt_codigo.tag_configure("operador", foreground="#D24D57")  
txt_codigo.tag_configure("simbolo", foreground="#5F6368")  
txt_codigo.tag_configure("error", foreground="#D9534F")  

txt_codigo.bind("<KeyRelease>", resaltar_sintaxis)

btn_compilar = tk.Button(frame_botones, text="Compilar", command=lambda: compilar(txt_codigo), bg="#0066CC", fg="white", font=("Arial", 12), relief="flat", padx=15, pady=5)
btn_compilar.pack(side="left", padx=10, pady=5)

btn_cargar = tk.Button(frame_botones, text="Cargar archivo", command=lambda: cargar_archivo(txt_codigo), bg="#007BFF", fg="white", font=("Arial", 12), relief="flat", padx=15, pady=5)
btn_cargar.pack(side="left", padx=10, pady=5)

lbl_errores = tk.Label(frame_errores, text="Errores:", bg="#E9F1FA", font=("Arial", 14, "bold"), fg="#005A8D")
lbl_errores.pack(padx=5, pady=5)

txt_errores = scrolledtext.ScrolledText(frame_errores, width=80, height=10, fg="#D9534F", font=("Consolas", 12), state="disabled", wrap=tk.WORD)
txt_errores.pack(padx=5, pady=5)

status_bar = tk.Label(root, text="Listo", anchor="w", bg="#007BFF", fg="white", font=("Arial", 10))
status_bar.pack(side="bottom", fill="x")

root.mainloop()
