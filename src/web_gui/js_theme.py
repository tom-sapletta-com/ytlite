#!/usr/bin/env python3
"""
JavaScript Theme Module for YTLite Web GUI
"""

def get_theme_js():
    """Return JavaScript code for theme functionality."""
    return """
// Theme management
function toggleTheme() {
  const body = document.body;
  const themeIcon = document.getElementById('theme-icon');
  const themeText = document.getElementById('theme-text');
  
  if (body.getAttribute('data-theme') === 'dark') {
    body.removeAttribute('data-theme');
    localStorage.setItem('ytlite-theme', 'light');
    if (themeIcon) themeIcon.textContent = '🌙';
    if (themeText) themeText.textContent = 'Dark';
  } else {
    body.setAttribute('data-theme', 'dark');
    localStorage.setItem('ytlite-theme', 'dark');
    if (themeIcon) themeIcon.textContent = '☀️';
    if (themeText) themeText.textContent = 'Light';
  }
}

// Load saved theme on page load
function loadTheme() {
  const savedTheme = localStorage.getItem('ytlite-theme');
  if (savedTheme === 'dark') {
    document.body.setAttribute('data-theme', 'dark');
    const themeIcon = document.getElementById('theme-icon');
    const themeText = document.getElementById('theme-text');
    if (themeIcon) themeIcon.textContent = '☀️';
    if (themeText) themeText.textContent = 'Light';
  }
}

window.toggleTheme = toggleTheme;
window.loadTheme = loadTheme;
"""
