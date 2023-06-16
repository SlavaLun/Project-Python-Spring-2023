from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy
from PIL import Image, ImageDraw
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog222.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
canvas = None
draw = None
brush_size = 5
color = (0, 0, 0)

UPLOAD_FOLDER = 'C:/Users/Alexandra/PycharmProjects/pythonProject2/static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/index')
def index():
    # Получаем список файлов из папки UPLOAD_FOLDER
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    # Отображаем список файлов на странице HTML
    return render_template('posts.html', files=files)


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    filename = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Article %r>' % self.id


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/posts')
def posts():
    articles = Article.query.order_by(Article.date.desc()).all()
    return render_template('posts.html', articles=articles)


@app.route('/posts/<int:id>')
def post_detail(id):
    article = Article.query.get(id)
    return render_template('post_detail.html', article=article)


@app.route('/posts/<int:id>/del')
def post_delete(id):
    article = Article.query.get_or_404(id)

    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return 'При удалении поста произошла ошибка'


@app.route('/like/<int:id>')
def like(id):
    article = Article.query.get(id)
    article.likes += 1
    db.session.commit()
    print(article.likes)
    return redirect(url_for('post_detail', id=article.id))


@app.route('/create_article', methods=['POST', 'GET'])
def create_article():
    if request.method == "POST":
        title = request.form['title']
        author = request.form['author']
        file = request.files['filename']
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        article = Article(title=title, author=author, filename=filename)

        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return 'Возникла непредвиденная ошибка'
    else:
        return render_template('create_article.html')


def draw_on_canvas():
    global canvas, draw
    data = request.get_json()

    if not canvas or not draw:
        return 'No canvas created.'

    if 'tool' not in data or 'position' not in data:
        return 'Invalid request data.'

    tool = data['tool']
    position = data['position']

    if tool == 'brush':
        draw.ellipse((position[0] - brush_size, position[1] - brush_size,
                      position[0] + brush_size, position[1] + brush_size), fill=color)

    if tool == 'eraser':
        draw.rectangle((position[0] - brush_size, position[1] - brush_size,
                        position[0] + brush_size, position[1] + brush_size), fill=(255, 255, 255, 0))

    return 'Drawing added to canvas.'


def save_canvas():
    global canvas

    if not canvas:
        return 'No canvas created.'

    canvas.save('static/modified_image.png')
    return send_file('static/modified_image.png', as_attachment=True)


def clear_canvas():
    global canvas, draw

    canvas = Image.new('RGBA', (800, 600), (255, 255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    return 'Canvas cleared.'


with app.app_context():
    db.create_all()
app.run(debug=True)
