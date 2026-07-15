"""Aplicación de escritorio para gestionar el Equipo de Transmisión y Recolección Plato.

La aplicación usa SQLite como base de datos local porque no requiere servidor y
Tkinter para la interfaz porque viene incluido con Python en la mayoría de
instalaciones.
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_TITLE = "Equipo de Transmisión y Recolección Plato"
APP_VERSION = "Versión 0.3.2026-07-15"
DB_PATH = Path(__file__).with_name("equipo_plato.db")
CARGOS = ("Recolector", "Transmisor", "Backup", "Coordinador de puesto")
MALLA_TRANSMISION_CARGOS = ("Transmisor", "Backup", "Coordinador de puesto")
MALLA_RECOLECCION_CARGOS = ("Recolector", "Backup")
TABLE_COLUMNS = ("puesto_trabajo", "cedula", "nombre", "telefono", "cargo", "mesa_inicial", "mesa_final")
COLUMN_TITLES = {
    "puesto_trabajo": "Puesto",
    "cedula": "Cédula",
    "nombre": "Nombre",
    "telefono": "Celular",
    "cargo": "Cargo",
    "mesa_inicial": "M. inicial",
    "mesa_final": "M. final",
}

DEFAULT_MEMBERS = [
    ("IED MARIA ALFARO DE OSPINO", "1081910709", "EDITH SABRINA ANDRADES BELTRAN", "", "Transmisor", "1", "8"),
    ("IED MARIA ALFARO DE OSPINO", "1004284951", "STEFANY YISEL MUÑOZ BARRIOS", "", "Coordinador de puesto", "9", "17"),
    ("ED GABRIEL ESCOBAR BALLESTA", "1081910817", "ERIKA PATRICIA VARGAS ARIAS", "", "Coordinador de puesto", "1", "6"),
    ("ED GABRIEL ESCOBAR BALLESTA", "1081914761", "MILADIS TAPIAS ACOSTA", "", "Transmisor", "7", "12"),
    ("GABRIEL ESCOBAR B. SD GABRIELITO", "1033705367", "MARIA FERNANDA MORALES PACHECO", "", "Coordinador de puesto", "1", "10"),
    ("GABRIEL ESCOBAR B. SD GABRIELITO", "1081927714", "PAULA FERNANDA OSPINA MACIAS", "", "Transmisor", "11", "20"),
    ("GABRIEL ESCOBAR B. SD GABRIELITO", "1083460271", "MERLIS PATRICIA ACUÑA IBAÑEZ", "", "Transmisor", "21", "30"),
    ("GABRIEL ESCOBAR B. SD GABRIELITO", "1081913155", "JAVIER DE JESUS CAÑA GAMARRA", "", "Transmisor", "31", "40"),
    ("IED JUANA ARIAS DE BENAVIDES", "1081924702", "LUIS ALLFREDO CORTINA MEDINA", "", "Coordinador de puesto", "1", "7"),
    ("IED JUANA ARIAS DE BENAVIDES", "1081916864", "GRISELDINA MARIA SAUMETH ARIAS", "", "Transmisor", "8", "15"),
    ("IED JUANA ARIAS DE BENAVIDES", "1081908047", "YULEINIS ANDREA GOMEZ CARET", "", "Transmisor", "16", "23"),
    ("IED VICTOR CAMARGO ALVAREZ", "1081917282", "SINDY JOHANIS RUIZ MADARIAGA", "", "Coordinador de puesto", "1", "8"),
    ("COORDINADOR PRINCIPAL", "", "OSCAR TOVAR VERBEL", "", "Coordinador de puesto", "", ""),
    ("BACKUP", "1080570852", "WENDY PAOLA JIMENEZ", "3106246847", "Backup", "", ""),
    ("BACKUP", "1045758017", "DAYANA VANESSA LEIVA ACUÑA", "3212599505", "Backup", "", ""),
    ("BACKUP", "1080570490", "IVAN ALFARO VISBAL", "3046681831", "Backup", "", ""),
    ("IED MARIA ALFARO DE OSPINO", "1.140.841.860", "GERALDINE OMAIRA MEDINA SAUMETH", "3024269991", "Recolector", "", ""),
    ("IED MARIA ALFARO DE OSPINO", "1.080.570.577", "JORGE LUIS MUÑOZ BARRIOS", "3002147276", "Recolector", "", ""),
    ("IED MARIA ALFARO DE OSPINO", "1.081.910.899", "MARIA ALEJANDRA MUÑOZ FONSECA", "3226816651", "Backup", "", ""),
    ("IED GABRIEL ESCOBAR BALLESTA", "1.081.920.063", "KATIA MILENA PULGAR SALAZAR", "", "Recolector", "", ""),
    ("IED GABRIEL ESCOBAR BALLESTA", "17.591.656", "DAVID GUILLERMO MENCO ZAFRA", "", "Recolector", "", ""),
    ("IED GABRIEL ESCOBAR B. SD GABRIELITO", "1.095.787.195", "MARYORI PAOLA ARREDONDO BAYONA", "3017156177", "Recolector", "", ""),
    ("IED GABRIEL ESCOBAR B. SD GABRIELITO", "1.081.910.371", "LUISA FERNANDA CIRO OROZCO", "3016049146", "Recolector", "", ""),
    ("IED GABRIEL ESCOBAR B. SD GABRIELITO", "39.101.071", "YINA PAOLA MULFORD CHARRIS", "3243061991", "Recolector", "", ""),
    ("IED GABRIEL ESCOBAR B. SD GABRIELITO", "1.193.535.357", "ANGY MILET GUTIERREZ AMARIS", "3008658504", "Recolector", "", ""),
    ("IED GABRIEL ESCOBAR B. SD GABRIELITO", "1.081.914.873", "DEISY MARIA AGUILAR VIDES", "", "Backup", "", ""),
    ("IED JUANA ARIAS DE BENAVIDES", "39.092.107", "LUZ KARIME MEDINA SAUMETH", "3007922216", "Recolector", "", ""),
    ("IED JUANA ARIAS DE BENAVIDES", "1.081.909.702", "KATIA MILENA CAMPUZANO VARGAS", "", "Recolector", "", ""),
    ("IED JUANA ARIAS DE BENAVIDES", "1.081.918.547", "MARIA FERNANDA DE AVILA RODRIGUEZ", "3112891891", "Recolector", "", ""),
    ("IED JUANA ARIAS DE BENAVIDES", "12.594.318", "OSCAR ALFREDO CORTINA DE ARCO", "3007210690", "Backup", "", ""),
    ("IED VICTOR CAMARGO ALVAREZ", "1.081.910.370", "LUCY MARCELA CIRO OROZCO", "3016123714", "Recolector", "", ""),
]


def _pdf_text(value: object) -> str:
    """Escapa texto para una cadena simple de PDF."""

    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _chunk_lines(lines: list[str], page_size: int = 42) -> list[list[str]]:
    return [lines[index : index + page_size] for index in range(0, len(lines), page_size)] or [[]]


def _table_pages(rows: list[tuple[str, ...]], rows_per_page: int = 18) -> list[list[tuple[str, ...]]]:
    return [rows[index : index + rows_per_page] for index in range(0, len(rows), rows_per_page)] or [[]]


def _fit_cell_text(value: object, max_chars: int) -> str:
    text = str(value).replace("\n", " ").strip()
    if len(text) <= max_chars:
        return text
    return f"{text[: max_chars - 3]}..."


def create_pdf(file_path: Path, title: str, rows: list[tuple[str, ...]]) -> None:
    """Crea un PDF sencillo con los datos organizados en tabla."""

    headers = [COLUMN_TITLES[column] for column in TABLE_COLUMNS]
    column_widths = [170, 90, 180, 95, 115, 65, 65]
    column_limits = [25, 14, 27, 14, 18, 8, 8]
    start_x = 31
    table_width = sum(column_widths)
    header_y = 505
    row_height = 24
    pages = _table_pages(rows)

    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    page_refs = " ".join(f"{4 + index * 2} 0 R" for index in range(len(pages)))
    objects.append(f"<< /Type /Pages /Kids [{page_refs}] /Count {len(pages)} >>".encode("latin-1"))
    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for index, page_rows in enumerate(pages):
        page_number = 4 + index * 2
        content_number = page_number + 1
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {content_number} 0 R >>".encode(
                "latin-1"
            )
        )

        commands = [
            "BT",
            "/F1 16 Tf",
            f"40 560 Td ({_pdf_text(title)}) Tj",
            "ET",
            "BT",
            "/F1 9 Tf",
            f"40 542 Td ({_pdf_text(APP_VERSION)} - Página {index + 1} de {len(pages)}) Tj",
            "ET",
            "0.85 w",
        ]

        def draw_row(y_position: int, values: list[object], is_header: bool = False) -> None:
            fill = "0.90 g" if is_header else "1 g"
            commands.extend(
                [
                    fill,
                    f"{start_x} {y_position} {table_width} {row_height} re f",
                    "0 g",
                    f"{start_x} {y_position} {table_width} {row_height} re S",
                ]
            )
            current_x = start_x
            for width, value, limit in zip(column_widths, values, column_limits):
                commands.append(f"{current_x} {y_position} {width} {row_height} re S")
                commands.extend(
                    [
                        "BT",
                        "/F1 8 Tf" if not is_header else "/F1 8.5 Tf",
                        f"{current_x + 4} {y_position + 9} Td ({_pdf_text(_fit_cell_text(value, limit))}) Tj",
                        "ET",
                    ]
                )
                current_x += width

        draw_row(header_y, headers, is_header=True)
        current_y = header_y - row_height
        for row in page_rows:
            draw_row(current_y, list(row))
            current_y -= row_height

        stream = "\n".join(commands).encode("latin-1", errors="replace")
        objects.append(
            b"<< /Length "
            + str(len(stream)).encode("ascii")
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        )

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, content in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode("ascii"))
        pdf.extend(content)
        pdf.extend(b"\nendobj\n")

    xref_position = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_position}\n%%EOF\n".encode(
            "ascii"
        )
    )
    file_path.write_bytes(pdf)


class MemberDatabase:
    """Capa pequeña para crear y consultar la base de datos SQLite."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._create_table()
        self._ensure_column(
            "cargo", "ALTER TABLE integrantes ADD COLUMN cargo TEXT NOT NULL DEFAULT 'Recolector'"
        )
        self._ensure_column(
            "puesto_trabajo",
            "ALTER TABLE integrantes ADD COLUMN puesto_trabajo TEXT NOT NULL DEFAULT ''",
        )
        self._ensure_column(
            "mesa_inicial",
            "ALTER TABLE integrantes ADD COLUMN mesa_inicial TEXT NOT NULL DEFAULT ''",
        )
        self._ensure_column(
            "mesa_final",
            "ALTER TABLE integrantes ADD COLUMN mesa_final TEXT NOT NULL DEFAULT ''",
        )
        self._migrate_legacy_voting_place_data()
        self.seed_default_members()

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
                    telefono TEXT NOT NULL,
                    puesto_trabajo TEXT NOT NULL DEFAULT '',
                    cargo TEXT NOT NULL DEFAULT 'Recolector',
                    mesa_inicial TEXT NOT NULL DEFAULT '',
                    mesa_final TEXT NOT NULL DEFAULT ''
                )
                """
            )

    def _ensure_column(self, column_name: str, alter_statement: str) -> None:
        """Agrega una columna si la base ya existía con una versión anterior."""

        with self._connect() as connection:
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(integrantes)").fetchall()
            }
            if column_name not in columns:
                connection.execute(alter_statement)

    def _migrate_legacy_voting_place_data(self) -> None:
        """Copia datos guardados antes como lugar_votacion al nuevo campo puesto_trabajo."""

        with self._connect() as connection:
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(integrantes)").fetchall()
            }
            if "lugar_votacion" in columns and "puesto_trabajo" in columns:
                connection.execute(
                    """
                    UPDATE integrantes
                    SET puesto_trabajo = lugar_votacion
                    WHERE puesto_trabajo = '' AND lugar_votacion <> ''
                    """
                )

    def seed_default_members(self) -> None:
        with self._connect() as connection:
            total_members = connection.execute("SELECT COUNT(*) FROM integrantes").fetchone()[0]
            if total_members:
                return

            connection.executemany(
                """
                INSERT INTO integrantes (
                    puesto_trabajo, cedula, nombre, telefono, cargo, mesa_inicial, mesa_final
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                DEFAULT_MEMBERS,
            )

    def list_members(
        self, cargos: tuple[str, ...] | None = None
    ) -> list[tuple[int, str, str, str, str, str, str, str]]:
        with self._connect() as connection:
            if cargos is None:
                return connection.execute(
                    """
                    SELECT id, puesto_trabajo, cedula, nombre, telefono, cargo, mesa_inicial, mesa_final
                    FROM integrantes
                    ORDER BY puesto_trabajo, cargo, nombre
                    """
                ).fetchall()

            placeholders = ",".join("?" for _cargo in cargos)
            return connection.execute(
                f"""
                SELECT id, puesto_trabajo, cedula, nombre, telefono, cargo, mesa_inicial, mesa_final
                FROM integrantes
                WHERE cargo IN ({placeholders})
                ORDER BY puesto_trabajo, cargo, nombre
                """,
                cargos,
            ).fetchall()

    def add_member(
        self,
        nombre: str,
        cedula: str,
        telefono: str,
        puesto_trabajo: str,
        cargo: str,
        mesa_inicial: str,
        mesa_final: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO integrantes (
                    nombre, cedula, telefono, puesto_trabajo, cargo, mesa_inicial, mesa_final
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (nombre, cedula, telefono, puesto_trabajo, cargo, mesa_inicial, mesa_final),
            )

    def update_member(
        self,
        member_id: int,
        nombre: str,
        cedula: str,
        telefono: str,
        puesto_trabajo: str,
        cargo: str,
        mesa_inicial: str,
        mesa_final: str,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE integrantes
                SET nombre = ?, cedula = ?, telefono = ?, puesto_trabajo = ?,
                    cargo = ?, mesa_inicial = ?, mesa_final = ?
                WHERE id = ?
                """,
                (
                    nombre,
                    cedula,
                    telefono,
                    puesto_trabajo,
                    cargo,
                    mesa_inicial,
                    mesa_final,
                    member_id,
                ),
            )

    def delete_member(self, member_id: int) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM integrantes WHERE id = ?", (member_id,))


class TeamApp(tk.Tk):
    """Interfaz con menú de botones para integrantes y reportes por malla."""

    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1040x660")
        self.minsize(920, 580)
        self.database = MemberDatabase()
        self.selected_member_id: int | None = None

        self.nombre_var = tk.StringVar()
        self.cedula_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.puesto_trabajo_var = tk.StringVar()
        self.cargo_var = tk.StringVar(value=CARGOS[0])
        self.mesa_inicial_var = tk.StringVar()
        self.mesa_final_var = tk.StringVar()

        self._build_layout()
        self.show_home()

    def _build_layout(self) -> None:
        header = ttk.Frame(self, padding=(18, 14, 18, 8))
        header.pack(fill="x")
        ttk.Label(header, text=APP_TITLE, font=("Arial", 20, "bold")).pack(anchor="w")
        ttk.Label(header, text=APP_VERSION, font=("Arial", 10, "italic")).pack(anchor="w")

        main_area = ttk.Frame(self, padding=(16, 8, 16, 16))
        main_area.pack(fill="both", expand=True)
        main_area.columnconfigure(1, weight=1)
        main_area.rowconfigure(0, weight=1)

        navigation = ttk.LabelFrame(main_area, text="Menú principal", padding=12)
        navigation.grid(row=0, column=0, sticky="ns", padx=(0, 14))

        button_options = {"fill": "x", "pady": 6, "ipady": 10}
        ttk.Button(navigation, text="Inicio", command=self.show_home).pack(**button_options)
        ttk.Button(navigation, text="Integrantes", command=self.show_integrantes).pack(
            **button_options
        )
        ttk.Button(
            navigation, text="Malla de transmisión", command=self.show_malla_transmision
        ).pack(**button_options)
        ttk.Button(
            navigation, text="Malla de recolección", command=self.show_malla_recoleccion
        ).pack(**button_options)

        ttk.Label(
            navigation,
            text="Los formularios e informes\nse abren al presionar\nsu botón.",
            justify="center",
        ).pack(pady=(18, 0))

        self.content = ttk.Frame(main_area)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=1)

        self.home_frame = ttk.Frame(self.content)
        self.integrantes_frame = ttk.Frame(self.content)
        self.report_frame = ttk.Frame(self.content)
        for frame in (self.home_frame, self.integrantes_frame, self.report_frame):
            frame.grid(row=0, column=0, sticky="nsew")

        self._build_home_frame()
        self._build_integrantes_frame()
        self._build_report_frame()

    def _build_home_frame(self) -> None:
        self.home_frame.columnconfigure(0, weight=1)
        ttk.Label(
            self.home_frame,
            text="PANTALLA INICIAL - VERSIÓN NUEVA",
            font=("Arial", 18, "bold"),
            foreground="#0a6f32",
        ).grid(row=0, column=0, pady=(28, 8))
        ttk.Label(
            self.home_frame,
            text="Si ves esta pantalla, sí estás ejecutando el archivo actualizado.",
            font=("Arial", 11),
        ).grid(row=1, column=0, pady=(0, 16))
        ttk.Label(
            self.home_frame,
            text="Seleccione una opción para continuar",
            font=("Arial", 16, "bold"),
        ).grid(row=2, column=0, pady=(0, 16))
        ttk.Button(self.home_frame, text="Integrantes", command=self.show_integrantes).grid(
            row=3, column=0, pady=8, ipadx=50, ipady=10
        )
        ttk.Button(
            self.home_frame, text="Malla de transmisión", command=self.show_malla_transmision
        ).grid(row=4, column=0, pady=8, ipadx=50, ipady=10)
        ttk.Button(
            self.home_frame, text="Malla de recolección", command=self.show_malla_recoleccion
        ).grid(row=5, column=0, pady=8, ipadx=50, ipady=10)

    def _build_integrantes_frame(self) -> None:
        self.integrantes_frame.rowconfigure(1, weight=1)
        self.integrantes_frame.columnconfigure(0, weight=1)

        form = ttk.LabelFrame(self.integrantes_frame, text="Datos del integrante")
        form.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        ttk.Label(form, text="Nombre").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.nombre_var).grid(
            row=0, column=1, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Cédula").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.cedula_var).grid(
            row=0, column=3, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Teléfono").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.telefono_var).grid(
            row=1, column=1, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Institución / puesto de trabajo").grid(
            row=1, column=2, padx=8, pady=8, sticky="w"
        )
        ttk.Entry(form, textvariable=self.puesto_trabajo_var).grid(
            row=1, column=3, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Cargo").grid(row=2, column=0, padx=8, pady=8, sticky="w")
        ttk.Combobox(
            form,
            textvariable=self.cargo_var,
            values=CARGOS,
            state="readonly",
        ).grid(row=2, column=1, padx=8, pady=8, sticky="ew")

        ttk.Label(form, text="Mesa inicial").grid(row=2, column=2, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.mesa_inicial_var).grid(
            row=2, column=3, padx=8, pady=8, sticky="ew"
        )

        ttk.Label(form, text="Mesa final").grid(row=3, column=0, padx=8, pady=8, sticky="w")
        ttk.Entry(form, textvariable=self.mesa_final_var).grid(
            row=3, column=1, padx=8, pady=8, sticky="ew"
        )

        buttons = ttk.Frame(form)
        buttons.grid(row=4, column=0, columnspan=4, padx=8, pady=(4, 10), sticky="e")
        ttk.Button(buttons, text="Guardar", command=self.save_member).pack(side="left", padx=4)
        ttk.Button(buttons, text="Limpiar", command=self.clear_form).pack(side="left", padx=4)
        ttk.Button(buttons, text="Eliminar", command=self.delete_selected_member).pack(
            side="left", padx=4
        )
        ttk.Button(
            buttons,
            text="Imprimir PDF",
            command=lambda: self.export_table_to_pdf(self.members_table, "Integrantes registrados"),
        ).pack(side="left", padx=4)

        table_frame = ttk.LabelFrame(self.integrantes_frame, text="Integrantes registrados")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.members_table = self._create_table(table_frame)
        self.members_table.bind("<<TreeviewSelect>>", self.load_selected_member)

    def _build_report_frame(self) -> None:
        self.report_frame.rowconfigure(1, weight=1)
        self.report_frame.columnconfigure(0, weight=1)

        report_header = ttk.Frame(self.report_frame)
        report_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        report_header.columnconfigure(0, weight=1)
        self.report_title = ttk.Label(report_header, font=("Arial", 14, "bold"))
        self.report_title.grid(row=0, column=0, sticky="w")
        ttk.Button(
            report_header,
            text="Imprimir PDF",
            command=lambda: self.export_table_to_pdf(
                self.report_table, self.report_title.cget("text")
            ),
        ).grid(row=0, column=1, sticky="e")

        table_frame = ttk.LabelFrame(self.report_frame, text="Listado")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
        self.report_table = self._create_table(table_frame)

    def _create_table(self, parent: ttk.Frame) -> ttk.Treeview:
        table = ttk.Treeview(parent, columns=TABLE_COLUMNS, show="headings", height=14)
        widths = {
            "puesto_trabajo": 220,
            "cedula": 120,
            "nombre": 220,
            "telefono": 120,
            "cargo": 150,
            "mesa_inicial": 80,
            "mesa_final": 80,
        }
        for column in TABLE_COLUMNS:
            table.heading(column, text=COLUMN_TITLES[column])
            table.column(column, width=widths[column])

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        return table

    def show_home(self) -> None:
        self.clear_form()
        self.home_frame.tkraise()

    def show_integrantes(self) -> None:
        self.integrantes_frame.tkraise()
        self.refresh_members_table()

    def show_malla_transmision(self) -> None:
        self._show_report(
            "Malla de transmisión: transmisores, backup y coordinadores de puesto",
            MALLA_TRANSMISION_CARGOS,
        )

    def show_malla_recoleccion(self) -> None:
        self._show_report("Malla de recolección: recolectores y backup", MALLA_RECOLECCION_CARGOS)

    def _show_report(self, title: str, cargos: tuple[str, ...]) -> None:
        self.clear_form()
        self.report_title.configure(text=title)
        self.refresh_table(self.report_table, cargos)
        self.report_frame.tkraise()

    def refresh_members_table(self) -> None:
        self.refresh_table(self.members_table)

    def get_table_rows(self, table: ttk.Treeview) -> list[tuple[str, ...]]:
        return [tuple(table.item(item, "values")) for item in table.get_children()]

    def export_table_to_pdf(self, table: ttk.Treeview, title: str) -> None:
        rows = self.get_table_rows(table)
        if not rows:
            messagebox.showwarning("Sin datos", "No hay datos para imprimir en PDF.")
            return

        file_name = filedialog.asksaveasfilename(
            title="Guardar lista en PDF",
            defaultextension=".pdf",
            filetypes=(("Archivo PDF", "*.pdf"),),
            initialfile=f"{title.lower().replace(' ', '_').replace(':', '')}.pdf",
        )
        if not file_name:
            return

        create_pdf(Path(file_name), title, rows)
        messagebox.showinfo("PDF creado", f"Lista guardada en:\n{file_name}")

    def refresh_table(self, table: ttk.Treeview, cargos: tuple[str, ...] | None = None) -> None:
        for item in table.get_children():
            table.delete(item)

        for (
            member_id,
            puesto_trabajo,
            cedula,
            nombre,
            telefono,
            cargo,
            mesa_inicial,
            mesa_final,
        ) in self.database.list_members(cargos):
            table.insert(
                "",
                "end",
                iid=str(member_id),
                values=(
                    puesto_trabajo,
                    cedula,
                    nombre,
                    telefono,
                    cargo,
                    mesa_inicial,
                    mesa_final,
                ),
            )

    def _validated_inputs(self) -> tuple[str, str, str, str, str, str, str] | None:
        nombre = self.nombre_var.get().strip()
        cedula = self.cedula_var.get().strip()
        telefono = self.telefono_var.get().strip()
        puesto_trabajo = self.puesto_trabajo_var.get().strip()
        cargo = self.cargo_var.get().strip()
        mesa_inicial = self.mesa_inicial_var.get().strip()
        mesa_final = self.mesa_final_var.get().strip()

        if not nombre or not cedula or not puesto_trabajo or not cargo:
            messagebox.showwarning(
                "Campos incompletos",
                "Complete nombre, cédula, institución / puesto de trabajo y cargo.",
            )
            return None

        if cargo not in CARGOS:
            messagebox.showwarning("Cargo inválido", "Seleccione un cargo válido de la lista.")
            return None

        return nombre, cedula, telefono, puesto_trabajo, cargo, mesa_inicial, mesa_final

    def save_member(self) -> None:
        values = self._validated_inputs()
        if values is None:
            return

        nombre, cedula, telefono, puesto_trabajo, cargo, mesa_inicial, mesa_final = values
        try:
            if self.selected_member_id is None:
                self.database.add_member(
                    nombre, cedula, telefono, puesto_trabajo, cargo, mesa_inicial, mesa_final
                )
                messagebox.showinfo("Guardado", "Integrante registrado correctamente.")
            else:
                self.database.update_member(
                    self.selected_member_id,
                    nombre,
                    cedula,
                    telefono,
                    puesto_trabajo,
                    cargo,
                    mesa_inicial,
                    mesa_final,
                )
                messagebox.showinfo("Actualizado", "Integrante actualizado correctamente.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Cédula duplicada", "Ya existe un integrante con esa cédula.")
            return

        self.clear_form()
        self.refresh_members_table()

    def load_selected_member(self, _event: tk.Event[tk.Misc]) -> None:
        selected = self.members_table.selection()
        if not selected:
            return

        self.selected_member_id = int(selected[0])
        (
            puesto_trabajo,
            cedula,
            nombre,
            telefono,
            cargo,
            mesa_inicial,
            mesa_final,
        ) = self.members_table.item(selected[0], "values")
        self.nombre_var.set(nombre)
        self.cedula_var.set(cedula)
        self.telefono_var.set(telefono)
        self.puesto_trabajo_var.set(puesto_trabajo)
        self.cargo_var.set(cargo)
        self.mesa_inicial_var.set(mesa_inicial)
        self.mesa_final_var.set(mesa_final)

    def delete_selected_member(self) -> None:
        if self.selected_member_id is None:
            messagebox.showwarning("Sin selección", "Seleccione un integrante de la tabla.")
            return

        confirmed = messagebox.askyesno("Confirmar eliminación", "¿Desea eliminar este integrante?")
        if not confirmed:
            return

        self.database.delete_member(self.selected_member_id)
        self.clear_form()
        self.refresh_members_table()
        messagebox.showinfo("Eliminado", "Integrante eliminado correctamente.")

    def clear_form(self) -> None:
        self.selected_member_id = None
        self.nombre_var.set("")
        self.cedula_var.set("")
        self.telefono_var.set("")
        self.puesto_trabajo_var.set("")
        self.cargo_var.set(CARGOS[0])
        self.mesa_inicial_var.set("")
        self.mesa_final_var.set("")
        if hasattr(self, "members_table"):
            self.members_table.selection_remove(self.members_table.selection())


def print_diagnostic() -> None:
    """Muestra datos para confirmar qué archivo app.py se está ejecutando."""

    print(APP_TITLE)
    print(APP_VERSION)
    print(f"Archivo ejecutado: {Path(__file__).resolve()}")
    print(f"Base de datos: {DB_PATH.resolve()}")
    print("Campos: puesto, cédula, nombre, celular, cargo, mesa inicial y mesa final")
    print("Botones: Inicio, Integrantes, Malla de transmisión, Malla de recolección")


def main() -> None:
    if "--check" in sys.argv or "--version" in sys.argv:
        print_diagnostic()
        return

    app = TeamApp()
    app.mainloop()


if __name__ == "__main__":
    main()
