# interfaz.py
import tkinter as tk
from tkinter import ttk, messagebox
from funciones import (
    socios,
    canchas,
    reservas,
    pagos,
    socio_nombre,
    minutos,
    disponible,
    combo_socios,
    combo_canchas,
    validar_fecha,
)


def limpiar_tree(tree):
    for item in tree.get_children():
        tree.delete(item)


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Punto Cancha - Menú Principal")
        self.root.geometry("600x560")
        self.estilo()
        self.menu()

    def estilo(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 20, "bold"))
        style.configure("Treeview", rowheight=26)

    def limpiar_ventana(self):
        for w in self.root.winfo_children():
            w.destroy()

    def salir(self):
        if messagebox.askyesno(
            "Confirmar salida", "¿Desea cerrar la aplicación?"
        ):
            self.root.destroy()

    def menu(self):
        self.limpiar_ventana()
        f = ttk.Frame(self.root, padding=30)
        f.pack(expand=True)

        ttk.Label(f, text="PUNTO CANCHA", style="Title.TLabel").pack(pady=10)
        ttk.Label(f, text="Sistema de Gestión de Reservas").pack(pady=(0, 20))

        botones = [
            ("Socios", self.socios),
            ("Canchas", self.canchas),
            ("Reservas", self.reservas),
            ("Modos de pago", self.pagos_ventana),
            ("Disponibilidad", self.disponibilidad),
            ("Reservas por cancha", self.reservas_por_cancha),
            ("Cerrar aplicación", self.salir),
        ]

        for texto, comando in botones:
            ttk.Button(f, text=texto, command=comando, width=30).pack(pady=4)

    def crear_toplevel(self, titulo, geometria):
        w = tk.Toplevel(self.root)
        w.title(titulo)
        w.geometry(geometria)
        w.transient(self.root)
        w.grab_set()
        return w

    # ---------------- SOCIOS ----------------
    def socios(self):
        w = self.crear_toplevel("Socios", "950x560")
        f = ttk.Frame(w, padding=15)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Gestión de Socios", style="Title.TLabel").pack(
            pady=8
        )

        form = ttk.LabelFrame(f, text="Datos", padding=10)
        form.pack(fill="x")

        campos = ["DNI", "Nombre", "Apellido", "Teléfono", "Email"]
        e = {}

        for i, campo in enumerate(campos):
            ttk.Label(form, text=campo).grid(
                row=i // 2, column=(i % 2) * 2, padx=5, pady=5
            )
            e[campo] = ttk.Entry(form, width=28)
            e[campo].grid(
                row=i // 2, column=(i % 2) * 2 + 1, padx=5, pady=5
            )

        tree = ttk.Treeview(f, columns=tuple(campos), show="headings")
        for c in campos:
            tree.heading(c, text=c)
            tree.column(c, width=145)
        tree.pack(fill="both", expand=True, pady=10)

        def cargar():
            limpiar_tree(tree)
            for s in socios:
                tree.insert(
                    "",
                    "end",
                    values=(
                        s["dni"],
                        s["nombre"],
                        s["apellido"],
                        s["telefono"],
                        s["email"],
                    ),
                )

        def limpiar():
            for x in e.values():
                x.delete(0, tk.END)

        def seleccionar(_=None):
            sel = tree.selection()
            if not sel:
                return
            limpiar()
            for x, valor in zip(
                e.values(), tree.item(sel[0], "values")
            ):
                x.insert(0, valor)

        def guardar():
            datos = {k: x.get().strip() for k, x in e.items()}
            if not all(datos.values()):
                messagebox.showwarning(
                    "Campos", "Complete todos los campos."
                )
                return
            if any(s["dni"] == datos["DNI"] for s in socios):
                messagebox.showwarning(
                    "DNI", "Ya existe un socio con ese DNI."
                )
                return
            socios.append(
                {
                    "dni": datos["DNI"],
                    "nombre": datos["Nombre"],
                    "apellido": datos["Apellido"],
                    "telefono": datos["Teléfono"],
                    "email": datos["Email"],
                }
            )
            cargar()
            limpiar()
            messagebox.showinfo("Éxito", "Socio registrado.")

        def modificar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(
                    "Selección", "Seleccione un socio."
                )
                return
            dni = tree.item(sel[0], "values")[0]
            for s in socios:
                if s["dni"] == dni:
                    s.update(
                        {
                            "dni": e["DNI"].get(),
                            "nombre": e["Nombre"].get(),
                            "apellido": e["Apellido"].get(),
                            "telefono": e["Teléfono"].get(),
                            "email": e["Email"].get(),
                        }
                    )
                    break
            cargar()
            limpiar()

        def eliminar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(
                    "Selección", "Seleccione un socio."
                )
                return
            dni = tree.item(sel[0], "values")[0]
            if messagebox.askyesno("Confirmar", "¿Eliminar el socio?"):
                socios[:] = [s for s in socios if s["dni"] != dni]
                cargar()
                limpiar()

        botones = ttk.Frame(f)
        botones.pack(fill="x")

        ttk.Button(botones, text="Nuevo", command=guardar).pack(
            side="left", padx=3
        )
        ttk.Button(botones, text="Modificar", command=modificar).pack(
            side="left", padx=3
        )
        ttk.Button(botones, text="Eliminar", command=eliminar).pack(
            side="left", padx=3
        )
        ttk.Button(botones, text="Limpiar", command=limpiar).pack(
            side="left", padx=3
        )
        ttk.Button(botones, text="Volver", command=w.destroy).pack(
            side="left", padx=3
        )

        tree.bind("<<TreeviewSelect>>", seleccionar)
        cargar()

    # ---------------- CANCHAS ----------------
    def canchas(self):
        w = self.crear_toplevel("Canchas", "700x500")
        f = ttk.Frame(w, padding=15)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Gestión de Canchas", style="Title.TLabel").pack(
            pady=8
        )

        form = ttk.Frame(f)
        form.pack(fill="x")

        ttk.Label(form, text="Número:").pack(side="left", padx=5)
        num = ttk.Entry(form, width=12)
        num.pack(side="left", padx=5)

        ttk.Label(form, text="Tipo:").pack(side="left", padx=5)
        tipo = ttk.Combobox(
            form, values=["Fútbol 5", "Fútbol 7"], state="readonly", width=12
        )
        tipo.pack(side="left", padx=5)

        ttk.Label(form, text="Estado:").pack(side="left", padx=5)
        estado = ttk.Combobox(
            form,
            values=["Disponible", "Mantenimiento", "Inactiva"],
            state="readonly",
            width=14,
        )
        estado.set("Disponible")
        estado.pack(side="left", padx=5)

        tree = ttk.Treeview(
            f, columns=("numero", "tipo", "estado"), show="headings"
        )
        for c in ("numero", "tipo", "estado"):
            tree.heading(c, text=c.title())
            tree.column(c, width=180)
        tree.pack(fill="both", expand=True, pady=10)

        def cargar():
            limpiar_tree(tree)
            for c in canchas:
                tree.insert(
                    "",
                    "end",
                    values=(c["numero"], c["tipo"], c.get("estado", "Disponible")),
                )

        def limpiar():
            num.delete(0, tk.END)
            tipo.set("")
            estado.set("Disponible")

        def guardar():
            if not num.get() or not tipo.get() or not estado.get():
                messagebox.showwarning("Campos", "Complete los campos.")
                return
            if any(c["numero"] == num.get() for c in canchas):
                messagebox.showwarning(
                    "Cancha", "Ese número ya existe."
                )
                return
            canchas.append(
                {"numero": num.get(), "tipo": tipo.get(), "estado": estado.get()}
            )
            cargar()
            limpiar()
            messagebox.showinfo("Éxito", "Cancha registrada.")

        def seleccionar(_=None):
            sel = tree.selection()
            if sel:
                v = tree.item(sel[0], "values")
                limpiar()
                num.insert(0, v[0])
                tipo.set(v[1])
                estado.set(v[2])

        def modificar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(
                    "Selección", "Seleccione una cancha."
                )
                return
            viejo = tree.item(sel[0], "values")[0]
            for c in canchas:
                if c["numero"] == viejo:
                    c.update(
                        {
                            "numero": num.get(),
                            "tipo": tipo.get(),
                            "estado": estado.get(),
                        }
                    )
            cargar()
            limpiar()

        def eliminar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning(
                    "Selección", "Seleccione una cancha."
                )
                return
            n = tree.item(sel[0], "values")[0]
            if messagebox.askyesno("Confirmar", "¿Eliminar la cancha?"):
                canchas[:] = [c for c in canchas if c["numero"] != n]
                cargar()
                limpiar()

        b = ttk.Frame(f)
        b.pack(fill="x")

        ttk.Button(b, text="Nueva", command=guardar).pack(
            side="left", padx=3
        )
        ttk.Button(b, text="Modificar", command=modificar).pack(
            side="left", padx=3
        )
        ttk.Button(b, text="Eliminar", command=eliminar).pack(
            side="left", padx=3
        )
        ttk.Button(b, text="Limpiar", command=limpiar).pack(
            side="left", padx=3
        )
        ttk.Button(b, text="Volver", command=w.destroy).pack(
            side="left", padx=3
        )

        tree.bind("<<TreeviewSelect>>", seleccionar)
        cargar()

    # ---------------- MODOS DE PAGO ----------------
    def pagos_ventana(self):
        w = self.crear_toplevel("Modos de pago", "450x350")

        f = ttk.Frame(w, padding=25)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Modos de pago", style="Title.TLabel").pack(pady=10)

        tree = ttk.Treeview(
            f, columns=("modo",), show="headings", height=5
        )
        tree.heading("modo", text="Modo de pago")
        tree.pack(fill="x", pady=15)

        for p in pagos:
            tree.insert("", "end", values=(p,))

        ttk.Label(
            f, text="Cada reserva utiliza un único modo de pago."
        ).pack(pady=10)
        ttk.Button(f, text="Volver", command=w.destroy).pack()

    # ---------------- FORMULARIO RESERVA ----------------
    def formulario_reserva(self, reserva=None):
        editar = reserva is not None
        w = self.crear_toplevel(
            "Modificar Reserva" if editar else "Nueva Reserva", "600x560"
        )

        f = ttk.Frame(w, padding=20)
        f.pack(fill="both", expand=True)

        ttk.Label(
            f,
            text="Modificar Reserva" if editar else "Nueva Reserva",
            style="Title.TLabel",
        ).pack(pady=10)

        form = ttk.LabelFrame(f, text="Datos", padding=15)
        form.pack(fill="x")

        labels = [
            "Socio",
            "Cancha",
            "Fecha (DD/MM/AAAA)",
            "Hora inicio",
            "Hora fin",
            "Modo de pago",
        ]
        widgets = {}

        for i, l in enumerate(labels):
            ttk.Label(form, text=l + ":").grid(
                row=i, column=0, sticky="e", padx=8, pady=7
            )

        widgets["Socio"] = ttk.Combobox(
            form, values=combo_socios(), state="readonly", width=30
        )
        widgets["Socio"].grid(row=0, column=1)

        widgets["Cancha"] = ttk.Combobox(
            form, values=combo_canchas(), state="readonly", width=30
        )
        widgets["Cancha"].grid(row=1, column=1)

        widgets["Fecha"] = ttk.Entry(form, width=32)
        widgets["Fecha"].insert(0, "20/09/2026")
        widgets["Fecha"].grid(row=2, column=1)

        widgets["Hora inicio"] = ttk.Entry(form, width=32)
        widgets["Hora inicio"].grid(row=3, column=1)

        widgets["Hora fin"] = ttk.Entry(form, width=32)
        widgets["Hora fin"].grid(row=4, column=1)

        widgets["Modo de pago"] = ttk.Combobox(
            form, values=pagos, state="readonly", width=30
        )
        widgets["Modo de pago"].grid(row=5, column=1)

        if editar:
            widgets["Socio"].set(
                next(
                    (
                        x
                        for x in combo_socios()
                        if x.startswith(reserva["dni"] + " -")
                    ),
                    "",
                )
            )
            widgets["Cancha"].set(
                next(
                    (
                        x
                        for x in combo_canchas()
                        if x.startswith(reserva["cancha"] + " -")
                    ),
                    "",
                )
            )
            widgets["Fecha"].delete(0, tk.END)
            widgets["Fecha"].insert(0, reserva["fecha"])
            widgets["Hora inicio"].insert(0, reserva["inicio"])
            widgets["Hora fin"].insert(0, reserva["fin"])
            widgets["Modo de pago"].set(reserva["pago"])

        def datos():
            socio = (
                widgets["Socio"].get().split(" - ")[0]
                if widgets["Socio"].get()
                else ""
            )
            cancha = (
                widgets["Cancha"].get().split(" - ")[0]
                if widgets["Cancha"].get()
                else ""
            )
            return (
                socio,
                cancha,
                widgets["Fecha"].get().strip(),
                widgets["Hora inicio"].get().strip(),
                widgets["Hora fin"].get().strip(),
                widgets["Modo de pago"].get(),
            )

        def verificar():
            d = datos()
            if not all(d):
                messagebox.showwarning(
                    "Campos", "Complete todos los campos."
                )
                return
            if not validar_fecha(d[2]):
                messagebox.showwarning(
                    "Fecha inválida", "Formato de fecha debe ser DD/MM/AAAA."
                )
                return
            if (
                minutos(d[3]) is None
                or minutos(d[4]) is None
                or minutos(d[4]) <= minutos(d[3])
            ):
                messagebox.showwarning(
                    "Horario", "La hora de fin debe ser posterior al inicio."
                )
                return
            if disponible(
                d[1],
                d[2],
                d[3],
                d[4],
                reserva["numero"] if editar else None,
            ):
                messagebox.showinfo(
                    "Disponible", "La cancha está disponible."
                )
            else:
                messagebox.showwarning(
                    "No disponible",
                    "La cancha está ocupada en ese horario.",
                )

        def guardar():
            d = datos()
            if not all(d):
                messagebox.showwarning(
                    "Campos", "Complete todos los campos."
                )
                return
            if not validar_fecha(d[2]):
                messagebox.showwarning(
                    "Fecha inválida", "Formato de fecha debe ser DD/MM/AAAA."
                )
                return
            if (
                minutos(d[3]) is None
                or minutos(d[4]) is None
                or minutos(d[4]) <= minutos(d[3])
            ):
                messagebox.showwarning("Horario", "Revise las horas.")
                return
            if not disponible(
                d[1],
                d[2],
                d[3],
                d[4],
                reserva["numero"] if editar else None,
            ):
                messagebox.showwarning(
                    "No disponible", "La cancha está ocupada."
                )
                return

            if editar:
                reserva.update(
                    {
                        "dni": d[0],
                        "cancha": d[1],
                        "fecha": d[2],
                        "inicio": d[3],
                        "fin": d[4],
                        "pago": d[5],
                    }
                )
            else:
                nuev_num = (
                    max([r["numero"] for r in reservas], default=0) + 1
                )
                reservas.append(
                    {
                        "numero": nuev_num,
                        "dni": d[0],
                        "cancha": d[1],
                        "fecha": d[2],
                        "inicio": d[3],
                        "fin": d[4],
                        "pago": d[5],
                        "estado": "Reservada",
                    }
                )

            messagebox.showinfo(
                "Éxito", "Reserva guardada correctamente."
            )
            w.destroy()
            self.mostrar_reservas()

        b = ttk.Frame(f)
        b.pack(pady=20)

        ttk.Button(
            b, text="Verificar disponibilidad", command=verificar
        ).pack(side="left", padx=4)
        ttk.Button(
            b, text="Guardar" if editar else "Reservar", command=guardar
        ).pack(side="left", padx=4)
        ttk.Button(b, text="Cancelar", command=w.destroy).pack(
            side="left", padx=4
        )

    # ---------------- LISTA DE RESERVAS ----------------
    def reservas(self):
        self.mostrar_reservas()

    def mostrar_reservas(self, datos_filtrados=None):
        w = self.crear_toplevel("Reservas", "1100x600")

        f = ttk.Frame(w, padding=15)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="Gestión de Reservas", style="Title.TLabel").pack(
            pady=8
        )

        tree = ttk.Treeview(
            f,
            columns=(
                "n",
                "socio",
                "cancha",
                "fecha",
                "inicio",
                "fin",
                "pago",
                "estado",
            ),
            show="headings",
        )
        titulos = {
            "n": "N°",
            "socio": "Socio",
            "cancha": "Cancha",
            "fecha": "Fecha",
            "inicio": "Inicio",
            "fin": "Fin",
            "pago": "Pago",
            "estado": "Estado",
        }
        for c, t in titulos.items():
            tree.heading(c, text=t)
            tree.column(c, width=120)
        tree.pack(fill="both", expand=True, pady=10)

        def cargar(lista=None):
            limpiar_tree(tree)
            origen = reservas if lista is None else lista
            for r in origen:
                tree.insert(
                    "",
                    "end",
                    values=(
                        r["numero"],
                        socio_nombre(r["dni"]),
                        r["cancha"],
                        r["fecha"],
                        r["inicio"],
                        r["fin"],
                        r["pago"],
                        r.get("estado", "Reservada"),
                    ),
                )

        def seleccion():
            s = tree.selection()
            if not s:
                messagebox.showwarning(
                    "Selección", "Seleccione una reserva."
                )
                return None
            n = int(tree.item(s[0], "values")[0])
            return next((r for r in reservas if r["numero"] == n), None)

        def modificar():
            r = seleccion()
            if r:
                w.destroy()
                self.formulario_reserva(r)

        def cancelar_reserva_accion():
            r = seleccion()
            if r and messagebox.askyesno(
                "Confirmar", "¿Desea cancelar esta reserva?"
            ):
                r["estado"] = "Cancelada"
                cargar()

        def detalle():
            r = seleccion()
            if r:
                s = next((x for x in socios if x["dni"] == r["dni"]), None)
                texto = (
                    f"Reserva N° {r['numero']}\n"
                    f"Socio: {socio_nombre(r['dni'])}\n"
                    f"Cancha: {r['cancha']}\n"
                    f"Fecha: {r['fecha']}\n"
                    f"Horario: {r['inicio']} - {r['fin']}\n"
                    f"Pago: {r['pago']}\n"
                    f"Estado: {r.get('estado', 'Reservada')}"
                )
                if s:
                    texto += (
                        f"\nDNI: {s['dni']}\n"
                        f"Teléfono: {s['telefono']}\n"
                        f"Email: {s['email']}"
                    )
                messagebox.showinfo("Detalle de reserva", texto)

        def filtrar():
            q = tk.Toplevel(w)
            q.title("Filtrar Reservas")
            q.geometry("450x330")
            q.transient(w)
            q.grab_set()

            x = ttk.Frame(q, padding=20)
            x.pack(fill="both", expand=True)

            ttk.Label(
                x, text="Filtrar Reservas", style="Title.TLabel"
            ).pack(pady=8)

            ttk.Label(x, text="Socio (DNI):").pack()
            dni = ttk.Entry(x)
            dni.pack(pady=5)

            ttk.Label(x, text="Cancha:").pack()
            ca = ttk.Combobox(
                x,
                values=["Todas"] + [c["numero"] for c in canchas],
                state="readonly",
            )
            ca.set("Todas")
            ca.pack(pady=5)

            ttk.Label(x, text="Fecha (DD/MM/AAAA):").pack()
            fe = ttk.Entry(x)
            fe.pack(pady=5)

            usar = tk.BooleanVar()
            ttk.Checkbutton(
                x, text="Usar fecha", variable=usar
            ).pack()

            def aplicar():
                if usar.get() and not validar_fecha(fe.get()):
                    messagebox.showwarning(
                        "Fecha", "Formato de fecha inválido."
                    )
                    return
                lista = [
                    r
                    for r in reservas
                    if (not dni.get() or dni.get() in r["dni"])
                    and (ca.get() == "Todas" or r["cancha"] == ca.get())
                    and (not usar.get() or r["fecha"] == fe.get())
                ]
                cargar(lista)
                q.destroy()

            ttk.Button(x, text="Filtrar", command=aplicar).pack(pady=10)

        b = ttk.Frame(f)
        b.pack(fill="x")

        ttk.Button(
            b,
            text="Nueva reserva",
            command=lambda: self.formulario_reserva(),
        ).pack(side="left", padx=3)
        ttk.Button(b, text="Modificar", command=modificar).pack(
            side="left", padx=3
        )
        ttk.Button(
            b, text="Cancelar Reserva", command=cancelar_reserva_accion
        ).pack(side="left", padx=3)
        ttk.Button(b, text="Filtrar", command=filtrar).pack(
            side="left", padx=3
        )
        ttk.Button(b, text="Detalle", command=detalle).pack(
            side="left", padx=3
        )
        ttk.Button(
            b,
            text="Comprobante",
            command=lambda: self.comprobante(seleccion()),
        ).pack(side="left", padx=3)
        ttk.Button(b, text="Volver", command=w.destroy).pack(
            side="left", padx=3
        )

        cargar(datos_filtrados)

    def comprobante(self, r):
        if not r:
            return
        w = self.crear_toplevel("Comprobante de Reserva", "500x450")

        f = ttk.Frame(w, padding=25)
        f.pack(fill="both", expand=True)

        ttk.Label(
            f, text="COMPROBANTE DE RESERVA", style="Title.TLabel"
        ).pack(pady=15)

        texto = (
            f"Reserva N°: {r['numero']}\n"
            f"Socio: {socio_nombre(r['dni'])}\n"
            f"Cancha: {r['cancha']}\n"
            f"Fecha: {r['fecha']}\n"
            f"Horario: {r['inicio']} - {r['fin']}\n"
            f"Modo de pago: {r['pago']}\n"
            f"Estado: {r.get('estado', 'Reservada')}"
        )
        ttk.Label(f, text=texto, justify="left", font=("Arial", 11)).pack(
            pady=20
        )

        ttk.Button(
            f,
            text="Imprimir",
            command=lambda: messagebox.showinfo(
                "Imprimir", "Función de impresión pendiente."
            ),
        ).pack(side="left", padx=5)
        ttk.Button(f, text="Volver", command=w.destroy).pack(
            side="left", padx=5
        )

    # ---------------- DISPONIBILIDAD ----------------
    def disponibilidad(self):
        w = self.crear_toplevel("Disponibilidad", "800x520")

        f = ttk.Frame(w, padding=15)
        f.pack(fill="both", expand=True)

        ttk.Label(
            f, text="Consulta de Disponibilidad", style="Title.TLabel"
        ).pack(pady=8)

        x = ttk.Frame(f)
        x.pack(fill="x")

        ttk.Label(x, text="Fecha (DD/MM/AAAA):").pack(side="left")
        fecha = ttk.Entry(x, width=12)
        fecha.insert(0, "20/09/2026")
        fecha.pack(side="left", padx=5)

        ttk.Label(x, text="Inicio:").pack(side="left")
        ini = ttk.Entry(x, width=8)
        ini.insert(0, "18:00")
        ini.pack(side="left", padx=5)

        ttk.Label(x, text="Fin:").pack(side="left")
        fin = ttk.Entry(x, width=8)
        fin.insert(0, "19:00")
        fin.pack(side="left", padx=5)

        tree = ttk.Treeview(
            f, columns=("n", "tipo", "estado", "disponible"), show="headings"
        )
        for c in ("n", "tipo", "estado", "disponible"):
            tree.heading(c, text=c.title())
            tree.column(c, width=170)
        tree.pack(fill="both", expand=True, pady=15)

        def consultar():
            limpiar_tree(tree)
            if not validar_fecha(fecha.get()):
                messagebox.showwarning(
                    "Fecha", "Formato de fecha debe ser DD/MM/AAAA."
                )
                return
            if (
                minutos(ini.get()) is None
                or minutos(fin.get()) is None
                or minutos(fin.get()) <= minutos(ini.get())
            ):
                messagebox.showwarning("Horario", "Revise las horas.")
                return
            for c in canchas:
                ok = disponible(
                    c["numero"], fecha.get(), ini.get(), fin.get()
                )
                tree.insert(
                    "",
                    "end",
                    values=(
                        c["numero"],
                        c["tipo"],
                        c.get("estado", "Disponible"),
                        "Sí" if ok else "No",
                    ),
                )

        ttk.Button(x, text="Consultar", command=consultar).pack(
            side="left", padx=10
        )
        ttk.Button(f, text="Volver", command=w.destroy).pack()
        consultar()

    # ---------------- RESERVAS POR CANCHA ----------------
    def reservas_por_cancha(self):
        w = self.crear_toplevel("Reservas por Cancha", "750x500")

        f = ttk.Frame(w, padding=15)
        f.pack(fill="both", expand=True)

        ttk.Label(
            f, text="Reservas por Cancha", style="Title.TLabel"
        ).pack(pady=8)

        tree = ttk.Treeview(
            f,
            columns=("n", "tipo", "estado", "cantidad"),
            show="headings",
        )
        for c, t in [
            ("n", "N° Cancha"),
            ("tipo", "Tipo"),
            ("estado", "Estado"),
            ("cantidad", "Cantidad de reservas"),
        ]:
            tree.heading(c, text=t)
            tree.column(c, width=170)
        tree.pack(fill="both", expand=True, pady=10)

        def cargar():
            limpiar_tree(tree)
            for c in canchas:
                cantidad = sum(
                    r["cancha"] == c["numero"]
                    and r.get("estado") == "Reservada"
                    for r in reservas
                )
                tree.insert(
                    "",
                    "end",
                    values=(
                        c["numero"],
                        c["tipo"],
                        c.get("estado", "Disponible"),
                        cantidad,
                    ),
                )

        ttk.Button(f, text="Consultar", command=cargar).pack(
            side="left", padx=5
        )
        ttk.Button(f, text="Volver", command=w.destroy).pack(
            side="left", padx=5
        )
        cargar()