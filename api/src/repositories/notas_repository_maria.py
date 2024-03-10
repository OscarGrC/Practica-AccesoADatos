from typing import Iterable, Optional
from models.Nota import Nota
from datetime import datetime
import mariadb
import uuid
import models.Nota as nota

class NotasRepositoryMaria():
    def __init__(self):
        self.table = "notas"
        self.db_user = "ejemplo@gmail.com"
        self.db_password = "mazosegura1234"
        print("Connecting...")      
        self.connect()
        self.create_tables()
        self.create_user()
        
    def connect(self):
        try:
            self.conn = mariadb.connect(
                host="mariadb",
                port=3306,
                user="root",
                password="example",
                database="testdb"
            )
            self.cursor = self.conn.cursor()
            print("Connected")
        except mariadb.Error as e:
            print(f"Error {e}") 

    def create_tables(self):
       self.cursor.execute(f"CREATE TABLE IF NOT EXISTS users (user_id VARCHAR(100) PRIMARY KEY,password VARCHAR(100))")
       self.cursor.execute(f"CREATE TABLE IF NOT EXISTS notas (id VARCHAR(100) PRIMARY KEY, titulo VARCHAR(100), contenido VARCHAR(255), fecha_creacion VARCHAR(100),fecha_modificacion VARCHAR(100), isTerminado BOOLEAN, isImportante BOOLEAN, user_id VARCHAR(100), FOREIGN KEY (user_id) REFERENCES users(user_id))")
       self.conn.commit()
       self.close()

    def create_user(self):
        self.connect()
        self.cursor.execute(f"INSERT IGNORE INTO users (user_id) VALUES (?)", (self.db_user,))
        self.conn.commit()
        self.close()

    def obtener_notas_por_usuario(self, email_usuario):
        notas = []  # Inicializar la lista de notas
        self.connect()
        self.cursor.execute(f"SELECT * FROM notas WHERE user_id = '{email_usuario}'")
        for nota in self.cursor:
            nota_obj = {
                "id": nota[0],
                "titulo": nota[1],
                "contenido": nota[2],
                "fecha_creacion": nota[3],
                "fecha_modificacion": nota[4],
                "isTerminado": bool(nota[5]),
                "isImportante": bool(nota[6])
            }
            notas.append(nota_obj) 
        self.close()  
        return notas

    def obtener_nota_por_id(self,nota_id, usuario_email):
        self.connect()
        self.cursor.execute(f"SELECT * FROM notas WHERE user_id = '{usuario_email}' AND id = '{nota_id}'")
        nota = self.cursor.fetchone()
        self.close()
        if nota is not None:
            nota_obj = {
                "id": nota[0],
                "titulo": nota[1],
                "contenido": nota[2],
                "fecha_creacion": nota[3],
                "fecha_modificacion": nota[4],
                "isTerminado": bool(nota[5]),
                "isImportante": bool(nota[6])
            }
            return nota_obj
        else:
            return None


    def crear_nota(self, titulo, texto, isTerminado, isImportante, email_usuario):
     fecha_actual = datetime.now()
     nota = {
         "_id": uuid.uuid4().hex,
         "titulo": titulo,
         "texto": texto,
         "fechaCreacion": fecha_actual.strftime("%Y-%m-%d %H:%M:"),
         "fechaUltimaModifcacion": fecha_actual.strftime("%Y-%m-%d %H:%M:"),
         "isTerminado": isTerminado,
         "isImportante": isImportante,
         "email_usuario": email_usuario
     }
     data = (nota["_id"], nota["titulo"], nota["texto"], nota["fechaCreacion"], isTerminado, isImportante, nota["fechaCreacion"], email_usuario)
     self.connect()
     self.cursor.execute(f"INSERT INTO notas (id, titulo, contenido, fecha_creacion, isTerminado, isImportante, fecha_modificacion, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
     self.conn.commit()
     if self.cursor.rowcount > 0:
         self.close()
         return nota["_id"]
     self.close()
     return None

    def borrar_nota(self, nota_id,usuario_email):
        self.connect()
        self.cursor.execute(f"DELETE FROM notas WHERE id = '{nota_id}'")
        rows_affected = self.cursor.rowcount  
        self.conn.commit()
        self.close()
        if rows_affected > 0:
            return True  
        else:
            return False 


    def delete_all_notas(self, usuario_email, confirmacion):
        if confirmacion:
             self.connect()
             self.cursor.execute(f"DELETE FROM notas WHERE user_id = '{usuario_email}'")
             self.conn.commit()
             self.close()
             return True
        else:
             return False 
       
    def actualizar_nota(self, nota_id, email_usuario, titulo=None, texto=None, isTerminado=None, isImportante=None):
        self.connect()
        self.cursor.execute(f"SELECT * FROM notas WHERE id = '{nota_id}' AND user_id = '{email_usuario}'")
        nota = self.cursor.fetchone()
        if not nota:
            self.close()
            return False  

        id_nota, titulo_actual, contenido_actual, fecha_creacion, fecha_modificacion, isTerminado_actual, isImportante_actual, user_id = nota

        if titulo is not None:
            titulo_actual = titulo
        if texto is not None:
            contenido_actual = texto
        if isTerminado is not None:
            isTerminado_actual = isTerminado
        if isImportante is not None:
            isImportante_actual = isImportante
        self.cursor.execute("""
            UPDATE notas 
            SET titulo = %s, contenido = %s, isTerminado = %s, isImportante = %s, fecha_modificacion = %s
            WHERE id = %s AND user_id = %s
        """, (titulo_actual, contenido_actual, isTerminado_actual, isImportante_actual, datetime.now(), nota_id, email_usuario))
        self.conn.commit()
        rows_affected = self.cursor.rowcount 
        self.close() 
        return rows_affected > 0  

    def enviar_nota(self, nota_id, email_usuario_origen, email_usuario_destino):
        self.connect()
        self.cursor.execute(f"SELECT * FROM users WHERE user_id = '{email_usuario_destino}'")
        destinatario_existente = self.cursor.fetchone()
        self.close()
        if not destinatario_existente:
            return False 
        nota = self.obtener_nota_por_id(nota_id, email_usuario_origen)
        if nota:
            self.connect()
            self.cursor.execute("""
                INSERT INTO notas (titulo, contenido, fecha_creacion, fecha_modificacion, isTerminado, isImportante, user_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (nota['titulo'], nota['contenido'], nota['fecha_creacion'], nota['fecha_modificacion'], nota['isTerminado'], nota['isImportante'], email_usuario_destino))
            self.conn.commit()
            self.close()  
            nota['usuario'] = email_usuario_destino
            return nota
        else:
            return None
    
    def close(self):
        self.cursor.close()
        self.conn.close()