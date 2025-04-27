import os
from servicios.gestion_tareas import GestionTareas
from servicios.terminal_ui import (
    mostrar_menu_inferior,
    formato_tareas,
    obtener_input,
    mostrar_mensaje,
    seleccionar_baul,
    obtener_nueva_tarea,
    obtener_id_tarea,
    obtener_nuevo_estado,
    obtener_grupo_filtro,
    obtener_estado_filtro,
    limpiar_consola,
)
from modelos.tarea import Tarea

def obtener_baules_disponibles():
    """Obtiene la lista de archivos .json en la carpeta 'data/baules/'."""
    ruta_baules = 'data/baules/'
    if not os.path.exists(ruta_baules):
        os.makedirs(ruta_baules)
        return []
    return [f.replace('.json', '') for f in os.listdir(ruta_baules) if f.endswith('.json')]

def main():
    limpiar_consola()
    baules_disponibles = obtener_baules_disponibles()
    nombre_baul_seleccionado = seleccionar_baul(baules_disponibles)

    if nombre_baul_seleccionado is None:
        mostrar_mensaje("Saliendo de la aplicación.", tipo="error")
        return

    gestor = GestionTareas(f"{nombre_baul_seleccionado}.json")
    mostrar_mensaje(f"¡Baúl seleccionado! Trabajando con: {os.path.basename(gestor.archivo)}", tipo="exito")

    while True:
        limpiar_consola()
        tareas = gestor.obtener_tareas()
        formato_tareas(tareas, os.path.basename(gestor.archivo))
        mostrar_menu_inferior(os.path.basename(gestor.archivo))
        opcion = obtener_input("Selecciona una opción: ").upper()

        if opcion == "N":
            tarea_data = obtener_nueva_tarea()
            tarea = Tarea(tarea_data["titulo"], tarea_data["descripcion"], tarea_data["fecha_limite"], tarea_data["grupo"], tarea_data["estado"], tarea_data["medio"])
            gestor.agregar_tarea(tarea)
            mostrar_mensaje(f"Tarea '{tarea.get_titulo()}' agregada.", tipo="exito")
        elif opcion == "L":
            pass  # La lista ya se muestra al inicio de cada ciclo
        elif opcion == "FE":
            estado_filtro = obtener_estado_filtro()
            tareas_filtradas = gestor.filtrar_tareas_por_estado(estado_filtro)
            formato_tareas(tareas_filtradas, os.path.basename(gestor.archivo))
            obtener_input("[bold yellow]Presiona Enter para continuar...[/bold yellow]") # Pausa para ver el resultado
        elif opcion == "FG":
            grupo_filtro = obtener_grupo_filtro()
            tareas_filtradas = gestor.filtrar_tareas_por_grupo(grupo_filtro)
            formato_tareas(tareas_filtradas, os.path.basename(gestor.archivo))
            obtener_input("[bold yellow]Presiona Enter para continuar...[/bold yellow]") # Pausa para ver el resultado
        elif opcion == "CE":
            id_tarea = obtener_id_tarea()
            nuevo_estado = obtener_nuevo_estado()
            try:
                gestor.cambiar_estado_tarea(id_tarea, nuevo_estado)
                mostrar_mensaje(f"Estado de la tarea con ID {id_tarea} cambiado a '{nuevo_estado}'.", tipo="exito")
            except ValueError as e:
                mostrar_mensaje(str(e), tipo="error")
        elif opcion == "MC":
            id_tarea = obtener_id_tarea()
            try:
                gestor.cambiar_estado_tarea(id_tarea, "completada")
                mostrar_mensaje(f"Tarea con ID {id_tarea} marcada como completada.", tipo="exito")
            except ValueError as e:
                mostrar_mensaje(str(e), tipo="error")
        elif opcion == "E":
            id_tarea = obtener_id_tarea()
            if gestor.eliminar_tarea_por_id(id_tarea):
                mostrar_mensaje(f"Tarea con ID {id_tarea} eliminada.", tipo="exito")
            else:
                mostrar_mensaje("Tarea no encontrada.", tipo="error")
        elif opcion == "CB":
            nuevo_nombre_baul = seleccionar_baul(obtener_baules_disponibles())
            if nuevo_nombre_baul:
                gestor = GestionTareas(f"{nuevo_nombre_baul}.json")
                mostrar_mensaje(f"Cambiado al baúl: {os.path.basename(gestor.archivo)}", tipo="exito")
            else:
                mostrar_mensaje("Cambio de baúl cancelado.", tipo="warning")
        elif opcion == "Q":
            mostrar_mensaje("Saliendo...", tipo="normal")
            break
        else:
            mostrar_mensaje("Opción no válida.", tipo="error")

if __name__ == "__main__":
    main()