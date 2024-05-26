from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_login import current_user, login_required
from functools import wraps
from mysqldb import DBConnector
import mysql.connector as connector

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

db_connector = DBConnector(app)
from auto import bp as auto_bp, init_login_manager

app.register_blueprint(auto_bp)
init_login_manager(app)

from users import bp as users_bp

app.register_blueprint(users_bp)

from user_actions import bp as user_actions_bp

app.register_blueprint(user_actions_bp)


@app.before_request
def record_action():
    if request.endpoint == 'static':
        return
    user_id = current_user.id if current_user.is_authenticated else None
    path = request.path
    connection = db_connector.connect()
    try:
        with connection.cursor(named_tuple=True, buffered=True) as cursor:
            query = "INSERT INTO user_actions (user_id, path) VALUES (%s, %s)"
            cursor.execute(query, (user_id, path))
            connection.commit()
    except connector.errors.DatabaseError as error:
        print(error)
        connection.rollback()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/secret')
@login_required
def secret():
    return render_template('secret.html')


@app.route('/counter')
def counter():
    session['counter'] = session.get('counter', 0) + 1
    return render_template('counter.html')
