from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    admin_id = db.Column(db.Integer(), primary_key = True)
    admin_name = db.Column(db.String(50), nullable = False)
    admin_email = db.Column(db.String(), nullable = False)
    admin_pw = db.Column(db.String(), nullable = False)

    def __repr__(self):
        return "<Admin %r>" % self.admin_name

class Section(db.Model):
    section_id = db.Column(db.Integer(), primary_key = True)
    section_name = db.Column(db.String(50), nullable = False)
    products = db.relationship("Product", backref = "section", cascade = ("all, delete"))

    def __repr__(self):
        return "<Section %r>" % self.section_name

class Product(db.Model):
    product_id = db.Column(db.Integer(), primary_key = True)
    product_name = db.Column(db.String(50), nullable = False)
    product_unit = db.Column(db.String(), nullable = False)
    product_quantity = db.Column(db.Integer())
    product_price = db.Column(db.Integer())
    sect = db.Column(db.Integer(), db.ForeignKey("section.section_id"), nullable = False)
    
    def __repr__(self):
        return "<Product %r>" % self.product_name
        
class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(50), nullable = False, unique = True)
    password = db.Column(db.String(50), nullable = False)
    usercart = db.relationship("Product", backref = "shopping", secondary = "association")

    def __repr__(self):
        return "<User %r>" % self.username
    
class Cart(db.Model):
    c_id = db.Column(db.Integer(), primary_key = True)
    u_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    p_id = db.Column(db.Integer(), db.ForeignKey("product.product_id"))
    p_name = db.Column(db.String(50))
    quantity = db.Column(db.Integer())
    price = db.Column(db.Integer())
    total = db.Column(db.Integer())


class Association(db.Model):
    id = db.Column(db.Integer(), db.ForeignKey("user.id"), primary_key = True)
    product_id=db.Column(db.Integer(), db.ForeignKey("product.product_id"), primary_key = True)
    

   