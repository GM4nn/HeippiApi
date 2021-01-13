from flask import Flask,request,jsonify,g
from config.config import DevelopmentConfig
from App.models import Usuarios,especialidades_medico_paciente
from App.forms import CreateUserForm,PasswordNew,especialidades_Medico_paciente
from App.models_instance import exportSqlORMandSeg
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from datetime import date, datetime
import wtforms_json
import json

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
jwt = JWTManager(app)
exportSqlORMandSeg.db.init_app(app)
db = exportSqlORMandSeg.db
wtforms_json.init()
base_url_api = "/api/v1"

@app.route(base_url_api)
def BienvenidaApiHeippi():
    return jsonify({"message": "Bienvenido a la api de prueba!"}), 200

###### SISTEMA DE LOGEO #####

@app.route('{}/auth'.format(base_url_api),methods=['POST'])
def authenticate():
    if not request.is_json:
        return jsonify({"message": "Falta un json en la solicitud"}), 400

    identificacion = request.json.get('identificacion', None)
    password = request.json.get('password', None)

    if not identificacion:
        return jsonify({"msg": "Falta el parametro de username"}), 400
    if not password:
        return jsonify({"msg": "Falta el parametro de password"}), 400

    username_current  = Usuarios.query.filter_by(identificacion = identificacion).first()

    if username_current is not None and username_current.verify_password(password):
        if username_current.tipo == "Medico" and username_current.change_first_password == 0:
            return jsonify({"message": "Debes cambiar tu contraseña"}), 400

        access_token = create_access_token(identity=username_current.to_dict())
        return jsonify(access_token=access_token), 200
    
    return jsonify({"msg": "Username o contraseñas invalidas"}), 401

###### END SISTEMA DE LOGEO #####


#PARA ACCEDER AL SISTEMA (INDEX) DE LA CLINICA
@app.route('{}/Sistema'.format(base_url_api))
@jwt_required
def sistema():
    return jsonify({'usuario':get_jwt_identity(),'message':'este usuario esta logueado y en el sistema'})


#FUNCION PARA CONVERTIR LAS FECHA Y HORAS A STR CUANDO SE SERIALIZA LOS DATOS 
def default(o):
    if isinstance(o, (datetime, date)):
        return str(o)


#####  METODOS PARA NO USAR REPEAT YOUR SELF #####

def register_user(get_data):
    create_form = CreateUserForm.from_json(get_data)
    if create_form.validate():
        user = Usuarios(
            create_form.username.data,
            create_form.email.data,
            create_form.fecha_nacimiento.data,
            create_form.direccion.data,
            create_form.identificacion.data,
            create_form.tipo.data,
            create_form.servicios_medicos.data,
            create_form.telefono.data,
            create_form.password.data,
        )
        db.session.add(user) #preparar la transaccion
        db.session.commit() # aqui nos aseguramos de que se escriba en la bd si ahy error hara un rolback
        return {'status':200,'message':'Usuario creado correctamente'}
    else:
        return {'message':'Error al enviar la informacion','errors':create_form.errors}

def update_user_password(get_data):
    create_form = PasswordNew.from_json(get_data)
    if create_form.validate():
        user = Usuarios.query.filter_by(identificacion = create_form.identificacion.data).first()
        hash_password = exportSqlORMandSeg.genera_hash(create_form.password.data)
        user.password = hash_password
        user.change_first_password = True
        db.session.add(user) #preparar la transaccion
        db.session.commit() # aqui nos aseguramos de que se escriba en la bd si ahy error hara un rolback
        return {'status':200,'message':'Contraseña reestablecida correctamente'}
    else:
        return {'message':'Error al enviar la informacion','errors':create_form.errors}

##### END METODOS PARA NO USAR REPEAT YOUR SELF #####



#actualizar contraseña
@app.route("{}/UserUpdatePassword".format(base_url_api), methods = ['POST'])
def updatePassword():
    return jsonify(update_user_password(request.get_json()))


##### GET REGISTERS ALL MEDICOS FROM HOSPITAL ######

