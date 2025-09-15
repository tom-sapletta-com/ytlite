import pytest
from playwright.sync_api import Page, expect
import time

@pytest.mark.e2e
def test_create_project(page: Page, live_server: str):
    """Test creating a new project via the web GUI."""
    PROJECT_NAME = f"e2e_test_{int(time.time())}"
    page.goto(live_server)

    page.click("button:has-text('New Project')")

    page.fill("input[name='project']", PROJECT_NAME)
    page.fill("textarea[name='markdown']", "# Test Title\n\nThis is a test paragraph.")
    page.select_option("select[name='voice']", 'en-US-AriaNeural')
    page.select_option("select[name='theme']", 'tech')

    page.click("button:has-text('Create Project')")

    expect(page.locator("#toast-container")).to_contain_text(f'Project "{PROJECT_NAME}" generated successfully.')
    expect(page.locator(f"#project-card-{PROJECT_NAME}")).to_be_visible()

@pytest.mark.e2e
def test_edit_project_and_regenerate(page: Page, live_server: str):
    """Test editing a project, changing settings, and regenerating media."""
    EDIT_PROJECT_NAME = f"e2e_edit_test_{int(time.time())}"
    page.goto(live_server)
    page.click("button:has-text('New Project')")
    page.fill("input[name='project']", EDIT_PROJECT_NAME)
    page.fill("textarea[name='markdown']", "# Edit Test\n\nContent to be edited.")
    page.select_option("select[name='theme']", 'tech')
    page.select_option("select[name='voice']", 'en-US-AriaNeural')
    page.click("button:has-text('Create Project')")
    expect(page.locator(f"#project-card-{EDIT_PROJECT_NAME}")).to_be_visible()

    page.click(f"#project-card-{EDIT_PROJECT_NAME} button:has-text('Edit')")

    expect(page.locator("input[name='project']")).to_have_value(EDIT_PROJECT_NAME)
    page.select_option("select[name='theme']", 'philosophy')
    page.select_option("select[name='voice']", 'pl-PL-MarekNeural')
    page.check("input[name='force_regenerate']")

    page.click("button:has-text('Update Project')")

    expect(page.locator("#toast-container")).to_contain_text(f'Project "{EDIT_PROJECT_NAME}" generated successfully.')

    page.click(f"#project-card-{EDIT_PROJECT_NAME} button:has-text('Edit')")
    expect(page.locator("select[name='theme']")).to_have_value('philosophy')
    expect(page.locator("select[name='voice']")).to_have_value('pl-PL-MarekNeural')

@pytest.mark.e2e
def test_delete_project(page: Page, live_server: str):
    """Test deleting a project via the web GUI."""
    PROJECT_TO_DELETE = f"e2e_delete_test_{int(time.time())}"
    page.goto(live_server)
    page.click("button:has-text('New Project')")
    page.fill("input[name='project']", PROJECT_TO_DELETE)
    page.fill("textarea[name='markdown']", "# To Be Deleted")
    page.click("button:has-text('Create Project')")
    expect(page.locator(f"#project-card-{PROJECT_TO_DELETE}")).to_be_visible()

    project_card = page.locator(f"#project-card-{PROJECT_TO_DELETE}")
    expect(project_card).to_be_visible()

    project_card.locator("button:has-text('Delete')").click()

    expect(page.locator("#toast-container")).to_contain_text(f'Project "{PROJECT_TO_DELETE}" deleted successfully')
    
    expect(project_card).not_to_be_visible()
