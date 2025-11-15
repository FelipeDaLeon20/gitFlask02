from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

from config import config



app = Flask(__name__)

CORS(app)


# -------------------------------
# CONEXIÓN A MYSQL CONNECTOR
# -------------------------------
def get_connection():
    try:
        return mysql.connector.connect(
            host=config['development']['MYSQL_HOST'],
            user=config['development']['MYSQL_USER'],
            password=config['development']['MYSQL_PASSWORD'],
            database=config['development']['MYSQL_DB']
        )
    except Error as ex:
        print("Error al conectar a la BD:", ex)
        return None


# -------------------------------
# LISTAR ALUMNOS
# -------------------------------
@app.route('/alumnos', methods=['GET'])
def listar_alumnos():
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT matricula, nombre, apaterno, amaterno, correo FROM alumnos")
        datos = cursor.fetchall()

        alumnos = []
        for fila in datos:
            alumnos.append({
                'matricula': fila[0],
                'nombre': fila[1],
                'apellido': fila[2],
                'correo': fila[4]
            })

        cursor.close()
        conexion.close()

        return jsonify({'alumnos': alumnos, 'mensaje': 'Alumnos encontrados', 'exito': True})

    except Exception as ex:
        return jsonify({'mensaje': f'Error al listar alumnos: {str(ex)}', 'exito': False})


# -------------------------------
# LEER ALUMNO BD
# -------------------------------
def leer_alumno_bd(matricula):
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute(
            "SELECT matricula, nombre, apaterno, amaterno, correo FROM alumnos WHERE matricula = %s",
            (matricula,)
        )
        datos = cursor.fetchone()

        cursor.close()
        conexion.close()

        if datos:
            return {
                'matricula': datos[0],
                'nombre': datos[1],
                'apaterno': datos[2],
                'amaterno': datos[3],
                'correo': datos[4]
            }
        return None

    except Exception as ex:
        raise ex


# -------------------------------
# LEER ALUMNO POR URL
# -------------------------------
@app.route('/alumnos/<mat>', methods=['GET'])
def leer_curso(mat):
    try:
        alumno = leer_alumno_bd(mat)
        if alumno:
            return jsonify({'alumno': alumno, 'mensaje': "Alumno encontrado.", 'exito': True})
        else:
            return jsonify({'mensaje': "Alumno no encontrado.", 'exito': False})

    except Exception:
        return jsonify({'mensaje': "Error", 'exito': False})


# -------------------------------
# REGISTRAR ALUMNO
# -------------------------------
@app.route("/alumnos", methods=['POST'])
def registrar_alumnos():
    try:
        alumno_existente = leer_alumno_bd(request.json['matricula'])
        if alumno_existente:
            return jsonify({'mensaje': "Alumno ya existe, no se puede duplicar", 'exito': False})

        conexion = get_connection()
        cursor = conexion.cursor()
        sql = """
        INSERT INTO alumnos (matricula, nombre, apaterno, amaterno, correo)
        VALUES (%s, %s, %s, %s, %s)
        """
        valores = (
            request.json['matricula'],
            request.json['nombre'],
            request.json['apaterno'],
            request.json['amaterno'],
            request.json['correo']
        )

        cursor.execute(sql, valores)
        conexion.commit()

        cursor.close()
        conexion.close()

        return jsonify({'mensaje': "Alumno registrado", 'exito': True})

    except Exception as ex:
        return jsonify({'mensaje': "Error: " + str(ex), 'exito': False})


# -------------------------------
# ERROR 404
# -------------------------------
def pagina_no_encontrada(error):
    return "<h1>La pagina que intentas buscar no existe</h1>", 404


def leer_alumno_bd(matricula):
    try:
        cursor=con.connection.cursor()
        sql="select * from alumnos  where matricula={0}".format(matricula)
        cursor.execute(sql)
        datos = cursor.fetchone()
     
        if datos != None:
           
            alumno={"matricula":datos[0],"nombre":datos[1],
                    "apaterno":datos[2],"amaterno":datos[3],
                    "correo":datos[4]}
            return alumno
        else:
            return None
 
    except Exception as ex:
        raise ex
   
   
@app.route("/alumnos/<mat>",methods=['GET'])
def leer_alumno(mat):
    try:
        alumno=leer_alumno_bd(mat)
        if alumno != None:
            return jsonify({'alumno':alumno,'mensaje':'Alumno encontrado','exito':True}),
        else:
            return jsonify({'alumno':alumno,'mensaje':'Alumno no encontrado','exito':False}),
       
    except Exception as ex:
        return jsonify({"message": "error {}".format(ex),'exito':False})

@app.route("/alumnos",methods=['POST'])
def registrar_alumno():
    try:
        alumno=leer_alumno_bd(request.json['matricula'])
        if alumno != None:
            return jsonify({'mensaje':"Alumno ya existe, no se puede duplicar",
                            'exito':False})
        else:
            cursor=con.connection.cursor()
            sql="""insert into alumnos (matricula,nombre,apaterno,amaterno,correo)
            values ('{0}','{1}','{2}','{3}','{4}')""".format(request.json['matricula'],
                request.json['nombre'],request.json['apaterno'],request.json['amaterno'],
                request.json['correo'])
            cursor.execute(sql)
            con.connection.commit()
            return jsonify({'mensaje':"Alumno registrado","exito":True})
       
    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})
 
 
@app.route('/alumnos/<mat>', methods=['PUT'])
def actualizar_curso(mat):
        try:
            alumno = leer_alumno_bd(mat)
            if alumno != None:
                cursor = con.connection.cursor()
                sql = """UPDATE alumnos SET nombre = '{0}', apaterno = '{1}', amaterno='{2}', correo='{3}'
                WHERE matricula = {4}""".format(request.json['nombre'], request.json['apaterno'], request.json['amaterno'],request.json['correo'], mat)
                cursor.execute(sql)
                con.connection.commit()  # Confirma la acción de actualización.
                return jsonify({'mensaje': "Alumno actualizado.", 'exito': True})
            else:
                return jsonify({'mensaje': "Alumno no encontrado.", 'exito': False})
        except Exception as ex:
            return jsonify({'mensaje': "Error {0} ".format(ex), 'exito': False})
   


# -------------------------------
# INICIO
# -------------------------------
if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()
