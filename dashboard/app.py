from flask import Flask, render_template
from datetime import datetime
import redis
import requests

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_today_date_key(metric):
    # Get a redis key with today's date embedded
    today = datetime.now().strftime('%Y-%m-%d')
    return f'{metric}:{today}'

@app.route('/')
def index():
    # Get task statistics by communicating with the Task Query Service
    stats_response = requests.get('http://task-query:5000/api/tasks/stats')
    stats = stats_response.json()
    
    # Get task update activity by communicating with the Task Update Service
    updates_response = requests.get('http://task-update:5000/api/task_updates')
    update_stats = updates_response.json()
    activity = {
        'updates': int(update_stats.get('updates_today') or 0),
        'new_tasks': int(update_stats.get('new_tasks') or 0)
    }

    return render_template('task-dashboard.html', stats=stats, activity=activity)

@app.route('/notify_new_task', methods=['POST'])
def notify_new_task():
    new_tasks_key = get_today_date_key('new_tasks_count')
    redis_client.incr(new_tasks_key)
    # Set expiry for 48 hours (to ensure it's available for the full day)
    redis_client.expire(new_tasks_key, 60*60*48)
    return {'status': 'success'}

@app.route('/notify_task_delete', methods=['POST'])
def notify_task_delete():
    new_tasks_key = get_today_date_key('new_tasks_count')
    current_count = int(redis_client.get(new_tasks_key) or 0)
    updates_key = get_today_date_key('updates_count')
    # Only decrement if the count is greater than 0
    if current_count > 0:
        redis_client.decr(new_tasks_key)
        redis_client.decr(updates_key)
    return {'status': 'success'}

@app.route('/notify_task_update', methods=['POST'])
def notify_task_update():
    # Use the date-based key
    updates_key = get_today_date_key('updates_count')
    redis_client.incr(updates_key)
    # Set expiry for 48 hours
    redis_client.expire(updates_key, 60*60*48)
    return {'status': 'success'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)