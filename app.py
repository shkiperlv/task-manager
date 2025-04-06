from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from extensions import db, login_manager
from models import User, Task
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
@app.route('/<filter>')
@login_required
def index(filter='all'):
    if filter == 'completed':
        tasks = Task.query.filter_by(user_id=current_user.id, completed=True).all()
    elif filter == 'pending':
        tasks = Task.query.filter_by(user_id=current_user.id, completed=False).all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', tasks=tasks)


@app.route('/add', methods=['POST'])
@login_required
def add_task():
    task_content = request.form['content']
    date_str = request.form.get('date')
    time_str = request.form.get('time')
    deadline = None
    if date_str and time_str:
        deadline_str = f"{date_str} {time_str}"
        deadline = datetime.strptime(deadline_str, '%d.%m.%Y %H:%M')
    new_task = Task(content=task_content, deadline=deadline, user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('You do not have access to this task.')
        return redirect(url_for('index'))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/complete/<int:id>')
@login_required
def complete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('You do not have access to this task.')
        return redirect(url_for('index'))
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        flash('You do not have access to this task.')
        return redirect(url_for('index'))

    if request.method == 'POST':
        task.content = request.form['content']
        date_str = request.form.get('date')
        time_str = request.form.get('time')
        if date_str and time_str:
            deadline_str = f"{date_str} {time_str}"
            task.deadline = datetime.strptime(deadline_str, '%d.%m.%Y %H:%M')
        else:
            task.deadline = None
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update.html', task=task)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('User with this email already exists.')
            return redirect(url_for('register'))
        new_user = User(email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Login.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Incorrect email or password.')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('tasks.db'):
            db.create_all()
    app.run(debug=True)
