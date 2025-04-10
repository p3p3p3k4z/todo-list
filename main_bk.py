import os
from servicios.gestion_tareas import GestionTareas
from modelos.tarea import Tarea

# Decorador para mejorar la visualización de las tareas
def formato_tareas(func):
    def wrapper(gestor, *args, **kwargs):
        tareas = func(gestor, *args, **kwargs)
        if tareas:
            for tarea in tareas:
                print("-" * 50)
                print(f"ID: {tarea.get_id()}")
                print(f"Título: {tarea.get_titulo()}")
                print(f"Descripción: {tarea.get_descripcion()}")
                print(f"Fecha límite: {tarea.get_fecha_limite()}")
                print(f"Grupo: {tarea.get_grupo()}")
                print(f"Estado: {tarea.get_estado().upper()}")
                print(f"Medio: {tarea.get_medio() if tarea.get_medio() else 'Ninguno'}")
                print("-" * 50)
        else:
            print(f"No hay tareas para mostrar en este baúl.")
    return wrapper

# Función para mostrar el menú de opciones
def mostrar_menu(nombre_baul):
    print(f"\n--- Menú ({nombre_baul}) ---")
    print("1. Agregar tarea")
    print("2. Listar todas las tareas")
    print("3. Filtrar tareas por estado")
    print("4. Filtrar tareas por grupo")
    print("5. Cambiar estado de tarea")
    print("6. Marcar tarea como completada")
    print("7. Eliminar tarea")
    print("8. Cambiar de baúl")  # Nueva opción
    print("9. Salir")

# Función para agregar una nueva tarea
def agregar_tarea(gestor):
    titulo = input("Título de la tarea: ")
    descripcion = input("Descripción de la tarea: ")
    fecha_limite = input("Fecha límite (YYYY-MM-DD): ")
    grupo = input("Grupo de la tarea: ")
    estado = input("Estado de la tarea (pendiente, asignada, en proceso, completada, cancelada): ")
    medio = input("Medio asociado (ruta a imagen/gif/video o dejar vacío): ")

    tarea = Tarea(titulo, descripcion, fecha_limite, grupo, estado, medio)
    gestor.agregar_tarea(tarea)
    print(f"Tarea '{titulo}' agregada correctamente al baúl.")

# Función para listar todas las tareas
@formato_tareas
def listar_tareas(gestor):
    return gestor.obtener_tareas()

# Función para filtrar tareas por estado
def filtrar_tareas_por_estado(gestor):
    estado = input("Filtrar por estado (pendiente, asignada, en proceso, completada, cancelada): ")
    tareas_filtradas = gestor.filtrar_tareas_por_estado(estado)
    if tareas_filtradas:
        for tarea in tareas_filtradas:
            print(tarea)
    else:
        print(f"No se encontraron tareas con el estado '{estado}' en este baúl.")

# Función para filtrar tareas por grupo
def filtrar_tareas_por_grupo(gestor):
    grupo = input("Filtrar por grupo: ")
    tareas_filtradas = gestor.filtrar_tareas_por_grupo(grupo)
    if tareas_filtradas:
        for tarea in tareas_filtradas:
            print(tarea)
    else:
        print(f"No se encontraron tareas con el grupo '{grupo}' en este baúl.")

# Función para cambiar el estado de una tarea
def cambiar_estado(gestor):
    id_tarea = input("Ingresa el ID de la tarea para cambiar el estado: ")
    nuevo_estado = input("Nuevo estado de la tarea (pendiente, asignada, en proceso, completada, cancelada): ")
    try:
        gestor.cambiar_estado_tarea(id_tarea, nuevo_estado)
        print(f"Estado de la tarea con ID {id_tarea} cambiado a '{nuevo_estado}' en este baúl.")
    except ValueError as e:
        print(e)

# Función para marcar una tarea como completada
def marcar_completada(gestor):
    id_tarea = input("Ingresa el ID de la tarea para marcar como completada: ")
    try:
        gestor.cambiar_estado_tarea(id_tarea, "completada")
        print(f"Tarea con ID {id_tarea} marcada como completada en este baúl.")
    except ValueError as e:
        print(e)

# Función para eliminar una tarea
def eliminar_tarea(gestor):
    id_tarea = input("Ingresa el ID de la tarea a eliminar: ")
    if gestor.eliminar_tarea_por_id(id_tarea):
        print(f"Tarea con ID {id_tarea} eliminada del baúl.")
    else:
        print("Tarea no encontrada en este baúl.")

def main():
    nombre_baul = input("Ingrese el nombre del baúl de tareas (dejar en blanco para 'tareas.json'): ")
    if not nombre_baul:
        nombre_baul = "tareas.json"
    gestor = GestionTareas(nombre_baul)

    while True:
        mostrar_menu(os.path.basename(gestor.archivo))  # Mostrar solo el nombre del archivo
        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            agregar_tarea(gestor)
        elif opcion == "2":
            listar_tareas(gestor)
        elif opcion == "3":
            filtrar_tareas_por_estado(gestor)
        elif opcion == "4":
            filtrar_tareas_por_grupo(gestor)
        elif opcion == "5":
            cambiar_estado(gestor)
        elif opcion == "6":
            marcar_completada(gestor)
        elif opcion == "7":
            eliminar_tarea(gestor)
        elif opcion == "8":
            nuevo_nombre_baul = input("Ingrese el nombre del nuevo baúl (dejar en blanco para 'tareas.json'): ")
            if not nuevo_nombre_baul:
                nuevo_nombre_baul = "tareas.json"
            gestor = GestionTareas(nuevo_nombre_baul)
        elif opcion == "9":
            print("Saliendo...")
            break
        # Aquí podrías añadir la opción 10 si decides integrarla con la API
        else:
            print("Opción no válida.")

if __name__ == "__main__":
    main()