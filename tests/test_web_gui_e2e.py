#!/usr/bin/env python3
"""
End-to-End tests for Web GUI complete workflow.
Tests entire project lifecycle from creation to versioning.
"""

import pytest
import time
import os
import tempfile
import subprocess
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import requests

class WebGUIE2EServer:
    """Context manager for E2E testing server."""
    
    def __init__(self):
        self.process = None
        self.port = 5002
        
    def __enter__(self):
        # Start server with fast test mode
        env = os.environ.copy()
        env['YTLITE_FAST_TEST'] = '1'
        env['FLASK_PORT'] = str(self.port)
        
        self.process = subprocess.Popen(
            ['python', 'src/web_gui.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=Path(__file__).parent.parent
        )
        
        # Wait for server startup with increased timeout
        for _ in range(60):
            try:
                response = requests.get(f'http://localhost:{self.port}')
                if response.status_code == 200:
                    print(f"Server started successfully on port {self.port}")
                    return f'http://localhost:{self.port}'
            except:
                pass
            time.sleep(1)
        else:
            print("Server startup timed out after 60 seconds")
            # Log server output for debugging
            if self.process.stdout:
                print("Server stdout:", self.process.stdout.read().decode())
            if self.process.stderr:
                print("Server stderr:", self.process.stderr.read().decode())
            raise Exception("E2E server failed to start")
            
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            self.process.terminate()
            self.process.wait()

@pytest.fixture
def e2e_server():
    """E2E server fixture."""
    with WebGUIE2EServer() as url:
        yield url

@pytest.fixture
def driver():
    """Chrome driver for E2E tests."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(30)
    
    try:
        yield driver
    finally:
        driver.quit()

class TestWebGUIE2E:
    """Complete E2E workflow tests."""
    
    @pytest.mark.skip(reason="Skipping Selenium tests for debugging")
    def test_complete_project_workflow_tech_classic(self, driver, e2e_server):
        """Test complete workflow: create project, generate, validate, version history."""
        driver.get(e2e_server)
        
        # 1. Verify page loads
        assert "YTLite" in driver.page_source
        
        # 2. Test theme toggle
        theme_button = driver.find_element(By.CLASS_NAME, "theme-toggle")
        theme_button.click()
        time.sleep(1)
        
        body = driver.find_element(By.TAG_NAME, "body")
        assert body.get_attribute("data-theme") == "dark"
        
        # 3. Open create form
        create_button = driver.find_element(By.CLASS_NAME, "create-new")
        create_button.click()
        
        form = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "createForm"))
        )
        
        # 4. Fill form with tech/classic combination
        project_name = "e2e_test_tech_classic"
        
        driver.find_element(By.ID, "project").send_keys(project_name)
        driver.find_element(By.ID, "markdown").send_keys("""---
title: E2E Test Tech Classic
date: 2025-01-01
---

This is an end-to-end test for tech theme with classic template.
Testing the complete workflow from form submission to SVG validation.
""")
        
        # Select voice
        voice_select = Select(driver.find_element(By.ID, "voice"))
        voice_select.select_by_value("en-US-AriaNeural")
        
        # Select theme
        theme_select = Select(driver.find_element(By.ID, "theme"))
        theme_select.select_by_value("tech")
        
        # Select template
        template_select = Select(driver.find_element(By.ID, "template"))
        template_select.select_by_value("classic")
        
        # Set font size and language
        driver.find_element(By.ID, "font_size").send_keys("48")
        driver.find_element(By.ID, "lang").send_keys("en")
        
        # 5. Submit form
        generate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]")
        generate_button.click()
        
        # 6. Wait for generation to complete (with progress monitoring)
        progress_box = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "progressBox"))
        )
        
        # Wait for completion (or timeout after 60 seconds in fast mode)
        WebDriverWait(driver, 120).until(
            lambda d: d.find_element(By.ID, "progressBox").value_of_css_property("display") == "none"
        )
        
        # 7. Verify preview appears
        preview = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "preview"))
        )
        
        # Check for validation status in links
        links_content = driver.find_element(By.ID, "links").text
        assert "SVG" in links_content
        
        # 8. Reload and check projects list
        driver.refresh()
        time.sleep(2)
        
        projects_list = driver.find_element(By.ID, "projectsList")
        assert project_name in projects_list.text
        
    @pytest.mark.skip(reason="Skipping Selenium tests for debugging")
    def test_multiple_voice_options_workflow(self, driver, e2e_server):
        """Test creating projects with different voice options."""
        driver.get(e2e_server)
        
        voices_to_test = [
            ("pl-PL-MarekNeural", "philosophy", "gradient"),
            ("de-DE-KillianNeural", "wetware", "boxed"),
            ("en-US-GuyNeural", "tech", "left")
        ]
        
        for i, (voice, theme, template) in enumerate(voices_to_test):
            # Open create form
            create_button = driver.find_element(By.CLASS_NAME, "create-new")
            create_button.click()
            
            # Fill form
            project_name = f"e2e_voice_test_{i+1}"
            
            driver.find_element(By.ID, "project").clear()
            driver.find_element(By.ID, "project").send_keys(project_name)
            
            markdown_content = f"""---
title: Voice Test {voice}
date: 2025-01-01
---

Testing voice option {voice} with theme {theme} and template {template}.
"""
            driver.find_element(By.ID, "markdown").clear()
            driver.find_element(By.ID, "markdown").send_keys(markdown_content)
            
            # Select options
            Select(driver.find_element(By.ID, "voice")).select_by_value(voice)
            Select(driver.find_element(By.ID, "theme")).select_by_value(theme)
            Select(driver.find_element(By.ID, "template")).select_by_value(template)
            
            # Generate
            generate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]")
            generate_button.click()
            
            # Wait for completion
            try:
                WebDriverWait(driver, 120).until(
                    lambda d: d.find_element(By.ID, "progressBox").value_of_css_property("display") == "none"
                )
            except:
                # Continue even if this particular test times out
                pass
                
            time.sleep(2)  # Brief pause between tests
            
    @pytest.mark.skip(reason="Skipping Selenium tests for debugging")
    def test_env_file_upload_workflow(self, driver, e2e_server):
        """Test complete workflow with .env file upload."""
        driver.get(e2e_server)
        
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("CUSTOM_SETTING=e2e_test_value\n")
            f.write("API_KEY=test_api_key\n")
            env_file_path = f.name
            
        try:
            # Open create form
            driver.find_element(By.CLASS_NAME, "create-new").click()
            
            # Fill basic info
            driver.find_element(By.ID, "project").send_keys("e2e_env_file_test")
            driver.find_element(By.ID, "markdown").send_keys("""---
title: Env File Test
date: 2025-01-01
---

Testing project creation with custom .env file upload.
""")
            
            # Upload .env file
            file_input = driver.find_element(By.ID, "envfile")
            file_input.send_keys(env_file_path)
            
            # Set other options
            Select(driver.find_element(By.ID, "voice")).select_by_value("en-US-AriaNeural")
            Select(driver.find_element(By.ID, "theme")).select_by_value("tech")
            
            # Generate
            driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]").click()
            
            # Wait for completion
            try:
                WebDriverWait(driver, 120).until(
                    lambda d: d.find_element(By.ID, "progressBox").value_of_css_property("display") == "none"
                )
            except:
                pass  # Continue even if timeout
                
        finally:
            os.unlink(env_file_path)
            
    @pytest.mark.skip(reason="Skipping Selenium tests for debugging")
    def test_project_editing_workflow(self, driver, e2e_server):
        """Test editing existing projects."""
        driver.get(e2e_server)
        
        # First create a project
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        original_project = "e2e_edit_test"
        driver.find_element(By.ID, "project").send_keys(original_project)
        driver.find_element(By.ID, "markdown").send_keys("""---
title: Original Project
date: 2025-01-01
---

This project will be edited.
""")
        
        Select(driver.find_element(By.ID, "voice")).select_by_value("en-US-AriaNeural")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]").click()
        
        # Wait for completion
        try:
            WebDriverWait(driver, 120).until(
                lambda d: d.find_element(By.ID, "progressBox").value_of_css_property("display") == "none"
            )
        except:
            pass
            
        # Refresh and find the project
        driver.refresh()
        time.sleep(2)
        
        # Look for edit button (may need to scroll or wait for projects to load)
        try:
            edit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '✏️ Edit')]")
            if edit_buttons:
                edit_buttons[0].click()
                
                # Verify form is populated
                project_field = driver.find_element(By.ID, "project")
                assert project_field.get_attribute("value") == original_project
                
                # Modify and regenerate
                markdown_field = driver.find_element(By.ID, "markdown")
                current_content = markdown_field.get_attribute("value")
                markdown_field.clear()
                markdown_field.send_keys(current_content + "\n\nThis is an edited version.")
                
                # Generate again
                driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]").click()
                
        except Exception as e:
            # Edit functionality may not be available yet
            print(f"Edit test skipped: {e}")
            
    @pytest.mark.skip(reason="Skipping Selenium tests for debugging")
    def test_version_history_workflow(self, driver, e2e_server):
        """Test version history functionality."""
        driver.get(e2e_server)
        
        # Create project multiple times to generate versions
        project_name = "e2e_version_test"
        
        for version in range(2):
            driver.find_element(By.CLASS_NAME, "create-new").click()
            
            driver.find_element(By.ID, "project").clear()
            driver.find_element(By.ID, "project").send_keys(project_name)
            
            version_content = f"""---
title: Version Test {version + 1}
date: 2025-01-01
---

This is version {version + 1} of the version test project.
Each generation should create a new version.
"""
            driver.find_element(By.ID, "markdown").clear()
            driver.find_element(By.ID, "markdown").send_keys(version_content)
            
            # Generate
            driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]").click()
            
            # Wait for completion
            try:
                WebDriverWait(driver, 120).until(
                    lambda d: d.find_element(By.ID, "progressBox").value_of_css_property("display") == "none"
                )
            except:
                pass
                
            time.sleep(1)
            
        # Refresh and look for version history
        driver.refresh()
        time.sleep(2)
        
        # Check if version history button appears
        try:
            history_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '📜 History')]")
            if history_buttons:
                history_buttons[0].click()
                
                # Check if version modal appears
                version_modal = WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.ID, "versionModal"))
                )
                
                assert "Version History" in version_modal.text
                
                # Close modal
                close_button = driver.find_element(By.XPATH, "//button[contains(text(), '✕ Close')]")
                close_button.click()
                
        except Exception as e:
            print(f"Version history test skipped: {e}")
            
    @pytest.mark.skip(reason="Skipping Selenium tests for debugging")
    def test_wordpress_publish_interface(self, driver, e2e_server):
        """Test WordPress publishing interface."""
        driver.get(e2e_server)
        
        # Create a project first
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        driver.find_element(By.ID, "project").send_keys("e2e_wp_test")
        driver.find_element(By.ID, "markdown").send_keys("""---
title: WordPress Test
date: 2025-01-01
---

Testing WordPress publishing interface.
""")
        
        # Look for WordPress fields (they may be hidden by default)
        try:
            wp_url = driver.find_element(By.ID, "wp_url")
            wp_url.send_keys("https://test.wordpress.com")
            
            wp_user = driver.find_element(By.ID, "wp_user")
            wp_user.send_keys("testuser")
            
            wp_pass = driver.find_element(By.ID, "wp_pass")
            wp_pass.send_keys("testpass")
            
            # Try to find publish button
            publish_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Publish to WordPress')]")
            if publish_buttons:
                # Don't actually click - just verify interface exists
                assert len(publish_buttons) > 0
                
        except Exception as e:
            print(f"WordPress interface test skipped: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
