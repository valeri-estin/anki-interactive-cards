"""Self-contained, Anki-synced review templates. Avoid addon-only runtime hooks."""
from pathlib import Path
from .localization import card_copy, text

WEB = Path(__file__).parent / 'web'
CSS = (WEB / 'card.css').read_text(encoding='utf-8')
JS = (WEB / 'card.js').read_text(encoding='utf-8')
NOTE_TYPES = {
    'choice': {'name':'AIC · Single Choice', 'fields':['Prompt','Options','Correct','Media References','Explanation','Prompt Image','Audio','UID','Source ID']},
    'multi': {'name':'AIC · Multiple Choice', 'fields':['Prompt','Options','Correct','Media References','Explanation','Prompt Image','Audio','UID','Source ID']},
    'sentence': {'name':'AIC · Sentence Builder', 'fields':['Prompt','Answer','Tokens','Alternatives','Mode','Distractors','Explanation','Prompt Image','Audio','UID','Source ID']},
}


def _root(kind: str, side: str, language: str = "en") -> str:
    fields = ('options','correct') if kind != 'sentence' else ('answer','tokens','alternatives','mode','distractors')
    data = ''.join('<div hidden data-aic-field="%s">{{%s}}</div>' % (field, {'options':'Options','correct':'Correct','answer':'Answer','tokens':'Tokens','alternatives':'Alternatives','mode':'Mode','distractors':'Distractors'}[field]) for field in fields)
    # Alternatives/Correct/Tokens are JSON field strings, parsed in runtime.
    if kind != 'sentence':
        data += '<div hidden data-aic-media>{{Media References}}</div>'
    output = '<div class="aic-solution" aria-label="%s"></div>' % text("card.solution_label", language) if side == 'back' else '<div class="aic-canvas%s" aria-label="%s"></div><div class="aic-actions"></div>' % (' aic-grid' if kind != 'sentence' else '', text("card.answers_label", language))
    return '''<div class="aic-root" data-kind="%s" data-side="%s" data-uid="{{UID}}">
<div class="aic-tag">%s</div><div class="aic-question">{{Prompt}}</div>
<div class="aic-hero">{{Prompt Image}}</div><div class="aic-audio">{{Audio}}</div>
%s%s<div class="aic-feedback" aria-live="polite"></div>
%s</div><script>%s</script>''' % (
        kind, side, text({"choice":"card.choice_tag","multi":"card.multi_tag","sentence":"card.sentence_tag"}[kind], language),
        data, output,
        '<div class="aic-caption">%s</div>' % text("card.caption", language) if side == 'front' else '<div class="aic-explanation">{{Explanation}}</div>',
        "window.AICCopy = " + card_copy(language) + ";\n" + JS)


def make_template(kind: str, language: str = "en") -> dict:
    return {'name': 'Interaktive Karte', 'qfmt': _root(kind,'front',language), 'afmt': _root(kind,'back',language)}
