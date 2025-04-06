import os
import json
import tkinter as tk
from tkinter import scrolledtext, filedialog
import struct

# Configuración de la ruta para TCL (ajústala según corresponda)
os.environ['TCL_LIBRARY'] = r"C:\Users\panda\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"

# Rutas base y carga del archivo JSON con definiciones de tokens
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "tabla_contenidos.json")
TABLA_SIMBOLOS_PATH = os.path.join(BASE_DIR, "tabla_simbolos.dat")


def cargar_tabla_simbolos_json():
    with open(JSON_PATH, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


tabla_simbolos_json = cargar_tabla_simbolos_json()

# Extraer definiciones desde el JSON
palabras_reservadas = set(item["token"] for item in tabla_simbolos_json["palabras_reservadas"])
operadores = set(
    tabla_simbolos_json["operadores_aritmeticos"] +
    tabla_simbolos_json["operadores_asignacion"] +
    tabla_simbolos_json["operadores_comparacion"] +
    tabla_simbolos_json.get("operadores_logicos", [])
)
simbolos_puntuacion = set(tabla_simbolos_json["simbolos_puntuacion"])

# Definir el formato del registro: 30 bytes para el identificador, 20 bytes para el token type.
RECORD_FORMAT = "30s20s"
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)


# --- Funciones para manejar la Tabla de Símbolos (archivo de acceso aleatorio) ---

def init_tabla_simbolos_file():
    """Crea o limpia el archivo de la Tabla de Símbolos."""
    with open(TABLA_SIMBOLOS_PATH, "wb") as f:
        pass  # Se crea un archivo vacío


def add_symbol(identifier, token_type):
    """
    Agrega el símbolo (identifier, token_type) a la tabla de símbolos en el archivo binario,
    sin duplicar.
    """
    identifier = identifier.strip()
    try:
        with open(TABLA_SIMBOLOS_PATH, "rb+") as f:
            exists = False
            while True:
                record_bytes = f.read(RECORD_SIZE)
                if not record_bytes:
                    break
                rec_id, rec_type = struct.unpack(RECORD_FORMAT, record_bytes)
                rec_id = rec_id.decode('utf-8').strip()
                if rec_id == identifier:
                    exists = True
                    break
            if not exists:
                # Preparar los datos en formato fijo
                rec_id_bytes = identifier.encode('utf-8').ljust(30, b' ')[:30]
                token_type_bytes = token_type.encode('utf-8').ljust(20, b' ')[:20]
                packed_record = struct.pack(RECORD_FORMAT, rec_id_bytes, token_type_bytes)
                f.write(packed_record)
    except FileNotFoundError:
        with open(TABLA_SIMBOLOS_PATH, "wb") as f:
            rec_id_bytes = identifier.encode('utf-8').ljust(30, b' ')[:30]
            token_type_bytes = token_type.encode('utf-8').ljust(20, b' ')[:20]
            packed_record = struct.pack(RECORD_FORMAT, rec_id_bytes, token_type_bytes)
            f.write(packed_record)


def load_tabla_simbolos():
    """Carga la tabla de símbolos desde el archivo binario y la devuelve como lista de tuplas."""
    symbols = []
    try:
        with open(TABLA_SIMBOLOS_PATH, "rb") as f:
            while True:
                record_bytes = f.read(RECORD_SIZE)
                if not record_bytes:
                    break
                rec_id, rec_type = struct.unpack(RECORD_FORMAT, record_bytes)
                rec_id = rec_id.decode('utf-8').strip()
                rec_type = rec_type.decode('utf-8').strip()
                symbols.append((rec_id, rec_type))
    except FileNotFoundError:
        pass
    return symbols


init_tabla_simbolos_file()


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


