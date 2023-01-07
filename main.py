from flask import Flask, render_template, request, redirect,url_for, session, flash
from clientform import ClientForm, LoginUser, Register
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
import requests

# from flask_ngrok import run_with_ngrok
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip'}
# Setting up the application
app = Flask(__name__)
app.config['SECRET_KEY'] = "secretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clients.db'
app.config['UPLOAD_FOLDER'] = 'static'

db = SQLAlchemy(app)
app.app_context().push()

class Client(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=False, nullable=False)
    name = db.Column(db.String, unique=False, nullable=True)
    email = db.Column(db.String, unique=False, nullable=True)
    address = db.Column(db.String, unique=False, nullable=True)
    phone = db.Column(db.String, unique=False, nullable=True)
    date = db.Column(db.String, unique=False, nullable=True)
    time = db.Column(db.String, unique=False, nullable=True)
    file = db.Column(db.String, unique=False, nullable=True)
    service = db.Column(db.String)
    package = db.Column(db.String)
    col13 = db.Column(db.String)
    col14 = db.Column(db.String)

    def __repr__(self):
        return '<Username: {}>'.format(self.username)

db.create_all()

# app.app_context().push()

# run_with_ngrok(app)

url = 'https://api.npoint.io/e21406b80f9016c674e8'
response = requests.get(url).json()

# making route
@app.route('/')
def home():

    data = response
    return render_template('index.html', json=data )

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username').lower()
        name = request.form.get('name')
        password = request.form.get('password')
        print(email,username,password)
        new_client = Client(email=email, username=username, password=password, name=name)
        db.session.add(new_client)
        db.session.commit()
        client = Client.query.all()
        print('client{}'.format(client))
        user = Client.query.filter_by(username=username).first()
        print(user.username)
        flash('halo {}, you are registered, please login'.format(user.username))
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUser()
    if request.method == 'POST':
        user = Client.query.filter_by(username=request.form['username']).scalar()
        if user == None:
            flash('user does no t exist')
        else:
            if not request.form['password'] == user.password:
                flash('wrong password', 'error')
            else:
                session['username'] = user.username
                flash(f"you are logged in, welcome {session['username']}")
                return redirect(url_for('home'))
        return render_template('login.html', form=form)
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        flash('you are logged out')
    else:
        flash('you are already logged out, please login again')
    return redirect(url_for('home'))

@app.route('/wtform', methods=['GET', 'POST'])
def wtform():
    name = None
    form = ClientForm()
    if 'username' in session:
        if request.method == 'POST':
            name = form.fullname.data
            email = form.email.data
            address = form.address.data
            phone = form.phone.data
            date = form.date.data
            time = form.time.data
            file = form.payment.data
            print(type(date))
            print(file.filename)
            client_to_update = Client.query.filter_by(username=session['username']).first()
            print(client_to_update.email)
            client_to_update.email = email
            client_to_update.name = name
            client_to_update.address = address
            client_to_update.phone = phone
            client_to_update.date = date.strftime("%Y %m %d")
            client_to_update.time = time.strftime("%H:%M:%S")
            client_to_update.file = file.filename
            db.session.commit()
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))

            return redirect(url_for('user'))
        return render_template("wtform.html", name=name, form=form)
    else:
        flash('you need to login')
        return redirect(url_for('home'))

@app.route('/user')
def user():
    if 'username' in session:
        user = Client.query.filter_by(username=session['username']).first()
        username = user.username
        name = user.name
        email = user.email
        address = user.address
        phone = user.phone
        date = user.date
        time = user.time
        if user.file == None:
            payment = 'kosong'
        else:

            payment = user.file
        return render_template('user.html', username=username, user=name, email=email, address=address, phone=phone, date=date, time=time, payment=payment)
    else:
        flash('you need to log in')
        return redirect(url_for('home'))



# running application
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)