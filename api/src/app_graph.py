import asyncio
from flask import Flask, request
from flask_graphql import GraphQLView
import graphene
from graphene import Mutation
from models.UsuarioType import UsuarioType
from repositories.usuario_repository_maria import UsuarioRepostoryMaria
from mappers.mappers import NotaMapper

from models.NotaType import NotaType
from repositories.notas_repository_maria import NotasRepositoryMaria
from repositories.notas_repository_mongo import NotasRepositoryMongo
from repositories.usuario_repository_mongo import UsuarioRepostoryMongo

# Define las mutaciones

DB_TYPE = "mariadb"
if DB_TYPE == "mongodb":
    nota_repo = NotasRepositoryMongo()
    user_repo = UsuarioRepostoryMongo()
elif DB_TYPE == "mariadb":
    nota_repo = NotasRepositoryMaria()
    user_repo = UsuarioRepostoryMaria()

class CrearNota(graphene.Mutation):
    class Arguments:
        titulo = graphene.String(required=True)
        texto = graphene.String(required=True)
        isImportante = graphene.Boolean(required=True)
        isTerminado = graphene.Boolean(required=True)

    success = graphene.Boolean()
    id = graphene.ID()
    message = graphene.String()

    def mutate(self, info,titulo, texto, isImportante, isTerminado):
        # Validar las credenciales del usuario
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            return CrearNota(success=False, message="Credenciales inválidas" , id=id)

        # Crear la nota y obtener su ID
        nota_id = nota_repo.crear_nota(titulo, texto, isImportante, isTerminado, email)
        if nota_id:
            user_repo.agregar_nota_a_usuario(email, nota_id)
            return CrearNota(success=True, message="Nota Guardada" ,id=nota_id)
        # Retornar la ID de la nota y éxito
        else:
            return CrearNota(success=False, message="No se ha podido guardar la nota", id=nota_id)
    
