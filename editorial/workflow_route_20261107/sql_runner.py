"""Desktop counterpart of the bounded native SQLite host, for private lab QA."""
import json,os,sqlite3,sys
request=json.loads(sys.argv[1]);db=sqlite3.connect(os.environ['ROUTE_SQL_DATABASE'],isolation_level=None)
db.execute('PRAGMA foreign_keys=ON')
if request.get('readOnly'):
 denied={sqlite3.SQLITE_INSERT,sqlite3.SQLITE_UPDATE,sqlite3.SQLITE_DELETE,sqlite3.SQLITE_CREATE_TABLE,sqlite3.SQLITE_DROP_TABLE,sqlite3.SQLITE_ALTER_TABLE,sqlite3.SQLITE_ATTACH,sqlite3.SQLITE_DETACH,sqlite3.SQLITE_PRAGMA}
 db.set_authorizer(lambda action,*_:sqlite3.SQLITE_DENY if action in denied else sqlite3.SQLITE_OK)
try:
 statements=[];pending=''
 for c in request['sql']:
  pending+=c
  if c==';' and sqlite3.complete_statement(pending):statements.append(pending);pending=''
 if pending.strip():statements.append(pending)
 columns=[];rows=[]
 for statement in statements:
  cursor=db.execute(statement,request.get('params',[]))
  if cursor.description:
   columns=[c[0] for c in cursor.description];rows=[[str(v) if v is not None else None for v in row] for row in cursor.fetchall()]
 if db.in_transaction:db.rollback();raise ValueError('Uncommitted transaction')
 value={'columns':columns,'rows':rows,'changes':db.execute('SELECT changes()').fetchone()[0]}
except Exception as error:
 if db.in_transaction:db.rollback()
 value={'error':str(error)}
print(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False));db.close()
