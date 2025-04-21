from flask import Flask, request, redirect, render_template
import redis
import uuid
import time
import requests

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0)


@app.route('/')
def index():
    return render_template('task_creation.html')

@app.route('/create', methods=['GET', 'POST'])
def create_task():
    if request.method == 'POST':
        # Generate a unique task ID
        task_id = str(uuid.uuid4())

        # Get task details from form
        title = request.form.get('title')
        description = request.form.get('description', '')
        priority = request.form.get('priority', 'medium')
        due_date = request.form.get('due_date', '')

        # Store task in Redis as a hash
        task_data = {
            'id': task_id,
            'title': title,
            'description': description,
            'priority': priority,
            'due_date': due_date,
            'status': 'pending',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }

        redis_client.hset(f'task:{task_id}', mapping=task_data)
        redis_client.sadd('tasks', task_id)

        # Notify dashboard
        try:
            requests.post('http://dashboard:5000/notify_new_task', data={'task_id': task_id})
        except Exception as e:
            print(f"Error notifying dashboard: {e}")

        # Redirect to success page
        return redirect('/success')
    # If GET request, render the form
    return render_template('task_creation.html')

@app.route('/success')
def success():
    return render_template('success-create.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
