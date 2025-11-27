import os
import sys
import json
import requests
import unittest
from unittest.mock import patch, MagicMock

# Add the backend directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend')))

class TestTaskAPI(unittest.TestCase):    
    BASE_URL = 'http://localhost:5000/api/tasks'
    
    def setUp(self):
        # This would be replaced with test database setup in a real scenario
        self.test_task = {
            'title': 'Test Task',
            'description': 'This is a test task',
            'status': 'pending'
        }
    
    def test_get_tasks_empty(self):
        """Test getting tasks when none exist"""
        response = requests.get(self.BASE_URL)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), 0)
    
    def test_create_task_success(self):
        """Test creating a new task successfully"""
        response = requests.post(self.BASE_URL, json={
            'title': 'New Task',
            'description': 'Task description',
            'status': 'pending'
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertIn('_id', data)
        self.assertEqual(data['title'], 'New Task')
        
        # Cleanup
        if '_id' in data:
            requests.delete(f"{self.BASE_URL}/{data['_id']}")
    
    def test_create_task_missing_title(self):
        """Test creating a task without required title"""
        response = requests.post(self.BASE_URL, json={
            'description': 'Task without title'
        })
        self.assertEqual(response.status_code, 400)
    
    def test_get_task_by_id(self):
        """Test retrieving a single task by ID"""
        # First create a task
        create_response = requests.post(self.BASE_URL, json={
            'title': 'Test Get Task',
            'description': 'Should be retrievable by ID'
        })
        task_id = create_response.json().get('_id')
        
        # Then try to get it
        response = requests.get(f"{self.BASE_URL}/{task_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'Test Get Task')
        
        # Cleanup
        if task_id:
            requests.delete(f"{self.BASE_URL}/{task_id}")
    
    def test_update_task(self):
        """Test updating an existing task"""
        # Create a task first
        create_response = requests.post(self.BASE_URL, json={
            'title': 'Original Title',
            'description': 'Original Description',
            'status': 'pending'
        })
        task_id = create_response.json().get('_id')
        
        # Update the task
        update_data = {
            'title': 'Updated Title',
            'status': 'in-progress'
        }
        response = requests.put(f"{self.BASE_URL}/{task_id}", json=update_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['title'], 'Updated Title')
        self.assertEqual(data['status'], 'in-progress')
        
        # Cleanup
        if task_id:
            requests.delete(f"{self.BASE_URL}/{task_id}")
    
    def test_delete_task(self):
        """Test deleting a task"""
        # Create a task to delete
        create_response = requests.post(self.BASE_URL, json={
            'title': 'Task to Delete',
            'description': 'This will be deleted'
        })
        task_id = create_response.json().get('_id')
        
        # Delete the task
        response = requests.delete(f"{self.BASE_URL}/{task_id}")
        self.assertEqual(response.status_code, 200)
        
        # Verify it's gone
        get_response = requests.get(f"{self.BASE_URL}/{task_id}")
        self.assertEqual(get_response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
