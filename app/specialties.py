from flask import Blueprint, render_template, g, session, redirect, url_for

specialties_bp = Blueprint('specialties', __name__)

@specialties_bp.route('/specialties')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre FROM especialidades ORDER BY nombre ASC")
    esps = cur.fetchall()
    cur.close()
    
    return render_template('specialties.html', especialidades=esps)