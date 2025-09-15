(function(){
  'use strict';

  // Track UI actions: set URL hash and send to backend logs
  function trackAction(action, context, opts) {
    try {
      if (!action) return;
      const updateHash = !opts || opts.updateHash !== false;
      if (updateHash) {
        window.location.hash = '#' + encodeURIComponent(String(action));
      }
      fetch('/api/ui_event', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action, context: context || {} })
      }).catch(function(){ /* ignore */ });
      if (typeof window.logEvent === 'function') {
        try { window.logEvent('UI: ' + action, 'info', context || {}); } catch (_) {}
      }
    } catch (_) { /* ignore */ }
  }

  // Expose for other scripts if needed
  window.trackAction = trackAction;

  // Global click listener: derive an action id and track it
  document.addEventListener('click', function (ev) {
    try {
      var t = ev.target && ev.target.closest && ev.target.closest('[data-action],button,a,[role="button"],[id]');
      if (!t) return;
      var act = t.getAttribute('data-action') || t.id || (t.tagName.toLowerCase() + (t.textContent ? ':' + t.textContent.trim().slice(0, 40) : ''));
      trackAction(act, { tag: t.tagName, id: t.id || null, classes: t.className || '' });
    } catch (_) {}
  });

  // Wrap common UI functions if present so programmatic calls also track
  function wrapIfExists(name) {
    var fn = window[name];
    if (typeof fn !== 'function') return;
    window[name] = function(){
      try { trackAction(name, { args_preview: arguments && arguments.length ? String(arguments[0]).slice(0, 80) : null }); } catch (_) {}
      return fn.apply(this, arguments);
    };
  }

  function wrapMulti(map) {
    Object.keys(map).forEach(function(name){ wrapIfExists(name); });
  }

  function initWraps() {
    wrapMulti({
      'toggleTheme': 1,
      'showFormForCreate': 1,
      'switchProjectView': 1,
      'generateProject': 1,
      'updateProject': 1,
      'deleteProject': 1,
      'publishToYoutube': 1,
      'publishToWordPress': 1,
      'showVersionHistory': 1,
      'restoreVersion': 1,
      'openSVGWithAutoplay': 1,
      'validateProject': 1,
      'editProject': 1,
      'generateMedia': 1,
      'hideProjectForm': 1
    });
    // Specialize switchProjectView to include view in the hash
    if (typeof window.switchProjectView === 'function') {
      const __orig = window.switchProjectView;
      window.switchProjectView = function(view) {
        try { trackAction('switchProjectView:' + view, { view: view }); } catch (_) {}
        return __orig.apply(this, arguments);
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function(){
      try { trackAction('pageLoad'); } catch (_) {}
      initWraps();
    });
  } else {
    try { trackAction('pageLoad'); } catch (_) {}
    initWraps();
  }
})();
