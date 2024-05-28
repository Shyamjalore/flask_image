from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config.from_object('config.Config')

# Setup MongoDB
client = MongoClient(app.config['MONGO_URI'])
db = client.get_default_database('image_database')

@app.route('/')
def index():
    sections = list(db.sections.find())
    photos = list(db.photos.find())
    return render_template('index.html', sections=sections, photos=photos)

@app.route('/photos')
def photos():
    photos = list(db.photos.find())
    return render_template('photos.html', photos=photos)

@app.route('/admin', methods=['GET', 'POST'])
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
    app.run(debug=True)
