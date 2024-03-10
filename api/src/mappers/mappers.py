from graphene import ObjectType
from datetime import datetime
from models.NotaType import NotaType
from models.Nota import Nota

class NotaMapper(ObjectType):
    @staticmethod
    def map_nota_to_notatype(nota : Nota) -> NotaType:
        return NotaType(
            titulo=nota["titulo"],
            texto=nota["texto"],
            isTerminado=nota["isTerminado"],
            isImportante=nota["isImportante"],
            id=nota["_id"],
            fechaCreacion=datetime.strptime(nota["fechaCreacion"], "%Y-%m-%d %H:%M"),
            fechaUltimaModificacion=datetime.strptime(nota["fechaUltimaModificacion"], "%Y-%m-%d %H:%M")
        )
    