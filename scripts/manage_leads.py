"""Local-only CLI for authorized operators to inspect and manage form submissions.

Examples:
    python scripts/manage_leads.py summary
    python scripts/manage_leads.py contacts
    python scripts/manage_leads.py subscribers
    python scripts/manage_leads.py export-contacts > contacts.csv
    python scripts/manage_leads.py export-subscribers > subscribers.csv
    python scripts/manage_leads.py unsubscribe person@example.com --confirm
    python scripts/manage_leads.py delete-contact 42 --confirm

Run only on a trusted host. Exports contain personal data and should never be committed.
"""
import argparse
import csv
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data" / "leads.sqlite3"
DATABASE = Path(os.environ.get("MMS_DATABASE", str(DEFAULT)))

def safe_cell(value):
    """Prevent CSV spreadsheet formula injection in exported untrusted fields."""
    s = str(value or "")
    return "'" + s if s.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")) else s

def read_rows(db, table):
    assert table in ("contacts", "subscribers")
    columns = ("id", "name", "email", "message", "created_at") if table == "contacts" else ("id", "email", "created_at", "status")
    result = db.execute("SELECT " + ",".join(columns) + " FROM " + table + " ORDER BY id DESC LIMIT 10000")
    return columns, list(result)

def cli(args=None):
    parser = argparse.ArgumentParser(description="Manage locally stored Mad Mallards Solutions leads")
    parser.add_argument("action", choices=("summary", "contacts", "subscribers", "export-contacts", "export-subscribers", "unsubscribe", "delete-contact", "delete-subscriber"))
    parser.add_argument("target", nargs="?", help="Email for unsubscribe or numeric record ID for delete")
    parser.add_argument("--confirm", action="store_true", help="Required for modifying records")
    options = parser.parse_args(args)
    if not DATABASE.exists():
        parser.error("Database not found. Start the website first. Expected: " + str(DATABASE))
    with sqlite3.connect(str(DATABASE)) as db:
        if options.action == "summary":
            print("Contacts:", db.execute("SELECT COUNT(*) FROM contacts").fetchone()[0])
            print("Subscribers pending:", db.execute("SELECT COUNT(*) FROM subscribers WHERE status='pending'").fetchone()[0])
            print("Subscribers unsubscribed:", db.execute("SELECT COUNT(*) FROM subscribers WHERE status='unsubscribed'").fetchone()[0])
        elif options.action in ("contacts", "subscribers", "export-contacts", "export-subscribers"):
            table = "contacts" if options.action.endswith("contacts") else "subscribers"
            columns,rows=read_rows(db, table)
            if options.action.startswith("export-"):
                writer=csv.writer(sys.stdout, lineterminator="\n")
                writer.writerow(columns)
                writer.writerows([[safe_cell(x) for x in row] for row in rows])
            else:
                print("Showing %d latest %s. Treat this output as private."%(len(rows),table), file=sys.stderr)
                for row in rows:
                    print(" | ".join(safe_cell(x) for x in row))
        else:
            if not options.confirm or not options.target:
                parser.error("This operation requires a target and --confirm")
            if options.action == "unsubscribe":
                result=db.execute("UPDATE subscribers SET status='unsubscribed' WHERE lower(email)=lower(?)",(options.target,))
            else:
                try:identifier=int(options.target)
                except ValueError:parser.error("Record ID must be an integer")
                table="contacts" if options.action == "delete-contact" else "subscribers"
                result=db.execute("DELETE FROM "+table+" WHERE id=?",(identifier,))
            print("Records changed:",result.rowcount)
            db.commit()

if __name__ == "__main__":
    cli()