@app.route("{}/MedicosRegistros".format(base_url_api))
@jwt_required
def medicosRegistros():
    if get_jwt_identity()['tipo'] == "Hospital":
        per_page = 2
        page = request.args.get('page',default = 1,type = int)
        esp_mec_pac = especialidades_medico_paciente.query.order_by(-especialidades_medico_paciente.id).paginate(page,per_page,False)
        return json.dumps(especialidades_medico_paciente.serialize_list(esp_mec_pac.items),indent=1, sort_keys=True,default=default) 
    else:
        return jsonify({'message':'Credenciales invalidas','errors':"Credenciales"})



####### MEDICO ########

#se registra el medico siempre y cuando sea de tipo Hospital
@app.route("{}/MedicoRegistrar".format(base_url_api), methods = ['POST'])
@jwt_required
def registrar_medico():
    #siempre y cuando sea el usuario de tipo hospital y valla a registrar si o si un medico, el sistema lo dejara hacerlo, de lo contrario, retornar un json con mensajes de error
    if(get_jwt_identity()['tipo'] == "Hospital" and request.get_json()["tipo"] == "Medico"):
        return jsonify(register_user(request.get_json()))
    else:
        return jsonify({'message':'Credenciales invalidas','errors':"Credenciales"})


#el medico aqui puede observar sus registros realizados a sus pacientes
@app.route("{}/PacienteBrindarEspecialdades".format(base_url_api), methods = ['POST','GET'])
@jwt_required
def medico_especialidad_to_paciente():
    if(get_jwt_identity()['tipo'] == "Medico"):
        if request.method == "POST": 
            create_form = especialidades_Medico_paciente.from_json(request.get_json())
            if create_form.validate():
                
                especialidades = especialidades_medico_paciente(
                        get_jwt_identity()['id'],
                        create_form.paciente.data,
                        create_form.especilidades.data
                )
                db.session.add(especialidades) #preparar la transaccion
                db.session.commit() # aqui nos aseguramos de que se escriba en la bd si ahy error hara un rolback
                return {'status':200,'message':'aplicado la especialidades correctamente'}
            else:
                return {'message':'Error al enviar la informacion','errors':create_form.errors}
        else:
            per_page = 2
            page = request.args.get('page',default = 1,type = int)
            esp_mec_pac = especialidades_medico_paciente.query.filter_by(medico = get_jwt_identity()['id']).order_by(-especialidades_medico_paciente.id).paginate(page,per_page,False)
            return json.dumps(especialidades_medico_paciente.serialize_list(esp_mec_pac.items),indent=1, sort_keys=True,default=default) 
    else:
        return jsonify({'message':'Credenciales invalidas','errors':"Credenciales"})
    
####### ENDMEDICO ########

####### USUARIOS PACIENTE Y HOSPITAL ########

#ver la informacion del usuario actual
@app.route("{}/Usuario".format(base_url_api),methods = ['GET'])
@jwt_required
def getUsuario():
    user = Usuarios.query.filter_by(id=get_jwt_identity()['id']).first_or_404()
    return jsonify(user.to_dict())


@app.route("{}/UsuariosRegistrar".format(base_url_api), methods = ['POST'])
def usuarios_registrar():
    if(request.get_json()["tipo"] != "Medico"):
        return jsonify(register_user(request.get_json()))
    return jsonify({'message':'No tienes permitido registrar medicos'}) , 401


@app.route("{}/UsuariosListar".format(base_url_api), methods = ['GET'])
def UsuariosListar():
    per_page = 2
    page = request.args.get('page',default = 1,type = int)
    usuarios = Usuarios.query.order_by(-Usuarios.id).paginate(page,per_page,False)
    return json.dumps(Usuarios.serialize_list(usuarios.items),default=default)

####### END USUARIOS PACIENTE Y HOSPITAL ########


if __name__ == '__main__':
    with app.app_context(): #sincronizo mi app como tambien mi base de datos
        exportSqlORMandSeg.db.create_all()
    app.run(debug=True,port = 8000)