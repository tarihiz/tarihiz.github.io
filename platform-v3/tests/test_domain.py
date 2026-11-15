import unittest
from copy import deepcopy
from api.domain import initial_state, save_values, move, TABLE, COMPARE
class WorkflowTests(unittest.TestCase):
 def test_no_skip(self):
  s=initial_state()
  for target in ['6','11','-1','bad']:
   with self.assertRaises(ValueError):move(s,target)
 def test_empty_metadata_blocked(self):
  with self.assertRaises(ValueError):move(initial_state(),'next')
 def test_initial_response_immutable(self):
  s=save_values(initial_state(),0,'Kaynak amacı ve tarihi önemlidir.');s=move(s,'next');s=move(s,'next')
  s=save_values(s,2,dict.fromkeys(TABLE,'Kanıta dayalı yanıt'));s=move(s,'next');s=move(s,'2')
  with self.assertRaises(ValueError):save_values(s,2,dict.fromkeys(TABLE,'Değiştirme'))
 def test_ai_cannot_be_skipped(self):
  s=initial_state();s.update(cursor=3,unlocked=3)
  with self.assertRaises(ValueError):move(s,'next')
 def test_wrong_fields_and_steps(self):
  s=initial_state()
  with self.assertRaises(ValueError):save_values(s,2,dict.fromkeys(TABLE,'x'))
  with self.assertRaises(ValueError):save_values(s,0,{'ready':True})
 def test_complete_workflow(self):
  s=initial_state()
  for i in range(11):
   self.assertEqual(s['cursor'],i)
   if i==0:s=save_values(s,0,'Kaynak künyesi değerlendirmesi')
   if i in (2,4):s=save_values(s,i,dict.fromkeys(TABLE,'Gerekçe ve kanıt'))
   if i in (7,9):s=save_values(s,i,dict.fromkeys(COMPARE,'Karşılaştırmalı gerekçe'))
   if i==10:s=save_values(s,10,'Kanıta ve belirsizliğe dayalı sonuç')
   if i in (3,8):s['chats']['single' if i==3 else 'multi']['ready']=True
   old=deepcopy(s);s=move(s,'next');self.assertEqual(old['cursor'],i)
  self.assertEqual(s['unlocked'],11)
  s=move(s,'7')
  with self.assertRaises(ValueError):save_values(s,7,dict.fromkeys(COMPARE,'Değiştirme'))
if __name__=='__main__':unittest.main()
