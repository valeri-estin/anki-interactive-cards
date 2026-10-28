"""Anki collection adapter. Deliberately does not touch cards' scheduling state."""
from __future__ import annotations
import html
import json
import uuid
from pathlib import Path
from .core import as_json_field, from_json_field, validate_choices, validate_sentence, tokenize_sentence, detect_media, choose_distractors, clean_text
from .templates import NOTE_TYPES, CSS, make_template
from .localization import legacy_format as lf, legacy_text as l


ADVANCED_FIELDS = {'Options', 'Correct', 'Media References', 'Answer', 'Tokens', 'Alternatives', 'Mode', 'Distractors', 'UID', 'Source ID'}

def ensure_types(col, update=False, language="en"):
    """Create missing notetypes. Existing custom templates only replaced explicitly."""
    installed = []
    for kind, spec in NOTE_TYPES.items():
        model = col.models.by_name(spec['name'])
        if model:
            present = {f['name'] for f in model['flds']}
            missing = set(spec['fields']) - present
            # V1.2 migration: append the optional Distractors field without
            # touching cards or customized templates. Older missing fields
            # indicate a broken/modified notetype and require manual review.
            if missing - ({'Distractors'} if kind == 'sentence' else set()):
                raise ValueError(lf('Notiztyp {name} hat fehlende Felder: {fields}. Bitte manuell prüfen.', name=spec['name'], fields=', '.join(sorted(missing))))
            if kind == 'sentence' and 'Distractors' in missing:
                fld = col.models.new_field('Distractors')
                fld['collapsed'] = True
                col.models.add_field(model, fld)
                model = col.models.by_name(spec['name'])
            changed = False
            for fld in model['flds']:
                should_collapse = fld['name'] in ADVANCED_FIELDS
                if bool(fld.get('collapsed', False)) != should_collapse:
                    fld['collapsed'] = should_collapse
                    changed = True
            if changed:
                col.models.update_dict(model)
            if not update:
                continue
        if model is None:
            model = col.models.new(spec['name'])
            for field in spec['fields']:
                fld = col.models.new_field(field)
                if field in ADVANCED_FIELDS:
                    fld['collapsed'] = True  # Native Anki 'Collapse by default' option
                col.models.add_field(model, fld)
            template = col.models.new_template('Interaktive Karte')
            template.update(make_template(kind, language))
            col.models.add_template(model,template)
            model['css'] = CSS
            col.models.add(model)
        else:
            template = make_template(kind, language)
            model['tmpls'][0]['qfmt'] = template['qfmt']
            model['tmpls'][0]['afmt'] = template['afmt']
            model['css'] = CSS
            for fld in model['flds']:
                fld['collapsed'] = fld['name'] in ADVANCED_FIELDS
            col.models.update_dict(model)
        installed.append(spec['name'])
    return installed


def media_filename(col, path_or_name: str) -> str:
    """Import local images once, or preserve existing Anki media names."""
    raw = path_or_name.strip()
    if not raw:
        return ''
    if raw.lower().startswith(('http:', 'https:', 'data:', 'javascript:', 'file:')):
        raise ValueError('Externe Bild-URLs sind nicht erlaubt. Bitte lokale Dateien verwenden.')
    p = Path(raw).expanduser()
    if p.exists() and p.is_file():
        if p.suffix.lower() not in ('.jpg','.jpeg','.png','.gif','.webp','.svg'):
            raise ValueError(l('Nicht unterstütztes Bildformat: ') + p.suffix)
        return col.media.add_file(str(p))
    if '/' in raw or '\\' in raw or '..' in raw:
        raise ValueError('Bild nicht gefunden: ' + raw)
    if p.suffix.lower() not in ('.jpg','.jpeg','.png','.gif','.webp','.svg'):
        raise ValueError('Bild muss PNG, JPG, GIF, WebP oder SVG sein.')
    return raw


def image_html(filename):
    return '<img src="%s">' % html.escape(filename,quote=True) if filename else ''


def new_payload(kind, prompt, *, options=None, correct=None, answer='', tokens=None,
                alternatives=None, mode='tiles', distractors=None, explanation='', prompt_image='', audio='', source_id='', uid=None):
    """Validate and transform display data into Anki field text."""
    prompt = prompt.strip()
    if not prompt:
        raise ValueError('Die Frage / der Ausgangssatz darf nicht leer sein.')
    fields = {'Prompt': html.escape(prompt), 'Explanation':html.escape(explanation).replace('\n','<br>'),
              'Prompt Image':prompt_image, 'Audio':audio, 'UID':uid or uuid.uuid4().hex,
              'Source ID':source_id}
    if kind in ('choice','multi'):
        validate_choices(options or [],correct or [],multi=(kind=='multi'))
        images = sorted({x.get('image','') for x in options if x.get('image')})
        fields.update({'Options':as_json_field(options),'Correct':as_json_field(correct),
                       'Media References':''.join(image_html(name) for name in images)})
    elif kind=='sentence':
        tokens = tokens if tokens is not None else tokenize_sentence(answer)
        validate_sentence(answer,alternatives or [],tokens,distractors or [])
        if mode not in ('tiles','typing','both'):
            raise ValueError(l('Ungültiger Satzmodus.'))
        fields.update({'Answer':html.escape(answer.strip()),'Tokens':as_json_field(tokens),
                       'Alternatives':as_json_field(alternatives or []),'Mode':mode,
                       'Distractors':as_json_field(distractors or [])})
    else: raise ValueError('Unbekannter Kartentyp: ' + kind)
    return fields


