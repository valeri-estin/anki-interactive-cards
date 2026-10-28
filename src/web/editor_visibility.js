/* Anki Interactive Cards - only affects the editor while an AIC notetype is active.
   Conservative DOM matching: never hides arbitrary containers or other addons.
   If Anki changes its editor markup, native collapsed-field metadata remains the fallback.
*/
(function () {
  'use strict';
  if (window.AICFieldVisibility) return;
  var technical = new Set();
  var show = false;
  var marked = new Set();
  var scheduled = false;
  var tag = document.createElement('style');
  tag.textContent = '.aic-technical-field-hidden { display:none !important; }';
  (document.head || document.documentElement).appendChild(tag);

  function exactName(el) {
    // Labels are not HTML content fields; compare the visible label text only.
    var name = (el.textContent || '').trim().replace(/\s+/g, ' ');
    return technical.has(name) ? name : null;
  }
  function isEditable(node) {
    return node.matches('anki-editable, [contenteditable="true"], textarea, .rich-text-editable');
  }
  function findRow(label) {
    // Do not hide an outer container with multiple field inputs.
    var el = label;
    for (var level = 0; el && level < 7; level++, el = el.parentElement) {
      if (el === document.body || el === document.documentElement) break;
      var inputs = Array.from(el.querySelectorAll('anki-editable, [contenteditable="true"], textarea, .rich-text-editable'));
      if (isEditable(el)) inputs.unshift(el);
      if (inputs.length === 1 && el !== label) {
        return el;
      }
    }
    return null;
  }
  function apply() {
    scheduled = false;
    var next = new Set();
    if (!show && technical.size) {
      var labels = document.querySelectorAll('[data-field-name], label, .fieldname, .field-name, .field-label, .field-header, .field-title, .field-label-text');
      for (var i = 0; i < labels.length; i++) {
        var label = labels[i];
        if (!exactName(label)) continue;
        var row = label.matches('[data-field-name]') && label.querySelector('anki-editable, [contenteditable="true"], textarea') ? label : findRow(label);
        if (row) next.add(row);
      }
    }
    marked.forEach(function (el) {
      if (!next.has(el)) el.classList.remove('aic-technical-field-hidden');
    });
    next.forEach(function (el) { el.classList.add('aic-technical-field-hidden'); });
    marked = next;
  }
  function queueApply() {
    if (scheduled) return;
    scheduled = true;
    Promise.resolve().then(apply);
  }
  window.AICFieldVisibility = {
    configure: function (names, reveal) {
      technical = new Set(Array.isArray(names) ? names : []);
      show = Boolean(reveal);
      queueApply();
    }
  };
  var observer = new MutationObserver(queueApply);
  observer.observe(document.documentElement, {childList:true, subtree:true});
  queueApply();
})();
