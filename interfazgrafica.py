
import os
os.environ['TCL_LIBRARY'] = r"C:\Users\panda\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"


import tkinter as tk
from tkinter import scrolledtext, filedialog

def compilar():
    # Obtiene el texto del área de código y simula la compilación
    codigo = txt_codigo.get("1.0", tk.END)
    errores = ""
    if "error" in codigo.lower():
        errores += "Se encontró la palabra 'error'.\n"
    else:
        errores = "Compilación exitosa: No se detectaron errores.\n"
    txt_errores.delete("1.0", tk.END)
    txt_errores.insert(tk.END, errores)

def cargar_archivo():
    # Abre el diálogo para seleccionar un archivo y lo carga en el área de código
    ruta = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
    if ruta:
        with open(ruta, "r", encoding="utf-8") as archivo:
            contenido = archivo.read()
        txt_codigo.delete("1.0", tk.END)
        txt_codigo.insert(tk.END, contenido)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Interfaz de Compilador Escolar")

# Menú de la aplicación
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Cargar archivo", command=cargar_archivo)
menu_bar.add_cascade(label="Archivo", menu=file_menu)
root.config(menu=menu_bar)

# Área para escribir el código
lbl_codigo = tk.Label(root, text="Código:")
lbl_codigo.pack(padx=5, pady=5)

txt_codigo = scrolledtext.ScrolledText(root, width=80, height=20)
txt_codigo.pack(padx=5, pady=5)

# Botón para compilar
btn_compilar = tk.Button(root, text="Compilar", command=compilar)
btn_compilar.pack(padx=5, pady=5)

# Área para mostrar errores
lbl_errores = tk.Label(root, text="Errores:")
lbl_errores.pack(padx=5, pady=5)

txt_errores = scrolledtext.ScrolledText(root, width=80, height=10, fg="red")
txt_errores.pack(padx=5, pady=5)

root.mainloop()
