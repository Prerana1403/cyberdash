from flask import Blueprint, request, render_template, url_for, session, flash, redirect
from models.user_model import User
from models import db


auth_bp=Blueprint(
    'auth',
    __name__,
    template_folder='templates/auth'
)


@auth_bp.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user: 
            session['username'] = user.username
            flash('login successful')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('username or password incorrect')
            return redirect(url_for('auth.login'))
    return render_template('login.html')


@auth_bp.route('/register',methods=['GET','POST'])    
def register():
    if request.method =='GET':
        return render_template('register.html')
    else:
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            session['username']=username
            flash('User already exists','error')
            return redirect(url_for('auth.register'))
        else:
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Success')
            return redirect(url_for('auth.login'))
    return render_template('register.html')


@auth_bp.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html',username=session['username'])
    else:
        flash("Please log in to continue", "error")
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('auth.login'))


@auth_bp.route('/forget_me')
def forget_me():
    if 'username' in session:
        user = User.query.filter_by(username=session['username']).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            session.pop('username', None)
            flash('Your account has been deleted', 'success')
            return redirect(url_for('auth.register'))
        else:
            flash('User not found', 'error')
    else:
        flash('You need to be logged in', 'error')
    return redirect(url_for('auth.login'))
