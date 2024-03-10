import datetime
import asyncio
from flask import Flask, jsonify, request, abort
from pymongo.errors import PyMongoError
from bson import ObjectId
import os
from dotenv import dotenv_values

import asyncio

from repositories.notas_repository_mongo import NotasRepositoryMongo
from repositories.usuario_repository_mongo import UsuarioRepostoryMongo
from repositories.notas_repository_maria import NotasRepositoryMaria
from repositories.usuario_repository_maria import UsuarioRepostoryMaria

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

DB_TYPE = "mariadb"

if DB_TYPE == "mongodb":
    nota_repo = NotasRepositoryMongo()
    user_repo = UsuarioRepostoryMongo()
elif DB_TYPE == "mariadb":
    nota_repo = NotasRepositoryMaria()
    user_repo = UsuarioRepostoryMaria()

from flask import Flask, jsonify, request

# Asegúrate de importar tus clases y módulos necesarios aquí
from pymongo.errors import PyMongoError

app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

# Obtener todas las notas del usuario  
@app.route('/notas', methods=['GET'])
def obtenerNotas():
    try:
        idc = request.headers.get('email')
        passw = request.headers.get('pass')
        if passw is None or idc is None:
            return jsonify({"message": "No hay credenciales"})
        
        if user_repo.validar_credenciales(idc, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  # Unauthorized       

        print("Obtener Notas")
        notas = nota_repo.obtener_notas_por_usuario(idc)
        if not notas:
            return jsonify({"error": "No se han encontrado más notas"})
        
        notasSerializadas = []
        for nota in notas:
            if isinstance(nota, dict):
                notasSerializadas.append(nota)
            else:
                notasSerializadas.append(nota.to_dict())

        return jsonify(notasSerializadas)
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500  # Retorna el error 500 para indicar un error interno del servidor

# Traer nota por su id
@app.route('/notas/<id>', methods=['GET'])
def obtenerNotaPorId(id):
    try:
        idc = request.headers.get('email')
        passw = request.headers.get('pass')
        if passw is None or idc is None:
            return jsonify({"message": "No hay credenciales"})
        
        if user_repo.validar_credenciales(idc, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  # Unauthorized       
        
        print(f"Obtener Nota con ID {id}")
        nota = nota_repo.obtener_nota_por_id(id, idc)
        if nota is None:
            return jsonify({"error": "No se ha encontrado la nota"})
        
        if isinstance(nota, dict):
            notaSerializada = nota
        else:
            notaSerializada = nota.to_dict()

        return jsonify(notaSerializada)
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500  # Retorna el error 500 para indicar un error interno del servidor

# Nueva Nota    
@app.route('/notas', methods=['POST'])
def guardarNota():
    try:
        # Obtener el email del encabezado
        email = request.headers.get('email')
        passw = request.headers.get('pass')
        if email is None:
            return jsonify({"error": "No se proporcionó el email en los encabezados"}), 400
        
        if user_repo.validar_credenciales(email, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  # Unauthorized
             
        # Obtener los datos de la nota del cuerpo de la solicitud
        data = request.json
        titulo = data.get('titulo')
        texto = data.get('texto')
        isTerminado = data.get('isTerminado')
        isImportante = data.get('isImportante')

        # Verificar si hay campos adicionales en la solicitud
        campos_extras = set(data.keys()) - {'titulo', 'texto', 'isTerminado', 'isImportante'}
        if campos_extras:
            return jsonify({"error": f"Campos no válidos en la solicitud: {', '.join(campos_extras)}"}), 400     
        
        # Verificar que los datos tengan informacion
        if not titulo or not texto or isTerminado is None or isImportante is None:
            return jsonify({"error": "Faltan campos obligatorios en la solicitud"}), 400
        
        # Guardar la nueva nota en el repositorio
        nota_id = nota_repo.crear_nota(titulo, texto, isTerminado, isImportante, email)
        if nota_id:
            user_repo.agregar_nota_a_usuario(email,nota_id)
            return jsonify({"success": True, "nota_id": str(nota_id)}), 200
        else:
            return jsonify({"error": "No se pudo guardar la nota"}), 500
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500
    
@app.route('/notas/<id>', methods=['DELETE'])
def borrarNota(id):
    try:
        idc = request.headers.get('email')
        passw = request.headers.get('pass')
        if passw is None or idc is None:
            return jsonify({"message": "No hay credenciales"})
        
        if user_repo.validar_credenciales(idc, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  # Unauthorized       

        # Intentar borrar la nota
        if nota_repo.borrar_nota(id, idc):
            user_repo.borrar_nota_de_usuario(idc, id)
            return jsonify({"message": "Nota eliminada correctamente"})
        else:
            return jsonify({"error": "No se ha encontrado la nota o no tienes permiso para borrarla"})
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500  # Retorna el error 500 para indicar un error interno del servidor


@app.route('/notas/delete_all', methods=['DELETE'])
def borrarTodasLasNotas():
    try:
        confirmacion = request.json.get('confirmacion')
        idc = request.headers.get('email')
        passw = request.headers.get('pass')
        confirmacion_bool = confirmacion.lower() == "true"

        if not confirmacion_bool:
            return jsonify({"error": "Confirmación requerida para eliminar todas las notas"}), 400       

        if not idc or not passw:
            return jsonify({"error": "Credenciales incompletas"}), 400

        if user_repo.validar_credenciales(idc, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  # Unauthorized
        
        # Intentar borrar todas las notas del usuario
        if nota_repo.delete_all_notas(idc, confirmacion_bool):
            user_repo.borrar_todas_las_notas_de_usuario(idc)
            return jsonify({"message": "Todas las notas fueron eliminadas correctamente"})
        else:
            return jsonify({"message": "Borrado de todas las notas cancelado"})
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500

# Actualizar nota
@app.route('/notas/<id>', methods=['PUT'])
def actualizarNota(id):
    try:
        # Obtener el correo electrónico del usuario de los encabezados de la solicitud
        idc = request.headers.get('email')
        passw = request.headers.get('pass')
        if passw is None or idc is None:
            return jsonify({"error": "Credenciales incompletas"}), 400
        
        if user_repo.validar_credenciales(idc, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  # Unauthorized
        
        # Obtener los datos de la nota del cuerpo de la solicitud
        data = request.json
        titulo = data.get('titulo')
        texto = data.get('texto')
        isTerminado = data.get('isTerminado')
        isImportante = data.get('isImportante')

        campos_extras = set(data.keys()) - {'titulo', 'texto', 'isTerminado', 'isImportante'}
        if campos_extras:
            return jsonify({"error": f"Campos no válidos en la solicitud: {', '.join(campos_extras)}"}), 400
        
        # Intentar actualizar la nota
        if nota_repo.actualizar_nota(id, idc, titulo, texto, isTerminado, isImportante):
            return jsonify({"message": "Nota actualizada correctamente"})
        else:
            return jsonify({"error": "No se ha encontrado la nota o no tienes permiso para actualizarla"})
    except Exception as e:
        return jsonify({"error": f"{e}"}), 500  # Retorna el error 500 para indicar un error interno del servidor

@app.route('/notas/enviar/<id>', methods=['POST'])
def enviarNota(id):
    try:
        idc = request.headers.get('email')
        passw = request.headers.get('pass')
        if passw is None or idc is None:
            return jsonify({"error": "Credenciales incompletas"}), 400
        
        if user_repo.validar_credenciales(idc, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  
        
        # Unauthorized
        
        # Obtener los datos del cuerpo de la solicitud
        data = request.json
        email_destino = data.get('email_destino')
        if email_destino is None:
            return jsonify({"error": "No se proporcionó el email destino en el cuerpo de la solicitud"}), 400
        
        usuario_destino = user_repo.obtener_usuario_por_email(email_destino)
        if not usuario_destino:
            return jsonify({"error": "El usuario destinatario no existe"}), 404  # Not Found

        # Llamar al repositorio de notas para enviar una copia de la nota
        nueva_nota_id = nota_repo.enviar_nota(id, idc, email_destino)

        if nueva_nota_id:
            user_repo.agregar_nota_a_usuario(email_destino,nueva_nota_id)
            return jsonify({"success": True, "nueva_nota_id": str(nueva_nota_id)}), 200
        else:
            return jsonify({"error": "No se pudo enviar la nota"}), 500
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500
    
@app.route('/usuarios', methods=['POST'])
def crearUsuario():
    try:
        # Obtener los datos del cuerpo de la solicitud
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Verificar que se proporcionaron los datos necesarios
        if not email or not password:
            return jsonify({"error": "Faltan campos obligatorios en la solicitud"}), 400
        
        campos_extras = set(data.keys()) - {'email', 'password'}
        if campos_extras:
            return jsonify({"error": f"Campos no válidos en la solicitud: {', '.join(campos_extras)}"}), 400

        # Intentar crear el usuario
        user_id = user_repo.crear_usuario(email, password)
        if user_id:
            return jsonify({"success": True, "user_id": str(user_id)}), 200
        else:
            return jsonify({"error": "Ya existe un usuario con ese email"}), 409  # Código de estado 409 para conflicto
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500

@app.route('/usuarios', methods=['GET'])
def obtenerUsuario():
    try:

        idc = request.headers.get('email')
        passw = request.headers.get('pass')
        if passw is None or idc is None:
            return jsonify({"message": "No hay credenciales"})
        
        if user_repo.validar_credenciales(idc, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  # Unauthorized

        usuario = user_repo.obtener_usuario_por_email(idc)
        if usuario:
            # Extraer el email y la lista de IDs de notas del usuario
            email_usuario = usuario.get("email")
            notas_usuario = usuario.get("notas", [])
            
            # Devolver el email y la lista de IDs de notas
            return jsonify({"email": email_usuario, "notas": notas_usuario}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500

@app.route('/usuarios', methods=['PUT'])
def actualizarUsuario():
    try:
        # Obtener las credenciales del usuario del encabezado
        email = request.headers.get('email')
        password = request.headers.get('pass')
        if email is None or password is None:
            return jsonify({"error": "Credenciales incompletas"}), 400

        # Verificar que la contraseña actual del usuario sea correcta
        if not user_repo.validar_credenciales(email, password):
            return jsonify({"error": "Credenciales incorrectas"}), 401  # Unauthorized

        # Obtener los datos del cuerpo de la solicitud
        data = request.json
        current_password = data.get('pass_actual')
        new_password = data.get('pass_nueva')

        # Verificar que se proporcionaron los datos necesarios
        if not current_password or not new_password:
            return jsonify({"error": "Faltan campos obligatorios en la solicitud"}), 400

        # Verificar que la contraseña actual coincida con la proporcionada en el cuerpo de la solicitud
        if not user_repo.validar_credenciales(email, current_password):
            return jsonify({"error": "La contraseña de confirmación no es válida"}), 400

        # Actualizar la contraseña del usuario
        if user_repo.actualizar_usuario(email, new_password):
            return jsonify({"success": True, "message": "Contraseña actualizada correctamente"}), 200
        else:
            return jsonify({"error": "No se pudo actualizar la contraseña o el usuario no existe"}), 404
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500

@app.route('/usuarios', methods=['DELETE'])
def borrarUsuario():
    try:
        # Obtener el email del encabezado
        email = request.headers.get('email')
        passw = request.headers.get('pass')
        
        if passw is None or email is None:
            return jsonify({"message": "No hay credenciales"})
        
        confirmacion = request.json.get('confirmacion')
        if confirmacion is None:
            return jsonify({"message": "Falta la confirmacion de borrado 'True'"})
        

        # Validar las credenciales del usuario
        if user_repo.validar_credenciales(email, passw) == 0:
            return jsonify({"error": "Credenciales inválidas"}), 401  # Unauthorized

        # Borrar todas las notas del usuario
        if nota_repo.delete_all_notas(email, confirmacion):
            # Si se borran las notas, proceder a borrar el usuario
            if user_repo.borrar_usuario(email):
                return jsonify({"message": "Usuario borrado correctamente"}), 200
            else:
                return jsonify({"error": "No se pudo borrar el usuario"}), 500
        else:
            return jsonify({"error": "No se pudieron borrar las notas del usuario"}), 500
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500
    
@app.route('/orden66', methods=['DELETE'])
def orden66():
    try:
        # Obtener la clave de seguridad unica para la orden 
        passw = request.headers.get('pass')
        
        if passw is None :
            return jsonify({"message": "No hay credenciales"})
        
        confirmacion = request.json.get('confirmacion')
        if confirmacion is None:
            return jsonify({"message": "Falta la confirmacion de borrado 'True'"})
        
        if passw != "execute order 66":
            return jsonify({"message": "ah ah ah, you didn`t say the magic word!"})
        # Borrar todo
        if user_repo.order66():   
             return jsonify({"message": "Yes my lord"}), 200
        else:
                return jsonify({"error": "No se pudo borrar"}), 500
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {e}"}), 500    

if __name__ == '__main__':
    asyncio.run(debug=True)