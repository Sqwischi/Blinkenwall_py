from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from flask import send_file
from flaskr.auth import login_required
from flaskr.db import get_db
import re
from . import __init__ 
import os
import json 
from flask import jsonify

configfile = None
with open('config.json', 'r') as f:
    configfile = json.load(f)

UPLOAD_FOLDER = configfile['UPLOAD_FOLDER'] if configfile['UPLOAD_FOLDER'] else "file_library"
ALLOWED_EXTENSIONS = configfile['ALLOWED_EXTENSIONS'] if configfile['ALLOWED_EXTENSIONS'] else {'gif'}
PAGESIZE= configfile['PAGESIZE'] if configfile['PAGESIZE'] else 12

bp = Blueprint('library', __name__)
@bp.route('/')
@bp.route('/<int:page>')
def index(page=0):
    
    db = get_db()
    posts = db.execute(
        'SELECT l.id, uri, created, author_id, username, type'
        ' FROM library l JOIN user u ON l.author_id = u.id'
        ' ORDER BY created DESC'
        ' LIMIT ?'
        ' OFFSET ?',
        (PAGESIZE, page*PAGESIZE,)
    ).fetchall()
    postcount = db.execute(
        'SELECT COUNT() FROM library',
    ).fetchone()['count()']
    return render_template('library/index.html', posts=posts, UPLOAD_FOLDER=UPLOAD_FOLDER, pagesize=PAGESIZE, postcount=postcount)



def get_post(id):
    post = get_db().execute(
        'SELECT l.id, uri, created, author_id, username, type'
        ' FROM library l JOIN user u ON l.author_id = u.id'
        ' WHERE l.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")


    return post

def get_last():
    post = get_db().execute(
        'SELECT id, library_id, created'
        ' FROM log'
        ' ORDER BY created DESC'
    ).fetchone()

    if post is None:
        abort(404, f"Post doesn't exist. Please select something else from library")

    return post

def add_log(id):
    db = get_db()
    db.execute(
        'INSERT INTO log (library_id)'
        ' VALUES (?)',
        (id,)
    )
    db.commit()
    return 

regex_shadertoy = r"(?:https?:\/\/)?(?:www\.)?shadertoy\.com\/(?:view|embed)\/([-a-zA-Z0-9_]+)(?:\?\S*)?"
regex_gif = r"\S*\.gif"
regex_youtube = r"(?:https?:\/\/)?(?:www\.)?youtu(?:\.be\/|be.com\/\S*(?:watch|embed)(?:(?:(?=\/[-a-zA-Z0-9_]{11,}(?!\S))\/)|(?:\S*v=|v\/)))([-a-zA-Z0-9_]{11,})"
def get_uri_type(uri):
    if re.search(regex_shadertoy, uri):
        return "SHADERTOY"
    if re.search(regex_gif, uri):
        return "GIF"
    if re.search(regex_youtube,uri):
        return "YOUTUBE"
    return None

def get_valid_uri(uri):
    uri_type = get_uri_type(uri)
    if uri_type:
        if uri_type == "SHADERTOY":
            return "https://www.shadertoy.com/embed/" + re.search(regex_shadertoy, uri).group(1)
        if uri_type == "YOUTUBE":
            return "https://www.youtube.com/embed/" + re.search(regex_youtube,uri).group(1)
        if uri_type == "GIF":
            return uri
    return None

def check_duplicate(uri):
    post = get_db().execute(
        'SELECT id, uri, created, author_id, type'
        ' FROM library'
        ' WHERE uri = ?',
        (uri,)
    ).fetchone()

    return post

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        uri = request.form['uri']
        error = None

        if not uri:
            error = 'content is required'
        elif not get_valid_uri(uri):
            error = "Content not valid" 
        elif check_duplicate(uri):
            error = "Content already exist."
    

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO library ( uri, author_id, type)'
                ' VALUES (?, ?, ?)',
                ( get_valid_uri(uri), g.user['id'],get_uri_type(uri))
            )
            db.commit(),
            return redirect(url_for('library.index'))

    return render_template('library/create.html') 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/create_file', methods=('GET', 'POST'))
@login_required
def create_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not get_valid_uri(filename):
                flash( "Content not valid") 
                return redirect(request.url)
            if check_duplicate(filename):
                flash("Content already exists")
                return redirect(request.url)
            file.save(os.path.join("flaskr/"+UPLOAD_FOLDER, filename))
            db = get_db()
            db.execute(
                'INSERT INTO library ( uri, author_id, type)'
                ' VALUES (?, ?, ?)',
                ( filename, g.user['id'],get_uri_type(filename))
            )
            db.commit()
            return redirect(url_for('library.index'))

    return render_template('library/create.html') 

def delete_file(filename):
    if os.path.exists("flaskr/"+UPLOAD_FOLDER + '/'+filename):
        os.remove("flaskr/"+UPLOAD_FOLDER + '/'+filename)
    return

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        uri = request.form['uri']
        error = None

        if not uri:
            error = 'content is required'
        elif not get_valid_uri(uri):
            error = "Content not valid" 
        elif check_duplicate(uri):
            error = "Content already exist."
        if error is not None:
            flash(error)
        
        
        
        else:
            if post['type'] in [e.upper() for e in ALLOWED_EXTENSIONS]:
                delete_file(post['uri'])
            db = get_db()
            db.execute(
                'UPDATE library SET uri = ?, type = ?'
                ' WHERE id = ?',
                ( get_valid_uri(uri), get_uri_type(uri), id)
            )
            db.commit()
            return redirect(url_for('library.index'))

    return render_template('library/update.html', post=post)

@bp.route('/<int:id>/update_file', methods=('GET', 'POST'))
@login_required
def update_file(id):
    post = get_post(id)
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not get_valid_uri(filename):
                flash( "Content not valid")
                return redirect(request.url) 
            if check_duplicate(filename):
                flash("Content already exists")
                return redirect(request.url)
            if post['type'] in [e.upper() for e in ALLOWED_EXTENSIONS]:
                delete_file(post['uri'])
            file.save(os.path.join("flaskr/"+UPLOAD_FOLDER, filename))
            db = get_db()
            db.execute(
                'UPDATE library SET uri = ?, type = ?'
                ' WHERE id = ?',
                ( filename, get_uri_type(filename), id)
            )
            return redirect(url_for('library.index'))

    return render_template('library/update.html', post=post) 

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    if post['type'] in [e.upper() for e in ALLOWED_EXTENSIONS]:
            delete_file(post['uri'])
    db = get_db()
    db.execute('DELETE FROM library WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('library.index'))


@bp.route('/blinkenwall', methods=('GET',))
def blinkenwall():
    post = get_post(get_last()['library_id'])

    error = None
    if error is not None:
        flash(error)
    return render_template('library/blinkenwall.html', post=post , UPLOAD_FOLDER=UPLOAD_FOLDER)

@bp.route('/blinkenwall/id', methods=('GET',))
def blinkenwallID():
    postid = get_post(get_last()['library_id'])['id']

    error = None
    if error is not None:
        flash(error)
    return jsonify(
        id=postid
    )


@bp.route('/' + UPLOAD_FOLDER + '/<int:id>', methods=('GET',))
def get_file(id):
    post = get_post(id)
    error = None
    if error is not None:
        flash(error)
    return send_file(UPLOAD_FOLDER + '/' + post['uri'])

@bp.route('/show/<int:id>', methods=('GET',))
@login_required
def set_to_show(id):
    add_log(id)
    return  "fix", 200