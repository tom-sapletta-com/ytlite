'use strict';

function ensureSelectValue(selectId, value) {
  const sel = document.getElementById(selectId);
  if (!sel || value == null) return;
  const strVal = String(value);
  const existing = Array.from(sel.options).find(o => o.value === strVal);
  if (!existing) {
    const opt = document.createElement('option');
    opt.value = strVal;
    opt.textContent = strVal;
    opt.setAttribute('data-custom', '1');
    sel.appendChild(opt);
    if (typeof logEvent === 'function') { try { logEvent(`Added custom option to #${selectId}: ${strVal}`, 'warn'); } catch (_) {} }
  }
  sel.value = strVal;
}

function showProjectForm() {
  const form = document.getElementById('projectForm');
  form.style.display = 'block';
  form.scrollIntoView({behavior: 'smooth'});
  if (!formHandlersAttached) {
    const contentEl = document.getElementById('content');
    contentEl.addEventListener('input', () => {
      const proj = document.getElementById('project').value.trim();
      if (proj) {
        localStorage.setItem(`ytlite:content:${proj}`, contentEl.value);
      }
    });
    formHandlersAttached = true;
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
  document.getElementById('generateBtn').style.display = 'inline-flex';
  document.getElementById('updateBtn').style.display = 'none';
  showProjectForm();
  const mp = document.getElementById('mediaPreview');
  const mpb = document.getElementById('mediaPreviewBody');
  if (mp) mp.style.display = 'none';
  if (mpb) mpb.innerHTML = '';
  const theme = document.getElementById('theme');
  const template = document.getElementById('template');
  const voice = document.getElementById('voice');
  const fontSize = document.getElementById('font_size');
  if (theme) theme.value = 'default';
  if (template) template.value = 'simple';
  if (voice) voice.value = 'en-US';
  if (fontSize) fontSize.value = 'medium';
}

function showFormForEdit() {
  document.getElementById('form-title').textContent = '✏️ Edit Project';
  document.getElementById('project').readOnly = true;
  document.getElementById('generateBtn').style.display = 'none';
  document.getElementById('updateBtn').style.display = 'inline-flex';
  showProjectForm();
}

function populateProjectForm(name, meta) {
  document.getElementById('project').value = name;
  const candidate = meta.markdown_content || meta.markdown || meta.content || meta.description;
  if (candidate && String(candidate).trim().length > 0) {
    document.getElementById('content').value = candidate;
    localStorage.setItem(`ytlite:content:${name}`, candidate);
    if (typeof logEvent === 'function') { try { logEvent(`Content loaded from metadata for ${name} (${candidate.length} chars)`, 'info'); } catch (_) {} }
  } else {
    const cached = localStorage.getItem(`ytlite:content:${name}`) || '';
    if (cached) {
      document.getElementById('content').value = cached;
      if (typeof logEvent === 'function') { try { logEvent(`Content restored from cache for ${name} (${cached.length} chars)`, 'warn'); } catch (_) {} }
    } else {
      if (typeof logEvent === 'function') { try { logEvent(`No content found in metadata for ${name}`, 'warn', {available: Object.keys(meta)}); } catch (_) {} }
    }
  }
  if (meta.voice) ensureSelectValue('voice', meta.voice);
  if (meta.theme) ensureSelectValue('theme', meta.theme);
  if (meta.template) ensureSelectValue('template', meta.template);
  if (meta.font_size) ensureSelectValue('font_size', meta.font_size);
}