def add_card(col, kind, deck_id, fields, existing_note=None):
    model = col.models.by_name(NOTE_TYPES[kind]['name'])
    if not model:
        ensure_types(col)
        model = col.models.by_name(NOTE_TYPES[kind]['name'])
    if existing_note:
        note = existing_note
        # Do not accidentally change an existing note's UID or scheduling.
        for key,val in fields.items():
            if key == 'UID' and note['UID']:
                continue
            note[key] = val
        col.update_note(note)
    else:
        note = col.new_note(model)
        for key,val in fields.items():
            note[key] = val
        note.add_tag('anki-interactive')
        col.add_note(note,deck_id)
    return note


def existing_generated(col, kind: str, source_id: str):
    """Lookup by exact Source ID, restricting note type; no double-generation."""
    model = col.models.by_name(NOTE_TYPES[kind]['name'])
    if not model:
        return None
    for nid in col.models.nids(model['id']):
        note = col.get_note(nid)
        if note['Source ID'] == source_id:
            return note
    return None


def source_rows(col, model_name, source_deck, front_field, back_field,
                image_field='', audio_field='', limit=5000):
    model = col.models.by_name(model_name)
    if not model:
        raise ValueError('Quell-Notiztyp nicht gefunden.')
    names = {f['name'] for f in model['flds']}
    for f in (front_field,back_field):
        if f not in names: raise ValueError('Feld fehlt in Quellnotiz: ' + f)
    if image_field and image_field not in names: raise ValueError('Bildfeld fehlt.')
    if audio_field and audio_field not in names: raise ValueError('Audiofeld fehlt.')
    # Query strictly scoped to deck; do not modify source notes.
    search = 'deck:"%s"' % source_deck.replace('"','')
    result = []
    for nid in col.find_notes(search):
        note = col.get_note(nid)
        if note.mid != model['id']:
            continue
        prompt, answer = clean_text(note[front_field]), clean_text(note[back_field])
        if not prompt or not answer:
            continue
        result.append({'nid':int(note.id),'prompt':prompt,'answer':answer,
                       'image':detect_media(note[image_field]) if image_field else '',
                       'audio':note[audio_field] if audio_field else ''})
        if len(result) >= limit:
            break
    return result


def generate_from_rows(col, rows, kind, target_deck, distractors=3, update_existing=False):
    """Create/update cards based on snapshot of source notes.

    Source image is interpreted as image of the answer (for image-choice). Other source
    rows provide labels/images for distractors. No scheduling state modified.
    """
    if kind not in ('choice','image','sentence'):
        raise ValueError(l('Nicht unterstützter Importmodus.'))
    if not 1 <= distractors <= 10:
        raise ValueError('1–10 falsche Antworten sind erlaubt.')
    if kind == 'image' and sum(bool(r['image']) for r in rows) < 2:
        raise ValueError(l('Bildauswahl benötigt mindestens zwei Quellnotizen mit Bildern.'))
    image_by_answer = {r['answer']:r['image'] for r in rows if r.get('image')}
    imported = updated = skipped = 0
    target_id = col.decks.id(target_deck)
    dest_kind = 'sentence' if kind == 'sentence' else 'choice'
    dest_model = col.models.by_name(NOTE_TYPES[dest_kind]['name'])
    generated_index = {}
    if dest_model:
        for existing_id in col.models.nids(dest_model['id']):
            existing_note = col.get_note(existing_id)
            source = existing_note['Source ID']
            if source:
                generated_index[source] = existing_note
    answers = [r['answer'] for r in rows]
    for row in rows:
        if kind == 'image' and not row['image']:
            skipped += 1; continue
        source_id = f"aic:{row['nid']}:{kind}"
        existing = generated_index.get(source_id)
        if existing and not update_existing:
            skipped += 1; continue
        if kind=='sentence':
            payload = new_payload('sentence',row['prompt'],answer=row['answer'],mode='both',
                                  tokens=tokenize_sentence(row['answer']),audio=row['audio'],source_id=source_id)
            note_kind='sentence'
        else:
            if kind == 'image':
                candidates = [x for x in answers if x in image_by_answer]
                distract = choose_distractors(row['answer'],candidates,distractors)
                options = [{'text':row['answer'],'image':row['image']}] + [
                    {'text':x,'image':image_by_answer[x]} for x in distract]
            else:
                distract = choose_distractors(row['answer'],answers,distractors)
                options = [{'text':row['answer'],'image':''}] + [{'text':x,'image':''} for x in distract]
            if len(options) < 2:
                skipped += 1; continue
            payload = new_payload('choice',row['prompt'],options=options,correct=[0],
                                  audio=row['audio'],source_id=source_id)
            note_kind='choice'
        add_card(col,note_kind,target_id,payload,existing)
        if existing: updated += 1
        else: imported += 1
    return {'created':imported,'updated':updated,'skipped':skipped}
