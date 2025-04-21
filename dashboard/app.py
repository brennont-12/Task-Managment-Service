from flask import Flask, render_template
from datetime import datetime
import redis
import requests

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)

@app.route('/')
def index():
    # Get task statistics by communicating with the Task Query Service
    try:
        stats_response = requests.get('http://task-query:5000/api/tasks/stats')
        stats = stats_response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting task stats: {e}")
        stats = {
            'total_tasks': 0,
            'status_counts': {'pending': 0, 'in_progress': 0, 'completed': 0},
            'priority_counts': {'low': 0, 'medium': 0, 'high': 0}
        }
    
    # Get task update activity by communicating with the Task Update Service
    try:
        updates_response = requests.get('http://task-update:5000/api/task_updates')
        update_stats = updates_response.json()
        activity = {
            'updates': int(update_stats.get('updates_today') or 0),
            'new_tasks': int(redis_client.get('new_tasks_count') or 0)
        }
    except requests.exceptions.RequestException as e:
        print(f"Error getting update stats: {e}")
        activity = {'updates': 0, 'new_tasks': 0}
    
    return render_template('task-dashboard.html', stats=stats, activity=activity)

@app.route('/notify_new_task', methods=['POST'])
def notify_new_task():
    redis_client.incr('new_tasks_count')
    return {'status': 'success'}

@app.route('/notify_task_delete', methods=['POST'])
def notify_task_delete():
    redis_client.decr('new_tasks_count')
    return {'status': 'success'}

@app.route('/notify_task_update', methods=['POST'])
def notify_task_update():
    redis_client.incr('updates_count')
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
