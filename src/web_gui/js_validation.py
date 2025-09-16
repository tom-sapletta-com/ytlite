#!/usr/bin/env python3
"""
JavaScript Validation Module for YTLite Web GUI
"""

def get_validation_js():
    """Return JavaScript code for form validation functionality."""
    return """
// Field validation
function validateField(fieldName) {
  const field = document.getElementById(fieldName);
  const errorDiv = document.getElementById(fieldName + '-error');
  const value = field.value.trim();
  
  let isValid = true;
  let errorMessage = '';
  
  if (!value) {
    isValid = false;
    errorMessage = 'This field is required';
  } else if (fieldName === 'project') {
    // Project name validation
    if (!/^[a-zA-Z0-9_-]+$/.test(value)) {
      isValid = false;
      errorMessage = 'Project name can only contain letters, numbers, hyphens, and underscores';
    } else if (value.length < 2) {
      isValid = false;
      errorMessage = 'Project name must be at least 2 characters long';
    } else if (value.length > 50) {
      isValid = false;
      errorMessage = 'Project name must be less than 50 characters';
    }
  } else if (fieldName === 'content') {
    // Content validation
    if (value.length < 10) {
      isValid = false;
      errorMessage = 'Content must be at least 10 characters long';
    } else if (value.length > 5000) {
      isValid = false;
      errorMessage = 'Content must be less than 5000 characters';
    }
  }
  
  // Update field styling and error message
  if (isValid) {
    field.classList.remove('error');
    field.classList.add('valid');
    if (errorDiv) {
      errorDiv.textContent = '';
      errorDiv.style.display = 'none';
    }
  } else {
    field.classList.remove('valid');
    field.classList.add('error');
    if (errorDiv) {
      errorDiv.textContent = errorMessage;
      errorDiv.style.display = 'block';
    }
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
      errors.map(err => '<li>' + err + '</li>').join('') + '</ul>';
    errorsDiv.style.display = 'block';
  } else {
    errorsDiv.style.display = 'none';
  }
}

// Ensure a select element contains a given value; if not, append a temporary option and select it
function ensureSelectValue(selectId, value) {
  const sel = document.getElementById(selectId);
  if (!sel || value == null) return;
  const strVal = String(value);
  
  // Check if option already exists
  for (let opt of sel.options) {
    if (opt.value === strVal) {
      sel.value = strVal;
      return;
    }
  }
  
  // Add temporary option
  const newOpt = document.createElement('option');
  newOpt.value = strVal;
  newOpt.textContent = strVal + ' (from project)';
  sel.appendChild(newOpt);
  sel.value = strVal;
}

window.validateField = validateField;
window.validateAllFields = validateAllFields;
window.showValidationErrors = showValidationErrors;
window.ensureSelectValue = ensureSelectValue;
"""
