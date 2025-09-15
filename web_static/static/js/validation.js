'use strict';

function validateField(fieldName) {
  const field = document.getElementById(fieldName);
  const errorDiv = document.getElementById(fieldName + '-error');
  const value = field.value.trim();
  
  let isValid = true;
  let errorMessage = '';
  
  switch (fieldName) {
    case 'project':
      if (!value) {
        isValid = false;
        errorMessage = 'Project name is required';
      } else if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
        isValid = false;
        errorMessage = 'Project name can only contain letters, numbers, hyphens, and underscores';
      } else if (value.length < 3) {
        isValid = false;
        errorMessage = 'Project name must be at least 3 characters long';
      } else if (value.length > 50) {
        isValid = false;
        errorMessage = 'Project name must be less than 50 characters';
      }
      break;
      
    case 'content':
      if (!value) {
        isValid = false;
        errorMessage = 'Content is required';
      } else if (value.length < 10) {
        isValid = false;
        errorMessage = 'Content must be at least 10 characters long';
      }
      break;
  }
  
  if (isValid) {
    field.parentNode.classList.remove('error');
    errorDiv.classList.remove('show');
    errorDiv.textContent = '';
  } else {
    field.parentNode.classList.add('error');
    errorDiv.classList.add('show');
    errorDiv.textContent = errorMessage;
  }
  
  return isValid;
}

function validateAllFields() {
  const projectValid = validateField('project');
  const contentValid = validateField('content');
  
  return projectValid && contentValid;
}

function showValidationErrors(errors) {
  const errorsDiv = document.getElementById('validationErrors');
  if (errors && errors.length > 0) {
    errorsDiv.innerHTML = '<strong>Please fix these errors:</strong><ul>' + 
      errors.map(error => `<li>${error}</li>`).join('') + '</ul>';
    errorsDiv.style.display = 'block';
  } else {
    errorsDiv.style.display = 'none';
  }
}

function validateContentRealtime(content) {
  const validationDiv = document.getElementById('validationStatus');
  if (!validationDiv) return;
  
  const errors = [];
  const warnings = [];
  
  if (!content.trim()) {
    warnings.push('Content is empty');
  }
  if (!content.includes('#')) {
    warnings.push('No headings found in content');
  }
  const lines = content.split('\n');
  lines.forEach((line, index) => {
    if (line.length > 200) {
      warnings.push(`Line ${index + 1} is very long (${line.length} chars)`);
    }
  });
  
  let statusClass = 'validation-valid';
  let statusText = '✅ Valid';
  
  if (errors.length > 0) {
    statusClass = 'validation-invalid';
    statusText = `❌ ${errors.length} error(s)`;
  } else if (warnings.length > 0) {
    statusClass = 'validation-warning';
    statusText = `⚠️ ${warnings.length} warning(s)`;
  }
  
  validationDiv.className = `validation-status ${statusClass}`;
  validationDiv.textContent = statusText;
}
