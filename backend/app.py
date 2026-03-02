import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# Database connection parameters
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', '5432')
DB_NAME = os.environ.get('DB_NAME', 'todoapp')
DB_USER = os.environ.get('DB_USER', 'todouser')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'todopassword123')
BACKEND_PORT = os.environ.get('BACKEND_PORT', '5000')

def get_db_connection():
    """Create a database connection"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database tables if they don't exist"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Create tasks table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(50) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cur.close()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    # Test database connection
    db_status = "connected"
    conn = get_db_connection()
    if not conn:
        db_status = "disconnected"
    else:
        conn.close()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'database': db_status,
        'service': 'backend'
    }), 200

# Get all tasks
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute('SELECT id, title, description, status, created_at FROM tasks ORDER BY id DESC')
        tasks = []
        for row in cur.fetchall():
            tasks.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'status': row[3],
                'created_at': row[4]
            })
        cur.close()
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Create a new task
@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO tasks (title, description, status) VALUES (%s, %s, %s) RETURNING id',
            (data['title'], data.get('description', ''), data.get('status', 'pending'))
        )
        task_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        return jsonify({'id': task_id, 'message': 'Task created successfully'}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Update a task
@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    data = request.get_json()
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        # Check if task exists
        cur.execute('SELECT id FROM tasks WHERE id = %s', (task_id,))
        if not cur.fetchone():
            return jsonify({'error': 'Task not found'}), 404
        
        # Update task
        cur.execute(
            'UPDATE tasks SET title = %s, description = %s, status = %s WHERE id = %s',
            (data.get('title'), data.get('description'), data.get('status'), task_id)
        )
        conn.commit()
        cur.close()
        return jsonify({'message': 'Task updated successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# Delete a task
@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        # Check if task exists
        cur.execute('SELECT id FROM tasks WHERE id = %s', (task_id,))
        if not cur.fetchone():
            return jsonify({'error': 'Task not found'}), 404
        
        # Delete task
        cur.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
        conn.commit()
        cur.close()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    # Initialize database
    init_database()
    # Run the app
    app.run(host='0.0.0.0', port=int(BACKEND_PORT))