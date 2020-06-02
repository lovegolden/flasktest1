from flask import render_template, redirect, url_for, flash, request,current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user,login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User,Post
from app.auth.email import send_password_reset_email
from datetime import datetime

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # 如果登录成功，next为绝对路径或者为空，转回index，避免转入其他带病毒网站
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # 如果客户已登录，返回首页
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    # 如果注册表单被提交，提交数据库，返回登录页面
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    # 其他情况返回注册页面
    return render_template('auth/register.html', title='Register',
                           form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('Check your email for the instructions to reset your password'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)

#重置密码
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # 用户是否登录
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    # 数据库获取用户ID
    user = User.verify_reset_password_token(token)
    # 用户不存在
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)



