from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

#ENV = 'prod'
ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jacksoninv.db'
else:
    #postgres://jackson_inventory_y1ni_user:hJdH5ksfB02loDrw4Kgccqtebvvmhm3l@dpg-chmnfkm4dad21k5r45cg-a.oregon-postgres.render.com/jackson_inventory_y1ni
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://jackson_inventory_y1ni_user:hJdH5ksfB02loDrw4Kgccqtebvvmhm3l@dpg-chmnfkm4dad21k5r45cg-a.oregon-postgres.render.com/jackson_inventory_y1ni'



app.config['SECRET_KEY'] = 'SUPER SECRET KEY'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message_category = "info"

from JacksonInventory import routes
