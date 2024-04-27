
# main.py
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_googleauth import GoogleAuth
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
auth = GoogleAuth(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200))
    complete = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user is not None and password == user.password:
        login_user(user)
        return redirect(url_for('todo'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('index'))

@app.route('/signup', methods=['POST'])
def signup():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    user = User(first_name=first_name, last_name=last_name, email=email)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect(url_for('todo'))

@app.route('/todo', methods=['GET', 'POST'])
@login_required
def todo():
    if request.method == 'POST':
        text = request.form['text']
        todo = Todo(text=text, complete=False, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('todo'))
    else:
        todos = Todo.query.filter_by(user_id=current_user.id).all()
        return render_template('todo.html', todos=todos)

@app.route('/edit_todo/<int:todo_id>', methods=['GET', 'POST'])
@login_required
def edit_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if request.method == 'POST':
        todo.text = request.form['text']
        todo.complete = request.form.get('complete', False)
        db.session.commit()
        return redirect(url_for('todo'))
    else:
        return render_template('edit_todo.html', todo=todo)

@app.route('/delete_todo/<int:todo_id>')
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todo'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
