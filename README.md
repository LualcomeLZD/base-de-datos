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
- Lugar de votación
- Cargo

Los cargos disponibles son:

- Recolector
- Transmisor
- Backup
- Coordinador de puesto

La cédula no se puede repetir, para evitar registrar dos veces a la misma persona.

## Opciones de la interfaz

La aplicación abre en una pantalla de inicio con botones. Desde esa pantalla se puede entrar a cada sección sin que todo se muestre de golpe:

- **Integrantes**: abre el formulario para crear, editar, limpiar o eliminar integrantes. También muestra el listado completo de integrantes registrados.
- **Malla de transmisión**: muestra un informe/listado de integrantes con cargo **Transmisor**, **Backup** o **Coordinador de puesto**.
- **Malla de recolección**: muestra un informe/listado de integrantes con cargo **Recolector** o **Backup**.

Para asignar a una persona a una malla, entra a **Integrantes** y selecciona su **Cargo**. Por ejemplo, si seleccionas **Transmisor** o **Coordinador de puesto**, esa persona aparecerá en la **Malla de transmisión**. Si seleccionas **Recolector**, aparecerá en la **Malla de recolección**.

## Cómo ejecutar la aplicación

1. Instala Python 3.10 o superior.
2. Desde esta carpeta, ejecuta:

   ```bash
   python app.py
   ```

3. Usa la pantalla inicial para entrar a **Integrantes**, **Malla de transmisión** o **Malla de recolección**.

## Uso básico

- Para registrar una persona, entra a **Integrantes**, escribe nombre, cédula, teléfono, lugar de votación y cargo, y presiona **Guardar**.
- Para editar una persona, entra a **Integrantes**, selecciónala en la tabla, cambia los datos y presiona **Guardar**.
- Para eliminar una persona, entra a **Integrantes**, selecciónala en la tabla y presiona **Eliminar**.
- Para iniciar un registro nuevo, presiona **Limpiar**.
- Para ver los informes, usa los botones **Malla de transmisión** y **Malla de recolección**.

## Archivo de datos

Cuando se ejecuta la aplicación, se crea automáticamente el archivo `equipo_plato.db` en esta carpeta. Ese archivo contiene la base de datos local.

Si ya tenías una base creada con una versión anterior de la aplicación, los campos **Cargo** y **Lugar de votación** se agregan automáticamente al abrir el programa. Los integrantes existentes quedan inicialmente como **Recolector** y con el lugar de votación vacío hasta que los edites.
