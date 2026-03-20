from flask import Blueprint, render_template, request, redirect, url_for, g, session

roles_bp = Blueprint('roles', __name__)

@roles_bp.route('/roles')
def index():
    if not session.get('user_id'):
        return redirect(url_for('main.index'))
    
    cur = g.db.cursor()
    cur.execute("SELECT id, nombre FROM roles ORDER BY id ASC")
    roles_list = cur.fetchall()
    cur.close()
    
    return render_template('roles.html', roles=roles_list)