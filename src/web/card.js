/* Anki Interactive Cards – inline, offline, no scheduler hooks / no dependencies. */
(function () {
  'use strict';
  function text(el, value) { el.textContent = value == null ? '' : String(value); return el; }
  function node(tag, cls, value) { var e = document.createElement(tag); if (cls) e.className = cls; if (value !== undefined) text(e, value); return e; }
  function data(root, name) { var el = root.querySelector('[data-aic-field="' + name + '"]'); return el ? el.textContent.trim() : ''; }
  function json(root, name, fallback) { try { return JSON.parse(data(root, name)); } catch (_) { return fallback; } }
  function norm(s) { return String(s || '').normalize('NFKC').toLocaleLowerCase().trim().replace(/[.!?…]+$/, '').trim().replace(/\s+/g, ' '); }
  function shuffle(xs) { var out = xs.slice(); for (var i = out.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var v = out[i]; out[i] = out[j]; out[j] = v; } return out; }
  function store(root, value) { var key='anki-interactive:' + root.getAttribute('data-uid'); var record={at:Date.now(),value:value}; window.__aicResponses=window.__aicResponses||{}; window.__aicResponses[key]=record; try { sessionStorage.setItem(key,JSON.stringify(record)); } catch (_) {} }
  function retrieve(root) { var key='anki-interactive:' + root.getAttribute('data-uid'); var v=null; try { v=JSON.parse(sessionStorage.getItem(key)||'null'); } catch (_) {} v=v||((window.__aicResponses||{})[key]); return v && Date.now()-v.at<1800000 ? v.value : null; }
  function clear(root) { var key='anki-interactive:' + root.getAttribute('data-uid'); if (window.__aicResponses) delete window.__aicResponses[key]; try { sessionStorage.removeItem(key); } catch (_) {} }
  function feedback(root, okay, message) { var e = root.querySelector('.aic-feedback'); e.className = 'aic-feedback ' + (okay ? 'good' : 'bad'); text(e, (okay ? '✓ ' : '✕ ') + message); e.setAttribute('role','status'); }
  function optionLabel(opt) { return String(opt.text || (opt.image ? 'Bild' : '')); }
  function imageElement(file) { var img = node('img','aic-thumb'); img.alt = ''; img.loading = 'lazy'; img.src = file; return img; }
  function action(label, fn, secondary) { var b = node('button', 'aic-action' + (secondary ? ' secondary' : ''), label); b.type='button'; b.addEventListener('click', fn); return b; }
  function selectionRoot(root, multi) {
    var options = json(root, 'options', []);
    var correct = json(root, 'correct', []);
    if (!Array.isArray(options) || !Array.isArray(correct) || !options.length) { feedback(root,false,'Ungültige Kartendaten. Bitte Notiz im Editor prüfen.'); return; }
    var grid = root.querySelector('.aic-canvas'), actions = root.querySelector('.aic-actions');
    var selected = [], done = false;
    var order = shuffle(options.map(function (_, i) { return i; }));
    if (options.some(function (x) { return !!x.image; })) root.classList.add('aic-images');
    if (multi) root.classList.add('aic-multi');
    var buttons = {};
    function update() {
      order.forEach(function (i) {
        var b = buttons[i];
        b.classList.toggle('aic-selected', selected.indexOf(i) !== -1);
        b.setAttribute('aria-pressed', selected.indexOf(i) !== -1 ? 'true' : 'false');
        if (done) {
          b.classList.toggle('aic-correct', correct.indexOf(i) !== -1);
          b.classList.toggle('aic-wrong', selected.indexOf(i) !== -1 && correct.indexOf(i) === -1);
          b.disabled = true;
        }
        if (multi) text(b.querySelector('.aic-check'), selected.indexOf(i) !== -1 ? '✓' : '');
      });
    }
    function finish() {
      if (done || !selected.length) return;
      done = true;
      var okay = selected.length === correct.length && selected.every(function (i) { return correct.indexOf(i) !== -1; });
      var right = correct.map(function (i) { return optionLabel(options[i]); }).join(', ');
      feedback(root, okay, okay ? 'Richtig!' : 'Nicht ganz. Richtig: ' + right);
      store(root, {type: multi ? 'multi' : 'choice', right: okay, chosen: selected.map(function (i) { return optionLabel(options[i]); })});
      update(); actions.textContent='';
    }
    order.forEach(function (i) {
      var opt = options[i];
      var b = node('button', 'aic-option'); b.type = 'button';
      if (multi) b.appendChild(node('span', 'aic-check'));
      if (opt.image) b.appendChild(imageElement(opt.image));
      // Never reveal the word beneath a picture on the question side.
      if (opt.text && !opt.image) b.appendChild(node('span', 'aic-label', opt.text));
      b.setAttribute('aria-label', opt.image ? ('Bildoption ' + (i + 1)) : opt.text);
      b.addEventListener('click', function () {
        if (done) return;
        if (multi) {
          var at = selected.indexOf(i); if (at === -1) selected.push(i); else selected.splice(at, 1);
          update();
        } else { selected = [i]; update(); finish(); }
      });
      buttons[i] = b; grid.appendChild(b);
    });
    if (multi) actions.appendChild(action('Auswahl prüfen', finish));
    update();
  }
  function sentenceRoot(root) {
    var answer = data(root,'answer');
    var alternatives = json(root,'alternatives', []);
    var tokens = json(root,'tokens', []);
    var mode = data(root,'mode') || 'tiles';
    var distractors = json(root, 'distractors', []);
    if (!Array.isArray(distractors)) distractors = [];
    if (!Array.isArray(tokens) || !tokens.length) { feedback(root,false,'Wortbausteine fehlen.'); return; }
    var canvas = root.querySelector('.aic-canvas'), actions = root.querySelector('.aic-actions');
    var sequence = [], done = false, current = mode === 'typing' ? 'typing' : 'tiles';
    var header = node('div'), area = node('div','aic-tile-area'), bank = node('div','aic-bank');
    var input = node('textarea','aic-type'); input.rows = 2; input.placeholder = 'Schreibe den vollständigen Satz …';
    input.setAttribute('aria-label', 'Satz eingeben');
    // Each token retains its own identity. Repeated required words remain
    // individually selectable; extra distractors are never mandatory.
    var available = tokens.map(function (value) { return {word:value, distractor:false}; })
      .concat(distractors.map(function (value) { return {word:value, distractor:true}; }));
    var shuffled = shuffle(available.map(function (_, i) { return i; }));
    if (distractors.length && mode !== 'typing') {
      canvas.classList.add('aic-has-distractors');
      canvas.appendChild(node('p','aic-distractor-hint','Nicht alle Wörter müssen verwendet werden.'));
    }
    function finish() {
      if (done) return;
      var typed = current === 'typing' ? input.value : sequence.map(function (i) { return available[i].word; }).join(' ');
      if (!typed.trim()) return;
      done = true;
      var acceptable = [answer].concat(Array.isArray(alternatives) ? alternatives : []);
      var okay = acceptable.some(function (x) { return norm(x) === norm(typed); });
      feedback(root, okay, okay ? 'Richtig!' : 'Nicht ganz. Lösung: ' + answer);
      store(root, {type: 'sentence', right: okay, chosen: typed});
      input.disabled = true;
      actions.textContent = '';
      redraw();
    }
    function redraw() {
      area.textContent=''; bank.textContent='';
      sequence.forEach(function (i, index) {
        var b = node('button','aic-token placed',available[i].word); b.type='button'; b.disabled = done;
        b.title = 'Wort wieder entfernen';
        b.addEventListener('click', function () { if (!done) { sequence.splice(index,1); redraw(); } });
        area.appendChild(b);
      });
      shuffled.forEach(function (i) {
        var b = node('button','aic-token',available[i].word); b.type='button';
        if (sequence.indexOf(i) !== -1) { b.classList.add('aic-used'); b.disabled = true; }
        if (done) b.disabled = true;
        b.addEventListener('click', function () { if (!done && sequence.indexOf(i) === -1) { sequence.push(i); redraw(); } });
        bank.appendChild(b);
      });
    }
    function setMode(next) {
      current=next; var tiles = current==='tiles';
      area.style.display = tiles ? 'flex' : 'none'; bank.style.display = tiles ? 'flex' : 'none'; input.style.display = tiles ? 'none' : 'block';
      Array.prototype.forEach.call(header.querySelectorAll('.aic-switch'), function (b) { b.classList.toggle('active', b.getAttribute('data-mode')===next); });
    }
    if (mode === 'both') {
      ['tiles','typing'].forEach(function (which) {
        var b = node('button','aic-switch',which==='tiles'?'Wortkacheln':'Schreiben'); b.type='button'; b.setAttribute('data-mode',which);
        b.addEventListener('click', function () { if (!done) setMode(which); }); header.appendChild(b);
      });
    }
    canvas.appendChild(header); canvas.appendChild(area); canvas.appendChild(bank); canvas.appendChild(input);
    actions.appendChild(action('Satz prüfen',finish));
    actions.appendChild(action('Zurücksetzen',function () { if (!done) { sequence=[]; input.value=''; redraw(); } },true));
    input.addEventListener('keydown', function (evt) { if (evt.key==='Enter' && !evt.shiftKey) { evt.preventDefault(); finish(); } });
    redraw(); setMode(current);
  }
  function backRoot(root) {
    var kind = root.getAttribute('data-kind'), output = root.querySelector('.aic-solution');
    var answer = data(root,'answer');
    if (kind==='sentence') text(output,answer);
    else {
      var opts = json(root,'options',[]), correct = json(root,'correct',[]);
      text(output, correct.map(function (i) { return opts[i] ? optionLabel(opts[i]) : ''; }).filter(Boolean).join(' · '));
      // Display correct answer images too.
      correct.forEach(function (i) { if (opts[i] && opts[i].image) { var img = imageElement(opts[i].image); img.style.maxHeight='180px'; output.appendChild(img); } });
    }
    var prev = retrieve(root);
    if (prev) feedback(root,prev.right, 'Deine Antwort: ' + (Array.isArray(prev.chosen) ? prev.chosen.join(', ') : prev.chosen));
  }
  function initialize(root) {
    if (root.getAttribute('data-aic-initialized')) return;
    root.setAttribute('data-aic-initialized','1');
    if (root.getAttribute('data-side') === 'back') { backRoot(root); return; }
    clear(root);
    if (root.getAttribute('data-kind') === 'sentence') sentenceRoot(root);
    else selectionRoot(root,root.getAttribute('data-kind') === 'multi');
  }
  Array.prototype.forEach.call(document.querySelectorAll('.aic-root'),initialize);
})();
