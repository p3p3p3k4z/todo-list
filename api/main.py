from fastapi import FastAPI, HTTPException, Path, Depends, Body
from typing import List, Optional
from pydantic import BaseModel
import uuid
from servicios.gestion_tareas import GestionTareas
from modelos.tarea import Tarea  # Asegúrate de que este import sea correcto

app = FastAPI()

class TareaAPI(BaseModel):
    id: Optional[str] = None
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    fecha_limite: Optional[str] = None
    grupo: Optional[str] = None
    estado: Optional[str] = "pendiente"
    medio: Optional[str] = None

def obtener_gestor_tareas(nombre_baul: str = Path(..., title="Nombre del baúl")):
    """Función de dependencia para obtener el gestor de tareas para un baúl."""
    return GestionTareas(nombre_baul)

@app.post("/baules/{nombre_baul}/tareas/", response_model=TareaAPI, status_code=201)
async def crear_tarea(nombre_baul: str = Path(..., title="Nombre del baúl"), tarea: TareaAPI = Body(...), gestor: GestionTareas = Depends(obtener_gestor_tareas)):
    """Crea una nueva tarea en el baúl especificado."""
    if tarea.estado not in Tarea.ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail=f"Estado no válido: '{tarea.estado}'. Los estados válidos son: {Tarea.ESTADOS_VALIDOS}")
    tarea_servicio = Tarea(
        titulo=tarea.titulo,
        descripcion=tarea.descripcion,
        fecha_limite=tarea.fecha_limite,
        grupo=tarea.grupo,
        estado=tarea.estado,
        medio=tarea.medio
    )
    gestor.agregar_tarea(tarea_servicio)
    tarea.id = tarea_servicio.get_id() # Asignar el ID generado
    return tarea

@app.get("/baules/{nombre_baul}/tareas/", response_model=List[TareaAPI])
async def listar_tareas(nombre_baul: str = Path(..., title="Nombre del baúl"), gestor: GestionTareas = Depends(obtener_gestor_tareas)):
    """Lista todas las tareas del baúl especificado."""
    tareas_servicio = gestor.obtener_tareas()
    return [TareaAPI(**tarea.a_diccionario()) for tarea in tareas_servicio]

@app.get("/baules/{nombre_baul}/tareas/{id_tarea}", response_model=TareaAPI)
async def obtener_tarea(nombre_baul: str = Path(..., title="Nombre del baúl"), id_tarea: str = Path(..., title="ID de la tarea a obtener"), gestor: GestionTareas = Depends(obtener_gestor_tareas)):
    """Obtiene una tarea específica por su ID."""
    tareas = gestor.obtener_tareas()
    for tarea in tareas:
        if tarea.get_id() == id_tarea:
            return TareaAPI(**tarea.a_diccionario())
    raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.put("/baules/{nombre_baul}/tareas/{id_tarea}", response_model=TareaAPI)
async def actualizar_tarea(nombre_baul: str = Path(..., title="Nombre del baúl"), id_tarea: str = Path(..., title="ID de la tarea a actualizar"), tarea_actualizada: TareaAPI = Body(...), gestor: GestionTareas = Depends(obtener_gestor_tareas)):
    """Actualiza una tarea existente en el baúl especificado."""
    tareas = gestor.obtener_tareas()
    for index, tarea in enumerate(tareas):
        if tarea.get_id() == id_tarea:
            tarea_servicio = Tarea(
                id_tarea=id_tarea,
                titulo=tarea_actualizada.titulo,
                descripcion=tarea_actualizada.descripcion,
                fecha_limite=tarea_actualizada.fecha_limite,
                grupo=tarea_actualizada.grupo,
                estado=tarea_actualizada.estado,
                medio=tarea_actualizada.medio
            )
            tareas[index] = tarea_servicio
            gestor.tareas = tareas
            gestor.guardar_tareas()
            return TareaAPI(**tarea_servicio.a_diccionario())
    raise HTTPException(status_code=404, detail="Tarea no encontrada")
    raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.put("/baules/{nombre_baul}/tareas/{id_tarea}/completar", response_model=TareaAPI)
async def completar_tarea(nombre_baul: str = Path(..., title="Nombre del baúl"), id_tarea: str = Path(..., title="ID de la tarea a completar"), gestor: GestionTareas = Depends(obtener_gestor_tareas)):
    """Marca una tarea como completada en el baúl especificado."""
    tareas = gestor.obtener_tareas()
    for tarea in tareas:
        if tarea.get_id() == id_tarea:
            tarea.set_estado("completada")
            gestor.guardar_tareas()
            return TareaAPI(**tarea.a_diccionario())
    raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.delete("/baules/{nombre_baul}/tareas/{id_tarea}", status_code=204)
async def eliminar_tarea(nombre_baul: str = Path(..., title="Nombre del baúl"), id_tarea: str = Path(..., title="ID de la tarea a eliminar"), gestor: GestionTareas = Depends(obtener_gestor_tareas)):
    """Elimina una tarea del baúl especificado."""
    if gestor.eliminar_tarea_por_id(id_tarea):
        return
    raise HTTPException(status_code=404, detail="Tarea no encontrada")

@app.delete("/baules/{nombre_baul}", status_code=204)
async def eliminar_baul_api(nombre_baul: str = Path(..., title="Nombre del baúl")):
    """Elimina un baúl específico."""
    if GestionTareas.eliminar_baul(nombre_baul):
        return
    raise HTTPException(status_code=404, detail=f"No se encontró el baúl '{nombre_baul}'.")