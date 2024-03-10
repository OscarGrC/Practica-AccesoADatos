from graphene import ObjectType, String, ID, DateTime, Boolean


class NotaType(ObjectType):
    id = ID()
    titulo = String()
    texto = String()
    fechaCreacion = DateTime()
    fechaUltimaModificacion = DateTime()
    isTerminado = Boolean()
    isImportante = Boolean()