import os, unittest
from uuid import uuid4
from unittest.mock import AsyncMock,patch
from fastapi import HTTPException
os.environ.setdefault('CODE_PEPPER','test-secret-which-is-long-enough-for-tests')
from api import app as module
from api.domain import initial_state
class APITests(unittest.IsolatedAsyncioTestCase):
 async def test_ownership_scoped(self):
  store=type('Store',(),{'call':AsyncMock(return_value=[])})();module.app.state.store=store
  with self.assertRaises(HTTPException) as ctx:await module.get_work(uuid4(),'owner-1')
  self.assertEqual(ctx.exception.status_code,404)
  self.assertEqual(store.call.call_args.kwargs['params']['participant_id'],'eq.owner-1')
 async def test_revision_conflict(self):
  w={'id':str(uuid4()),'participant_id':'p','revision':2}
  with self.assertRaises(HTTPException) as ctx:await module.commit(w,initial_state(),1)
  self.assertEqual(ctx.exception.status_code,409)
 async def test_atomic_conflict(self):
  store=type('Store',(),{'call':AsyncMock(return_value=[])})();module.app.state.store=store
  w={'id':str(uuid4()),'participant_id':'p','revision':2}
  with self.assertRaises(HTTPException) as ctx:await module.commit(w,initial_state(),2)
  self.assertEqual(ctx.exception.status_code,409)
 async def test_pdf_blocked_until_finish(self):
  with patch.object(module,'get_work',AsyncMock(return_value={'state':initial_state()})):
   with self.assertRaises(HTTPException) as ctx:await module.report(uuid4(),'p')
   self.assertEqual(ctx.exception.status_code,422)
 async def test_rate_limit_enforced(self):
  module.app.state.store=type('Store',(),{'call':AsyncMock(return_value=False)})()
  with self.assertRaises(HTTPException) as ctx:await module.budget('key',12,300)
  self.assertEqual(ctx.exception.status_code,429)
if __name__=='__main__':unittest.main()
