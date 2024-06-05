from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object('config.Config')


app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'beingmanish35@gmail.com',
    MAIL_PASSWORD = 'wbiq lobk jhhz kocu'
    
)
mail = Mail(app)

# Setup MongoDB
client = MongoClient(app.config['MONGO_URI'])
db = client.get_default_database('mimage_database')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Admin(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return Admin(user_id)

@app.route('/')
def index():
    sections = list(db.sections.find())
    photos = list(db.photos.find())
    return render_template('index.html', sections=sections, photos=photos)


@app.route('/submit_form', methods=['POST'])
def submit_form():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        mobilenumber = request.form['mobilenumber']
        hobby = request.form['hobby']
        
        db.volunteers.insert_one({
            'name': name,
            'address': address,
            'email': email,
            'mobilenumber': mobilenumber,
            'hobby': hobby
        })
        mail.send_message('New message from ' + name,
                          sender=email,
                          recipients = ['beingmanish35@gmail.com'],
                          body = address + "\n" + hobby  + "\n" + mobilenumber
                          )
        
    flash('Your form is successfully submitted')
    return redirect(url_for('index'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        if username == 'admin' and password == 'password':
            user = Admin(id=1)
            login_user(user)
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/volunteer')
@login_required
def admin_volunteer():
    volunteers = list(db.volunteers.find())
    return render_template('admin_volunteer.html', volunteers=volunteers)

@app.route('/edit/<volunteer_id>', methods=['GET', 'POST'])
@login_required
def edit_volunteer(volunteer_id):
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        mobilenumber = request.form['mobilenumber']
        hobby = request.form['hobby']
        
        db.volunteers.update_one(
            {'_id': ObjectId(volunteer_id)},
            {'$set': {
                'name': name,
                'address': address,
                'email': email,
                'mobilenumber': mobilenumber,
                'hobby': hobby
            }}
        )
        return redirect(url_for('admin_volunteer'))
    
    volunteer = db.volunteers.find_one({'_id': ObjectId(volunteer_id)})
    return render_template('edit_volunteer.html', volunteer=volunteer)

@app.route('/admin/delete/<volunteer_id>', methods=['POST'])
@login_required
def delete_volunteer(volunteer_id):
    db.volunteers.delete_one({'_id': ObjectId(volunteer_id)})
    return redirect(url_for('admin_volunteer'))

@app.route('/photos')
def photos():
    photos = list(db.photos.find())
    return render_template('photos.html', photos=photos)

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        if 'photo' in request.files:
            photo = request.files['photo']
            filename = secure_filename(photo.filename)
            content_type = photo.content_type
            db.photos.insert_one({'filename': filename, 'content_type': content_type, 'data': photo.read()})
        
        if 'content' in request.form:
            section_name = request.form.get('section_name')
            content = request.form.get('content')
            db.sections.update_one(
                {'section_name': section_name},
                {'$set': {'content': content}},
                upsert=True
            )
        return redirect(url_for('admin'))
    
    sections = list(db.sections.find())
    photos = list(db.photos.find())
    return render_template('admin.html', sections=sections, photos=photos)

@app.route('/delete_photo/<photo_id>', methods=['POST'])
def delete_photo(photo_id):
    db.photos.delete_one({'_id': ObjectId(photo_id)})
    return redirect(url_for('admin'))

@app.route('/delete_section/<section_id>', methods=['POST'])
def delete_section(section_id):
    db.sections.delete_one({'_id': ObjectId(section_id)})
    return redirect(url_for('admin'))

@app.route('/photo/<photo_id>')
def serve_photo(photo_id):
    photo = db.photos.find_one({'_id': ObjectId(photo_id)})
    return app.response_class(photo['data'], mimetype=photo['content_type'])

if __name__ == '__main__':
    app.run(debug = True)
