from flask import Flask, request, jsonify, render_template, redirect
import redis
from datetime import datetime

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)

def get_today_date_key(metric):
    # Get a redis key with today's date embedded
    today = datetime.now().strftime('%Y-%m-%d')
    return f'{metric}:{today}'

def get_all_tasks():
    tasks = []
    task_ids = redis_client.smembers('tasks')
    for task_id in task_ids:
        task_data = redis_client.hgetall(f'task:{task_id.decode()}')
        if task_data:
            task = {key.decode(): value.decode() for key, value in task_data.items()}
            tasks.append(task)
    return tasks

@app.route('/')
def index():
    tasks = get_all_tasks()
    return render_template('task-query.html', tasks=tasks)

@app.route('/filter')
def filter_tasks():
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')
    tasks = get_all_tasks()
    
    if status != 'all':
        tasks = [task for task in tasks if task['status'] == status]
    if priority != 'all':
        tasks = [task for task in tasks if task['priority'] == priority]
    
    return render_template('task-query.html', tasks=tasks)

@app.route('/delete-all', methods=['POST'])
def delete_all_tasks():
    task_keys = redis_client.keys('task:*')
    
    pipeline = redis_client.pipeline()
    
    for task_key in task_keys:
        pipeline.delete(task_key)
    
    if redis_client.exists('tasks'):
        pipeline.delete('tasks')
    
    new_tasks_key = get_today_date_key('new_tasks_count')
    updates_key = get_today_date_key('updates_count')
    
    pipeline.set(new_tasks_key, 0)
    pipeline.set(updates_key, 0)
    
    pipeline.execute()
    
    # Return success
    return redirect('/success')

@app.route('/success')
def success():
    return render_template('success-delete-all.html')

@app.route('/api/tasks')
def api_tasks():
    tasks = get_all_tasks()
    return jsonify(tasks)

@app.route('/api/task/<task_id>')
def api_task(task_id):
    task_data = redis_client.hgetall(f'task:{task_id}')
    if not task_data:
        return jsonify({"error": "Task not found"}), 404
    task = {key.decode(): value.decode() for key, value in task_data.items()}
    return jsonify(task)

@app.route('/api/tasks/stats')
def api_tasks_stats():
    # API Endpoint to get task statistics
    tasks = get_all_tasks()
    
    status_counts = {
        'pending': 0,
        'in_progress': 0,
        'completed': 0
    }
    
    priority_counts = {
        'low': 0,
        'medium': 0,
        'high': 0
    }
    
    for task in tasks:
        status = task.get('status', 'pending')
        priority = task.get('priority', 'medium')
        
        if status in status_counts:
            status_counts[status] += 1
        
        if priority in priority_counts:
            priority_counts[priority] += 1
    
    return jsonify({
        'total_tasks': len(tasks),
        'status_counts': status_counts,
        'priority_counts': priority_counts
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)