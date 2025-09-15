'use strict';

(function(){
  function init() {
    if (typeof initLogger === 'function') initLogger();
    if (typeof loadTheme === 'function') loadTheme();
    if (typeof loadProjects === 'function') loadProjects();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
