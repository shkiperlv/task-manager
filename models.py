from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Uzdevuma unikālais ID
    content = db.Column(db.String(200), nullable=False)  # Uzdevuma saturs (nevar būt tukšs)
    deadline = db.Column(db.DateTime)  # Termiņš, pēc izvēles
    completed = db.Column(db.Boolean, default=False)  # Vai uzdevums ir pabeigts
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Attiecība ar lietotāju (svešatslēga)

    def __repr__(self):
        return f'<Task {self.id} - {self.content[:20]}>'  # Teksta reprezentācija konsolē

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)  # Lietotāja unikālais ID
    email = db.Column(db.String(150), unique=True, nullable=False)  # E-pasts (unikāls un obligāts)
    password_hash = db.Column(db.String(256), nullable=False)  # Saglabāta paroles hash vērtība

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)  # Šifrē paroli izmantojot hash funkciju

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  # Pārbauda paroli salīdzinot hash