import uuid
import json

class Tarea:
    ESTADOS_VALIDOS = ["pendiente", "asignada", "en proceso", "completada", "cancelada"]

    def __init__(self, titulo, descripcion, fecha_limite, grupo, estado="pendiente", medio=None, id_tarea=None):
        self._id = id_tarea or str(uuid.uuid4())
        self._titulo = titulo
        self._descripcion = descripcion
        self._fecha_limite = fecha_limite
        self._grupo = grupo
        self.set_estado(estado)  # Se utiliza el setter para validar el estado
        self._medio = medio  # Ruta a imagen, gif o video

    def get_id(self):
        return self._id

    def get_titulo(self):
        return self._titulo

    def set_titulo(self, nuevo_titulo):
        self._titulo = nuevo_titulo

    def get_descripcion(self):
        return self._descripcion

    def set_descripcion(self, nueva_descripcion):
        self._descripcion = nueva_descripcion

    def get_fecha_limite(self):
        return self._fecha_limite

    def set_fecha_limite(self, nueva_fecha):
        self._fecha_limite = nueva_fecha

    def get_grupo(self):
        return self._grupo

    def set_grupo(self, nuevo_grupo):
        self._grupo = nuevo_grupo

    def get_estado(self):
        return self._estado

    def set_estado(self, nuevo_estado):
        if nuevo_estado in self.ESTADOS_VALIDOS:
            self._estado = nuevo_estado
        else:
            raise ValueError("Estado no válido.")

    def get_medio(self):
        return self._medio

    def set_medio(self, nuevo_medio):
        self._medio = nuevo_medio

    def __str__(self):
        return (f"ID: {self.get_id()}\n"
                f"Título: {self.get_titulo()}\n"
                f"Descripción: {self.get_descripcion()}\n"
                f"Fecha límite: {self.get_fecha_limite()}\n"
                f"Grupo: {self.get_grupo()}\n"
                f"Estado: {self.get_estado().upper()}\n"
                f"Medio: {self.get_medio() if self.get_medio() else 'Ninguno'}")

    def a_diccionario(self):
        return {
            "id": self.get_id(),
            "titulo": self.get_titulo(),
            "descripcion": self.get_descripcion(),
            "fecha_limite": self.get_fecha_limite(),
            "grupo": self.get_grupo(),
            "estado": self.get_estado(),
            "medio": self.get_medio()
        }

    @staticmethod
    def desde_diccionario(datos):
        tarea = Tarea(
            titulo=datos["titulo"],
            descripcion=datos["descripcion"],
            fecha_limite=datos["fecha_limite"],
            grupo=datos["grupo"],
            estado=datos.get("estado", "pendiente"),
            medio=datos.get("medio")
        )
        tarea._id = datos["id"]  # Asignar el ID desde el diccionario
        return tarea
