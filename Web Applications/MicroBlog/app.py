import os
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

# ---------------------- App factory/config ----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-hi-github!')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///microblog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# --------------------------- Models ----------------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

# --------------------------- Forms -----------------------------
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create account')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError('Username is already taken.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign in')

class PostForm(FlaskForm):
    body = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=280)])
    submit = SubmitField('Post')

# ----------------------- Login manager -------------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create DB on first run
with app.app_context():
    db.create_all()

# --------------------------- Routes ----------------------------
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('index.html', pagination=pagination, posts=pagination.items)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        u = User(username=form.username.data.strip())
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        login_user(u)
        flash('Welcome to MicroBlog!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=form.username.data.strip()).first()
        if u and u.check_password(form.password.data):
            login_user(u)
            flash(f'Hello, {u.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Signed out.', 'info')
    return redirect(url_for('index'))

@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        p = Post(body=form.body.data.strip(), author=current_user)
        db.session.add(p)
        db.session.commit()
        flash('Posted!', 'success')
        return redirect(url_for('index'))
    return render_template('new_post.html', form=form)

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = db.session.get(Post, post_id) or abort(404)
    if post.author != current_user:
        abort(403)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.body = form.body.data.strip()
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('index'))
    return render_template('edit_post.html', form=form, post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = db.session.get(Post, post_id) or abort(404)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('index'))

@app.route('/u/<string:username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(author=user).order_by(Post.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('profile.html', user=user, posts=pagination.items, pagination=pagination)

if __name__ == '__main__':
    # Enable reloader, debug in dev
    app.run(debug=True)