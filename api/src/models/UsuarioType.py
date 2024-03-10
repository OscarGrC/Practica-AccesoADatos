import graphene


class UsuarioType(graphene.ObjectType):
    email = graphene.String()
    notas = graphene.List(graphene.ID)