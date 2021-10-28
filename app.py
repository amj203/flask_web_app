from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'i love coding but its hard'
UPLOAD_FOLDER = 'D:/code/web/flask/flask homepage/static/uploads/'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLACHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key= True)
    first_name = db.Column(db.String(50), nullable= False)
    name = db.Column(db.String(50), nullable= False, unique= True)
    password = db.Column(db.String(50), nullable= False)
    join_date = db.Column(db.DateTime, default= datetime.utcnow)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    user_id = db.Column(db.Integer, nullable= False)
    path = db.Column(db.Text, nullable= False)
    name = db.Column(db.String(50), nullable= False)
    mimetype = db.Column(db.String(10), nullable= False)
    add_date = db.Column(db.DateTime, default= datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/login', methods=["GET","POST"])
def login():

    if request.method == "POST":
        username = request.form['username']
        if not username:
            flash('Enter a username !')
            return redirect('/error')
        password = request.form['password']
        if not password:
            flash('Enter a password !')
            return redirect('/error')

        user = User.query.filter_by(name=username).scalar()
        if not user:
            flash('Wrong username !')
            return redirect('/error')
        if check_password_hash(user.password, password):
            login_user(user)
            try:
                UPLOAD_FOLDER = app.config['UPLOAD_FOLDER'] + username
                os.mkdir(UPLOAD_FOLDER)
            except:
                pass
            return redirect('/')
        else:
            flash('Wrong password !')
            return redirect('/error')

    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/images')
@login_required
def images():
    images = Image.query.filter_by(user_id = current_user.id).all()
    return render_template('images.html',data = images)

@app.route('/delete', methods=["GET","POST"])
@login_required
def delete():
    images = Image.query.filter_by(user_id = current_user.id).all()
    if request.method == "POST":
        option = request.form['delete']
        try:
            image = Image.query.filter_by(name=option).first()
            UPLOAD_FOLDER = app.config['UPLOAD_FOLDER'] + current_user.name
            path = os.path.join(UPLOAD_FOLDER,image.name)
            os.remove(path)
            db.session.delete(image)
            db.session.commit()
            return redirect('/images')
        except:
            return 'error',400
    else:
        return render_template('delete.html',images = images)
        
@app.route('/upload' , methods=["GET","POST"])
@login_required
def upload():
    if request.method == "POST":
        image = request.files['pic']
        if not image:
            flash("choose an image")
            return redirect('/error')
        
        filename = secure_filename(image.filename)
        UPLOAD_FOLDER = 'static/uploads/' + current_user.name
        image.save(os.path.join(UPLOAD_FOLDER, filename))
        try:
            new_image = Image(user_id= current_user.id, path= UPLOAD_FOLDER + '/' + filename, name= filename, mimetype= image.mimetype)
            db.session.add(new_image)
            db.session.commit()
            return redirect('/images')
        except:
            return 'error', 400
    else:
        return render_template('upload.html')


@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        users = User.query.all()
        first = request.form['firstname']
        if not first:
            flash('Enter a first name !')
            return redirect('/error')
        username = request.form['username']
        if not username:
            flash('Enter a username')
            return redirect('/error')
        input_password = request.form['password']
        password = generate_password_hash(input_password)
        if not password:
            flash('Enter a password !')
            return redirect('/error')
        for user in users:
            if user.name != username:
                continue
            else:
                flash('Username Taken !')
                return redirect('/error')
        
        newuser = User(first_name=first, name=username, password= password)
        try:
            db.session.add(newuser)
            db.session.commit()
            return redirect('/login')
        except :
            return 'error', 400
    else:
        return render_template('register.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/parts')
def parts():
    return render_template('parts.html')

@app.route('/types')
def types():
    return render_template('types.html')

@app.route('/error')
def error():
    return render_template('error.html')


def add_user(first_name,name,password):
    user = User(first_name=first_name, name = name, password = password)
    db.session.add(user)
    db.session.commit()

def test():
    username = 'moaz'
    user = User.query.filter_by(name=username).scalar()
    print(user.password)

def user_info():
    print(current_user.name + current_user.password + current_user.id)

if __name__ == "__main__":
    app.run(debug=False)