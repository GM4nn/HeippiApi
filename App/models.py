import datetime
from .models_instance import exportSqlORMandSeg as m
from sqlalchemy_serializer import SerializerMixin
from .serializer import Serializer
db = m.db


class Usuarios(db.Model,SerializerMixin,Serializer):
    serialize_only = ("id","identificacion","username","email","tipo","change_first_password","direccion",)
    id = db.Column(db.Integer, primary_key = True)
    identificacion = db.Column(db.BigInteger, unique = True)
    username = db.Column(db.String(40), unique = True)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(94))
    direccion = db.Column(db.String(50))
    tipo = db.Column(db.String(20))
    servicios_medicos = db.Column(db.ARRAY(db.String(90)))
    fecha_nacimiento = db.Column(db.Date)
    especiliades_pacientes = db.relationship("especialidades_medico_paciente",backref='user')
    change_first_password = db.Column(db.Boolean,default=False)
    telefono = db.Column(db.BigInteger)
    created_date = db.Column(db.DateTime, default = datetime.datetime.now)
    
    def __init__(self,username,email,fecha_nacimiento,direccion,identificacion,tipo,servicios_medicos,telefono,password): #se llama al iniciar
        self.username = username
        self.email = email
        self.fecha_nacimiento = fecha_nacimiento
        self.direccion = direccion
        self.identificacion = identificacion
        self.servicios_medicos = servicios_medicos
        self.telefono = telefono
        self.tipo = tipo
        self.password = self.__create_password(password)

    def __create_password(self,password): #funcion personalizada
        return m.genera_hash(password)

    def verify_password(self,password): #funcion personalizada
        return m.check_password(self.password,password) #compara la passwords hasheada con la password en texto plano que pasa por argumento
    
    
    def serialize(self):
        d = Serializer.serialize(self)
        del d['password']
        return d

class especialidades_medico_paciente(db.Model,SerializerMixin,Serializer):
    __tablename__ = "especialidades_medico_paciente"
    id = db.Column(db.Integer, primary_key = True)
    medico = db.Column(db.Integer, db.ForeignKey(Usuarios.id))#medico
    paciente = db.Column(db.String(80))
    especilidades = db.Column(db.ARRAY(db.String(80)))

    def __init__(self,medico,paciente,especilidades): #se llama al iniciar
        self.medico = medico
        self.paciente = paciente
        self.especilidades = especilidades

    def serialize(self):
        d = Serializer.serialize(self)
        return d