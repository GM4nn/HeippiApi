
from wtforms import Form, StringField, TextField,HiddenField,PasswordField,IntegerField,FieldList,DateField,FormField
from wtforms.fields.html5 import EmailField
from wtforms import validators 
from .models import Usuarios
import math

def rangeValid(form,field):
    digits = int(math.log10(field.data))+1
    if field.data < 0 :
        raise validators.ValidationError('dijite el campo {} que sea mayor que 0'.format(field.data))
    if not (digits > 0 and digits < 50):
        raise validators.ValidationError('dijite el campo {} que sea valido'.format(field.data))

def tipos(form,field):
    tipos = ['Hospital','Paciente','Medico']
    boolFullField = True
    if field.data not in tipos:
        raise validators.ValidationError("Ingrese un tipo valido")
    elif field.data == "Hospital" or field.data == "Medico":       
        boolFullField = form.username.data is not None and form.direccion.data is not None and len(form.servicios_medicos.data) != 0
    elif field.data == "Paciente":
        boolFullField = form.username.data is not None and form.direccion.data is not None and form.fecha_nacimiento.data is not None and len(form.servicios_medicos.data) == 0

    if not boolFullField:
        raise validators.ValidationError("El tipo {} le faltan campos por llenar o existen campos que no es de este tipo".format(field.data))

def validate_username(form,field):
    username = field.data
    user = Usuarios.query.filter_by(username = username).first()
    if user is not None:
        raise validators.ValidationError('El username ya se encuentra registrado')

def validate_email(form,field):
    email = field.data
    email_get = Usuarios.query.filter_by(email = email).first()
    if email_get is not None:
        raise validators.ValidationError('El email ya se encuentra registrado')

def validate_identificacion(form,field):
    ident = field.data
    ident_get = Usuarios.query.filter_by(identificacion = ident).first()
    if ident_get is not None:
        raise validators.ValidationError('Esta identificacion ya se encuentra registrada')


class PasswordNew(Form):
    identificacion = StringField('Username',[
        validators.Required(message = "la identificacion es requerida"),
        validators.length(min = 4, max = 50, message="Ingrese un username valido"),
    ])
    password = PasswordField('Password',[
        validators.Required(message = "el password es requerido")
    ])


class CreateUserForm(Form):
    username = StringField('Username',[
        validators.Required(message = "El username es requerido"),
        validators.length(min = 4, max = 50, message="Ingrese un username valido"),
        validate_username
    ])
    email = EmailField('Correo electronico',[
        validators.Required(message = "El email es requerido"),
        validators.Email(message = "Ingrese un email valido"),
        validate_email
    ])
    log_user_type = StringField('Correo electronico', validators = [validators.Optional(),validators.length(min = 4, max = 50, message="La direccion es demasiado larga"),])
    direccion = StringField('Correo electronico', validators = [validators.Optional(),validators.length(min = 4, max = 50, message="La direccion es demasiado larga"),])
    tipo = StringField('tipo',[
        validators.Required(message = "El tipo es requerido"),
        validators.length(min = 4, max = 50, message="Ingrese un tipo valido"),
        tipos
    ])
    fecha_nacimiento = DateField('fecha_nacimiento', format="%d/%m/%Y", validators = [validators.Optional()])
    identificacion = IntegerField('identificacion',[
        validators.Required(message = "La identificacion es requerida"),
        validate_identificacion,
        rangeValid
    ])                            
    servicios_medicos = FieldList(StringField('servicios_medicos'),min_entries=0,max_entries = 10,)
    telefono = IntegerField('telefono',[
        validators.Required(message = "El telefono es requerido"),
        rangeValid
    ])
    password = PasswordField('Password',[
        validators.Required(message = "el password es requerido")
    ])


class especialidades_Medico_paciente(Form):
    #el medico se consigue por medio de la JWT
    paciente = StringField('paciente',[
        validators.Required(message = "El paciente es requerido"),
        validators.length(min = 4, max = 50, message="Ingrese un nombre de paciente valido")
    ])
    especilidades = FieldList(StringField('especilidades'),min_entries=0,max_entries = 10,validators = [validators.Required(message = "Las especiladidas son requeridas")])
