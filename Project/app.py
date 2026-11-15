from flask import Flask, render_template, request, url_for, redirect
from flask_cors import CORS
from models import *
from resources import *
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
import random

#============================================-Configuration-==============================================
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///mygrocery.sqlite3"
app.config['SECRET_KEY'] = 'secret@#!key^@iitm2021'
CORS(app)
api.init_app(app)
db.init_app(app)
app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#=============================================-Controllers-===============================================
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    def validate_username(self,username):
        existing_user_username = User.query.filter_by(username=username.data).first()

        if existing_user_username:
            raise ValidationError("Username already exists. Please choose a different username")
            
class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(),Length(min=4,max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Login")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        newuser = User(username=form.username.data, password=hashed_password)
        db.session.add(newuser)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html',form=form)

@app.route('/profile')
@login_required
def profile():
    uid=User.query.get(current_user.id)
    data=[]
    for i in range(len(uid.usercart)):
        order=uid.usercart[i].product_name
        data.append(order)
    return render_template('profile.html', data=data)

@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    products = Product.query.all()
    sections = Section.query.all()
    return render_template('dashboard.html',sections = sections, products=products)

@app.route('/search', methods = ['GET','POST'])
def search():
    products=Product.query.all()
    sections=Section.query.all()
    q=request.form["word"]
    query="%"+q+"%"
    result=(Product.query.filter(Product.product_name.like(query)).all())
    return render_template('search.html', q=q, result=result, product=products, sections=sections)

@app.route('/<int:section_id>/products', methods = ['GET','POST'])
@login_required
def sect_products(section_id):
    if request.method == 'GET':
        s1=Section.query.get(section_id)
        products = Product.query.filter_by(sect=section_id).all()
        return render_template('section_product.html', products = products, s_name = s1.section_name, sect_id=section_id)

@app.route('/products/<int:product_id>', methods = ['GET','POST'])
@login_required
def cart(product_id):
    p1=Product.query.get(product_id)
    uid=User.query.get(current_user.id)
    if request.method == 'GET':
        return render_template('cart.html',p1=p1)
    if request.method == 'POST':
        quantity=int(request.form["quantity"])
        total=quantity*int(p1.product_price)
        c1=Cart(u_id=current_user.id, p_id=product_id, p_name=p1.product_name, quantity=quantity, price= p1.product_price,total=total)
        newq=p1.product_quantity-quantity
        Product.query.get(product_id).product_quantity = int(newq)
        p1.shopping.append(uid)
        db.session.add(c1)
        db.session.commit()
        return redirect('/buy')

@app.route('/buy')
@login_required
def buy():
    cart=Cart.query.filter(Cart.u_id==current_user.id).all()
    sum=0
    for i in cart:
        sum+=i.total
    return render_template('buy.html', cart=cart, sum=sum) 
    
@app.route('/<int:c_id>/review', methods=['GET','POST'])
def review(c_id):
    cart=Cart.query.get(c_id)
    p1=Product.query.get(cart.p_id)
    if request.method=='POST':
        d1=Cart.query.filter(Cart.c_id==c_id).one()
        newq=p1.product_quantity+cart.quantity
        Product.query.get(cart.p_id).product_quantity = int(newq)
        db.session.delete(d1)
        db.session.commit()
        return redirect('/buy')
    if request.method=='GET':
        return render_template('review.html', cart=cart)
    
@app.route('/checkout')
@login_required
def checkout():
    num=random.randint(100,2500)
    return render_template('checkout.html',num=num)

#================================================-Admin part-==================================================

@app.route('/admin', methods = ['GET','POST'])
def admin():      
    if request.method == 'POST':
        admin=Admin.query.get(1).admin_email
        pw=Admin.query.get(1).admin_pw
        if (admin == request.form["admin_email"]) and (pw == request.form["pw"]):
            return redirect('/admin_dashboard')
        return render_template('admin.html') 
    return render_template('admin.html') 
      
@app.route('/admin_dashboard', methods=['GET','POST'])
def admin_dashboard():
    all_sections=Section.query.all()
    name = Admin.query.get(1).admin_name
    return render_template('admin_dashboard.html', name=name, all_sections=all_sections)

@app.route('/admin/create', methods = ['GET', 'POST'])
def create():
    section=Section.query.all()
    if request.method == 'POST':
        s1=Section(section_name = request.form["section"])
        db.session.add(s1)
        db.session.commit()
        return redirect('/admin_dashboard')
    return render_template('s_create.html',section=section)

@app.route('/admin/<int:section_id>/update', methods = ['GET','POST'])
def update(section_id):
    section=Section.query.get(section_id)
    if request.method == 'POST':
        Section.query.get(section_id).section_name = request.form["section"]
        db.session.commit()
        return redirect('/admin_dashboard')
    return render_template('s_update.html',section=section)

@app.route('/admin/<int:section_id>/delete', methods = ['GET','POST'])
def delete(section_id):
    section=Section.query.get(section_id)
    if request.method == 'POST':
        d1=Section.query.filter(Section.section_id==section_id).one()
        db.session.delete(d1)
        db.session.commit()
        return redirect('/admin_dashboard')
    return render_template('s_delete.html', section=section)

@app.route('/admin/<int:section_id>/product', methods = ['GET','POST'])
def product(section_id):
    sec=Section.query.get(section_id)
    products = Product.query.filter_by(sect=section_id).all()  
    if request.method == 'POST':
        name=request.form["p_name"]
        unit=request.form["p_unit"]
        quantity=request.form["quantity"]
        price=request.form["p_price"]
        p1=Product(product_name=name, product_unit=unit, product_quantity=quantity, product_price=price, sect=section_id)
        db.session.add(p1)
        db.session.commit()
        return redirect('/admin_dashboard')
    return render_template('create_product.html', section_id=section_id, sec=sec, products=products)

@app.route('/admin/<int:product_id>/edit', methods=['GET','POST'])
def u_product(product_id):
    product=Product.query.get(product_id)
    if request.method == 'GET':
        return render_template('edit_product.html', product=product)
    if request.method == 'POST':
        Product.query.get(product_id).product_name = request.form["p_name"]
        Product.query.get(product_id).product_unit = request.form["p_unit"]
        stock=request.form["quantity"]
        Product.query.get(product_id).product_quantity = int(stock)
        Product.query.get(product_id).product_price = request.form["p_price"] 
        db.session.commit()
        return redirect('/admin_dashboard')

@app.route('/admin/products', methods=['GET','POST'])
def all_products():
    products=Product.query.all()
    sections=Section.query.all()
    if request.method=='GET':
        return render_template('all_products.html',products=products, sections=sections)
    return redirect('/admin_dashboard')

@app.route('/admin/<int:product_id>', methods=['POST','GET'])
def p_remove(product_id):
    if request.method == 'POST':
        d1=Product.query.get(product_id)
        db.session.delete(d1)
        db.session.commit()
        return redirect('/admin/products')
    if request.method == 'GET':
        return render_template('confirm.html', product_id=product_id)
    
if __name__ == "__main__":
    app.run(debug = True)