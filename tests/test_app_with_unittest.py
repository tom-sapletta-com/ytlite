import unittest
import os
import sys
from pathlib import Path

# Ensure src is in the path for imports
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from web_gui import create_app

class TestApp(unittest.TestCase):

    def setUp(self):
        """Set up a new app instance for each test."""
        os.environ['YTLITE_FAST_TEST'] = '1'
        app = create_app({'TESTING': True, 'DEBUG': False})
        self.client = app.test_client()

    def test_generate_with_overrides(self):
        """Test that the /api/generate endpoint runs successfully with form overrides."""
        project = f"unittest_overrides_1"
        markdown = "# Unittest Override Test\nThis is a test."
        
        form_data = {
            "project": project,
            "markdown": markdown,
            "voice": "en-US-AriaNeural",
            "theme": "dark",
            "font_size": "large"
        }

        response = self.client.post(
            "/api/generate",
            data=form_data,
            content_type="multipart/form-data",
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'generated successfully', response.data)

if __name__ == '__main__':
    unittest.main()
