from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from PIL import Image
import os
import zipfile
import shutil
import time

app = Flask(__name__)
app.secret_key = 'kdhananjay444'

# Configuration for the first part of the code (Media and Gallery)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.config['UPLOAD_FOLDER'] = 'path/to/your/upload/folder'

class Media(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(255), nullable=False)

# Configuration for the second part of the code (Blog)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)  
    image = db.Column(db.String(255), nullable=False)

owner_credentials = {'rv': 'rv@82102'}

# Function to get paginated posts


# Combined Home route
@app.route('/')
def home():
    posts = Post.query.all()
    media_list = Media.query.all()
    return render_template('home.html', posts=posts, media_list=media_list)

# Common routes for both applications
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/course') 
def course():
    return render_template('course.html')

# Redirect signin to dashboard
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'rv' and password == owner_credentials['rv']:
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('signin.html')

# Dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if 'title_to_edit' in request.form:
            title_to_edit = request.form['title_to_edit']
            post_to_edit = Post.query.filter_by(title=title_to_edit).first()

            if post_to_edit:
                return render_template('edit_blog.html', post=post_to_edit)
            else:
                flash('Blog post not found. Please enter a valid title.')
                return redirect(url_for('dashboard'))

        elif 'title_to_delete' in request.form:
            title_to_delete = request.form['title_to_delete']
            post_to_delete = Post.query.filter_by(title=title_to_delete).first()

            if post_to_delete:
                db.session.delete(post_to_delete)
                db.session.commit()
                flash('Blog post deleted successfully!')
            else:
                flash('Blog post not found. Please enter a valid title.')

    posts = Post.query.all()
    media_list = Media.query.all()
    return render_template('dashboard.html', posts=posts, media_list=media_list)

# Add a new route for the gallery
@app.route('/gallery')
def gallery():
    media_list = Media.query.all()
    return render_template('gallery.html', media_list=media_list)

# Add media upload and deletion routes
@app.route('/upload_media', methods=['POST'])
def upload_media():
    title = request.form['title']
    media_file = request.files['media']

    if media_file:
        # Determine media type based on file extension
        media_type = 'image' if media_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) else 'video'

        # Ensure the 'static/media' directory exists
        media_dir = os.path.join('static', 'media')
        os.makedirs(media_dir, exist_ok=True)

        # Save media file
        media_filename = secure_filename(media_file.filename)
        media_file.save(os.path.join(media_dir, media_filename))

        # Create Media object and add to the database
        new_media = Media(title=title, filename=media_filename)
        db.session.add(new_media)
        db.session.commit()

        flash('Media uploaded successfully!')
    else:
        flash('No media file selected.')

    return redirect(url_for('gallery'))

# Add route to handle media deletion
@app.route('/delete_media', methods=['POST'])
def delete_media():
    media_id = request.form['media_id']
    media_to_delete = Media.query.get(media_id)

    if media_to_delete:
        try:
            media_path = os.path.join('static/media', media_to_delete.filename)
            os.remove(media_path)
        except FileNotFoundError:
            pass

        db.session.delete(media_to_delete)
        db.session.commit()
        flash('Media deleted successfully!')
    else:
        flash('Media not found.')

    return redirect(url_for('gallery'))

# View content route
@app.route('/view/<int:content_id>')
def view_content(content_id):
    content = Media.query.get(content_id)
    return render_template('view_content.html', content=content)

# Blog routes
@app.route('/blog')
def blog():
    posts = Post.query.all()
    return render_template('blog.html', posts=posts)


# Add route to handle blog post deletion
@app.route('/delete_blog', methods=['POST'])
def delete_blog():
    title_to_delete = request.form['title_to_delete']
    post_to_delete = Post.query.filter_by(title=title_to_delete).first()

    if post_to_delete:
        try:
            image_path = os.path.join('static/images', post_to_delete.image)
            os.remove(image_path)
        except FileNotFoundError:
            pass

        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Blog post deleted successfully!')
        return redirect(url_for('home'))
    else:
        flash('Blog post not found. Please enter a valid title.')

    return redirect(url_for('blog'))

# Add route to handle blog post editing
@app.route('/edit_blog', methods=['GET', 'POST'])
def edit_blog():
    if request.method == 'POST':
        title_to_edit = request.form['title_to_edit']
        post_to_edit = Post.query.filter_by(title=title_to_edit).first()

        if post_to_edit:
            try:
                post_to_edit.title = request.form['title']
                post_to_edit.content = request.form['content']
                
                image = request.files['image']

                if image:
                    image.save(os.path.join('static/images', image.filename))
                    post_to_edit.image = image.filename

                db.session.commit()
                flash('Blog post updated successfully!')
                return redirect(url_for('home'))
            except Exception as e:
                flash(f'Error updating blog post: {str(e)}')
        else:
            flash('Blog post not found. Please enter a valid title.')

    posts = Post.query.all()
    return redirect(url_for('blog'))

# Add route to handle adding new blog posts
@app.route('/add_blog', methods=['POST'])
def add_post():
    title = request.form['title']
    content = request.form['content']
    image = request.files['image']

    image.save(os.path.join('static', 'images', secure_filename(image.filename)))

    new_post = Post(title=title, content=content, image=image.filename)
    db.session.add(new_post)
    db.session.commit()
    print(f"Saving image to: {os.path.join('static', 'images', secure_filename(image.filename))}")

    flash('Thank you for adding a new blog!')
    time.sleep(2)

    return redirect(url_for('blog'))

# Route for viewing a single blog post
@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get(post_id)
    return render_template('post_detail.html', post=post)

# Route for downloading a blog post
@app.route('/download_blog', methods=['POST'])
def download_blog():
    title_to_download = request.form['title_to_download']
    post_to_download = Post.query.filter_by(title=title_to_download).first()

    if post_to_download:
        folder_name = f'{title_to_download}_blog'
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)

        # Create the folder
        os.makedirs(folder_path, exist_ok=True)

        # Save the text information to a TXT file
        txt_file_path = os.path.join(folder_path, f'{title_to_download}_info.txt')
        with open(txt_file_path, 'w') as txt_file:
            txt_file.write(f'Title: {post_to_download.title}\n\n')
            txt_file.write(f'Content:\n{post_to_download.content}')

        # Save the image in JPEG format
        image_path = os.path.join('static/images', post_to_download.image)
        image_file_path = os.path.join(folder_path, f'{title_to_download}_image.jpg')
        with Image.open(image_path) as img:
            img.convert('RGB').save(image_file_path, 'JPEG')

        # Create a zip file
        zip_file_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{title_to_download}_blog.zip')
        with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
            zip_file.write(txt_file_path, f'{title_to_download}_info.txt')
            zip_file.write(image_file_path, f'{title_to_download}_image.jpg')

        # Return the zip file as a download
        return send_file(zip_file_path, as_attachment=True)

    else:
        flash('Blog post not found. Please enter a valid title.')

    return redirect(url_for('dashboard'))

# Additional routes from the original code
@app.route('/detail')
def detail():
    return render_template('detail.html')

@app.route('/feature')
def feature():
    return render_template('feature.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/testimonial')
def testimonial():
    return render_template('testimonial.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/join_us')
def join_us():
    return render_template('join_us.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
