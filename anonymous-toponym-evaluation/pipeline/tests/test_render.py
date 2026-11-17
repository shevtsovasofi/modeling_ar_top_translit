import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from render import *
from run_pipeline import preserve_marks
class TestRender(unittest.TestCase):
 def setUp(self):self.r=Renderer()
 def test_street(self):
  x=self.r.render('شارع فيصل','شَارِع فَيْصَل')
  self.assertEqual(x['final_en'],'Faisal Street');self.assertEqual(x['final_ru'],'Улица Фейсал')
 def test_title(self):
  x=self.r.render('شارع الملك فيصل','شَارِع الْمَلِك فَيْصَل')
  self.assertEqual(x['final_en'],'King Faisal Street')
  self.assertEqual(x['status'],'review')
  self.assertIn('russian_inflection_required',x['warnings'])
 def test_article(self):
  self.assertEqual(render_word('الشَّمْس','en')[0],'Al Shams')
  self.assertEqual(render_word('الشَّمْس','ru')[0],'Аль Шамс')
  self.assertEqual(render_word('الشَّمْس','en','phonetic')[0],'Ash-Shams')
  self.assertEqual(render_word('قَمَر','en')[0],'Qamar')
 def test_terminal_consonants(self):
  for word in ['الشَّمْس','قَمَر','خَلِيل','تِيت','سُور','صَدُّوق']:
   for language in ['en','ru']:
    self.assertNotIn('incomplete_diacritization',render_word(word,language)[1],word)
  self.assertIn('incomplete_diacritization',render_word('قمر','en')[1])
  self.assertIn('incomplete_diacritization',render_word('قَمّر','en')[1])
 def test_vowels(self):
  for word,en,ru in [('نُور','Nur','Нур'),('خَلِيل','Khalil','Халил'),('فَيْصَل','Faysal','Файсал'),('دَوْر','Dawr','Даур'),('مَكَّة','Makka','Макка'),('آدَم','Adam','Адам'),('سُؤَال','Su\'al','Суал')]:
   self.assertEqual(render_word(word,'en')[0],en,word);self.assertEqual(render_word(word,'ru')[0],ru,word)
 def test_safety(self):
  self.assertEqual(self.r.render('خليل','جَلِيل')['status'],'rejected')
  self.assertIn('incomplete_diacritization',self.r.render('قمر','قمر')['warnings'])
  self.assertIsNone(self.r.match('زهرة النور')[0])
  self.assertIn('ambiguous_generic',self.r.match('عين النور')[2])
  self.assertIsNotNone(self.r.match('عين النور','عين')[0])
 def test_longest(self):self.assertEqual(self.r.match('طريق سريع فيصل')[0]['ar_term'],'طريق سريع')
 def test_marks(self):self.assertEqual(preserve_marks('خُلَيل','خَلِيل'),'خُلَيل')
 def test_overrides(self):
  r=Renderer(overrides=[{'name_ar':'قمر','country':'XX','en':'Known','ru':'Форма','source':'manual-v1'}])
  self.assertEqual(r.render('قمر','قَمَر',country='XX')['final_en'],'Known')
  self.assertNotEqual(r.render('قمر','قَمَر',country='YY')['final_en'],'Known')
class MetricTests(unittest.TestCase):
 def test_character_score(self):
  from score_labels import score
  self.assertEqual(score([('abc','abc')])['character_f1'],1)
  self.assertAlmostEqual(score([('abc','adc')])['character_f1'],2/3)
  self.assertEqual(score([('', 'abc')])['character_f1'],0)
  self.assertAlmostEqual(score([('ab','abc')])['character_f1'],4/5)
if __name__=='__main__':unittest.main()
