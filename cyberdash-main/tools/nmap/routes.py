from flask import Blueprint, request, render_template, flash, redirect, url_for, session
import subprocess
import shlex
from models.nmap_model import NmapResult
from models import db

nmap_bp = Blueprint(
    'nmap',
    __name__,
    template_folder='templates/nmap'
)

@nmap_bp.route('/nmap_home')
def nmap_home():
    if 'username' in session:
        return render_template('nmap_dashboard.html', username=session['username'])
    else:
        flash("Please log in to continue", "error")
        return redirect(url_for('auth.login'))

@nmap_bp.route('/nmap-scan', methods=['POST'])
def nmap_scan():
    target = request.form['target']
    flags = request.form['flags']

    try:
        command = ['nmap'] + shlex.split(flags) + [target]
        result = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)

        # Save result
        new_scan = NmapResult(
            target=target,
            flags=flags,
            result=result
        )
        db.session.add(new_scan)
        db.session.commit()

        return render_template('nmap_dashboard.html', result=result, command=' '.join(command))

    except subprocess.CalledProcessError as e:
        return f"<pre>Nmap Error:\n{e.output}</pre>"
    except Exception as e:
        return f"<pre>Unexpected Error:\n{str(e)}</pre>"

@nmap_bp.route('/nmap/history')
def nmap_history():
    results = NmapResult.query.order_by(NmapResult.timestamp.desc()).all()
    return render_template('nmap_history.html', results=results)

@nmap_bp.route('/nmap/delete/<int:id>')
def delete_entry(id):
    entry = NmapResult.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted!", "success")
    return redirect(url_for('nmap.nmap_history'))
