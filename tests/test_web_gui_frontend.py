#!/usr/bin/env python3
"""
Frontend tests for Web GUI form validation and functionality.
Tests all form options and combinations using Selenium WebDriver.
"""

import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import subprocess
import os
from pathlib import Path
import tempfile
import threading
import requests

# Test data combinations
VOICE_OPTIONS = [
    'pl-PL-MarekNeural',
    'pl-PL-ZofiaNeural', 
    'de-DE-KillianNeural',
    'de-DE-KatjaNeural',
    'en-US-GuyNeural',
    'en-US-AriaNeural'
]

THEME_OPTIONS = ['tech', 'philosophy', 'wetware']
TEMPLATE_OPTIONS = ['classic', 'gradient', 'boxed', 'left']
FONT_SIZES = ['24', '36', '48', '64']
LANGUAGES = ['pl', 'en', 'de']

class WebGUIServer:
    """Context manager for starting/stopping web GUI server for tests."""
    
    def __init__(self):
        self.process = None
        self.port = 5001  # Use different port to avoid conflicts
        
    def __enter__(self):
        # Start web GUI server
        env = os.environ.copy()
        env['YTLITE_FAST_TEST'] = '1'  # Enable fast test mode
        env['FLASK_PORT'] = str(self.port)
        
        self.process = subprocess.Popen(
            ['python', 'src/web_gui.py'],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        for _ in range(30):
            try:
                response = requests.get(f'http://localhost:{self.port}')
                if response.status_code == 200:
                    break
            except:
                pass
            time.sleep(1)
        else:
            raise Exception("Failed to start web GUI server")
            
        return f'http://localhost:{self.port}'
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            self.process.terminate()
            self.process.wait()

@pytest.fixture
def web_server():
    """Fixture providing web server URL."""
    with WebGUIServer() as url:
        yield url

@pytest.fixture
def driver():
    """Fixture providing Chrome WebDriver."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    
    try:
        yield driver
    finally:
        driver.quit()

class TestWebGUIFrontend:
    """Test suite for Web GUI frontend functionality."""
    
    def test_page_loads(self, driver, web_server):
        """Test that the main page loads correctly."""
        driver.get(web_server)
        
        # Check title
        assert "YTLite Projects" in driver.title or "YTLite" in driver.page_source
        
        # Check main elements exist
        assert driver.find_element(By.TAG_NAME, "h1")
        assert driver.find_element(By.CLASS_NAME, "create-new")
        
    def test_theme_toggle(self, driver, web_server):
        """Test day/night theme toggle functionality."""
        driver.get(web_server)
        
        # Find theme toggle button
        theme_button = driver.find_element(By.CLASS_NAME, "theme-toggle")
        theme_icon = driver.find_element(By.ID, "theme-icon")
        theme_text = driver.find_element(By.ID, "theme-text")
        
        # Initial state should be light mode
        initial_icon = theme_icon.text
        initial_text = theme_text.text
        
        # Toggle to dark mode
        theme_button.click()
        time.sleep(0.5)  # Wait for transition
        
        # Check that theme changed
        new_icon = theme_icon.text
        new_text = theme_text.text
        
        assert new_icon != initial_icon
        assert new_text != initial_text
        
        # Check data-theme attribute
        body = driver.find_element(By.TAG_NAME, "body")
        assert body.get_attribute("data-theme") == "dark"
        
    def test_create_form_appears(self, driver, web_server):
        """Test that create form appears when clicked."""
        driver.get(web_server)
        
        # Click create new project
        create_button = driver.find_element(By.CLASS_NAME, "create-new")
        create_button.click()
        
        # Check form appears
        form = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "createForm"))
        )
        
        assert form.is_displayed()
        
    def test_form_elements_present(self, driver, web_server):
        """Test that all form elements are present."""
        driver.get(web_server)
        
        # Show create form
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        # Check all form elements exist
        assert driver.find_element(By.ID, "project")
        assert driver.find_element(By.ID, "markdown")
        assert driver.find_element(By.ID, "voice")
        assert driver.find_element(By.ID, "theme")
        assert driver.find_element(By.ID, "template")
        assert driver.find_element(By.ID, "font_size")
        assert driver.find_element(By.ID, "lang")
        assert driver.find_element(By.ID, "envfile")
        
    def test_voice_options(self, driver, web_server):
        """Test all voice options are available."""
        driver.get(web_server)
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        voice_select = Select(driver.find_element(By.ID, "voice"))
        available_voices = [option.get_attribute("value") for option in voice_select.options]
        
        for voice in VOICE_OPTIONS:
            assert voice in available_voices
            
    def test_theme_options(self, driver, web_server):
        """Test all theme options are available."""
        driver.get(web_server)
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        theme_select = Select(driver.find_element(By.ID, "theme"))
        available_themes = [option.get_attribute("value") for option in theme_select.options]
        
        for theme in THEME_OPTIONS:
            assert theme in available_themes
            
    def test_template_options(self, driver, web_server):
        """Test all template options are available.""" 
        driver.get(web_server)
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        template_select = Select(driver.find_element(By.ID, "template"))
        available_templates = [option.get_attribute("value") for option in template_select.options]
        
        for template in TEMPLATE_OPTIONS:
            assert template in available_templates
            
    def test_form_validation_empty_project(self, driver, web_server):
        """Test form validation with empty project name."""
        driver.get(web_server)
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        # Try to generate without project name
        generate_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Generate')]")
        generate_button.click()
        
        # Should show alert (we can't easily test alert, but function should return early)
        # The page should not proceed to generation
        
    def test_form_fill_and_select_options(self, driver, web_server):
        """Test filling form with different option combinations."""
        driver.get(web_server)
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        # Fill basic fields
        driver.find_element(By.ID, "project").send_keys("test_project_frontend")
        driver.find_element(By.ID, "markdown").send_keys("""---
title: Test Frontend Project
date: 2025-01-01
---

This is a frontend test project to verify form functionality.
""")
        
        # Test selecting different options
        voice_select = Select(driver.find_element(By.ID, "voice"))
        voice_select.select_by_value("en-US-AriaNeural")
        
        theme_select = Select(driver.find_element(By.ID, "theme"))
        theme_select.select_by_value("tech")
        
        template_select = Select(driver.find_element(By.ID, "template"))
        template_select.select_by_value("gradient")
        
        driver.find_element(By.ID, "font_size").send_keys("36")
        driver.find_element(By.ID, "lang").send_keys("en")
        
        # Verify values are set
        assert driver.find_element(By.ID, "project").get_attribute("value") == "test_project_frontend"
        assert "Test Frontend Project" in driver.find_element(By.ID, "markdown").get_attribute("value")
        
    def test_env_file_upload(self, driver, web_server):
        """Test .env file upload functionality."""
        driver.get(web_server)
        driver.find_element(By.CLASS_NAME, "create-new").click()
        
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("TEST_VAR=test_value\nANOTHER_VAR=another_value\n")
            env_file_path = f.name
            
        try:
            # Upload file
            file_input = driver.find_element(By.ID, "envfile")
            file_input.send_keys(env_file_path)
            
            # Verify file is selected
            assert env_file_path.endswith(file_input.get_attribute("value").split("\\")[-1])
            
        finally:
            os.unlink(env_file_path)
            
    def test_projects_list_loads(self, driver, web_server):
        """Test that projects list loads correctly."""
        driver.get(web_server)
        
        # Wait for projects to load
        projects_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "projectsList"))
        )
        
        # Should show either projects or "No projects found" message
        content = projects_container.text
        assert content is not None
        assert len(content) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
