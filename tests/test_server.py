import os,sqlite3,subprocess,sys,tempfile,time,unittest,urllib.error,urllib.parse,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SiteTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory()
  cls.port=18979
  cls.db=Path(cls.tmp.name)/'test.sqlite3'
  cls.proc=subprocess.Popen([sys.executable,str(ROOT/'server.py')],cwd=ROOT,env={**os.environ,'MMS_PORT':str(cls.port),'MMS_DATABASE':str(cls.db)},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for _ in range(70):
   try:
    urllib.request.urlopen('http://127.0.0.1:%d/health'%cls.port,timeout=.3)
    break
   except Exception:time.sleep(.1)
  else:raise RuntimeError('Could not start test server')
 @classmethod
 def tearDownClass(cls):
  cls.proc.terminate();cls.proc.wait(timeout=5);cls.tmp.cleanup()
 def get(self,path):return urllib.request.urlopen('http://127.0.0.1:%d%s'%(self.port,path))
 def post(self,path,data):
  raw=urllib.parse.urlencode(data).encode()
  return urllib.request.urlopen(urllib.request.Request('http://127.0.0.1:%d%s'%(self.port,path),data=raw,method='POST'))
 def test_pages_and_assets(self):
  for path in ['/','/blog/','/privacy.html','/blog/automation-without-the-hype.html','/blog/small-business-cloud.html','/blog/monitoring-what-matters.html','/scrollcraft.js','/styles.css']:
   with self.subTest(path=path):
    with self.get(path) as response:
     self.assertEqual(response.status,200)
     self.assertGreater(len(response.read()),300)
 def test_contact_and_subscription(self):
  self.assertEqual(self.post('/api/contact',{'name':'Tester','email':'test@example.com','message':'A long enough question about our cloud needs.'}).status,201)
  for _ in range(2):self.assertEqual(self.post('/api/subscribe',{'email':'test@example.com'}).status,201)
  with sqlite3.connect(str(self.db)) as c:
   self.assertEqual(c.execute('SELECT count(*) FROM contacts').fetchone()[0],1)
   self.assertEqual(c.execute('SELECT count(*) FROM subscribers').fetchone()[0],1)
   self.assertEqual(c.execute('SELECT status FROM subscribers').fetchone()[0],'pending')
 def test_bad_email(self):
  with self.assertRaises(urllib.error.HTTPError) as err:self.post('/api/subscribe',{'email':'invalid'})
  self.assertEqual(err.exception.code,400)
 def test_unknown_page(self):
  with self.assertRaises(urllib.error.HTTPError) as err:self.get('/invalid-page-123.html')
  self.assertEqual(err.exception.code,404)
if __name__=='__main__':unittest.main()
