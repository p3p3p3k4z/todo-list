import json
import os
from modelos.tarea import Tarea

BAULES_FOLDER = 'data/baules'

class GestionTareas:

    """
    Gestiona la colección de tareas, permitiendo realizar diversos metodos

    Attributes:
        archivo (str): La ruta al archivo JSON donde se almacenan las tareas.
        tareas (list): Una lista de objetos Tarea que representa todas las tareas gestionadas.
    """

    def __init__(self, nombre_archivo="tareas.json"):
        os.makedirs(BAULES_FOLDER, exist_ok=True)  # Crear la carpeta si no existe
        self.archivo = os.path.join(BAULES_FOLDER, self._asegurar_extension(nombre_archivo))
        self.tareas = self.cargar_tareas()

    def _asegurar_extension(self, nombre_archivo):
        if not nombre_archivo.lower().endswith(".json"):
            return nombre_archivo + ".json"
        return nombre_archivo

    # Cargar tareas desde el archivo JSON especificado
    def cargar_tareas(self):
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                return [Tarea.desde_diccionario(tarea) for tarea in datos]
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            print(f"Error al decodificar el archivo JSON: {self.archivo}. Se iniciará con una lista de tareas vacía.")
            return []
        except Exception as e:
            print(f"Ocurrió un error al cargar las tareas desde {self.archivo}: {e}")
            return []

    # Guardar tareas al archivo JSON especificado
    def guardar_tareas(self):
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                json.dump([tarea.a_diccionario() for tarea in self.tareas], f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ocurrió un error al guardar las tareas en {self.archivo}: {e}")

    def agregar_tarea(self, tarea):
        self.tareas.append(tarea)
        self.guardar_tareas()

    def editar_tarea(self, id_tarea, nuevos_datos):
        """
        Edita una tarea existente por su ID.

        Args:
            id_tarea (str): El ID de la tarea a editar.
            nuevos_datos (dict): Un diccionario con los nuevos datos de la tarea.
                Las claves del diccionario deben ser los nombres de los atributos de la tarea
                (por ejemplo, "titulo", "descripcion", "fecha_limite", "grupo", "estado", "medio").
        """
        tarea = next((t for t in self.tareas if t.get_id() == id_tarea), None)
        if tarea:
            if "titulo" in nuevos_datos:
                tarea.set_titulo(nuevos_datos["titulo"])
            if "descripcion" in nuevos_datos:
                tarea.set_descripcion(nuevos_datos["descripcion"])
            if "fecha_limite" in nuevos_datos:
                tarea.set_fecha_limite(nuevos_datos["fecha_limite"])
            if "grupo" in nuevos_datos:
                tarea.set_grupo(nuevos_datos["grupo"])
            if "estado" in nuevos_datos:
                tarea.set_estado(nuevos_datos["estado"])
            if "medio" in nuevos_datos:
                tarea.set_medio(nuevos_datos["medio"])
            self.guardar_tareas()
        else:
            raise ValueError("Tarea no encontrada.")

    def filtrar_tareas_por_estado(self, estado):
        return [tarea for tarea in self.tareas if tarea.get_estado().lower() == estado.lower()]

    def filtrar_tareas_por_grupo(self, grupo):
        return [tarea for tarea in self.tareas if tarea.get_grupo() and tarea.get_grupo().lower() == grupo.lower()]

    def cambiar_estado_tarea(self, id_tarea, nuevo_estado):
        tarea = next((t for t in self.tareas if t.get_id() == id_tarea), None)
        if tarea:
            tarea.set_estado(nuevo_estado)
            self.guardar_tareas()
        else:
            raise ValueError("Tarea no encontrada.")

    def obtener_tareas(self):
        return self.tareas

    def eliminar_tarea_por_id(self, id_tarea):
        tarea_a_eliminar = next((t for t in self.tareas if t.get_id() == id_tarea), None)
        if tarea_a_eliminar:
            self.tareas.remove(tarea_a_eliminar)
            self.guardar_tareas()
            return True
        return False

    @staticmethod
    def eliminar_baul(nombre_baul: str):
        """Elimina un archivo de baúl específico."""
        ruta_archivo = os.path.join(BAULES_FOLDER, GestionTareas._asegurar_extension_estatico(nombre_baul))
        try:
            os.remove(ruta_archivo)
            return True
        except FileNotFoundError:
            return False

    @staticmethod
    def _asegurar_extension_estatico(nombre_archivo):
        if not nombre_archivo.lower().endswith(".json"):
            return nombre_archivo + ".json"
        return nombre_archivo