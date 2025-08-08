from flask import Flask, render_template, request
import requests

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:demo@localhost/comision_a'

db = SQLAlchemy(app) 
db.init_app(app)
migrate = Migrate(app, db)


@app.route("/")
def index():
    return render_template(
        "index.html")


if __name__ == '__main__':
    app.run(debug=True)