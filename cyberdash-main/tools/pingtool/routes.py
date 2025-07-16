from flask import Flask, Blueprint, request, render_template, flash, redirect, url_for, session
import subprocess
from models.ping_model import PingResult
from models import db


ping_bp = Blueprint(
    'pingtool',
    __name__,
    template_folder='templates/pingtool'
)


@ping_bp.route('/ping',methods=['GET','POST'])
def ping():
    result=None
    if request.method == 'GET':
        return render_template('ping_dashboard.html')
    else:
        target = request.form['target']
        try:
            result = subprocess.check_output(['ping','-n','3',target], stderr=subprocess.STDOUT, text=True)
            ping_result=PingResult(target=target, result=result)
            db.session.add(ping_result)
            db.session.commit()
        except subprocess.CalledProcessError as e:
            result = e.output
            flash('Ping Failed!', 'error')
        return render_template('ping_dashboard.html', result=result)


@ping_bp.route('/ping_home')
def ping_home():
    if 'username' in session:
        return render_template('ping_dashboard.html', username=session['username'])
    else:
        flash("Please log in to continue", "error")
        return redirect(url_for('auth.login'))

        
@ping_bp.route('/ping/history')
def ping_history():
    results = PingResult.query.all()
    return render_template('ping_history.html',results=results)


@ping_bp.route('/ping/delete/<int:id>')
def delete_ping(id):
    entry = PingResult.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash("Ping entry deleted!", "success")
    return redirect(url_for('pingtool.ping_history'))