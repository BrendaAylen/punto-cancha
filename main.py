# main.py
# Verifica la conexión a la base de datos e inicia la interfaz gráfica.

import tkinter as tk
from tkinter import messagebox

from db import probar_conexion, ErrorBD
from interfaz import App

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # ocultar la ventana mientras se verifica la base
    try:
        probar_conexion()
    except ErrorBD as e:
        messagebox.showerror("Base de datos", str(e))
        root.destroy()
        raise SystemExit(1)
    root.deiconify()
    app = App(root)
    root.mainloop()
    
