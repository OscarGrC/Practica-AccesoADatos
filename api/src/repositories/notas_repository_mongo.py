from flask import jsonify
from pymongo import MongoClient
import models.Nota as Nota
import uuid
from datetime import datetime

class NotasRepositoryMongo:
    def __init__(self,):
        self.client = MongoClient('mongodb://root:example@mongodb:27017/')
        self.db = self.client["Notas"]
        self.notas_collection = self.db["notas"]

    def crear_nota(self, titulo, texto, isTerminado, isImportante, email_usuario):

        fecha_actual = datetime.now()
        nota = {
            "_id": uuid.uuid4().hex,
            "titulo": titulo,
            "texto": texto,
            "fechaCreacion": fecha_actual.strftime("%Y-%m-%d %H:%M"),
            "fechaUltimaModificacion": fecha_actual.strftime("%Y-%m-%d %H:%M"),
            "isTerminado": isTerminado,
            "isImportante": isImportante,
            "email_usuario": email_usuario
        }
        self.notas_collection.insert_one(nota)
        return nota["_id"]

    def obtener_nota_por_id(self, nota_id, usuario_email):
        return self.notas_collection.find_one({"_id": nota_id, "email_usuario": usuario_email})

    def obtener_notas_por_usuario(self, email_usuario):
        return list(self.notas_collection.find({"email_usuario": email_usuario}))

    def actualizar_nota(self, nota_id, email_usuario, titulo=None, texto=None, isTerminado=None, isImportante=None):
    # Verificar si la nota pertenece al usuario que realiza la solicitud
        nota = self.notas_collection.find_one({"_id": nota_id, "email_usuario": email_usuario})
        if not nota:
            return False  # La nota no pertenece al usuario, por lo que no se puede actualizar

        # Actualizar los datos de la nota
        update_data = {"fechaUltimaModificacion": datetime.now().strftime("%Y-%m-%d %H:%M")}
        if titulo:
            update_data["titulo"] = titulo
        if texto:
            update_data["texto"] = texto
        if isTerminado is not None:
            update_data["isTerminado"] = isTerminado
        if isImportante is not None:
            update_data["isImportante"] = isImportante

        # Ejecutar la actualización en la base de datos
        result = self.notas_collection.update_one({"_id": nota_id}, {"$set": update_data})
        return result.modified_count > 0  # Devolver True si se realizó la actualización correctamente


    def borrar_nota(self, nota_id, usuario_email):
        nota = self.notas_collection.find_one({"_id": nota_id, "email_usuario": usuario_email})
        if nota:
            self.notas_collection.delete_one({"_id": nota_id})
            return True  
        else:
            return False  
        
    def delete_all_notas(self, usuario_email, confirmacion):
        if confirmacion:
            self.notas_collection.delete_many({"email_usuario": usuario_email})
            return True  # Todas las notas del usuario fueron eliminadas correctamente
        else:
            return False  # No se confirmó el borrado, no se realizaron cambios en la base de datos

    def enviar_nota(self, nota_id, email_usuario_origen, email_usuario_destino):
    # Obtener la nota por su ID
        nota = self.obtener_nota_por_id(nota_id, email_usuario_origen)
        if nota:
            # Crear una copia de la nota cambiando el email del usuario destinatario
            nueva_nota_id = self.crear_nota(
                texto=nota['texto'],
                titulo=nota['titulo'],
                isTerminado=nota['isTerminado'],
                isImportante=nota['isImportante'],
                email_usuario=email_usuario_destino
        )
            return nueva_nota_id
        else:
            return None

