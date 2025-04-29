from flask import Flask, render_template
from datetime import datetime
import redis
import requests

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)

# Function to get a key with today's date embedded
def get_today_date_key(metric):
    # Get a redis key with today's date embedded
    today = datetime.now().strftime('%Y-%m-%d')
    return f'{metric}:{today}'

# Dashboard route
@app.route('/')
def index():
    stats_response = requests.get('http://task-query:5000/api/tasks/stats')
    stats = stats_response.json()
    
    updates_response = requests.get('http://task-update:5000/api/task_updates')
    update_stats = updates_response.json()
    activity = {
        'updates': int(update_stats.get('updates_today') or 0),
        'new_tasks': int(update_stats.get('new_tasks') or 0)
    }

    return render_template('task-dashboard.html', stats=stats, activity=activity)

# Notify the dashboard that a new task was created
@app.route('/notify_new_task', methods=['POST'])
def notify_new_task():
    new_tasks_key = get_today_date_key('new_tasks_count')
    redis_client.incr(new_tasks_key)
    redis_client.expire(new_tasks_key, 60*60*48)
    return {'status': 'success'}

# Notify the dashboard that a task was deleted
@app.route('/notify_task_delete', methods=['POST'])
def notify_task_delete():
    new_tasks_key = get_today_date_key('new_tasks_count')
    current_count = int(redis_client.get(new_tasks_key) or 0)
    updates_key = get_today_date_key('updates_count')
    if current_count > 0:
        redis_client.decr(new_tasks_key)
        redis_client.decr(updates_key)
    return {'status': 'success'}

# Notify the dashboard that a task was updated
@app.route('/notify_task_update', methods=['POST'])
def notify_task_update():
    # Use the date-based key
    updates_key = get_today_date_key('updates_count')
    redis_client.incr(updates_key)
    redis_client.expire(updates_key, 60*60*48)
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)