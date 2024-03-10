import mariadb
from models.usuario import Usuario

class UsuarioRepostoryMaria:
    def __init__(self):
        self.table = "notas"
        self.db_user = "ejemplo@gmail.com"
        self.db_password = "mazosegura1234"
        print("Connecting...")      
        self.connect()
        self.create_tables()
       
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
   
    def close(self):
            self.cursor.close()
            self.conn.close()

    def create_tables(self):
       self.cursor.execute(f"CREATE TABLE IF NOT EXISTS users (user_id VARCHAR(100) PRIMARY KEY,password VARCHAR(100))")
       self.cursor.execute(f"CREATE TABLE IF NOT EXISTS notas (id VARCHAR(100) PRIMARY KEY, titulo VARCHAR(100), contenido VARCHAR(255), fecha_creacion VARCHAR(100),fecha_modificacion VARCHAR(100), isTerminado BOOLEAN, isImportante BOOLEAN, user_id VARCHAR(100), FOREIGN KEY (user_id) REFERENCES users(user_id))")
       self.conn.commit()
       self.close()

    def crear_usuario(self, email, password):
        self.connect()
        self.cursor.execute(f"SELECT * FROM users WHERE user_id = '{email}'")
        existing_user = self.cursor.fetchone()
        self.close()
        if existing_user:
            return None 
        self.connect()
        self.cursor.execute("INSERT INTO users (user_id, password) VALUES (%s, %s)", (email, password))
        self.conn.commit()
        self.close()  
        return email
 
    def borrar_usuario(self, email):
        existing_user = self.obtener_usuario_por_email(email)
        if existing_user:
            self.connect()
            self.cursor.execute(f"DELETE FROM users WHERE user_id = '{email}'")
            self.conn.commit()
            self.close()
            return True  
        else:
            return False 

    def actualizar_usuario(self, email, nueva_contraseña):
        self.connect()
        self.cursor.execute(f"UPDATE users SET password = '{nueva_contraseña}' WHERE user_id = '{email}'")
        self.conn.commit()
        rows_affected = self.cursor.rowcount
        self.close()
        return True  
      
  
    def obtener_usuario_por_email(self, email):
        self.connect()
        self.cursor.execute(f"SELECT * FROM users WHERE user_id = '{email}'")
        user = self.cursor.fetchone()
        self.close()
        if user is not None:
            user_obj = {"email": user[0]}
        notas = self.obtener_notas_por_usuario(email)    
        notas_dict = {"notas": notas}  # Convertir la lista de notas a un diccionario
        user_obj.update(notas_dict)
        return user_obj
        
    def obtener_notas_por_usuario(self, email_usuario):
        notas = []  # Inicializar la lista de notas
        self.connect()
        self.cursor.execute(f"SELECT id FROM notas WHERE user_id = '{email_usuario}'")
        for nota_id in self.cursor:
            notas.append(nota_id[0])  # Agregar solo el ID de la nota a la lista
        self.close()  
        return notas

    def validar_credenciales(self, email, password):
        self.connect()
        self.cursor.execute(f"SELECT * FROM users WHERE user_id = '{email}' AND password = '{password}'")
        usuario = self.cursor.fetchone()
        self.close()
        return usuario

    def agregar_nota_a_usuario(self, email, nota_id):
        return True
        
    def borrar_nota_de_usuario(self, email, nota_id):
        return True

    def borrar_todas_las_notas_de_usuario(self, email):
        return True
        
    def orden66(self):
        self.connect()
        self.cursor.execute(f"DELETE * FROM users")
        self.conn.commit()
        self.close()
        return True  

