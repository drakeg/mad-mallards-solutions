"""Zero-dependency website and SQLite form receiver."""
import json, os, re, sqlite3, time
from collections import defaultdict, deque
from email.parser import BytesParser
from email.policy import default
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import parse_qs, urlsplit
ROOT=Path(__file__).resolve().parent
SITE=ROOT/"site"
DB=Path(os.environ.get("MMS_DATABASE",str(ROOT/"data"/"leads.sqlite3")))
HOST=os.environ.get("MMS_HOST","127.0.0.1")
PORT=int(os.environ.get("MMS_PORT","8097"))
LIMITS=defaultdict(deque)
LOCK=Lock()
EMAIL=re.compile(r"^[^\s@<>]{1,64}@[^\s@<>]{1,189}\.[A-Za-z]{2,63}$")
def connection():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(str(DB),timeout=10)
    c.execute("PRAGMA busy_timeout=10000")
    c.execute("CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT NOT NULL,message TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS subscribers (id INTEGER PRIMARY KEY,email TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,status TEXT NOT NULL DEFAULT 'pending')")
    return c
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(SITE),**kwargs)
    def end_headers(self):
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Referrer-Policy","strict-origin-when-cross-origin")
        self.send_header("Content-Security-Policy","default-src 'self'; style-src 'self' https://fonts.googleapis.com 'unsafe-inline'; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'")
        super().end_headers()
    def respond(self,status,data):
        body=json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(body)))
        self.send_header("Cache-Control","no-store")
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        path=urlsplit(self.path).path
        if path=="/health":return self.respond(200,{"status":"ok"})
        if path=="/":self.path="/index.html"
        elif path=="/blog":
            self.send_response(308)
            self.send_header("Location","/blog/")
            self.end_headers()
            return
        super().do_GET()
    def do_POST(self):
        path=urlsplit(self.path).path
        if path not in ("/api/contact","/api/subscribe"):
            return self.respond(404,{"error":"Not found."})
        kind=self.headers.get("Content-Type","").split(";")[0]
        if kind not in ("application/x-www-form-urlencoded","multipart/form-data"):
            return self.respond(415,{"error":"Unsupported form encoding."})
        try:size=int(self.headers.get("Content-Length","0"))
        except ValueError:return self.respond(400,{"error":"Invalid content length."})
        if size<=0 or size>12000:return self.respond(413,{"error":"Submission too large."})
        ip=self.client_address[0]
        now=time.monotonic()
        with LOCK:
            q=LIMITS[ip]
            while q and now-q[0]>60:q.popleft()
            if len(q)>=10:return self.respond(429,{"error":"Too many attempts. Try again later."})
            q.append(now)
        try:
            raw=self.rfile.read(size)
            if kind=="application/x-www-form-urlencoded":
                parsed=parse_qs(raw.decode("utf-8"),keep_blank_values=True,max_num_fields=12)
                fields={k:v[0] for k,v in parsed.items()}
            else:
                message=BytesParser(policy=default).parsebytes(b"Content-Type: "+self.headers["Content-Type"].encode()+b"\r\nMIME-Version: 1.0\r\n\r\n"+raw)
                if not message.is_multipart():return self.respond(400,{"error":"Invalid form."})
                parts=list(message.iter_parts())
                if len(parts)>12:return self.respond(400,{"error":"Too many fields."})
                fields={}
                for part in parts:
                    key=part.get_param("name",header="content-disposition")
                    if not key or part.get_filename():return self.respond(400,{"error":"No file uploads."})
                    fields[key]=part.get_content()
            def field(key):
                v=fields.get(key,"")
                return v.strip() if isinstance(v,str) else ""
            if field("website"):return self.respond(200,{"message":"Thanks."})
            email=field("email").lower()
            if len(email)>254 or not EMAIL.fullmatch(email):
                return self.respond(400,{"error":"Enter a valid email."})
            with connection() as c:
                if path=="/api/contact":
                    name,message=field("name"),field("message")
                    if not (1<=len(name)<=120 and 10<=len(message)<=4000):
                        return self.respond(400,{"error":"Enter a name and message of at least 10 characters."})
                    c.execute("INSERT INTO contacts(name,email,message) VALUES(?,?,?)",(name,email,message))
                    return self.respond(201,{"message":"Message saved. Thank you for getting in touch!"})
                c.execute("INSERT OR IGNORE INTO subscribers(email) VALUES(?)",(email,))
                return self.respond(201,{"message":"You're on the list. Newsletter emails are not yet configured."})
        except (ValueError,KeyError,sqlite3.Error,TypeError):
            return self.respond(400,{"error":"Could not process submission."})
if __name__=="__main__":
    with connection():pass
    print("Serving at http://%s:%s"%(HOST,PORT),flush=True)
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
