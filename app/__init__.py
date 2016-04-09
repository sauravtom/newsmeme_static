from flask import Flask

app = Flask(__name__, static_url_path='/static')
from app import views

app.config['SECRET_KEY'] = 'thisisarandomstring007becauseilovejamesbond'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

