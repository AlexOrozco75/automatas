
import os
os.environ['TCL_LIBRARY'] = r"C:\Users\panda\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"


import tkinter as tk
import tkinter as tk
from tkinter import scrolledtext


def compilar():
    # Obtiene el contenido del área de código
    codigo = txt_codigo.get("1.0", tk.END)

    # Aquí puedes implementar la lógica de compilación o análisis
    # En este ejemplo, simplemente se simula la búsqueda de la palabra "error"
    errores = ""
    if "error" in codigo.lower():
        errores += "Se encontró la palabra 'error' en el código.\n"
    else:
        errores = "Compilación exitosa: No se detectaron errores.\n"

    # Limpia el área de errores y muestra el resultado
    txt_errores.delete("1.0", tk.END)
    txt_errores.insert(tk.END, errores)


# Configuración de la ventana principal
root = tk.Tk()
root.title("Interfaz de Compilador Escolar")

# Área para escribir el código
lbl_codigo = tk.Label(root, text="Código:")
lbl_codigo.pack(padx=5, pady=5)

txt_codigo = scrolledtext.ScrolledText(root, width=80, height=20)
txt_codigo.pack(padx=5, pady=5)

# Botón para compilar
btn_compilar = tk.Button(root, text="Compilar", command=compilar)
btn_compilar.pack(padx=5, pady=5)

# Área para mostrar los errores
lbl_errores = tk.Label(root, text="Errores:")
lbl_errores.pack(padx=5, pady=5)

txt_errores = scrolledtext.ScrolledText(root, width=80, height=10, fg="red")
txt_errores.pack(padx=5, pady=5)

root.mainloop()
