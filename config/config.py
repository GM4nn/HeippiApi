import os
from dotenv import load_dotenv
load_dotenv()

class Config(object):
    SECRET_KEY = "my_secret_key"

    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("CONECT_DATABASE")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'CONEXION EN MODO DE PRODUCCION'
    SQLALCHEMY_TRACK_MODIFICATIONS = False