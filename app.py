"""Aplicación de escritorio para gestionar el Equipo de Transmisión y Recolección Plato.

La aplicación usa SQLite como base de datos local porque no requiere servidor y
Tkinter para la interfaz porque viene incluido con Python en la mayoría de
instalaciones.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

APP_TITLE = "Equipo de Transmisión y Recolección Plato"
DB_PATH = Path(__file__).with_name("equipo_plato.db")


class MemberDatabase:
    """Capa pequeña para crear y consultar la base de datos SQLite."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _create_table(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS integrantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cedula TEXT NOT NULL UNIQUE,
                    telefono TEXT NOT NULL
                )
                """
            )

    def list_members(self) -> list[tuple[int, str, str, str]]:
        with self._connect() as connection:
            return connection.execute(
                "SELECT id, nombre, cedula, telefono FROM integrantes ORDER BY nombre"
            ).fetchall()

    def add_member(self, nombre: str, cedula: str, telefono: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO integrantes (nombre, cedula, telefono) VALUES (?, ?, ?)",
                (nombre, cedula, telefono),
            )

    def update_member(self, member_id: int, nombre: str, cedula: str, telefono: str) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE integrantes
                SET nombre = ?, cedula = ?, telefono = ?
                WHERE id = ?
                """,
                (nombre, cedula, telefono, member_id),
            )

    def delete_member(self, member_id: int) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM integrantes WHERE id = ?", (member_id,))


class TeamApp(tk.Tk):
    """Interfaz gráfica sencilla para registrar, editar y borrar integrantes."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("820x520")
        self.minsize(760, 460)
        self.database = MemberDatabase()
        self.selected_member_id: int | None = None

        self.nombre_var = tk.StringVar()
        self.cedula_var = tk.StringVar()
        self.telefono_var = tk.StringVar()

        self._build_layout()
        self.refresh_members()

    def _build_layout(self) -> None:
        title = ttk.Label(self, text=APP_TITLE, font=("Arial", 18, "bold"))
        title.pack(pady=(16, 8))

        form = ttk.LabelFrame(self, text="Datos del integrante")
        form.pack(fill="x", padx=16, pady=8)
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Nombre").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.nombre_var).grid(
            row=0, column=1, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Cédula").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.cedula_var).grid(
            row=1, column=1, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Teléfono").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.telefono_var).grid(
            row=2, column=1, padx=8, pady=8, sticky="ew"
        )

        buttons = ttk.Frame(form)
        buttons.grid(row=3, column=0, columnspan=2, padx=8, pady=(4, 10), sticky="e")
        ttk.Button(buttons, text="Guardar", command=self.save_member).pack(side="left", padx=4)
        ttk.Button(buttons, text="Limpiar", command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(buttons, text="Eliminar", command=self.delete_selected_member).pack(
            side="left", padx=4
        )

        table_frame = ttk.LabelFrame(self, text="Integrantes registrados")
        table_frame.pack(fill="both", expand=True, padx=16, pady=(4, 16))

        columns = ("nombre", "cedula", "telefono")
        self.table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        self.table.heading("nombre", text="Nombre")
        self.table.heading("cedula", text="Cédula")
        self.table.heading("telefono", text="Teléfono")
        self.table.column("nombre", width=280)
        self.table.column("cedula", width=180)
        self.table.column("telefono", width=180)
        self.table.bind("<<TreeviewSelect>>", self.load_selected_member)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def refresh_members(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

        for member_id, nombre, cedula, telefono in self.database.list_members():
            self.table.insert("", "end", iid=str(member_id), values=(nombre, cedula, telefono))

    def _validated_inputs(self) -> tuple[str, str, str] | None:
        nombre = self.nombre_var.get().strip()
        cedula = self.cedula_var.get().strip()
        telefono = self.telefono_var.get().strip()

        if not nombre or not cedula or not telefono:
            messagebox.showwarning("Campos incompletos", "Complete nombre, cédula y teléfono.")
            return None

        return nombre, cedula, telefono

    def save_member(self) -> None:
        values = self._validated_inputs()
        if values is None:
            return

        nombre, cedula, telefono = values
        try:
            if self.selected_member_id is None:
                self.database.add_member(nombre, cedula, telefono)
                messagebox.showinfo("Guardado", "Integrante registrado correctamente.")
            else:
                self.database.update_member(self.selected_member_id, nombre, cedula, telefono)
                messagebox.showinfo("Actualizado", "Integrante actualizado correctamente.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Cédula duplicada", "Ya existe un integrante con esa cédula.")
            return

        self.clear_form()
        self.refresh_members()

    def load_selected_member(self, _event: tk.Event[tk.Misc]) -> None:
        selected = self.table.selection()
        if not selected:
            return

        self.selected_member_id = int(selected[0])
        nombre, cedula, telefono = self.table.item(selected[0], "values")
        self.nombre_var.set(nombre)
        self.cedula_var.set(cedula)
        self.telefono_var.set(telefono)

    def delete_selected_member(self) -> None:
        if self.selected_member_id is None:
            messagebox.showwarning("Sin selección", "Seleccione un integrante de la tabla.")
            return

        confirmed = messagebox.askyesno("Confirmar eliminación", "¿Desea eliminar este integrante?")
        if not confirmed:
            return

        self.database.delete_member(self.selected_member_id)
        self.clear_form()
        self.refresh_members()
        messagebox.showinfo("Eliminado", "Integrante eliminado correctamente.")

    def clear_form(self) -> None:
        self.selected_member_id = None
        self.nombre_var.set("")
        self.cedula_var.set("")
        self.telefono_var.set("")
        self.table.selection_remove(self.table.selection())


def main() -> None:
    app = TeamApp()
    app.mainloop()


if __name__ == "__main__":
    main()
