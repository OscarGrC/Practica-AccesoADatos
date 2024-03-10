from pymongo import MongoClient

from models.usuario import Usuario

class UsuarioRepostoryMongo:
    def __init__(self):
        self.client = MongoClient('mongodb://root:example@mongodb:27017/')
        self.db = self.client["Notas"]
        self.usuarios_collection = self.db["usuarios"]

    def crear_usuario(self, email, password):

        existing_user = self.obtener_usuario_por_email(email)
        if existing_user:
            return None
        
        usuario = {
            "email": email,
            "password": password,
            "notas": []  
        }
        result = self.usuarios_collection.insert_one(usuario)
        return str(result.inserted_id)

    def obtener_usuario_por_email(self, email):
        return self.usuarios_collection.find_one({"email": email})

    def validar_credenciales(self, email, password):
        return self.usuarios_collection.count_documents({"email": email, "password": password})


    def agregar_nota_a_usuario(self, email, nota_id):

        usuario = self.obtener_usuario_por_email(email)
        if usuario:
            # Actualizar la lista de notas del usuario
            notas = usuario.get('notas', [])
            notas.append(nota_id)
            # Actualizar el documento del usuario en la base de datos
            self.usuarios_collection.update_one({"email": email}, {"$set": {"notas": notas}})
            return True
        else:
            return False  # Usuario no encontrado
        
    def borrar_nota_de_usuario(self, email, nota_id):

        usuario = self.obtener_usuario_por_email(email)
        if usuario:
            notas = usuario.get('notas', [])
            # Verificar si la nota está en la lista
            if nota_id in notas:
                # Remover la nota de la lista
                notas.remove(nota_id)
                # Actualizar el documento del usuario en la base de datos
                self.usuarios_collection.update_one({"email": email}, {"$set": {"notas": notas}})
                return True
            else:
                return False  # La nota no está en la lista de notas del usuario
        else:
            return False  # Usuario no encontrado

    def borrar_todas_las_notas_de_usuario(self, email):
        usuario = self.obtener_usuario_por_email(email)
        if usuario:
            # Borrar la lista de notas del usuario
            self.usuarios_collection.update_one({"email": email}, {"$set": {"notas": []}})
            return True
        else:
            return False 
        
    def actualizar_usuario(self, email, nueva_contraseña):
        
        usuario = self.usuarios_collection.find_one({"email": email})
        if usuario:
            # Actualizar la contraseña del usuario
            resultado = self.usuarios_collection.update_one(
                {"email": email},
                {"$set": {"password": nueva_contraseña}}
            )
            if resultado.modified_count > 0:
                return True  # La contraseña se actualizó correctamente
            else:
                return False  # La contraseña no se pudo actualizar
        else:
            return  False
    
    def borrar_usuario(self, email):
        usuario = self.obtener_usuario_por_email(email)
        if usuario:
            # Si el usuario existe, borrarlo de la base de datos
            result = self.usuarios_collection.delete_one({"email": email})
            if result.deleted_count > 0:
                return True  # Se borró correctamente
        return False  # El usuario no existe o no se pudo borrar

    def orden66(self):
        self.usuarios_collection.delete_many({})
        self.db.drop_collection("notas")
        return True