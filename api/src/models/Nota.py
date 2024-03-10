from datetime import datetime
import uuid

class Nota:

    def __init__(self
                 , titulo
                 , texto
                 , isTerminado : bool
                 , isImportante : bool
                 , id = uuid.uuid4()
                 , fechaCreacion = datetime.now().strftime("%Y-%m-%d %H:%M")
                 , fechaUltimaModificacion = datetime.now().strftime("%Y-%m-%d %H:%M")):
        self.id = id
        self.titulo = titulo
        self.texto = texto
        self.fechaCreacion = fechaCreacion
        self.fechaUltimaModificacion = fechaUltimaModificacion
        self.isTerminado = isTerminado
        self.isImportante = isImportante

    def to_dict(self):
        return {
            "id": str(self.id),
            "titulo": self.titulo,
            "texto": self.texto,
            "fechaCreacion": self.fechaCreacion,
            "fechaUltimaModificacion": self.fechaUltimaModificacion,
            "isTerminado": self.isTerminado,
            "isImportante": self.isImportante
        }
    
    
