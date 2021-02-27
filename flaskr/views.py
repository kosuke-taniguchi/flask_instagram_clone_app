from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, login_user, logout_user, current_user
from flaskr.forms import SignupForm, LoginForm, PostForm, EditProfileForm, CommentForm, EditPostForm, SearchForm, SearchFriendsForm
from flaskr.models import User, Post, Comment, PostLike
from datetime import date, datetime
from flaskr import db


bp = Blueprint('app', __name__, url_prefix='')


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    form = SearchForm(request.form)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=12)
    if request.method == 'POST' and form.validate():
        posts = Post.search_by_content(form.search_content.data).order_by(Post.date_posted.desc()).paginate(page=page, per_page=12)
    return render_template('home.html', posts=posts, form=form)

@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.query.filter(User.id==user_id).first()
        username = form.username.data
        email = form.email.data
        password = form.password.data
        file = request.files[form.picture_path.name].read()
        if file:
            file_name = str(user_id) + '_' + str(int(datetime.now().timestamp())) + '.jpg'
            picture_path = 'flaskr/static/user_image/' + file_name
            open(picture_path, 'wb').write(file)
            user = User(
                username,
                email,
                password,
                'user_image/' + file_name
            )
            user.add_user()
            return redirect(url_for('app.login'))
        user = User(
          username,
          email,
          password
        )
        user.add_user()
        return redirect(url_for('app.login'))
    return render_template('signup.html', form=form)

@bp.route('/login', methods=['GET', 'POST']) 
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        email = form.email.data
        password = form.password.data
        user = User.select_user_by_email(email)
        if user and user.validate_password(password):
            login_user(user)
            next = request.args.get('next')
            if not next:
                next = url_for('app.home')
            return redirect(next)
        elif not user:
            flash('このユーザーは存在しません')
        elif not user.validate_password(password):
            flash('メールアドレスとパスワードが一致しません')
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app.login'))

@bp.route('/post', methods=['GET', 'POST'])
@login_required
def post():
    form = PostForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        content = form.content.data
        author = form.author.data
        date_posted = date.today()
        edit_count = 0
        file = request.files[form.picture_path.name].read()
        like_count = 0
        file_name = user_id + '_' + str(int(datetime.now().timestamp())) + '.jpg'
        picture_path = 'flaskr/static/post_image/' + file_name
        open(picture_path, 'wb').write(file)
        post = Post(         
            'post_image/' + file_name,
            content,
            like_count,
            author,
            user_id,
            date_posted,
            edit_count
        )
        post.add_post()
        return redirect(url_for('app.home'))
    return render_template('post.html', form=form)

@bp.route('/current_user_profile')
@login_required
def current_user_profile():
    user_id = current_user.get_id()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(Post.user_id==user_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=12)
    return render_template('current_user_profile.html', posts=posts)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(request.form)
    if request.method == 'POST' and form.validate():
        user_id = current_user.get_id()
        user = User.query.get(user_id)
        with db.session.begin(subtransactions=True):
            username = form.username.data
            profile_comment = form.profile_comment.data
            file = request.files[form.picture_path.name].read()
            user.username = username
            user.profile_comment = profile_comment
            if file:
                file_name = user_id + '_' + str(int(datetime.now().timestamp())) + '.jpg'
                picture_path = 'flaskr/static/user_image/' + file_name
                open(picture_path, 'wb').write(file)
                user.picture_path = 'user_image/' + file_name
        db.session.commit()
        return redirect(url_for('app.current_user_profile'))
    return render_template('edit_profile.html', form=form)

@bp.route('/delete_post/<int:post_id>')
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    post.delete_post()
    return redirect(url_for('app.home'))

@bp.route('/see_post/<int:post_id>')
@login_required
def see_post(post_id):
    post = Post.query.get(post_id)
    comments = Comment.query.filter(Comment.post_id==post_id).all()
    if int(post.edit_count) > 0:
        has_edited = True
        return render_template('see_post.html', post=post, comments=comments, has_edited=has_edited)
    return render_template('see_post.html', post=post, comments=comments)
    
@bp.route('/likes/<int:post_id>/<action>')
@login_required
def likes(post_id, action):
    post = Post.query.filter(Post.id==post_id).first()
    if action == 'like':
        current_user.like_post(post)
        post.like_count += 1
        db.session.commit()
    elif action == 'unlike':
        current_user.unlike_post(post)
        post.like_count -= 1
        db.session.commit()
    return redirect(url_for('app.see_post', post_id=post_id))

@bp.route('/post_comment/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_comment(post_id):
    form = CommentForm(request.form)
    if request.method == 'POST' and form.validate():
        author = form.author.data
        content = form.content.data
        user_id = current_user.id
        comment = Comment(
            author,
            content,
            post_id,
            user_id
        )
        comment.add_comment()
        return redirect(url_for('app.see_post', post_id=post_id))
    return render_template('post_comment.html', form=form)

@bp.route('/edit_post/<int:post_id>', methods=['GET','POST'])
@login_required
def edit_post(post_id):
    form = EditPostForm(request.form)
    post = Post.query.filter(Post.id==post_id).first()
    if request.method == 'POST' and form.validate():
        content = form.content.data
        post.content = content
        post.edit_count += 1
        db.session.commit()
        return redirect(url_for('app.see_post', post_id=post_id))
    return render_template('edit_post.html', form=form, post=post)

@bp.route('/delete_comment/<int:post_id>/<int:comment_id>')
@login_required
def delete_comment(post_id, comment_id):
    comment = Comment.query.get(comment_id)
    comment.delete_comment()
    return redirect(url_for('app.see_post', post_id=post_id))

@bp.route('/user_profile/<int:user_id>')
@login_required
def user_profile(user_id):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter(User.id==user_id).first()
    posts = Post.query.filter(Post.user_id==user_id).order_by(Post.date_posted.desc()).paginate(page=page, per_page=12)
    return render_template('user_profile.html', user=user, posts=posts, user_id=user_id)

@bp.route('/liked_posts/<int:user_id>')
@login_required
def liked_posts(user_id):
    user = User.query.get(user_id)
    post_likes = PostLike.query.filter(PostLike.user_id==user_id)
    posts = []
    for post_like in post_likes:
        post = Post.query.filter(Post.id==post_like.post_id).first()
        posts.append(post)
    return render_template('liked_posts.html', posts=posts, user=user)

@bp.route('/search_friends', methods=['GET', 'POST'])
@login_required
def search_friends():
    page = request.args.get('page', 1, type=int)
    form = SearchFriendsForm(request.form)
    users = None
    if request.method == 'POST' and form.validate():
        users = User.seach_by_username(form.username.data).paginate(page=page, per_page=10)
    return render_template('search_friends.html', form=form, users=users)