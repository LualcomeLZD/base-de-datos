# Equipo de Transmisión y Recolección Plato

Aplicación sencilla para manejar la información de integrantes de un grupo llamado **Equipo de Transmisión y Recolección Plato**.

## Lenguaje y base de datos elegidos

Se eligió **Python** con **SQLite** porque es una combinación simple para empezar:

- Python es fácil de leer y modificar.
- SQLite guarda la información en un archivo local llamado `equipo_plato.db`.
- No se necesita instalar ni configurar un servidor de base de datos.
- La interfaz usa Tkinter, una librería gráfica incluida con Python en muchas instalaciones.

## Información que maneja

La base de datos guarda estos campos por integrante:

- Nombre
- Cédula
- Teléfono
- Cargo

Los cargos disponibles son:

- Recolector
- Transmisor
- Backup
- Coordinador de puesto

La cédula no se puede repetir, para evitar registrar dos veces a la misma persona.

## Opciones de la interfaz

La aplicación muestra tres botones principales:

- **Integrantes**: muestra todos los integrantes registrados y permite crear, editar o eliminar personas.
- **Malla de transmisión**: muestra los integrantes con cargo de transmisor, backup o coordinador de puesto.
- **Malla de recolección**: muestra los integrantes con cargo de recolector, backup o coordinador de puesto.

Para asignar a una persona a una malla, edita su **Cargo** en la sección de integrantes. Por ejemplo, si seleccionas el cargo **Transmisor**, esa persona aparecerá en la **Malla de transmisión**; si seleccionas **Recolector**, aparecerá en la **Malla de recolección**.

## Cómo ejecutar la aplicación

1. Instala Python 3.10 o superior.
2. Desde esta carpeta, ejecuta:

   ```bash
   python app.py
   ```

3. Usa la ventana para guardar, editar, eliminar o revisar integrantes por malla.

## Uso básico

- Para registrar una persona, escribe nombre, cédula, teléfono y cargo, y presiona **Guardar**.
- Para editar una persona, selecciónala en la tabla, cambia los datos y presiona **Guardar**.
- Para eliminar una persona, selecciónala en la tabla y presiona **Eliminar**.
- Para iniciar un registro nuevo, presiona **Limpiar**.
- Para cambiar entre listados, usa los botones **Integrantes**, **Malla de transmisión** y **Malla de recolección**.

## Archivo de datos

Cuando se ejecuta la aplicación, se crea automáticamente el archivo `equipo_plato.db` en esta carpeta. Ese archivo contiene la base de datos local.

Si ya tenías una base creada con una versión anterior de la aplicación, el campo **Cargo** se agrega automáticamente al abrir el programa y los integrantes existentes quedan inicialmente como **Recolector**.