class EliminarNota(Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    res = graphene.Boolean()
    message = graphene.String()    
    id = graphene.ID()

    def mutate(self, info, id):
        # Validar las credenciales del usuario
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            return (EliminarNota(id, "Credenciales invalidas", None))

        if (nota_repo.borrar_nota(id, email) == 0):
            return (EliminarNota(False, "La nota no se ha podido eliminar"), id)
        else:
            user_repo.borrar_nota_de_usuario(id)
            return (EliminarNota(True, "Nota eliminada", id))

class DeleteAll(Mutation):
    class Arguments:
        confirmacion = graphene.String(required=True)

    message = graphene.String()

    def mutate(self, info, confirmacion):
        # Validar las credenciales del usuario
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            return DeleteAll("Credenciales inválidas")

        if confirmacion == True:
            return DeleteAll("No has confirmado que quieres borrar todas las notas")


        if (nota_repo.delete_all_notas(confirmacion=confirmacion, usuario_email=email)):
            user_repo.borrar_todas_las_notas_de_usuario(email)
            return (DeleteAll("Notas eliminadas correctamente"))
        else:
            return (DeleteAll("No se han podido borrar las notas"))
        
class ActualizarNota(Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        titulo = graphene.String(required=False)
        texto = graphene.String(required=False)
        isImportante = graphene.Boolean(required=False)
        isTerminado = graphene.Boolean(required=False)
    
    success = graphene.Boolean()
    message = graphene.String()    

    def mutate (self, info, id, titulo=None, texto=None, isImportante=None, isTerminado=None):
        # Validar las credenciales del usuario
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            return ActualizarNota(success=False, message="Credenciales inválidas")
        
        if nota_repo.actualizar_nota(nota_id=id, email_usuario=email, titulo=titulo, texto=texto, isTerminado=isTerminado, isImportante=isImportante):
            return ActualizarNota(success=True, message="Nota Actualizada")
        else:
            return ActualizarNota(success=False, message="No se ha podido actualizar la nota")

class EnviarNota (Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        email_destino = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    id = graphene.ID()

    def mutate(self, info, id, email_destino):
        # Validar las credenciales del usuario
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            return EnviarNota(success=False, message="Credenciales inválidas")
        
        if user_repo.obtener_usuario_por_email(email_destino) is None:
            return EnviarNota(success=False, message="El usuario receptor no existe")
        
        id_nota_enviada = nota_repo.enviar_nota(id,email,email_destino)
        if id_nota_enviada is None:
            return (EnviarNota(success=False, message="La nota no se ha podido enviar debido a un error o que no le pertenece")) 
        else:
            return (EnviarNota(success=True, message="La nota ha sido enviada correctamente", id=id_nota_enviada))  

class NuevoUsuario(Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    email = graphene.ID()

    def mutate(self,info, email, password):
        if not user_repo.obtener_usuario_por_email(email) is None:
            return NuevoUsuario(success=False, message="Ya existe un usuario con este email", email=email)
        
        if user_repo.crear_usuario(email, password) is None:
            return NuevoUsuario(success=False, message="El usuario no ha podido crearse", email=email)
        else:
            return NuevoUsuario(success=True, message="El usuario ha sido creado", email=email)

class ActualizarUsuario(Mutation):
    class Arguments:
        password_confirmacion = graphene.String(required=True)
        new_password = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, password_confirmacion, new_password):
        # Validar las credenciales del usuario
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            return ActualizarUsuario(success=False, message="Credenciales inválidas")
        
        if not user_repo.validar_credenciales(email, password_confirmacion):
            return ActualizarUsuario(success=False, message="La contraseña de confirmación no es válida")

        if user_repo.actualizar_usuario(email, new_password):
            return ActualizarUsuario(success=True, message="Contraseña guardada correctamente")
        else:
            return ActualizarUsuario(success=False, message="La contraseña no se ha guadado correctamente")
        
class EliminarUsuario (Mutation):
    class Arguments:
        confirmacion = graphene.Boolean(required = True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, confirmacion):
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            return EliminarUsuario(success=False, message="Credenciales inválidas")
        if not confirmacion:
            return EliminarUsuario(success=False, message="Debes confirmar el borrado del usuario")
        
        # Borrar todas las notas del usuario
        if nota_repo.delete_all_notas(email, confirmacion):
            # Si se borran las notas, proceder a borrar el usuario
            if user_repo.borrar_usuario(email):
                return EliminarUsuario(success=True, message="Usuario borrado correctamente")
            else:
                return EliminarUsuario(success=False, message="No se pudo borrar el usuario")
        else:
            return EliminarUsuario(success=False, message="No se pudieron borrar las notas del usuario")

class Mutations(graphene.ObjectType):
    CrearNota = CrearNota.Field()
    EliminarNota = EliminarNota.Field()
    DeleteAll = DeleteAll.Field()
    ActualizarNota = ActualizarNota.Field()
    EnviarNota = EnviarNota.Field()
    NuevoUsuario = NuevoUsuario.Field()
    ActualizarUsuario = ActualizarUsuario.Field()
    EliminarUsuario = EliminarUsuario.Field()

# Define las consultas (queries)
class Query(graphene.ObjectType):
    notas = graphene.List(NotaType)
    nota_por_id = graphene.Field(NotaType, id=graphene.ID(required=True))
    usuario = graphene.Field(UsuarioType)
    
    def resolve_notas(self, notas):
        
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            raise Exception("Credenciales inválidas")
        notas = nota_repo.obtener_notas_por_usuario(email)
        return [NotaMapper.map_nota_to_notatype(nota) for nota in notas]
    
    def resolve_nota_por_id(self, info, id):
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            raise Exception("Credenciales inválidas")
        nota = nota_repo.obtener_nota_por_id(id, email)
        return NotaMapper.map_nota_to_notatype(nota)
    
    def resolve_usuario(self, usuario):
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not user_repo.validar_credenciales(email, password):
            raise Exception("Credenciales inválidas")

        return user_repo.obtener_usuario_por_email(email)
        



schema = graphene.Schema(query=Query, mutation=Mutations)

app = Flask(__name__)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

if __name__ == '__main__':
    asyncio.run(debug=True)
