import os
os.environ['TCL_LIBRARY'] = r"C:\Users\panda\AppData\Local\Programs\Python\Python313\tcl\tcl8.6"


import tkinter as tk

def mostrar_mensaje():
    ventana = tk.Tk()
    ventana.title("Hola Mundo")
    etiqueta = tk.Label(ventana, text="Hola, mundo", font=("Arial", 20))
    etiqueta.pack(pady=20)
    ventana.mainloop()

mostrar_mensaje()
