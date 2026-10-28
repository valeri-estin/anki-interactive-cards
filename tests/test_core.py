import random
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from src.core import (as_json_field, from_json_field, answer_key, clean_text,
                      validate_choices, validate_sentence, choose_distractors, detect_media)
from src.anki_bridge import new_payload
from src.templates import make_template, NOTE_TYPES, CSS

class CoreTests(unittest.TestCase):
    def test_json_round_trip_unicode_html(self):
        p=[{'text':'città e "casa" & <più>', 'image':'e & a.jpg'}]
        self.assertEqual(from_json_field(as_json_field(p)),p)

    def test_sentence_normalization(self):
        self.assertEqual(answer_key('  Sono   a casa! '),answer_key('sono a casa'))
        self.assertNotEqual(answer_key('citta'),answer_key('città'))

    def test_choice_checks(self):
        items=[{'text':'casa','image':''},{'text':'libro','image':''}]
        validate_choices(items,[0])
        validate_choices(items,[0,1],multi=True)
        with self.assertRaises(ValueError): validate_choices(items,[0,1])
        with self.assertRaises(ValueError): validate_choices(items,[7],multi=True)
        with self.assertRaises(ValueError): validate_choices(items+items,[0])
        # image-only choices allowed (unique filenames)
        validate_choices([{'text':'','image':'a.jpg'},{'text':'','image':'b.jpg'}],[0])

    def test_sentence_optional_wrong_tiles(self):
        from src.core import validate_sentence
        validate_sentence('sono a casa', [], ['sono', 'a', 'casa'], ['il', 'andare'])
        with self.assertRaisesRegex(ValueError, 'identisch'):
            validate_sentence('sono a casa', [], ['sono', 'a', 'casa'], ['casa'])
        with self.assertRaisesRegex(ValueError, 'doppelt'):
            validate_sentence('sono a casa', [], ['sono', 'a', 'casa'], ['il', 'IL'])
        with self.assertRaises(ValueError):
            validate_sentence('sono a casa', [], ['sono', 'a', 'casa'], [' '])
        with self.assertRaises(ValueError):
            validate_sentence('sono a casa', [], ['sono', 'a', 'casa'], ['il'] * 61)

    def test_sentence_checks(self):
        validate_sentence('sono a casa',[],['sono','a','casa'])
        with self.assertRaises(ValueError):validate_sentence('sono a casa',[],['a','sono','casa'])

    def test_distractors(self):
        result=choose_distractors('la casa',['la casa','LA CASA','il libro','la pizza','la città','la pizza'],3,random.Random(3))
        self.assertEqual(len(result),3)
        self.assertNotIn('la casa',result)
        self.assertEqual(len(set(result)),3)

    def test_media_detection(self):
        self.assertEqual(detect_media('<img src="test.webp">'),'test.webp')
        self.assertEqual(detect_media('https://test.org/img.png'),'')
        self.assertEqual(detect_media('<img src="javascript:evil.png">'),'')
        self.assertEqual(detect_media('../other/test.png'),'')

    def test_payload_note_fields(self):
        result=new_payload('choice','das Haus',options=[{'text':'la casa','image':''},{'text':'il libro','image':''}],correct=[0])
        self.assertEqual(from_json_field(result['Correct']),[0])
        self.assertEqual(len(result['UID']),32)
        self.assertEqual(new_payload('sentence','Ich bin zu Hause',answer='sono a casa')['Mode'],'tiles')

    def test_templates(self):
        for kind in NOTE_TYPES:
            t=make_template(kind)
            self.assertIn('<script>',t['qfmt'])
            self.assertIn('<script>',t['afmt'])
            self.assertIn('data-side="back"',t['afmt'])
            self.assertNotIn('pycmd(',t['qfmt'])
        self.assertIn('.aic-option',CSS)

if __name__=='__main__':unittest.main()
