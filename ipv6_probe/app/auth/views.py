from flask import render_template, url_for, redirect, flash
from . import auth
from ..models import User
from .forms import LoginForm
from flask_login import login_user, logout_user, login_required, current_user


@auth.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, False)
            return redirect(url_for('main.index'))
        flash('用户名或密码错误')
    return render_template('login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('auth.login'))
