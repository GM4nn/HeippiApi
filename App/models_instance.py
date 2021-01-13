from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,check_password_hash,safe_str_cmp

class exportSqlORMandSeg():
    db = SQLAlchemy()
    genera_hash = generate_password_hash
    check_password = check_password_hash
    safe_str_cmp = safe_str_cmp

    