from flask import render_template, flash, redirect,url_for,request
from app import app,db
from app.forms import LoginForm,RegistrationForm,EditProfileForm,PostForm,ResetPasswordRequestForm,ResetPasswordForm
from flask_login import current_user, login_user,logout_user,login_required
from app.models import User,Post
from werkzeug.urls import url_parse
from datetime import datetime
from app.email import send_password_reset_email

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    #request.form.get("key", type=str, default=None) 获取表单数据
    #request.values.get("key") 获取所有参数
    #request.args.get("page") 获取get请求参数，默认值是1，从第一页开始
    page = request.args.get('page', 1, type=int)
    #分页查询，显示第一页，每页显示3个post
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    # has_next: True if there is at least one more page after the current one
    # has_prev: True if there is at least one more page before the current one
    # next_num: page number for the next page
    # prev_num: page number for the previous page
    #如果posts.has_next存在，next_url=\index?page=2,否则=None
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            #如果登录成功，next为绝对路径或者为空，转回index，避免转入其他带病毒网站
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    #如果客户已登录，返回首页
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #实例化注册表单
    form = RegistrationForm()
    #如果注册表单被提交，提交数据库，返回登录页面
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    #其他情况返回注册页面
    return render_template('register.html', title='Register', form=form)

#用户个人网页
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    #获得路由参数，默认为1
    page = request.args.get('page', 1, type=int)
    #paginate数据库的分页功能，
    #参数，page：从第几页开始，app.config['POSTS_PER_PAGE']：每页页数，False：返回超出范围的空列表
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    #如果posts.has_next为空，返回None
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

#更新用户最近一次登录时间到数据库
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#用户主页about me 编辑页面
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

#关注其他用户
@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(username))
    return redirect(url_for('user', username=username))

#取消关注其他用户
@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))

#显示所有用户POST，方便关注。共用一个index页面，使用了{% if form %}
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

#重置密码
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    #用户是否登录
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    #数据库获取用户ID
    user = User.verify_reset_password_token(token)
    #用户不存在
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    #数据提交数据库
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)