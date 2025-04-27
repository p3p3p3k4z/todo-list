import os
from rich.console import Console
from rich.panel import Panel
from pynput import keyboard
from data.ascci import baul_ascci, ascci_banner
from rich.table import Table
from rich.style import Style
from modelos.tarea import Tarea

console = Console()

def seleccionar_baul(baules_disponibles):
    """Permite al usuario seleccionar un baúl usando las flechas izquierda/derecha y Enter."""
    if not baules_disponibles:
        console.print(Panel("[bold yellow]No se encontraron baúles disponibles en data/baules/.[/bold yellow]\n"
                              "[italic]Crea archivos .json en esa carpeta para comenzar.[/italic]"))
        return None

    seleccion = 0
    seleccionado = False  # Variable para indicar si se presionó Enter

    def mostrar_seleccion(current_selection):
        console.clear()
        console.print(ascci_banner, style="green")
        console.print(baul_ascci, style="bold blue")
        console.print(Panel(f"[bold green]Baúl seleccionado:[/bold green] [bold reverse white]{baules_disponibles[current_selection]}[/bold reverse white]\n"
                              "[italic yellow]Usa las flechas izquierda/derecha para navegar y Enter para seleccionar. Presiona 'q' para salir.[/italic yellow]"))

    mostrar_seleccion(seleccion)

    def on_press(key):
        nonlocal seleccion, seleccionado
        try:
            if key == keyboard.Key.left:
                seleccion = (seleccion - 1) % len(baules_disponibles)
                mostrar_seleccion(seleccion)
            elif key == keyboard.Key.right:
                seleccion = (seleccion + 1) % len(baules_disponibles)
                mostrar_seleccion(seleccion)
            elif key == keyboard.Key.enter:
                seleccionado = True
                listener.stop()
            elif key.char == 'q':
                listener.stop()
                return False
        except AttributeError:
            pass

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

    if seleccionado:
        return baules_disponibles[seleccion]
    else:
        return None

def mostrar_menu_inferior(nombre_baul):
    #console.print(Panel(f"[bold green]--- Menú ({nombre_baul}) ---[/bold green]", expand=False))
    comandos = {
        "N": "Agregar tarea",
        "L": "Listar tareas",
        "FE": "Filtrar por estado",
        "FG": "Filtrar por grupo",
        "CE": "Cambiar estado",
        "MC": "Marcar completada",
        "E": "Eliminar tarea",
        "CB": "Cambiar baúl",
        "Q": "Salir",
    }
    comando_str = " | ".join(f"[yellow]{key}[/yellow]:[white]{value}[/white]" for key, value in comandos.items())
    console.print(Panel(comando_str, expand=False))

def formato_tareas(tareas, nombre_baul_archivo):
    if not tareas:
        console.print(Panel("[bold red]No hay tareas para mostrar.[/bold red]"))
        return

    console.print(Panel(f"[bold cyan]Tareas en {nombre_baul_archivo}[/bold cyan]"))
    tareas_mostradas = 0
    tareas_por_pagina = 5  

    for i in range(0, len(tareas), tareas_por_pagina):
        pagina = tareas[i : i + tareas_por_pagina]
        for tarea in pagina:
            estado = tarea.get_estado().upper()
            estado_style = Style(bold=True)
            if estado == "COMPLETADA":
                estado_style += Style(color="green")
            elif estado == "EN PROCESO":
                estado_style += Style(color="blue")
            elif estado == "ASIGNADA":
                estado_style += Style(color="magenta")
            elif estado == "CANCELADA":
                estado_style += Style(color="red")
            else:
                estado_style += Style(color="yellow")

            table = Table(show_header=False, box=None)
            table.add_column(style="bold yellow", justify="left", width=15)
            table.add_column(justify="left", overflow="fold")

            table.add_row("ID:", str(tarea.get_id()))
            table.add_row("Descripción:", tarea.get_descripcion())
            table.add_row("Fecha límite:", tarea.get_fecha_limite() or "[italic red]Ninguna[/italic red]")
            table.add_row("Grupo:", tarea.get_grupo())
            table.add_row("Estado:", f"[{estado_style}]{estado}[/{estado_style}]")
            table.add_row("Medio:", tarea.get_medio() or "[italic red]Ninguno[/italic red]")

            panel = Panel(table, title=f"[bold bright_magenta]{tarea.get_titulo()}[/bold bright_magenta]")
            console.print(panel)

def obtener_input(prompt):
    return console.input(prompt)

def mostrar_mensaje(mensaje, tipo="normal"):
    if tipo == "exito":
        console.print(f"[green]{mensaje}[/green]")
    elif tipo == "error":
        console.print(f"[bold red]{mensaje}[/bold red]")
    elif tipo == "warning":
        console.print(f"[yellow]{mensaje}[/yellow]")
    else:
        console.print(mensaje)

def obtener_nueva_tarea():
    titulo = obtener_input("Título: ")
    descripcion = obtener_input("Descripción: ")
    fecha_limite = obtener_input("Fecha límite (YYYY-MM-DD): ")
    grupo = obtener_input("Grupo: ")
    estado = obtener_input(f"Estado ({', '.join(Tarea.ESTADOS_VALIDOS)}): ")
    medio = obtener_input("Medio (opcional): ")
    return {"titulo": titulo, "descripcion": descripcion, "fecha_limite": fecha_limite, "grupo": grupo, "estado": estado, "medio": medio}

def obtener_id_tarea():
    return obtener_input("ID de la tarea: ")

def obtener_nuevo_estado():
    return obtener_input(f"Nuevo estado ({', '.join(Tarea.ESTADOS_VALIDOS)}): ")

def obtener_grupo_filtro():
    return obtener_input("Grupo a filtrar: ")

def obtener_estado_filtro():
    return obtener_input(f"Estado a filtrar ({', '.join(Tarea.ESTADOS_VALIDOS)}): ")

def limpiar_consola():
    console.clear()