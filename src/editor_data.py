"""Pure helpers for the native Anki editor integration.

Only auxiliary AIC fields are generated; user's rich-text Prompt, images, audio,
explanations and source markers are never overwritten by the assistant dialog.
"""
from __future__ import annotations
import uuid
from .core import as_json_field, from_json_field, validate_choices, validate_sentence, tokenize_sentence
from .localization import legacy_text as l


def kind_for_model(model):
    from .templates import NOTE_TYPES
    for kind, spec in NOTE_TYPES.items():
        if model and model['name'] == spec['name']:
            return kind
    return None


def fields_from_note_info(model, fields):
    names = [x['name'] for x in model['flds']]
    if len(fields) != len(names):
        raise ValueError(l('Feldanzahl der Anki-Notiz hat sich geändert. Bitte erneut öffnen.'))
    return dict(zip(names, fields))


def choice_fields(options, correct, *, multi=False, media_names=None):
    """Validate original order; Anki review front may randomize display order."""
    validate_choices(options, correct, multi=multi)
    from .anki_bridge import image_html
    imgs = sorted(set(media_names if media_names is not None else [x.get('image', '') for x in options]) - {''})
    return {
        'Options': as_json_field(options),
        'Correct': as_json_field(correct),
        'Media References': ''.join(image_html(name) for name in imgs),
    }


def sentence_fields(answer, tokens=None, alternatives=None, mode='both', distractors=None):
    answer = answer.strip()
    tokens = tokenize_sentence(answer) if tokens is None else tokens
    alternatives = alternatives or []
    distractors = distractors or []
    validate_sentence(answer, alternatives, tokens, distractors)
    if mode not in ('tiles', 'typing', 'both'):
        raise ValueError(l('Ungültiger Satzmodus.'))
    import html
    return {
        'Answer': html.escape(answer), 'Tokens': as_json_field(tokens),
        'Alternatives': as_json_field(alternatives), 'Mode': mode,
        'Distractors': as_json_field(distractors),
    }


def merge_aux_fields(note_values, aux):
    """Return a new mapping; preserve all other fields and stable UID."""
    result = dict(note_values)
    result.update(aux)
    if not result.get('UID'):
        result['UID'] = uuid.uuid4().hex
    return result


def validate_note(kind, values):
    """Refuse malformed cards from native Add mode, including manual JSON entry."""
    from .core import clean_text
    if not clean_text(values.get('Prompt', '')):
        raise ValueError('Bitte zuerst eine Frage (Prompt) eingeben.')
    if kind in ('choice', 'multi'):
        opts = from_json_field(values.get('Options', ''), None)
        correct = from_json_field(values.get('Correct', ''), None)
        if not isinstance(opts, list) or not isinstance(correct, list):
            raise ValueError(l('Bitte „AIC · Antworten bearbeiten“ öffnen und Antworten festlegen.'))
        validate_choices(opts, correct, multi=kind == 'multi')
    elif kind == 'sentence':
        answer = clean_text(values.get('Answer', ''))
        tokens = from_json_field(values.get('Tokens', ''), None)
        alternatives = from_json_field(values.get('Alternatives', ''), [])
        if not isinstance(tokens, list) or not isinstance(alternatives, list):
            raise ValueError(l('Bitte Satzbausteine über „AIC · Antworten bearbeiten“ konfigurieren.'))
        distractors = from_json_field(values.get('Distractors', ''), [])
        if not isinstance(distractors, list):
            raise ValueError(l('Falsche Wortkacheln müssen eine Liste sein.'))
        validate_sentence(answer, alternatives, tokens, distractors)
        if values.get('Mode') not in ('tiles', 'typing', 'both'):
            raise ValueError(l('Bitte einen gültigen Satzmodus wählen.'))
