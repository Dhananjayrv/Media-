from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import time
import os

app = Flask(__name__)
app.secret_key = 'kdhananjay444'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for Blog Post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=False)

# Dummy credentials for demonstration purposes
owner_credentials = {'rv': 'rv@82102'}

# Existing routes
@app.route('/')
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/course') 
def course():

    return render_template('course.html')

@app.route('/blog')
def blog():
    posts = Post.query.all()
    return render_template('blog.html', posts=posts)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Check credentials
        username = request.form['username']
        password = request.form['password']

        if username == 'rv' and password == owner_credentials['rv']:
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')

    return render_template('signin.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if 'title_to_edit' in request.form:
            # Edit blog post
            title_to_edit = request.form['title_to_edit']
            post_to_edit = Post.query.filter_by(title=title_to_edit).first()

            if post_to_edit:
                return render_template('edit_blog.html', post=post_to_edit)
            else:
                flash('Blog post not found. Please enter a valid title.')
                return redirect(url_for('dashboard'))

        elif 'title_to_delete' in request.form:
            # Delete blog post
            title_to_delete = request.form['title_to_delete']
            post_to_delete = Post.query.filter_by(title=title_to_delete).first()

            if post_to_delete:
                db.session.delete(post_to_delete)
                db.session.commit()
                flash('Blog post deleted successfully!')
            else:
                flash('Blog post not found. Please enter a valid title.')

    # Fetch the updated list of posts
    posts = Post.query.all()

    return render_template('dashboard.html', posts=posts)

@app.route('/delete_blog', methods=['POST'])
def delete_blog():
    title_to_delete = request.form['title_to_delete']
    post_to_delete = Post.query.filter_by(title=title_to_delete).first()

    if post_to_delete:
        try:
            # Delete the associated image file
            image_path = os.path.join('static/images', post_to_delete.image)
            os.remove(image_path)
        except FileNotFoundError:
            pass  # Ignore if the file is not found

        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Blog post deleted successfully!')

        # Redirect to the home page after deleting the blog post
        return redirect(url_for('home'))
    else:
        flash('Blog post not found. Please enter a valid title.')

    # Redirect to the home page if the blog post is not found
    return redirect(url_for('home'))

# Add support for GET and POST requests to the /edit_blog route
@app.route('/edit_blog', methods=['GET', 'POST'])
def edit_blog():
    if request.method == 'POST':
        title_to_edit = request.form['title_to_edit']
        post_to_edit = Post.query.filter_by(title=title_to_edit).first()

        if post_to_edit:
            try:
                post_to_edit.title = request.form['title']
                post_to_edit.content = request.form['content']
                
                # Access the image file from request.files
                image = request.files['image']

                if image:
                    # Process the updated image (save it to a folder, etc.)
                    image.save(os.path.join('static/images', image.filename))
                    post_to_edit.image = image.filename

                db.session.commit()
                flash('Blog post updated successfully!')
                return redirect(url_for('home'))
            except Exception as e:
                # Add a flash message for debugging purposes
                flash(f'Error updating blog post: {str(e)}')
        else:
            flash('Blog post not found. Please enter a valid title.')

    # Fetch the updated list of posts
    posts = Post.query.all()

    return render_template('dashboard.html', posts=posts)

@app.route('/add_blog', methods=['POST'])
def add_post():
    # Get data from the form
    title = request.form['title']
    content = request.form['content']
    image = request.files['image']

    # Process the image (save it to a folder, etc.)
    # For simplicity, save the image in the 'static' folder
    image.save(f'static/images/{image.filename}')

    # Add the post to the database
    new_post = Post(title=title, content=content, image=image.filename)
    db.session.add(new_post)
    db.session.commit()

    # Flash a thank you message
    flash('Thank you for adding a new blog!')

    # Wait for 2 seconds before redirecting to the home page
    time.sleep(2)

    return redirect(url_for('blog'))

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get(post_id)
    return render_template('post_detail.html', post=post)



@app.route('/detail')
def detail():
    # Add logic or retrieve data for the detail page
    return render_template('detail.html')

@app.route('/feature')
def feature():
    # Add logic or retrieve data for the feature page
    return render_template('feature.html')

@app.route('/team')
def team():
    # Add logic or retrieve data for the team page
    return render_template('team.html')

@app.route('/testimonial')
def testimonial():
    # Add logic or retrieve data for the testimonial page
    return render_template('testimonial.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/join_us')
def join_us():
    # Add logic or retrieve data for the join_us page
    return render_template('join_us.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
