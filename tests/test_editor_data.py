import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))
from src.editor_data import (
    choice_fields, sentence_fields, merge_aux_fields, validate_note,
    kind_for_model, fields_from_note_info
)
from src.core import from_json_field
from src.templates import NOTE_TYPES, CSS, make_template

class EditorDataTests(unittest.TestCase):
    def test_choice_multi_data_and_media(self):
        options = [{'text':'Haus', 'image':'haus.png'}, {'text':'Buch', 'image':'buch.png'},
                   {'text':'Pizza', 'image':''}]
        out = choice_fields(options, [0,2], multi=True)
        self.assertEqual(from_json_field(out['Correct']), [0,2])
        self.assertIn('haus.png', out['Media References'])
        self.assertIn('buch.png', out['Media References'])
        self.assertEqual(out['Media References'].count('<img'),2)
        with self.assertRaises(ValueError): choice_fields(options,[0,2])
        with self.assertRaises(ValueError): choice_fields(options,[7],multi=True)

    def test_sentence_data(self):
        out = sentence_fields('sono a casa', None, ['io sono a casa'], 'both')
        self.assertEqual(from_json_field(out['Tokens']),['sono','a','casa'])
        validate_note('sentence',{'Prompt':'Ich bin da',**out})
        self.assertEqual(from_json_field(out['Distractors']), [])
        extras = sentence_fields('sono a casa', None, [], 'tiles', ['il', 'andare'])
        self.assertEqual(from_json_field(extras['Distractors']), ['il', 'andare'])
        validate_note('sentence',{'Prompt':'Ich bin zu Hause',**extras})
        with self.assertRaisesRegex(ValueError, 'identisch'):
            sentence_fields('sono a casa', None, [], 'tiles', ['casa'])
        with self.assertRaises(ValueError): sentence_fields('sono a casa',['casa','sono','a'])

    def test_preserve_rich_text_and_identity(self):
        options = choice_fields([{'text':'a','image':''},{'text':'b','image':''}], [0])
        source = {'Prompt':'<b>Frage!</b>', 'Explanation':'<i>Hinweis</i>',
                  'UID':'stable','Source ID':'aic:123:choice','Options':'old'}
        merged = merge_aux_fields(source,options)
        self.assertEqual(merged['Prompt'], '<b>Frage!</b>')
        self.assertEqual(merged['Explanation'],'<i>Hinweis</i>')
        self.assertEqual(merged['Source ID'],'aic:123:choice')
        self.assertEqual(merged['UID'], 'stable')
        validate_note('choice', merged)
        self.assertEqual(source['Options'], 'old')
        merged2 = merge_aux_fields({'Prompt':'Frage'}, options)
        self.assertEqual(len(merged2['UID']),32)

    def test_no_invalid_note(self):
        for kind in ('choice','multi'):
            with self.assertRaises(ValueError): validate_note(kind,{'Prompt':'Test'})
        with self.assertRaises(ValueError): validate_note('sentence',{'Prompt':'Test','Answer':'abc','Tokens':'[]','Mode':'both'})

    def test_notetype_identification(self):
        for kind,spec in NOTE_TYPES.items():
            mock={'name':spec['name'],'flds':[{'name':n} for n in spec['fields']]}
            self.assertEqual(kind_for_model(mock),kind)
            self.assertEqual(fields_from_note_info(mock,['']*len(spec['fields'])), dict.fromkeys(spec['fields'],''))
        self.assertIsNone(kind_for_model({'name':'Basic'}))

    def test_theme_is_neutral_and_grid_present(self):
        self.assertNotIn('#58a700', CSS.lower())
        self.assertIn('--aic-color-accent', CSS)
        self.assertIn('class="aic-canvas aic-grid"',make_template('choice')['qfmt'])
        self.assertIn('class="aic-canvas"',make_template('sentence')['qfmt'])

if __name__ == '__main__': unittest.main()
