#!/usr/bin/env python3
"""
JavaScript Forms Module for YTLite Web GUI
"""

def get_forms_js():
    """Return JavaScript code for form management functionality."""
    return """
// Form management
function showProjectForm() {
  const form = document.getElementById('projectForm');
  form.style.display = 'block';
  form.scrollIntoView({behavior: 'smooth'});
  
  // Attach form event listeners if not already attached
  if (!window.formHandlersAttached) {
    attachFormHandlers();
    window.formHandlersAttached = true;
  }
}

function hideProjectForm() {
  document.getElementById('projectForm').style.display = 'none';
  const mp = document.getElementById('mediaPreview');
  if (mp) mp.style.display = 'none';
}

function showFormForCreate() {
  document.getElementById('form-title').textContent = '📝 Create New Project';
  document.getElementById('project').readOnly = false;
  document.getElementById('project').value = '';
  document.getElementById('content').value = '';
  document.getElementById('generateBtn').style.display = 'inline-block';
  document.getElementById('updateBtn').style.display = 'none';
  
  // Reset form fields to defaults
  const voice = document.getElementById('voice');
  if (voice) voice.value = 'en-US-AriaNeural';
  const theme = document.getElementById('theme');
  if (theme) theme.value = 'tech';
  const template = document.getElementById('template');
  if (template) template.value = 'classic';
  const lang = document.getElementById('lang');
  if (lang) lang.value = 'en';
  const fontSize = document.getElementById('font_size');
  if (fontSize) fontSize.value = 'medium';
  
  showProjectForm();
}

function showFormForEdit() {
  document.getElementById('form-title').textContent = '✏️ Edit Project';
  document.getElementById('project').readOnly = true;
  document.getElementById('generateBtn').style.display = 'none';
  document.getElementById('updateBtn').style.display = 'inline-block';
  showProjectForm();
}

function populateProjectForm(name, meta) {
  document.getElementById('project').value = name;
  
  const candidate = meta.markdown_content || meta.markdown || meta.content || meta.description;
  if (candidate) {
    document.getElementById('content').value = candidate;
  }
  
  // Set form fields from metadata using helper function
  if (meta.voice) ensureSelectValue('voice', meta.voice);
  if (meta.theme) ensureSelectValue('theme', meta.theme);
  if (meta.template) ensureSelectValue('template', meta.template);
  if (meta.language || meta.lang) ensureSelectValue('lang', meta.language || meta.lang);
  if (meta.font_size) ensureSelectValue('font_size', meta.font_size);
  
  // Update media preview
  if (typeof updateMediaPreview === 'function') {
    updateMediaPreview(name);
  }
}

function attachFormHandlers() {
  // Real-time validation
  const projectField = document.getElementById('project');
  const contentField = document.getElementById('content');
  
  if (projectField) {
    projectField.addEventListener('input', () => validateField('project'));
    projectField.addEventListener('blur', () => validateField('project'));
  }
  
  if (contentField) {
    contentField.addEventListener('input', () => validateField('content'));
    contentField.addEventListener('blur', () => validateField('content'));
  }
}

window.showProjectForm = showProjectForm;
window.hideProjectForm = hideProjectForm;
window.showFormForCreate = showFormForCreate;
window.showFormForEdit = showFormForEdit;
window.populateProjectForm = populateProjectForm;
window.attachFormHandlers = attachFormHandlers;
"""
