from JacksonInventory import db, login_manager
from JacksonInventory import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    #items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    barcode = db.Column(db.String(length=40), nullable=False, unique=True)
    productname = db.Column(db.String(length=150), nullable=False, unique=True)
    qty = db.Column(db.Integer())
    minqty = db.Column(db.Integer())
    productimage = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategory.id'), nullable=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(75), unique=True)
    items = db.relationship('Item', backref='category', lazy=True)

class Subcategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subcategory = db.Column(db.String(75), unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    items = db.relationship('Item', backref='subcategory', lazy=True)