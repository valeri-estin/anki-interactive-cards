"""Pure logic for Anki Interactive Cards. No Anki / Qt imports."""
from __future__ import annotations
import html
import json
import random
from .localization import legacy_text as l
import re
import unicodedata
from pathlib import Path

SUPPORTED_IMAGES = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg'}
TYPES = {'choice', 'multi', 'sentence'}


def clean_text(s: str) -> str:
    s = re.sub(r'<br\s*/?>', ' ', s, flags=re.I)
    s = re.sub(r'</(?:div|p)>', ' ', s, flags=re.I)
    s = re.sub(r'<[^>]*>', '', s)
    return html.unescape(s).strip()


def canonical(s: str) -> str:
    return ' '.join(unicodedata.normalize('NFKC', clean_text(s)).casefold().split())


def as_json_field(value) -> str:
    return html.escape(json.dumps(value, ensure_ascii=False, separators=(',', ':')), quote=True)


def from_json_field(s: str, default=None):
    try:
        return json.loads(html.unescape(s))
    except (ValueError, TypeError):
        return default


def tokenize_sentence(s: str) -> list[str]:
    """Whitespace tokenizer. Preserve punctuation attached to tokens."""
    return s.strip().split()


def answer_key(value: str) -> str:
    """Normalize written responses; ignore sentence-final punctuation, not diacritics."""
    value = unicodedata.normalize('NFKC', value).casefold().strip()
    value = re.sub(r'[.!?…]+$', '', value).strip()
    return ' '.join(value.split())


def validate_choices(options: list[dict], correct: list[int], multi=False) -> None:
    if not 2 <= len(options) <= 24:
        raise ValueError(l('Erforderlich sind 2 bis 24 Antwortmöglichkeiten.'))
    if len(options) != len({canonical(x.get('text','')) or ('@image:' + x.get('image','')) for x in options}):
        raise ValueError(l('Antwortoptionen benötigen unterschiedliche Bezeichnungen.'))
    for opt in options:
        if not (opt.get('text', '').strip() or opt.get('image', '').strip()):
            raise ValueError(l('Jede Antwort benötigt Text oder ein Bild.'))
    if not correct or not all(isinstance(i, int) and 0 <= i < len(options) for i in correct):
        raise ValueError(l('Mindestens eine korrekte Auswahl muss gesetzt sein.'))
    if len(set(correct)) != len(correct):
        raise ValueError(l('Korrekte Indizes müssen eindeutig sein.'))
    if not multi and len(correct) != 1:
        raise ValueError(l('Single Choice benötigt genau eine richtige Antwort.'))


def validate_sentence(answer: str, alternatives: list[str], tokens: list[str], distractors=None) -> None:
    if not answer.strip():
        raise ValueError(l('Der Zielsatz darf nicht leer sein.'))
    if not tokens:
        raise ValueError(l('Der Satz benötigt mindestens einen Wortbaustein.'))
    if answer_key(' '.join(tokens)) != answer_key(answer):
        raise ValueError(l('Die Wortbausteine müssen zusammen den Zielsatz ergeben.'))
    distractors = [] if distractors is None else distractors
    if not isinstance(distractors, list) or not all(isinstance(x, str) for x in distractors):
        raise ValueError(l('Falsche Wortkacheln müssen eine Liste von Texten sein.'))
    if not all(x.strip() for x in distractors):
        raise ValueError(l('Leere falsche Wortkacheln sind nicht erlaubt.'))
    if len(tokens) + len(distractors) > 60:
        raise ValueError(l('Maximal 60 Wortkacheln insgesamt (richtige und falsche).'))
    # Duplicate *labels* are meaningful among correct tiles (e.g. "I I"),
    # but a distractor identical to a required tile is ambiguous to the learner.
    normalized = [answer_key(x) for x in distractors]
    if len(normalized) != len(set(normalized)):
        raise ValueError(l('Falsche Wortkacheln dürfen nicht doppelt vorkommen.'))
    correct_labels = {answer_key(x) for x in tokens}
    if any(x in correct_labels for x in normalized):
        raise ValueError(l('Eine falsche Wortkachel darf nicht identisch mit einer richtigen sein.'))


def choose_distractors(correct: str, pool: list[str], count: int = 3, rng=None) -> list[str]:
    """Deterministic under injected RNG; lexical heuristic is not semantic validation."""
    rng = rng or random.Random()
    if count < 0:
        raise ValueError('count must be nonnegative')
    unique = {}
    for raw in pool:
        candidate = clean_text(raw)
        key = canonical(candidate)
        if key and key != canonical(correct) and key not in unique:
            unique[key] = candidate
    items = list(unique.values())
    # Prefer candidates of similar word-count and length; random tie breaker.
    rng.shuffle(items)
    items.sort(key=lambda x: (abs(len(x.split())-len(correct.split())), abs(len(x)-len(correct))))
    return items[:count]


def detect_media(value: str) -> str:
    """Get filename of first <img src=...> or plain media filename; no arbitrary URL imports."""
    match = re.search(r'<img\b[^>]*\bsrc\s*=\s*[\'\"]([^\'\"]+)[\'\"]', value, re.I)
    candidate = html.unescape(match.group(1)) if match else clean_text(value)
    if candidate.lower().startswith(('http:', 'https:', 'file:', 'data:', 'javascript:')):
        return ''
    candidate = candidate.strip()
    if '/' in candidate or '\\' in candidate or '..' in candidate:
        return ''
    return candidate if Path(candidate).suffix.lower() in SUPPORTED_IMAGES else ''
