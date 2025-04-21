from flask import Flask, request, jsonify, render_template, redirect
import redis

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)


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
    
    # Apply filters
    if status != 'all':
        tasks = [task for task in tasks if task['status'] == status]
    
    if priority != 'all':
        tasks = [task for task in tasks if task['priority'] == priority]
    
    return render_template('task-query.html', tasks=tasks)

@app.route('/delete-all', methods=['POST'])
def delete_all_tasks():
    # Get all keys that match task:* pattern
    task_keys = redis_client.keys('task:*')

    # Check what type the 'tasks' key is
    redis_client.type('tasks').decode() if redis_client.exists('tasks') else 'non-existent'
    
    # Create a pipeline
    pipeline = redis_client.pipeline()
    
    # Delete all task:* keys directly
    for task_key in task_keys:
        pipeline.delete(task_key)
    
    # Delete the 'tasks' key regardless of its type
    if redis_client.exists('tasks'):
        pipeline.delete('tasks')

    # Reset the new_tasks_count
    pipeline.set('new_tasks_count', 0)   
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
    """API endpoint for the Dashboard service to get task statistics"""
    tasks = get_all_tasks()
    
    # Count tasks by status
    status_counts = {
        'pending': 0,
        'in_progress': 0,
        'completed': 0
    }
    
    # Count tasks by priority
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