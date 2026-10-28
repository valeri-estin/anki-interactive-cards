"""Chromium smoke tests for client-only card runtime. Run: python tests/test_browser.py"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]))
from src.core import as_json_field
from src.templates import make_template, CSS
from playwright.async_api import async_playwright


def card_html(kind,fields,side='front'):
    t=make_template(kind)
    rendered=t['qfmt' if side=='front' else 'afmt']
    for k,v in fields.items(): rendered=rendered.replace('{{'+k+'}}',v)
    return '<!doctype html><meta charset="utf-8"><style>'+CSS+'</style>'+rendered

async def run_tests():
    async with async_playwright() as p:
        browser=await p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=await browser.new_page()
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        shared={'Prompt':'das Haus','Options':as_json_field([{'text':x,'image':''} for x in ['la casa','il libro','la pizza','la città']]),
                'Correct':as_json_field([0]),'Explanation':'', 'Prompt Image':'', 'Audio':'','UID':'demo-choice'}
        await page.set_content(card_html('choice',shared))
        assert await page.locator('.aic-option').count()==4
        await page.get_by_role('button',name='la casa').click()
        assert 'Richtig' in await page.locator('.aic-feedback').inner_text()
        await page.set_content(card_html('choice',shared,'back'))
        assert 'la casa' in await page.locator('.aic-solution').inner_text()
        assert 'Deine Antwort' in await page.locator('.aic-feedback').inner_text()

        multi={**shared,'UID':'demo-multi','Prompt':'Welche sind Nomen?',
               'Correct':as_json_field([0,1])}
        await page.set_content(card_html('multi',multi))
        await page.get_by_role('button',name='la casa').click()
        await page.get_by_role('button',name='il libro').click()
        await page.get_by_role('button',name='Auswahl prüfen').click()
        assert 'Richtig' in await page.locator('.aic-feedback').inner_text()

        sentence={'UID':'demo-sentence','Prompt':'Ich bin zu Hause','Answer':'sono a casa',
                  'Tokens':as_json_field(['sono','a','casa']), 'Alternatives':as_json_field(['io sono a casa']),
                  'Mode':'both','Explanation':'','Prompt Image':'','Audio':''}
        await page.set_content(card_html('sentence',sentence))
        for token in ['sono','a','casa']:
            await page.locator('.aic-bank').get_by_role('button',name=token,exact=True).click()
        await page.get_by_role('button',name='Satz prüfen').click()
        assert 'Richtig' in await page.locator('.aic-feedback').inner_text()
        await page.set_content(card_html('sentence',sentence))
        await page.get_by_role('button',name='Schreiben').click()
        await page.locator('textarea.aic-type').fill('sono a casa!')
        await page.get_by_role('button',name='Satz prüfen').click()
        assert 'Richtig' in await page.locator('.aic-feedback').inner_text()

        wrong_tiles = {**sentence, 'UID':'demo-wrong-tiles',
                       'Mode':'tiles', 'Distractors':as_json_field(['il', 'andare'])}
        await page.set_content(card_html('sentence',wrong_tiles))
        assert await page.locator('.aic-bank .aic-token').count() == 5
        assert 'Nicht alle Wörter' in await page.locator('.aic-distractor-hint').inner_text()
        for token in ['sono','a','casa']:
            await page.locator('.aic-bank').get_by_role('button',name=token,exact=True).click()
        await page.get_by_role('button',name='Satz prüfen').click()
        assert 'Richtig' in await page.locator('.aic-feedback').inner_text()
        await page.set_content(card_html('sentence',wrong_tiles))
        for token in ['sono','il','a','casa']:
            await page.locator('.aic-bank').get_by_role('button',name=token,exact=True).click()
        await page.get_by_role('button',name='Satz prüfen').click()
        assert 'Nicht ganz' in await page.locator('.aic-feedback').inner_text()
        await page.set_content(card_html('sentence',{**wrong_tiles, 'UID':'demo-old', 'Distractors':''}))
        assert await page.locator('.aic-bank .aic-token').count() == 3

        # Only AIC technical field rows may be hidden; changes to the selected
        # notetype or the 'show technical' toggle must restore their visibility.
        await page.set_content('''<div id="editor">
          <div class="field-row"><label class="field-label">Prompt</label><div contenteditable="true"></div></div>
          <div class="field-row"><label class="field-label">Answer</label><div contenteditable="true"></div></div>
          <div class="field-row"><label class="field-label">Distractors</label><div contenteditable="true"></div></div>
          <div class="field-row"><label class="field-label">Explanation</label><div contenteditable="true"></div></div>
          </div>''')
        await page.evaluate((Path(__file__).parents[1]/'src/web/editor_visibility.js').read_text(encoding='utf-8'))
        await page.evaluate('window.AICFieldVisibility.configure(["Answer","Distractors"],false)')
        assert await page.locator('.aic-technical-field-hidden').count() == 2
        await page.evaluate('window.AICFieldVisibility.configure(["Answer","Distractors"],true)')
        assert await page.locator('.aic-technical-field-hidden').count() == 0
        await page.evaluate('window.AICFieldVisibility.configure(["Answer","Distractors"],false)')
        await page.evaluate('window.AICFieldVisibility.configure([],false)')
        assert await page.locator('.aic-technical-field-hidden').count() == 0

        image={**shared,'UID':'demo-images','Options':as_json_field([
            {'text':'la casa','image':'home.png'}, {'text':'il libro','image':'book.png'}]),
            'Correct':as_json_field([0])}
        await page.set_content(card_html('choice',image))
        assert await page.locator('.aic-thumb').count()==2
        assert await page.locator('.aic-label').count()==0
        # In image mode no text answer is shown, but image src identifies it in this test.
        await page.locator('.aic-option').filter(has=page.locator('img[src="home.png"]')).click()
        assert 'Richtig' in await page.locator('.aic-feedback').inner_text()
        assert not errors, errors
        print('Browser tests: 8/8 scenarios passed (choice, back, multi, tiles, typing, image, wrong tiles, editor visibility).')
        await browser.close()

if __name__ == '__main__':asyncio.run(run_tests())
