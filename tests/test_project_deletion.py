"""Test project deletion functionality."""
import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import the Flask app from the correct location
from src.ytlite_web_gui import create_production_app

# Create the app instance for testing
app = create_production_app()


class TestProjectDeletion:
    """Test project deletion via API and Web GUI."""
    
    @pytest.fixture
    def client(self):
        """Flask test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary test project."""
        # Create a temporary project directory
        output_dir = Path('output/projects')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        project_name = 'test_deletion_project'
        project_dir = output_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Create test files
        (project_dir / f'{project_name}.svg').write_text('<svg></svg>')
        (project_dir / 'test.txt').write_text('test content')
        
        # Create versions directory with history
        versions_dir = project_dir / 'versions'
        versions_dir.mkdir(exist_ok=True)
        (versions_dir / f'{project_name}_v1.svg').write_text('<svg>v1</svg>')
        (versions_dir / f'{project_name}_v2.svg').write_text('<svg>v2</svg>')
        
        yield project_name, project_dir
        
        # Cleanup
        if project_dir.exists():
            shutil.rmtree(project_dir)
    
    def test_delete_project_success(self, client, temp_project):
        """Test successful project deletion."""
        project_name, project_dir = temp_project
        
        # Ensure project exists
        assert project_dir.exists()
        assert (project_dir / f'{project_name}.svg').exists()
        assert (project_dir / 'versions').exists()
        
        # Delete project
        response = client.post('/api/delete_project', 
                             json={'project': project_name, 'confirm': True})
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'deleted successfully' in data['message']
        
        # Verify project is deleted
        assert not project_dir.exists()
    
    def test_delete_project_missing_name(self, client):
        """Test deletion with missing project name."""
        response = client.post('/api/delete_project', json={'confirm': True})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing project name' in data['error']
    
    def test_delete_project_no_confirmation(self, client):
        """Test deleting a project without confirmation."""
        # Create a test project
        project_name = "test_no_confirm"
        project_dir = os.path.join(app.config.get('OUTPUT_DIR', 'output'), 'projects', project_name)
        os.makedirs(project_dir, exist_ok=True)
        with open(os.path.join(project_dir, 'test.txt'), 'w') as f:
            f.write("test")

        response = client.post('/api/delete_project', json={"project": project_name})
        self.assertEqual(response.status_code, 200)  
        data = response.get_json()
        self.assertFalse(data.get('success', False))  
        self.assertIn('error', data)  
        self.assertTrue(os.path.exists(project_dir), "Project directory should not be deleted without confirmation")

    def test_delete_nonexistent_project(self, client):
        """Test deleting a project that does not exist."""
        response = client.post('/api/delete_project', json={"project": "nonexistent", "confirm": True})
        self.assertEqual(response.status_code, 200)  
        data = response.get_json()
        self.assertFalse(data.get('success', False))  
        self.assertIn('error', data)  

    def test_delete_project_security_check(self, client):
        """Test security check for project deletion (prevent path traversal)."""
        response = client.post('/api/delete_project', json={"project": "../malicious/path", "confirm": True})
        self.assertEqual(response.status_code, 200)  
        data = response.get_json()
        self.assertFalse(data.get('success', False))  
        self.assertIn('error', data)  
        self.assertIn('invalid project name', data['error'].lower(), "Should prevent path traversal attacks")
    
    def test_delete_project_with_special_characters(self, client):
        """Test deletion with special characters in project name."""
        # Create project with safe special characters
        output_dir = Path('output/projects')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        project_name = 'test-project_123'
        project_dir = output_dir / project_name
        project_dir.mkdir(exist_ok=True)
        (project_dir / f'{project_name}.svg').write_text('<svg></svg>')
        
        try:
            response = client.post('/api/delete_project', 
                                 json={'project': project_name, 'confirm': True})
            
            assert response.status_code == 200
            assert not project_dir.exists()
        finally:
            if project_dir.exists():
                shutil.rmtree(project_dir)


class TestProjectDeletionIntegration:
    """Integration tests for project deletion workflow."""
    
    def test_delete_after_generation(self):
        """Test deleting a project after generating it."""
        # This would be an integration test with actual project generation
        # For now, we'll create a mock test
        pass
    
    def test_delete_with_version_history(self):
        """Test deletion preserves no traces of version history."""
        # Create test project with extensive version history
        output_dir = Path('output/projects')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        project_name = 'test_version_history_deletion'
        project_dir = output_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Create main SVG
        (project_dir / f'{project_name}.svg').write_text('<svg>main</svg>')
        
        # Create extensive version history
        versions_dir = project_dir / 'versions'
        versions_dir.mkdir(exist_ok=True)
        for i in range(1, 10):
            (versions_dir / f'{project_name}_v{i}.svg').write_text(f'<svg>version {i}</svg>')
        
        try:
            # Test deletion via API
            with app.test_client() as client:
                response = client.post('/api/delete_project', 
                                     json={'project': project_name, 'confirm': True})
                
                assert response.status_code == 200
                assert not project_dir.exists()
                assert not versions_dir.exists()
        finally:
            if project_dir.exists():
                shutil.rmtree(project_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
