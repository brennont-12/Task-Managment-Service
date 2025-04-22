# Task Management System

This project is a **Task Management System** built using Flask, Redis, and Docker. It allows users to create, update, delete, and query tasks, as well as view task statistics on a dashboard. The system is designed to be modular, with separate services for task creation, querying, updating, and a dashboard for analytics.

---

## Features

- **Task Creation**: Create new tasks with attributes like title, description, priority, due date, and status.
- **Task Querying**: View all tasks, filter tasks by status or priority, and delete all tasks.
- **Task Updating**: Update task details or delete individual tasks.
- **Dashboard**: View task statistics, including total tasks, status distribution, and priority distribution.
- **Microservices Architecture**: Each service (creation, query, update, dashboard) runs independently and communicates via REST APIs.
- **Redis Integration**: Tasks are stored in Redis for fast and efficient data access.
- **Dockerized Deployment**: All services are containerized using Docker for easy deployment and scalability.

---

## Architecture

The system consists of the following services:

1. **Task Creation Service** (`task-creation`):
   - Allows users to create new tasks.
   - Notifies the dashboard service when a new task is created.

2. **Task Query Service** (`task-query`):
   - Displays all tasks and allows filtering by status or priority.
   - Provides an API for retrieving task details and statistics.

3. **Task Update Service** (`task-update`):
   - Allows users to update task details or delete individual tasks.
   - Notifies the dashboard service when a task is updated or deleted.

4. **Dashboard Service** (`dashboard`):
   - Displays task statistics, including total tasks, status distribution, and priority distribution.
   - Tracks system activity, such as new tasks and updates.

5. **Redis**:
   - Acts as the primary data store for tasks and statistics.

6. **NGINX**:
   - Acts as a reverse proxy to route requests to the appropriate service.

---

## Prerequisites

- Docker and Docker Compose installed on your system.
- Python 3.8+ (if running services locally without Docker).

---

## Installation and Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>
2. Build and start the services using Docker Compose:
    ```
    docker-compose up --build
    ```
3. Access the application:

Dashboard: http://<local-ip>/
Task Creation: http://<local-ip>/task-create/
Task Query: http://<local-ip>/query/
Task Update: http://<local-ip>/update/

## Usage

### Task Creation
1. Navigate to the **Task Creation** page: [http://<local-ip>/task-create/](http://<local-ip>/task-create/).
2. Fill in the task details (title, description, priority, due date).
3. Submit the form to create a new task.

### Task Querying
1. Navigate to the **Task Query** page: [http://<local-ip>/query/](http://<local-ip>/query/).
2. View all tasks or filter tasks by status or priority.
3. Use the "Delete All Tasks" button to remove all tasks.

### Task Updating
1. Navigate to the **Task Query** page: [http://<local-ip>/query/](http://<local-ip>/query/).
2. Click "Edit" on a task to update its details.
3. Update the task details or delete the task.

### Dashboard
1. Navigate to the **Dashboard** page: [http://<local-ip>/](http://<local-ip>/).
2. View task statistics, including total tasks, status distribution, and priority distribution.

## API Endpoints

### Task Query Service
- **GET /api/tasks**: Retrieve all tasks.
- **GET /api/task/<task_id>**: Retrieve details of a specific task.
- **GET /api/tasks/stats**: Retrieve task statistics.

### Task Update Service
- **POST /notify_task_update**: Notify the dashboard of a task update.
- **POST /notify_task_delete**: Notify the dashboard of a task deletion.

### Dashboard Service
- **POST /notify_new_task**: Notify the dashboard of a new task.

---

## Environment Variables

The following environment variables can be configured in the `docker-compose.yaml` file:

- **`REDIS_HOST`**: Hostname for the Redis service (default: `redis`).
- **`REDIS_PORT`**: Port for the Redis service (default: `6379`).

## Contributing

Contributions are welcome! To contribute to this project, follow these steps:

1. **Fork the Repository**:  
   Click the "Fork" button at the top of this repository to create your own copy.

2. **Clone the Repository**:  
   Clone your forked repository to your local machine:
   ```bash
   git@github.com:<Your-Username>/Task-Managment-Service.git