# --- Funciones de la Interfaz ---

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
        elif tipo in ("IDENTIFICADOR", "NUMERO"):
            add_symbol(token, tipo)

    if errores:
        txt_errores.insert(tk.END, "Errores encontrados:\n")
        for error in errores:
            txt_errores.insert(tk.END, error + "\n")
    else:
        txt_errores.insert(tk.END, "Compilación exitosa: No se encontraron errores.\n")

    txt_errores.config(state="disabled")


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


def mostrar_tabla_simbolos():
    symbols = load_tabla_simbolos()
    ventana = tk.Toplevel(root)
    ventana.title("Tabla de Símbolos")
    txt_tabla = scrolledtext.ScrolledText(ventana, width=50, height=20, font=("Consolas", 12))
    txt_tabla.pack(padx=5, pady=5)
    if symbols:
        for ident, tipo in symbols:
            txt_tabla.insert(tk.END, f"{ident} - {tipo}\n")
    else:
        txt_tabla.insert(tk.END, "La tabla de símbolos está vacía.")


# Configuración de la interfaz gráfica (GUI) - Versión moderna
root = tk.Tk()
root.title("VLAD.io")
root.geometry("900x700")
root.configure(bg="#2e2e2e")  

# Fuentes y colores modernos
fuente_general = ("Segoe UI", 11)
color_fondo = "#2e2e2e"
color_texto = "#ffffff"
color_boton = "#444"
color_boton_hover = "#666"
color_input_bg = "#1e1e1e"

def estilo_boton(btn):
    btn.configure(
        bg=color_boton,
        fg="white",
        activebackground=color_boton_hover,
        relief="flat",
        font=fuente_general,
        padx=10,
        pady=5,
        cursor="hand2"
    )

# Menú superior
menu_bar = tk.Menu(root, bg=color_boton, fg="white", activebackground=color_boton_hover, font=fuente_general)
file_menu = tk.Menu(menu_bar, tearoff=0, bg=color_boton, fg="white", activebackground=color_boton_hover, font=fuente_general)
file_menu.add_command(label="Cargar archivo", command=lambda: cargar_archivo(txt_codigo))
menu_bar.add_cascade(label="Archivo", menu=file_menu)
root.config(menu=menu_bar)

# Label
lbl_codigo = tk.Label(root, text="Código:", font=fuente_general, bg=color_fondo, fg=color_texto)
lbl_codigo.pack(padx=5, pady=(10, 2))

# Código fuente
txt_codigo = scrolledtext.ScrolledText(root, width=100, height=20, font=("Consolas", 12), bg=color_input_bg, fg=color_texto, insertbackground="white")
txt_codigo.pack(padx=10, pady=5)
txt_codigo.tag_configure("reservada", foreground="#569CD6")  # Azul
txt_codigo.tag_configure("operador", foreground="#D16969")  # Rojo
txt_codigo.tag_configure("simbolo", foreground="#C586C0")   # Violeta
txt_codigo.tag_configure("error", foreground="#D7BA7D")     # Naranja
txt_codigo.bind("<KeyRelease>", resaltar_sintaxis)

# Botones
frame_botones = tk.Frame(root, bg=color_fondo)
frame_botones.pack(pady=10)

btn_compilar = tk.Button(frame_botones, text="Compilar", command=lambda: compilar(txt_codigo))
btn_ver_tabla = tk.Button(frame_botones, text="Ver Tabla de Símbolos", command=mostrar_tabla_simbolos)

estilo_boton(btn_compilar)
estilo_boton(btn_ver_tabla)

btn_compilar.grid(row=0, column=0, padx=10)
btn_ver_tabla.grid(row=0, column=1, padx=10)

# Errores
lbl_errores = tk.Label(root, text="Errores:", font=fuente_general, bg=color_fondo, fg=color_texto)
lbl_errores.pack(padx=5, pady=(10, 2))

txt_errores = scrolledtext.ScrolledText(root, width=100, height=10, font=("Consolas", 12), bg=color_input_bg, fg="#ff4c4c", insertbackground="white", state="disabled")
txt_errores.pack(padx=10, pady=5)

root.mainloop()
