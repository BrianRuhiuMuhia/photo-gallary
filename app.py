import os
from flask import Flask,redirect,url_for,render_template,flash
from flask_wtf import FlaskForm
from wtforms import FileField,SubmitField,StringField,EmailField,PasswordField
from wtforms.validators import InputRequired,Length
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,login_required,login_user,current_user,logout_user,UserMixin
from random import randint
app=Flask(__name__)
DB_NAME="database.sqlite"
file_name=None
EXTENSIONS=['jpg','png']
app.config['SECRET_KEY']='QWERTY'
app.config['UPLOAD_FOLDER']="static/IMAGES"
app.config['SQLALCHEMY_DATABASE_URI']=f"sqlite:///{DB_NAME}"
db=SQLAlchemy(app=app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app=app)
login_manager.login_view="login"
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
PATH=os.path.join(os.path.dirname(__file__),app.config['UPLOAD_FOLDER'])
class Image(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),unique=True)
    user=db.Column(db.Integer,db.ForeignKey("user.id"))
class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(100))
    last_name=db.Column(db.String(50))
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))
    image=db.relationship("Image")
class UploadForm(FlaskForm):
    file=FileField(validators=[InputRequired()])
    submit=SubmitField("Submit")
class LoginForm(FlaskForm):
    first_name=StringField(validators=[InputRequired(),Length(min=4,max=10)])
    last_name=StringField(validators=[InputRequired(),Length(min=4,max=10)])
    email=EmailField(validators=[InputRequired(),Length(min=4,max=100)])
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)])
    submit=SubmitField("Submit")
class RegisterForm(FlaskForm):
    first_name=StringField(validators=[InputRequired(),Length(min=4,max=10)])
    last_name=StringField(validators=[InputRequired(),Length(min=4,max=10)])
    email=EmailField(validators=[InputRequired(),Length(min=4,max=100)])
    password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)])
    confirm_password=PasswordField(validators=[InputRequired(),Length(min=4,max=20)])
    submit=SubmitField("Submit")
@app.route("/login",methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            if user.password==form.password.data and user.first_name == form.first_name.data and user.last_name == form.last_name.data:
                login_user(user,remember=True)
                flash("successful Login")
                return redirect("/")
            else:
                if user.password != form.password.data:
                    flash("Wrong Password",category="error")
                if user.first_name  != form.first_name.data:
                    flash("Wrong First Name",category="error")
                if user.last_name  != form.last_name.data:
                    flash("Wrong Last Name",category="error")
        else:
            flash("Register",category="error")
            return redirect(url_for("register")) 
    return render_template("login.html",form=form,user=current_user)
@app.route("/register",methods=["POST","GET"])
def register():
    form=RegisterForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            flash("Already Registered",category='error')
            return redirect(url_for("login"))
        if form.confirm_password.data != form.password.data:
            flash("Passwords Must Match")
            return redirect(url_for("register"))
        user=User(first_name=form.first_name.data,last_name=form.last_name.data,email=form.email.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration Complete",category="success")
        return redirect(url_for('login'))
    return render_template("register.html",form=form,user=current_user)
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
@app.route("/upload",methods=['GET','POST'])
@login_required
def upload():
    global file_name
    form=UploadForm()
    if form.validate_on_submit():
        file=form.file.data
        if not check_filename(file.filename):
            flash("File must be a jpg or png",category='error')
            return redirect(url_for("upload"))
        file_name=secure_filename(add_key(file.filename))
        file.save(os.path.join(PATH,file_name))
        image=Image(name=file_name,user=current_user.id)
        db.session.add(image)
        db.session.commit()
        flash("Image Saved",category='success')
        return redirect(url_for("upload"))
    return render_template("upload.html",form=form,user=current_user)
def check_filename(filename):
    return "." in filename and  filename.split(".",1)[1] in EXTENSIONS
def add_key(filename):
    file=filename.split(".",1)
    name=file[0]
    ext=file[1]
    name=str(randint(0,10000000))
    return str((name + "." + ext))
@app.route("/")
@login_required
def home():
    return render_template("home.html",user=current_user)
@app.route("/delete<id>",methods=['GET','POST'])
@login_required
def delete(id):
    image=Image.query.filter_by(id=id).first()
    if image:
      os.unlink(os.path.join(PATH,image.name))
      db.session.delete(image)
      db.session.commit()
    return redirect("/")
def forgot_password():
    pass
if __name__=="__main__":
    db.create_all()
    app.run(debug=True)