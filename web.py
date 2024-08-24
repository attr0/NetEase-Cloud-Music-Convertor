from flask import Flask
from flask import render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from task import *

import os
current_directory = os.getcwd()

db = SQLAlchemy(model_class=Base)

app = Flask(__name__, instance_path=current_directory, root_path=current_directory)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_ECHO'] = DB_DEBUG
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 30, type=int)
    sort_order = request.args.get('sort_order', 'desc', type=str)

    if sort_order == 'desc':
        tasks = Task.query.order_by(Task.task_id.desc()).paginate(page=page, per_page=per_page)
    else:
        tasks = Task.query.order_by(Task.task_id.asc()).paginate(page=page, per_page=per_page)

    task_count = Task.query.count()
    finished_count = Task.query.filter(Task.state != TaskState.FINISHED).count()

    return render_template(
        'index.html', tasks=tasks, 
        current_per_page=per_page, current_sort_order=sort_order,
        task_count=task_count, finished_count=finished_count)

@app.route('/update-task/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task = Task.query.get(task_id)
    page = request.form.get('page', 1, type=int)
    per_page = request.form.get('per_page', 30, type=int)
    sort_order = request.form.get('sort_order', 'desc', type=str)
    if task:
        task.state = request.form['state']
        db.session.commit()
    return redirect(url_for('index', page=page, per_page=per_page, sort_order=sort_order))

app.run(debug=True)