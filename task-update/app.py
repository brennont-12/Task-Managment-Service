from flask import Flask, request, redirect, render_template
from datetime import datetime as dt
import redis
import requests

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route('/')
def index():
    task_id = request.args.get('task_id')
    if not task_id:
        return redirect('/query/')
    # First, check if the task exists by communicating with the Task Query Service
    try:
        response = requests.get(f'http://task-query:5000/api/task/{task_id}')
        if response.status_code != 200:
            return f"Task with ID {task_id} not found.", 404
        task = response.json()
        return render_template('task-update.html', task=task)
    except requests.exceptions.RequestException as e:
        return f"Error communicating with Task Query Service: {e}", 500

@app.route('/save', methods=['POST'])
def save_task():
    task_id = request.form.get('task_id')
    
    # Check if task exists
    if not redis_client.exists(f'task:{task_id}'):
        return f"Task with ID {task_id} not found.", 404
    
    # Check which button was clicked
    if 'delete' in request.form:
        # Remove the task from the tasks set
        redis_client.srem('tasks', task_id)
        # Delete the task hash
        redis_client.delete(f'task:{task_id}')
        try:
            requests.post('http://dashboard:5000/notify_task_delete',
                         data={'task_id': task_id})
        except requests.exceptions.RequestException as e:
            print(f"Error notifying dashboard: {e}")
        return redirect('/delete_success')
    
    # Handle update (default case)
    title = request.form.get('title')
    description = request.form.get('description', '')
    priority = request.form.get('priority', 'medium')
    due_date = request.form.get('due_date', '')
    status = request.form.get('status', 'pending')
    
    # Update task in Redis
    task_data = {
        'id': task_id,
        'title': title,
        'description': description,
        'priority': priority,
        'due_date': due_date,
        'status': status
    }
    redis_client.hset(f'task:{task_id}', mapping=task_data)
    
    # Notify the dashboard service about the task update
    try:
        requests.post('http://dashboard:5000/notify_task_update',
                     data={'task_id': task_id})
    except requests.exceptions.RequestException as e:
        print(f"Error notifying dashboard: {e}")
    
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
        'updates_today': int(redis_client.get('updates_count')) or 0,
        'new_tasks': int(redis_client.get('new_tasks_count')) or 0
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)