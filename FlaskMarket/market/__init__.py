

import sqlite3

connection = sqlite3.connect('market.db')

from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/ADMIN/.vscode/.vscode/FlaskMarket/market.db'
app.config['SECRET_KEY'] = '8ad23f8c1fc35fb1668cff85'
db = SQLAlchemy(app)



bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


#class Animal(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(100), nullable=False, unique=True)
#    breed = db.Column(db.String(100), nullable=False)
#    species = db.Column(db.String(100), nullable=False)
#    average_lifespan = db.Column(db.Integer, nullable=True)
#    description = db.Column(db.Text, nullable=True)


login_manager.login_view = "login_page"  # Redirects users to login if not logged in
login_manager.login_message_category = "info"
from market import routes

#from flask import from animals import db
#db.create_all()Flask, render_template
#from flask_sqlalchemy import SQLAlchemy

#db = SQLAlchemy()  # Create the SQLAlchemy instance

#def create_app():
#    app = Flask(__name__)
#    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///market.db'  # Change to your database URI
#    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
#    db.init_app(app)  # Register the database with the app

#    with app.app_context():
#        db.create_all()  # Ensure tables are created

#    return app