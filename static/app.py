import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Admin, Project, Message

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


# Инициализация БД и создание тестового админа
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        test_admin = Admin(username='admin', password='password123')  # Упрощено для учебного проекта
        db.session.add(test_admin)
        db.session.commit()


# Маршруты
@app.route('/')
def index():
    projects = Project.query.all() # Добавляем чтение проектов для вывода на главный экран
    return render_template('index.html', projects=projects)


@app.route('/portfolio')
def portfolio():
    projects = Project.query.all()
    return render_template('portfolio.html', projects=projects)


@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        text = request.form.get('text', '').strip()

        # Серверная валидация
        if not name or not email or not text:
            flash('Все поля обязательны для заполнения!', 'danger')
            return redirect(url_for('contacts'))

        new_msg = Message(name=name, email=email, text=text)
        db.session.add(new_msg)
        db.session.commit()
        flash('Сообщение успешно отправлено!', 'success')
        return redirect(url_for('index'))
    return render_template('contacts.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Admin.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('admin_panel'))
        flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if request.method == 'POST':
        # Добавление нового проекта
        title = request.form.get('title', '').strip()
        desc = request.form.get('description', '').strip()
        link = request.form.get('link', '').strip()

        if title and desc:
            new_project = Project(title=title, description=desc, link=link)
            db.session.add(new_project)
            db.session.commit()
            flash('Проект успешно добавлен!', 'success')
            return redirect(url_for('admin_panel'))

    projects = Project.query.all()
    messages = Message.query.all()
    return render_template('admin.html', projects=projects, messages=messages)


if __name__ == '__main__':
    app.run(debug=True)
