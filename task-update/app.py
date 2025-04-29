from flask import Flask, request, redirect, render_template
from datetime import datetime as dt
import redis
import requests

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_today_date_key(metric):
    # Get a redis key with today's date embedded
    today = dt.now().strftime('%Y-%m-%d')
    return f'{metric}:{today}'

def get_updates_today():
    # Get the number of updates for today, using date-based data
    updates_key = get_today_date_key('updates_count')
    count = redis_client.get(updates_key)
    return int(count) if count else 0

def get_new_tasks_today():
    # Get the number of updates for today, using date-based data
    new_tasks_key = get_today_date_key('new_tasks_count')
    count = redis_client.get(new_tasks_key)
    return int(count) if count else 0

@app.route('/')
def index():
    task_id = request.args.get('task_id')
    if not task_id:
        return redirect('/query/')
    
    # Check if the task exists by communicating with the Task Query Service
    response = requests.get(f'http://task-query:5000/api/task/{task_id}')
    if response.status_code != 200:
        return f"Task with ID {task_id} not found.", 404
    task = response.json()
    return render_template('task-update.html', task=task)

@app.route('/save', methods=['POST'])
def save_task():
    task_id = request.form.get('task_id')
    
    if not redis_client.exists(f'task:{task_id}'):
        return f"Task with ID {task_id} not found.", 404
    
    # Check which button was clicked
    if 'delete' in request.form:
        # Remove the task from the tasks set
        redis_client.srem('tasks', task_id)
        # Delete the task hash
        redis_client.delete(f'task:{task_id}')

        requests.post('http://dashboard:5000/notify_task_delete', data={'task_id': task_id})
        
        return redirect('/delete_success')
    
    title = request.form.get('title')
    description = request.form.get('description', '')
    priority = request.form.get('priority', 'medium')
    due_date = request.form.get('due_date', '')
    status = request.form.get('status', 'pending')
    
    task_data = {
        'id': task_id,
        'title': title,
        'description': description,
        'priority': priority,
        'due_date': due_date,
        'status': status
    }
    redis_client.hset(f'task:{task_id}', mapping=task_data)
    
    requests.post('http://dashboard:5000/notify_task_update',data={'task_id': task_id})
    
    return redirect('/success')

@app.route('/success')
def success():
    return render_template('success-update.html')

@app.route('/delete_success')
def delete_success():
    return render_template('success-delete.html')

@app.route('/api/task_updates')
def get_task_updates():
    return {
        'updates_today': get_updates_today(),
        'new_tasks': get_new_tasks_today()
    }

@app.route('/notify_task_update', methods=['POST'])
def notify_task_update():
    # Increment the date-based counter
    updates_key = get_today_date_key('updates_count')
    redis_client.incr(updates_key)
    redis_client.expire(updates_key, 60*60*48)
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)