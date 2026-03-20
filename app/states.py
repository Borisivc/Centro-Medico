from flask import Blueprint, render_template, g, session, redirect, url_for

states_bp = Blueprint('states', __name__)

@states_bp.route('/states')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre FROM estados_agenda ORDER BY id ASC")
    ests = cur.fetchall()
    cur.close()
    
    return render_template('states.html', estados=ests)