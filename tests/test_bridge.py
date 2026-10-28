import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from src.anki_bridge import ensure_types, generate_from_rows, new_payload
from src.core import from_json_field
from src.templates import NOTE_TYPES

class FakeNote:
    def __init__(self,model,nid=0):
        self._model=model
        self.data={f['name']:'' for f in model['flds']}
        self.id=nid
        self.tags=[]
    def __getitem__(self,key):return self.data[key]
    def __setitem__(self,key,val):self.data[key]=val
    def add_tag(self,tag):self.tags.append(tag)

class FakeModels:
    def __init__(self):self.data={};self.notes={}
    def by_name(self,name):return self.data.get(name)
    def new(self,name):return {'name':name,'id':len(self.data)+1,'flds':[],'tmpls':[],'css':''}
    def new_field(self,name):return {'name':name}
    def add_field(self,model,field):model['flds'].append(field)
    def new_template(self,name):return {'name':name,'qfmt':'','afmt':''}
    def add_template(self,model,template):model['tmpls'].append(template)
    def add(self,model):self.data[model['name']]=model;self.notes[model['id']]=[]
    def update_dict(self,model):self.data[model['name']]=model
    def nids(self,mid):return self.notes.get(mid,[])

class FakeDecks:
    def id(self,name):return 99

class FakeCol:
    def __init__(self):self.models=FakeModels();self.decks=FakeDecks();self.notes={};self.counter=100
    def new_note(self,model):return FakeNote(model)
    def add_note(self,note,deck_id):
        self.counter+=1;note.id=self.counter
        self.notes[note.id]=note
        self.models.notes[note._model['id']].append(note.id)
    def update_note(self,note):self.notes[note.id]=note
    def get_note(self,nid):return self.notes[nid]

class BridgeTests(unittest.TestCase):
    def test_install_types(self):
        col=FakeCol()
        self.assertEqual(len(ensure_types(col)),3)
        self.assertEqual(len(ensure_types(col)),0)
        for kind,spec in NOTE_TYPES.items():
            self.assertIn('data-kind="'+kind+'"',col.models.by_name(spec['name'])['tmpls'][0]['qfmt'])
            self.assertTrue(next(f for f in col.models.by_name(spec['name'])['flds'] if f['name']=='UID')['collapsed'])

    def test_existing_sentence_notetype_migrates_without_replacing_template(self):
        col=FakeCol(); ensure_types(col)
        model=col.models.by_name(NOTE_TYPES['sentence']['name'])
        custom_template='<div>Meine angepasste Vorlage</div>'
        model['tmpls'][0]['qfmt']=custom_template
        model['flds']=[f for f in model['flds'] if f['name']!='Distractors']
        for fld in model['flds']:
            if fld['name']=='Answer': fld['collapsed']=False
        ensure_types(col)
        model=col.models.by_name(NOTE_TYPES['sentence']['name'])
        self.assertEqual([f['name'] for f in model['flds']].count('Distractors'),1)
        self.assertTrue(next(f for f in model['flds'] if f['name']=='Answer')['collapsed'])
        self.assertEqual(model['tmpls'][0]['qfmt'],custom_template)
        ensure_types(col)
        self.assertEqual([f['name'] for f in model['flds']].count('Distractors'),1)
        ensure_types(col,update=True)
        self.assertIn('data-aic-field="distractors"',model['tmpls'][0]['qfmt'])

    def test_batch_idempotent_and_update(self):
        col=FakeCol();ensure_types(col)
        rows=[{'nid':i,'prompt':f'Wort {i}','answer':s,'image':f'{s}.png','audio':''}
              for i,s in enumerate(['la casa','il libro','la pizza','la città'],1)]
        first=generate_from_rows(col,rows,'choice','Italiano',3)
        self.assertEqual(first,{'created':4,'updated':0,'skipped':0})
        self.assertEqual(len(col.notes),4)
        second=generate_from_rows(col,rows,'choice','Italiano',3)
        self.assertEqual(second,{'created':0,'updated':0,'skipped':4})
        notes=list(col.notes.values());old_uid=notes[0]['UID']
        rows[0]['prompt']='Geänderte Frage'
        third=generate_from_rows(col,rows,'choice','Italiano',3,update_existing=True)
        self.assertEqual(third,{'created':0,'updated':4,'skipped':0})
        self.assertEqual(notes[0]['UID'],old_uid)
        self.assertEqual(notes[0]['Prompt'],'Geänderte Frage')
        self.assertEqual(from_json_field(notes[0]['Correct']),[0])

    def test_batch_image_and_sentence(self):
        col=FakeCol();ensure_types(col)
        rows=[{'nid':i,'prompt':f'Wort {i}','answer':s,'image':f'{s}.png','audio':''}
              for i,s in enumerate(['la casa','il libro','la pizza'],1)]
        created=generate_from_rows(col,rows,'image','Italia',2)
        self.assertEqual(created['created'],3)
        self.assertIn('<img src=',next(iter(col.notes.values()))['Media References'])
        created=generate_from_rows(col,rows,'sentence','Italia',2)
        self.assertEqual(created['created'],3)
        self.assertEqual(len(col.notes),6)

if __name__=='__main__':unittest.main()
