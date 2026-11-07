"""Author the six-stage engineering route; retain every previous learning identity."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;C=ROOT/'courses/projects'
def read(p):return json.loads(p.read_text())
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
LABS=[]
UNITS=[('route-git','Git: Changes to History','Review, commit, branch and recover'),('route-cli','CLI: A Reliable Interface','Arguments, configuration, streams and exit codes'),('route-http','HTTP API: Explicit Contracts','Routing, request limits, responses and retries'),('route-sql','SQL: Durable State','Schema, queries, parameters and atomic changes'),('route-diagnostics','Diagnostics: Explain a Failure','Context, correlation, latency and retry budgets'),('route-delivery','Delivery: A Repeatable Release','Checks, configuration, artifacts and rollback')]
course=read(C/'course.json')
if not (HERE/'previous-identities.json').exists():
 save(HERE/'previous-identities.json',{'unitIDs':course['unitIDs'],'lessons':[read(p) for p in sorted((C/'lessons').glob('*.json'))]})

def lab(unit,id,title,concept,rule,explanation,signature,body,cases,task,question,answers,feedback,commands,reference,setup='',mutant=None,extra=''):
 starter=setup+signature+' {\n    todo!("implement the contract")\n}\n'
 solution=setup+signature+' {\n'+body+'\n}\n'
 assertions='\n'.join(f'assert_eq!({call}, {expected}, "case {i+1}");' for i,(call,expected) in enumerate(cases))
 harness='mod solution;\nfn main() {\n'+assertions+'\n'+extra+'\nprintln!("PASS '+id+'");\n}\n'
 example=solution+'\nfn main() {\n'+assertions.replace('solution::','')+'\nprintln!("worked example passed");\n}\n'
 add(unit,id,title,concept,rule,explanation,starter,solution,harness,example,cases,task,question,answers,feedback,commands,reference,
     mutant=setup+signature+' {\n'+(mutant or 'panic!("wrong implementation")')+'\n}\n')

def add(unit,id,title,concept,rule,explanation,starter,solution,harness,example,cases,task,question,answers,feedback,commands,reference,profile='std-v1',mutant=''):
 uid=UNITS[unit][0];order=sum(x['unit']==unit for x in LABS)
 wrong_answer=answers[1];correct_index=(len(LABS)*2+1)%len(answers)
 if correct_index:answers=answers[-correct_index:]+answers[:-correct_index]
 formatted=subprocess.run(['rustfmt','--edition','2024','--config','max_width=72'],input=example,text=True,capture_output=True,check=True)
 example=formatted.stdout
 explanation+='\n\nThe route project is Task Ledger: first keep a reproducible source history, then expose its data through a CLI and HTTP boundary, persist it in SQL, diagnose failures and prepare a release. This lesson owns one contract in that project. Run the worked example before changing the starter and explain which input makes the tempting shortcut fail.\n\nTerminal practice: '+commands+'\n\nThe compiler lab is independent of the reading question. Edit solution.rs; the app supplies a separate caller with normal, empty and adversarial inputs. A successful unchanged demonstration does not prove your implementation. After the lab, apply the same contract to the route companion project. Its README separates the on-device adapter from the desktop Cargo/TCP profile.'
 item={'id':id,'parentID':uid,'order':order,'title':title,'concept':concept,'minutes':25,'exerciseKind':'runnable','writing':{
 'summary':concept+'.','rule':rule,'explanation':explanation,'exampleCode':example,'exampleCaption':('This Rust reading prints a SQL statement. The independent compiler lab executes it against real SQLite.' if profile=='sqlite-v1' else 'The worked implementation exercises '+concept.lower()+'. Its tests demonstrate the stated finite contract.'),'practiceCode':starter,'task':task+' Keep the public signature. Open the compiler lab and edit solution.rs; do not edit the private verification caller.','success':'The separate caller accepts the changed solution and rejects unchanged TODO, a wrong implementation and a printed success message.','question':question,'answers':answers,'correctAnswer':correct_index,'feedback':feedback},
 'depth':{'misconception':wrong_answer,'correction':rule,'traceSteps':[{'title':'Identify the boundary','detail':concept+'. Write down its accepted inputs and observable output.'},{'title':'Exercise the failure','detail':feedback},{'title':'Check the independent caller','detail':task}],'transferChallenge':'Apply this contract to Task Ledger, introduce the failure described in the lesson, and show the failing check before fixing it.','connections':[]},'resources':[{'title':'Primary reference','url':reference}]}
 existing=C/'lessons'/f'{id}.json'
 if existing.exists() and read(existing).get('illustration'):item['illustration']=read(existing)['illustration']
 save(C/'lessons'/f'{id}.json',item)
 challenge={'lessonID':id,'patternID':id,'projectName':id+'-lab','source':starter,'verificationSource':harness,'verificationCases':[{'kind':'visible' if i==0 else 'boundary' if i==1 else 'semantic','input':call,'expectedAnswer':expected} for i,(call,expected) in enumerate(cases)],'expectedOutput':'PASS '+id+'\n','requiredSourceFragments':['pub fn '+solution.split('pub fn ',1)[1].split('(',1)[0]],'forbiddenSourceFragments':['todo!("implement the contract")'],'executionProfile':profile}
 save(C/'checks'/f'{id}.json',{'challenge':challenge,'evidence':{'kind':'algorithmChallenge','expectedOutput':{'kind':'exact','value':challenge['expectedOutput']},'requiredSourceFragments':challenge['requiredSourceFragments'],'forbiddenSourceFragments':challenge['forbiddenSourceFragments']}})
 project=C/'projects'/id;save(project/'project.json',{'name':id+'-lab','entryFile':'solution.rs'});(project/'solution.rs').write_text(starter)
 (project/'README.md').write_text('# '+title+'\n\n'+task+'\n\nTerminal companion: '+commands+'\n\nThe private verification caller is supplied by the installed lesson. SQL-profile lessons require workflow-terminal-v1; they execute real SQLite in a fresh database. The complete Task Ledger source is in the route companion files.\n')
 LABS.append({'unit':unit,'id':id,'reference':solution,'starter':starter,'mutant':mutant,'harness':harness,'reading':example,'expectedOutput':challenge['expectedOutput'],'profile':profile})

GIT='https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository'
lab(0,'route-git-review','Review the Exact Change','Distinguish changed, added and deleted paths','Compare source snapshots by path and content before selecting a commit.',
'''A worktree is the collection you are editing. A commit records a particular tree; autosave protects edits but does not create a commit. Review both before selecting paths. A file can disappear, appear, or keep its name while its contents change. Looking only for new names misses modifications and deletions.

Build the candidate path set from both trees and compare values. Return each changed path once in lexical order. File ordering is presentation, not Git object identity. This lab models text trees; real Git also stores modes and opaque bytes. In the native terminal, inspect actual history through the existing libgit2-backed commands. The selected-path commit profile commits exactly the reviewed paths, so unrelated edits stay uncommitted.''',
'pub fn changed(before: &[(&str, &str)], after: &[(&str, &str)]) -> Vec<String>',
'''let a: std::collections::BTreeMap<_,_> = before.iter().copied().collect();
let b: std::collections::BTreeMap<_,_> = after.iter().copied().collect();
a.keys().chain(b.keys()).copied().collect::<std::collections::BTreeSet<_>>().into_iter().filter(|k| a.get(k)!=b.get(k)).map(str::to_owned).collect()''',
[('solution::changed(&[("a","1")], &[("a","2"),("b","3")])','vec!["a".to_owned(),"b".to_owned()]'),('solution::changed(&[], &[])','Vec::<String>::new()'),('solution::changed(&[("gone","x")], &[])','vec!["gone".to_owned()]'),('solution::changed(&[("a","1")], &[("a","1")])','Vec::<String>::new()')],
'Return the sorted unique paths whose contents differ between two trees; include additions and deletions. Each input has unique paths.',
'An existing file keeps its name but changes content. Should it appear in the review?', ['Yes, content is part of the snapshot','Only newly named files belong in a change review','Autosave makes the edit a commit'],
'Comparing only path names misses modified content; comparing only the new tree misses deletions.',
'Run git status and git diff src/main.rs before committing. The terminal uses real Git; the lab isolates the tree-comparison contract.',GIT,mutant='Vec::new()')
lab(0,'route-git-select','Commit Only Reviewed Paths','Construct the selected commit tree','An unselected worktree edit must not silently enter a selected-path commit.',
'''Task Ledger changes its CLI and a private scratch note at the same time. A commit intended to fix CLI parsing should contain the CLI change, leaving the note outside history. The tree to commit begins with HEAD, not with every current worktree file. Apply selected additions, modifications and deletions onto that tree.

A selection can include a deleted path: remove it from the commit tree instead of resurrecting its old text. Unknown selected paths have no effect in this model. An actual Git operation additionally validates file paths, expected HEAD and concurrent editor revisions. The terminal deliberately uses selected-path commits rather than pretending to implement an independent staging area. Desktop Git can use its index; distinguish that workflow from this app profile.''',
'pub fn selected_tree(head: &[(&str,&str)], work: &[(&str,&str)], selected: &[&str]) -> Vec<(String,String)>',
'''let mut tree: std::collections::BTreeMap<String,String> = head.iter().map(|(k,v)|(k.to_string(),v.to_string())).collect();
let work: std::collections::BTreeMap<_,_> = work.iter().copied().collect();
for path in selected { if let Some(value)=work.get(path) { tree.insert(path.to_string(),value.to_string()); } else { tree.remove(*path); } }
tree.into_iter().collect()''',
[('solution::selected_tree(&[("a","old"),("b","old")], &[("a","new"),("b","secret")], &["a"])','vec![("a".to_owned(),"new".to_owned()),("b".to_owned(),"old".to_owned())]'),('solution::selected_tree(&[], &[("a","x")], &[])','vec![]'),('solution::selected_tree(&[("a","x")], &[], &["a"])','vec![]'),('solution::selected_tree(&[], &[("b","x")], &["b","b"])','vec![("b".to_owned(),"x".to_owned())]')],
'Return the HEAD tree with only selected paths replaced from the worktree, or removed if selected and missing. Sort by path; paths are unique in each input.',
'Which tree is the starting point for a selected-path commit?', ['HEAD, followed by selected changes','The whole current worktree always enters the commit','The selected filenames without their contents'],
'Starting from the whole worktree includes unrelated edits.',
'Configure git config user.name and user.email, then git commit -m "Validate CLI input" -- src/main.rs; inspect git status afterwards.',GIT,mutant='work.iter().map(|(k,v)|(k.to_string(),v.to_string())).collect()')
lab(0,'route-git-branch','Switch Without Losing Work','Protect dirty worktrees during checkout','Require a clean worktree before this profile replaces files from another branch.',
'''Branches name positions in history. Creating a branch does not copy a folder, and switching it is not merely changing a label: the target tree can replace editor files. A clean-checkout policy is easy to explain and test. It refuses the operation whenever the current worktree differs from its HEAD, including an untracked file or deletion.

Compare trees without relying on their enumeration order. A new branch can be created while preserving current edits, but switching uses the clean-tree precondition in this terminal. A desktop client may support more nuanced preservation or stash; those are distinct contracts. After committing, refresh status before switching, because a successful commit of one captured snapshot does not prove newer typing was also committed.''',
'pub fn clean(work: &[(&str,&str)], head: &[(&str,&str)]) -> bool',
'work.iter().copied().collect::<std::collections::BTreeMap<_,_>>() == head.iter().copied().collect::<std::collections::BTreeMap<_,_>>()',
[('solution::clean(&[("b","2"),("a","1")], &[("a","1"),("b","2")])','true'),('solution::clean(&[],&[])','true'),('solution::clean(&[("a","new")], &[("a","old")])','false'),('solution::clean(&[("extra","x")], &[])','false'),('solution::clean(&[], &[("gone","x")])','false')],
'Return whether two unique-path trees have identical contents, independent of enumeration order.',
'Can an untracked file matter to a clean-checkout policy?', ['Yes; the worktree differs from HEAD','Only tracked modifications can make a checkout unsafe','Changing branch names preserves every file automatically'],
'An added or deleted file is a tree difference even when tracked file contents match.',
'Run git branch feature-cli, git status, then git switch feature-cli after the tree is clean.',GIT,mutant='true')
lab(0,'route-git-recover','Recover One Historical File','Restore narrowly from a known revision','A one-file restore must preserve every unrelated current edit.',
'''A rollback need not replace a whole project. To recover one file, first inspect its contents at an exact historical commit, compare it with the current file, then confirm the replacement. A full commit identity makes the preview stable while branch names continue moving.

The native git restore command opens a preview; applying the restore remains an explicit UI action. This lab models the resulting tree change: replace just the requested path from the historical tree, or remove it if it did not exist there. Preserve unrelated work and deterministic ordering. Restoring a file is also an uncommitted edit; review and commit it as a new change when it belongs in shared history. Do not rewrite already shared history to hide an ordinary correction.''',
'pub fn restore(work: &[(&str,&str)], historical: &[(&str,&str)], path: &str) -> Vec<(String,String)>',
'''let mut tree: std::collections::BTreeMap<String,String> = work.iter().map(|(k,v)|(k.to_string(),v.to_string())).collect();
if let Some((_,text))=historical.iter().find(|(p,_)|*p==path) { tree.insert(path.to_owned(),text.to_string()); } else { tree.remove(path); }
tree.into_iter().collect()''',
[('solution::restore(&[("a","new"),("b","keep")], &[("a","old")], "a")','vec![("a".to_owned(),"old".to_owned()),("b".to_owned(),"keep".to_owned())]'),('solution::restore(&[], &[], "missing")','vec![]'),('solution::restore(&[("a","x")], &[], "a")','vec![]'),('solution::restore(&[], &[("a","x")], "a")','vec![("a".to_owned(),"x".to_owned())]')],
'Return the current tree with exactly one path restored from a historical tree. Absence in history removes that path.',
'After restoring one historical file, what happens to unrelated current edits?', ['They stay in the worktree','All files should revert to the historical tree','A restore rewrites every previous commit'],
'Replacing the entire tree loses unrelated edits and exceeds the requested recovery.',
'Use git log, git show <full-commit>:src/main.rs, then git restore --source <full-commit> -- src/main.rs and inspect the preview.',GIT,mutant='historical.iter().map(|(k,v)|(k.to_string(),v.to_string())).collect()')

CLI='https://rust-cli.github.io/book/index.html'
lab(1,'route-cli-arguments','Parse a CLI Contract','Preserve arguments and reject ambiguous input','Parse the entire invocation before applying any side effect.',
'''A shell groups text into arguments before a Rust program sees it. Quotes preserve a space or an empty argument; they are not usually part of the resulting argument. Cargo consumes its options before the double dash and passes the remainder to the executable. The first executable argument is conventionally the program name and is not a user command.

Task Ledger accepts exactly `list` or `add TITLE`. Reject an unknown command, a missing title and extra arguments. Trim the title for domain validation, while retaining internal spaces and Unicode. Do not partially add a task before discovering a later invalid option. The independent lab takes only the already-separated user arguments; the companion main passes `std::env::args().skip(1)`.''',
'pub fn command(args: &[&str]) -> Result<String,String>',
'''match args { ["list"] => Ok("list".to_owned()), ["add",title] if !title.trim().is_empty() => Ok(format!("add:{}",title.trim())), _=>Err("usage".to_owned()) }''',
[('solution::command(&["add","  learn Rust 🦀  "])','Ok("add:learn Rust 🦀".to_owned())'),('solution::command(&[])','Err("usage".to_owned())'),('solution::command(&["add",""])','Err("usage".to_owned())'),('solution::command(&["list","extra"])','Err("usage".to_owned())'),('solution::command(&["list"])','Ok("list".to_owned())')],
'Accept exactly list or add plus one nonblank title. Return list or add:TITLE with the title trimmed; reject every other shape with Err("usage").',
'Which invocation passes one title containing a space?', ['cargo run -- add "learn Rust"','cargo run add learn Rust','Quotes always become part of the Rust title'],
'The shell supplies argument boundaries; Cargo needs the double dash before application arguments.',
'Run cargo run -- add "learn Rust" and cargo run -- add "" against the companion CLI.',CLI,mutant='Ok("list".to_owned())')
lab(1,'route-cli-config','Resolve Configuration Once','Apply explicit configuration precedence','Choose flag over environment over default, then validate the chosen value.',
'''Configuration can come from a flag, an environment variable or a default. Establish precedence before parsing so a broken lower-priority value does not override an explicit valid flag. Conversely, do not silently fall back when the chosen highest-priority value is malformed: the operator needs to know their request was rejected.

The list limit must be an integer from 1 to 100. Absence selects 20, but an explicitly empty string is an invalid value, not absence. In production, report which configuration source failed without printing secrets. Invocation environment in Crabrix is passed only to the student program; it never changes the compiler or dependency build-script environment. This prevents an educational flag from accidentally reconfiguring the toolchain.''',
'pub fn limit(flag: Option<&str>, environment: Option<&str>) -> Result<u16,String>',
'''let raw=flag.or(environment).unwrap_or("20");
match raw.parse::<u16>() { Ok(n) if (1..=100).contains(&n) => Ok(n), _=>Err("invalid limit".to_owned()) }''',
[('solution::limit(Some("7"),Some("bad"))','Ok(7)'),('solution::limit(None,None)','Ok(20)'),('solution::limit(None,Some("100"))','Ok(100)'),('solution::limit(Some(""),Some("5"))','Err("invalid limit".to_owned())'),('solution::limit(Some("0"),None)','Err("invalid limit".to_owned())'),('solution::limit(None,Some("101"))','Err("invalid limit".to_owned())')],
'Choose flag, otherwise environment, otherwise 20. Parse the chosen string as u16 and accept only 1..=100; return invalid limit on failure.',
'An explicit valid flag overrides a malformed environment value. What should happen?', ['Use the flag','Reject the unrelated lower-priority value','Always use the default'],
'Precedence decides the authoritative value before validation; invalid authoritative input must still fail.',
'Run env TASK_LIMIT=7 cargo run -- list. Compare with env TASK_LIMIT=bad cargo run -- list.',CLI,mutant='Ok(20)')
lab(1,'route-cli-streams','Process Bounded Standard Input','Treat input as data with resource limits','Check byte limits before retaining input and validate complete records.',
'''Standard input makes a tool composable: a file can feed the same parser as typed input. Rust strings are UTF-8; byte length and character count answer different questions. A memory budget is measured in bytes, so an emoji can consume several bytes of the budget. A record title is a nonblank line after trimming, with at most 80 Unicode scalar values in this lab.

Reject the complete input if its byte size exceeds the supplied budget or any title is too long. Ignore blank lines and keep record order. A production streaming parser additionally stops accumulation as it reads; this exercise receives an already bounded string to isolate validation. The companion reads through a limited reader and detects one byte beyond its limit. Do not advertise a post-read length check as protection against an unbounded stream.''',
'pub fn titles(input: &str, max_bytes: usize) -> Result<Vec<String>,String>',
'''if input.len()>max_bytes { return Err("too large".to_owned()); }
let mut out=Vec::new(); for line in input.lines() { let value=line.trim(); if value.chars().count()>80 { return Err("title too long".to_owned()); } if !value.is_empty() { out.push(value.to_owned()); } } Ok(out)''',
[('solution::titles(" one\n\n two \r\n",100)','Ok(vec!["one".to_owned(),"two".to_owned()])'),('solution::titles("",0)','Ok(vec![])'),('solution::titles("🦀",3)','Err("too large".to_owned())'),('solution::titles(&"x".repeat(81),100)','Err("title too long".to_owned())'),('solution::titles("🦀",4)','Ok(vec!["🦀".to_owned()])')],
'Reject input exceeding max_bytes; trim lines, omit blanks, reject titles longer than 80 Unicode scalar values, and preserve order.',
'Which size controls a UTF-8 input memory budget?', ['Encoded byte length','Only the number of visible characters','The number of newline separators'],
'An emoji can fit one scalar position while exceeding a three-byte budget.',
'Create input.txt, then run cargo run -- import < input.txt; inspect stderr for an oversized record.',CLI,mutant='Ok(Vec::new())')
lab(1,'route-cli-exit','Separate Output from Failure','Return observable stdout, stderr and exit status','Data goes to stdout; a failure has stderr context and a nonzero status.',
'''Automation observes a program through more than its printed text. A machine may consume stdout as data and use the exit status to decide whether the next stage may run. Putting an error into stdout while returning success makes a broken command look like a valid empty result.

Use status 0 for a successful task count and 2 for a usage or input error in this CLI contract. Error text belongs on stderr and ends in a newline. Do not add a success banner to machine-readable stdout. A program that crashes or fails compilation is different from a deliberate domain error; retain that distinction when diagnosing the terminal result. The finite lab models the three outputs so tests can assert them separately; the companion uses println, eprintln and process::exit at its actual boundary.''',
'pub fn report(result: Result<usize,&str>) -> (String,String,u8)',
'''match result { Ok(n)=>(format!("{n}\\n"),String::new(),0), Err(e)=>(String::new(),format!("error: {e}\\n"),2) }''',
[('solution::report(Ok(3))','("3\n".to_owned(),"".to_owned(),0)'),('solution::report(Ok(0))','("0\n".to_owned(),"".to_owned(),0)'),('solution::report(Err("invalid title"))','("".to_owned(),"error: invalid title\n".to_owned(),2)'),('solution::report(Err("missing input"))','("".to_owned(),"error: missing input\n".to_owned(),2)')],
'Return stdout, stderr and exit code. Success emits COUNT followed by newline only on stdout with 0; errors emit error: MESSAGE followed by newline only on stderr with 2.',
'A command prints an error but exits with status 0. What is wrong for automation?', ['The command reports success through its status','Any text on stderr automatically changes the exit status','Exit codes are only decorative'],
'Writing stderr does not itself set a nonzero process exit status.',
'Run a valid and an invalid companion CLI invocation and compare output, error stream and exit result.',CLI,mutant='(String::new(),String::new(),0)')

HTTP='https://www.rfc-editor.org/rfc/rfc9110.html'
lab(2,'route-http-routing','Route Method and Path Together','Separate unknown routes from disallowed methods','Resolve the resource first, then the allowed HTTP method.',
'''An HTTP method is part of the request contract. GET /tasks lists tasks; POST /tasks creates one. A known resource with a disallowed method is different from a path the application does not own. This lab returns 405 for unsupported methods on /tasks and 404 for unknown paths; GET /health returns 200, while other health methods return 405.

The request target can include a query string. Separate it before matching the path, but do not lowercase the path or decode arbitrary escapes without a policy: route names can be case sensitive. The lab implements literal paths only. A desktop Axum router handles the transport; the on-device adapter passes a bounded real HTTP request to Rust through stdin. It is an HTTP/1.x adapter with one response per connection, not an implementation of every HTTP version or chunked body mode.''',
'pub fn route(method: &str, target: &str) -> u16',
'''match target.split('?').next().unwrap_or("") { "/tasks" => match method { "GET"=>200,"POST"=>201,_=>405 }, "/health"=>if method=="GET" {200}else{405}, _=>404 }''',
[('solution::route("GET","/tasks?limit=5")','200'),('solution::route("GET","/missing")','404'),('solution::route("DELETE","/tasks")','405'),('solution::route("POST","/tasks")','201'),('solution::route("GET","/Tasks")','404'),('solution::route("POST","/health")','405')],
'Match literal /tasks and /health after removing the query string. GET tasks=200, POST tasks=201, GET health=200; other methods on those paths=405, unknown paths=404.',
'What distinguishes 405 from 404 in this routing contract?', ['The resource exists but the method is disallowed','Both statuses always mean the same thing','An unknown path should return 200 with an empty body'],
'Matching only a method or only a path loses the distinction between unsupported operations and unknown resources.',
'Run cargo serve --port 8080 --database tasks.db, then curl -i http://127.0.0.1:8080/tasks and curl -i -X DELETE http://127.0.0.1:8080/tasks. Stop with http stop.',HTTP,mutant='200')
lab(2,'route-http-limits','Validate Before Applying Effects','Check declared and actual request size','A body-length mismatch is a framing error; an exceeded limit is a resource error.',
'''A request can advertise one size and deliver another. A server needs limits on both the declared size and accumulated bytes. Check limits before parsing the domain object or applying writes, otherwise an oversized request can consume unbounded resources or leave partial state.

This function receives an optional parsed Content-Length, actual byte count and maximum. Return 413 if either known size exceeds the maximum. Otherwise a present length that differs from actual input returns 400; valid bounded input returns 200. Missing length is accepted by this isolated policy when transport framing has already supplied a complete body. The native HTTP adapter has a stricter framing profile: it rejects chunked transfer, duplicate lengths and pipelined bytes. Never use this size-only policy as a complete HTTP parser.''',
'pub fn body_status(declared: Option<usize>, actual: usize, maximum: usize) -> u16',
'''if actual>maximum || declared.is_some_and(|n| n>maximum) { 413 } else if declared.is_some_and(|n| n!=actual) { 400 } else { 200 }''',
[('solution::body_status(Some(5),5,10)','200'),('solution::body_status(Some(0),0,0)','200'),('solution::body_status(Some(20),0,10)','413'),('solution::body_status(Some(5),4,10)','400'),('solution::body_status(None,11,10)','413'),('solution::body_status(None,5,10)','200')],
'Return 413 if declared or actual bytes exceed maximum; otherwise 400 for a present mismatching length; otherwise 200.',
'Can a small declared length replace a limit on actual bytes?', ['No, actual bytes also need a bound','Yes, clients always report an accurate size','Only decoded character count matters'],
'Clients can lie or disconnect mid-body, so declared size alone is insufficient.',
'Use curl -i -H "Content-Type: application/json" -d @request.json http://127.0.0.1:8080/tasks and compare a rejected oversized title with a valid request.',HTTP,mutant='200')
lab(2,'route-http-json','Encode a Valid JSON Boundary','Escape JSON strings without corrupting Unicode','Escape control characters, quotes and backslashes while preserving Unicode data.',
'''JSON is a wire format, not arbitrary quoted text. A title containing a quote or newline must remain one string value. Direct interpolation can terminate a string or create a response that no client can decode. Escape the JSON control set while retaining the original Unicode scalar values.

The exercise builds one JSON string value, including its surrounding quotes. It is deliberately small enough to inspect; the desktop service should use Serde instead of maintaining a general JSON implementation. Do not treat this function as a parser, canonical JSON signer or complete serializer. HTTP response byte lengths must be computed from encoded UTF-8 bytes after serialization, not from character count. The local adapter recalculates Content-Length and closes each connection so an edited response cannot smuggle a second framed response.''',
'pub fn json_string(value: &str) -> String',
r'''let mut out=String::from("\"");
for c in value.chars() {
    match c {
        '"'=>out.push_str("\\\""), '\\'=>out.push_str("\\\\"),
        '\n'=>out.push_str("\\n"), '\r'=>out.push_str("\\r"), '\t'=>out.push_str("\\t"),
        c if c<' '=>out.push_str(&format!("\\u{:04x}",c as u32)), c=>out.push(c)
    }
}
out.push('"'); out''',
[('solution::json_string("hi")','"\\\"hi\\\""'),('solution::json_string("")','"\\\"\\\""'),('solution::json_string("a\\\"b")','"\\\"a\\\\\\\"b\\\""'),('solution::json_string("a\nb")','"\\\"a\\\\nb\\\""'),('solution::json_string("🦀")','"\\\"🦀\\\""')],
'Return a quoted JSON string; escape quote, backslash, newline, carriage return and tab, encode remaining controls below U+0020 as lowercase four-digit \\u escapes, and retain other Unicode scalars.',
'Which response length belongs in Content-Length?', ['The serialized body byte length','The number of Rust char values','The unescaped input title length'],
'Escaping and UTF-8 encoding can both change byte length.',
'Inspect curl -i output for a title containing quotes. Compare the response Content-Length with its encoded body.',HTTP,mutant='format!("\\\"{value}\\\"")')
lab(2,'route-http-idempotency','Retry Without Duplicating Tasks','Bind an idempotency key to one request payload','Reuse a stored result only when the key and original payload agree.',
'''A timeout does not prove that the server performed no work. It can commit a task and lose the response. An unconditional retry then creates a duplicate. Store a stable request key with the original payload and result; on a repeated request, compare the payload before reusing that result.

This lab models the decision without claiming an in-memory map is durable. A new key creates once, the same key and payload replays, and the same key with a different payload conflicts. Missing or blank keys are invalid. Production storage must enforce the key uniqueness and the business write in one transaction. Set an explicit retention policy; expiring a key changes how late retries behave. The SQL and capstone stages demonstrate that the deduplication record belongs beside the committed task.''',
'pub fn retry_decision(key: &str, payload: &str, previous: Option<(&str,&str)>) -> u16',
'''if key.trim().is_empty() {400} else {match previous {Some((old_key,old_payload)) if old_key==key => if old_payload==payload {200}else{409}, _=>201}}''',
[('solution::retry_decision("k","title",None)','201'),('solution::retry_decision("","title",None)','400'),('solution::retry_decision("k","title",Some(("k","title")))','200'),('solution::retry_decision("k","other",Some(("k","title")))','409'),('solution::retry_decision("new","x",Some(("old","x")))','201')],
'Return 400 for a blank key; 200 for the same stored key and payload; 409 for the same key with another payload; 201 for a new key.',
'A repeated key arrives with different content. What should happen?', ['Reject the conflict','Return a successful response for the unrelated original request','Always create another task'],
'An idempotency key identifies the original operation, not permission to change its payload.',
'Create one task twice with curl using the same Idempotency-Key header, then change the title while retaining the key.',HTTP,mutant='201')

SQL_HELPER=r'''
fn quote(s: &str) -> String {
    let mut out=String::from("\"");
    for c in s.chars() { match c { '"'=>out.push_str("\\\""), '\\'=>out.push_str("\\\\"), '\n'=>out.push_str("\\n"), '\r'=>out.push_str("\\r"), '\t'=>out.push_str("\\t"), c if c<' '=>out.push_str(&format!("\\u{:04x}",c as u32)), c=>out.push(c) } }
    out.push('"'); out
}
fn db(sql: &str, params: &[&str], readonly: bool) -> String {
    let request=format!("{{\"sql\":{},\"params\":[{}],\"readOnly\":{}}}",quote(sql),params.iter().map(|s|quote(s)).collect::<Vec<_>>().join(","),readonly);
    #[cfg(target_arch="wasm32")]
    {
        #[link(wasm_import_module="crabrix_sql")]
        unsafe extern "C" { #[link_name="crabrix_sql_query"] fn crabrix_sql_query(p:*const u8,n:usize,out:*mut u8,cap:usize)->i32; }
        let mut out=vec![0u8;65536];
        let size=unsafe { crabrix_sql_query(request.as_ptr(),request.len(),out.as_mut_ptr(),out.len()) };
        assert!(size>=0 && (size as usize)<=out.len(),"bounded SQL bridge failed");
        out.truncate(size as usize); String::from_utf8(out).unwrap()
    }
    #[cfg(not(target_arch="wasm32"))]
    {
        let output=std::process::Command::new("python3").arg(std::env::var("ROUTE_SQL_RUNNER").unwrap()).arg(request).output().unwrap();
        assert!(output.status.success());String::from_utf8(output.stdout).unwrap().trim().to_owned()
    }
}
fn ok(sql:&str) { let result=db(sql,&[],false); assert!(!result.contains("\"error\""),"SQL operation failed: {result}"); }
fn rejects(sql:&str) { assert!(db(sql,&[],false).contains("\"error\""),"invalid write was accepted"); }
fn same(sql:&str,params:&[&str],oracle:&str) { assert_eq!(db(sql,params,true),db(oracle,&[],true),"query result differs from independent fixture"); }
'''
def sql_lab(id,title,concept,rule,explanation,signature,body,harness,cases,task,question,answers,feedback,commands):
 starter=signature+' {\n    todo!("implement the contract")\n}\n';solution=signature+' {\n'+body+'\n}\n'
 example=solution+'\nfn main() { println!("{}",'+signature.split('pub fn ')[1].split('(')[0]+'('+('10' if 'amount:' in signature else '')+')); }\n'
 add(3,id,title,concept,rule,explanation,starter,solution,'mod solution;\n'+SQL_HELPER+'\nfn main() {\n'+harness+'\nprintln!("PASS '+id+'");\n}\n',example,cases,task,question,answers,feedback,commands,'https://www.sqlite.org/lang.html','sqlite-v1',signature+' { '+{
 'route-sql-schema': '\"CREATE TABLE tasks(id INTEGER PRIMARY KEY,title TEXT,done INTEGER DEFAULT 0)\"',
 'route-sql-query': '\"SELECT t.id,t.title,p.name FROM tasks t JOIN projects p ON p.id=t.project_id ORDER BY p.name,t.id\"',
 'route-sql-parameters': '\"SELECT id FROM tasks WHERE title LIKE ?1 ORDER BY id\"',
 'route-sql-transactions': 'format!(\"UPDATE accounts SET balance=balance+{amount} WHERE id=2; UPDATE accounts SET balance=balance-{amount} WHERE id=1;\")'
 }[id]+' }\n' )
sql_lab('route-sql-schema','Make Invalid Rows Impossible','Enforce domain invariants in a real database','Validate in Rust for helpful errors and in SQL for every writer.',
'''Task Ledger must not accept empty titles just because a caller bypasses the API. A database schema is an independent enforcement boundary. Give each task an integer primary key, require a title whose trimmed length is between 1 and 80, and constrain done to exactly 0 or 1 with a default of 0.

A CHECK returning null can behave differently from a false expression; NOT NULL remains a separate requirement. A default applies when a column is omitted, not when a caller explicitly sends null. SQLite trim without a second argument removes ordinary spaces, rather than Rust's full Unicode whitespace set. Store canonical titles and keep that policy explicit. Migration history belongs in version control. Once a production schema exists, changing CREATE TABLE text does not update an existing database: write and test a migration. This lab starts from a fresh SQLite database and executes your DDL, then tries valid, null, empty, duplicate and out-of-domain writes. It does not merely compare the SQL text.''',
'pub fn schema() -> &\'static str',
'''"CREATE TABLE tasks(id INTEGER PRIMARY KEY, title TEXT NOT NULL CHECK(length(trim(title)) BETWEEN 1 AND 80), done INTEGER NOT NULL DEFAULT 0 CHECK(done IN (0,1)));"''',
'''ok(solution::schema());
ok("INSERT INTO tasks(id,title) VALUES(1,'learn SQL');");
same("SELECT id,title,done FROM tasks",&[],"SELECT 1 AS id,'learn SQL' AS title,0 AS done");
for invalid in ["INSERT INTO tasks VALUES(2,'',0)","INSERT INTO tasks VALUES(2,'   ',0)","INSERT INTO tasks VALUES(2,NULL,0)","INSERT INTO tasks VALUES(2,'x',NULL)","INSERT INTO tasks VALUES(2,'x',2)","INSERT INTO tasks VALUES(1,'duplicate',0)"] {rejects(invalid);}
rejects(&format!("INSERT INTO tasks VALUES(2,'{}',0)","x".repeat(81)));
ok("INSERT INTO tasks VALUES(2,'valid',1)");''',
[('create tasks schema','valid task inserts'),('blank/null title','rejected by SQLite'),('duplicate primary key','rejected by SQLite'),('done=2','rejected by SQLite')],
'Return DDL creating tasks(id INTEGER PRIMARY KEY,title TEXT NOT NULL,done INTEGER NOT NULL DEFAULT 0). Enforce a trimmed title length of 1..=80 and done IN (0,1) using SQL constraints.',
'Why keep SQL constraints when the Rust handler already validates titles?', ['Other writers and future bugs can bypass the handler','A Rust validation function automatically changes the database schema','Defaults reject every explicit null'],
'The database must protect its own invariant independently of one application entry point.',
'Run sqlite3 tasks.db .read migrations/001.sql, then attempt valid and invalid INSERT statements. The compiler lab executes your DDL against fresh real SQLite.')
sql_lab('route-sql-query','Query the Right Rows in a Stable Order','Filter, join and order by the intended relationship','Specify both the inclusion rule and deterministic ordering.',
'''A task report joins tasks to projects and lists unfinished tasks in active projects. Joining by a coincidentally equal name or forgetting the done filter may pass a tiny happy-path fixture. Seed unrelated, archived and completed records so each predicate has observable consequences.

SQL does not promise result ordering without ORDER BY. Sort by project name and then task ID to break ties. A LEFT JOIN and an INNER JOIN have different contracts: this report includes only tasks with an existing active project. The task title does not participate in grouping or identity. Inspect the query plan after establishing correctness, then consider an index on the actual filter/join keys. An index is not permission to change which rows appear. The independent checker rebuilds fixtures and executes your query, allowing different correct SQL formulations.''',
'pub fn report_sql() -> &\'static str',
'''"SELECT t.id,t.title,p.name FROM tasks t JOIN projects p ON p.id=t.project_id WHERE t.done=0 AND p.active=1 ORDER BY p.name,t.id"''',
'''ok("CREATE TABLE projects(id INTEGER PRIMARY KEY,name TEXT,active INTEGER); CREATE TABLE tasks(id INTEGER PRIMARY KEY,title TEXT,done INTEGER,project_id INTEGER);");
let oracle="SELECT tasks.id,tasks.title,projects.name FROM projects INNER JOIN tasks ON tasks.project_id=projects.id WHERE projects.active=1 AND tasks.done=0 ORDER BY projects.name ASC,tasks.id ASC";
same(solution::report_sql(),&[],oracle);
ok("INSERT INTO projects VALUES(1,'Z',1),(2,'A',1),(3,'hidden',0); INSERT INTO tasks VALUES(9,'nine',0,1),(7,'seven',0,2),(2,'two',0,2),(3,'done',1,2),(4,'archived',0,3),(5,'orphan',0,99);");
same(solution::report_sql(),&[],oracle);
ok("UPDATE projects SET active=0 WHERE id=2;");same(solution::report_sql(),&[],oracle);''',
[('empty tables','empty report'),('unfinished active tasks','included and ordered'),('done/archived/orphan tasks','excluded'),('project becomes inactive','rows disappear')],
'Return a read-only query producing columns id,title,name for unfinished tasks in active projects. Tables are tasks(id,title,done,project_id) and projects(id,name,active); join on project_id=id, order by project name then task ID.',
'What guarantees stable order when project names tie?', ['ORDER BY project name and task ID','The storage order of inserted rows','The presence of any index'],
'Neither insertion order nor a query plan is a contract for row ordering.',
'Run sqlite3 tasks.db .read reports/pending.sql; compare the output after completing a task and archiving its project.')
sql_lab('route-sql-parameters','Bind Values Instead of SQL Syntax','Keep untrusted text in a parameter slot','A title is data even when it contains quotes or SQL-looking text.',
'''A title can contain an apostrophe or text that resembles SQL. Concatenating it into a WHERE clause turns data into syntax and makes quoting rules part of the security boundary. Bind the title into a placeholder instead; the database receives the statement structure separately from the value.

The local bridge accepts JSON with sql and params fields. The desktop SQLx profile uses its own bind API; placeholders differ across drivers, so SQLite ?1 is not PostgreSQL $1. This lesson grades a read-only SQLite query with exactly one positional title parameter. Fixtures include an apostrophe, Unicode, and an injection-shaped title that must match only itself. LIKE is a different search contract and should not replace exact equality. Parameterization does not grant access control: the application must still decide which caller is allowed to read a project.''',
'pub fn title_sql() -> &\'static str',
'''"SELECT id FROM tasks WHERE title=?1 ORDER BY id"''',
'''ok("CREATE TABLE tasks(id INTEGER PRIMARY KEY,title TEXT); INSERT INTO tasks VALUES(1,'plain'),(2,'Ada''s task'),(3,'🦀'),(4,'plain'),(5,'x'' OR 1=1 --'),(6,'%'),(7,'anything');");
for (title,oracle) in [("plain","SELECT id FROM tasks WHERE id IN (1,4) ORDER BY id"),("Ada's task","SELECT 2 AS id"),("🦀","SELECT 3 AS id"),("x' OR 1=1 --","SELECT 5 AS id"),("missing","SELECT id FROM tasks WHERE 0"),("%","SELECT 6 AS id")]{same(solution::title_sql(),&[title],oracle);}''',
[('plain title','all exact matches'),('apostrophe in title','preserved as data'),('injection-shaped title','only that title matches'),('missing title','no rows')],
'Return a read-only query selecting task IDs with title exactly equal to parameter ?1, ordered by id. Table tasks has id and title columns; do not interpolate a title into SQL.',
'Does binding a title give it permission to become a SQL clause?', ['No, it stays a value','Yes, a quote in the value closes the SQL string','Parameters replace the authorization policy'],
'A parameter cannot change statement structure; authorization remains a separate application decision.',
'Inspect the companion db::query call: the title travels in params, while SQL remains unchanged. Use a title containing an apostrophe in the HTTP request.')
sql_lab('route-sql-transactions','Commit Related Changes Atomically','Roll back a failed multi-write operation','All related writes belong to one transaction with an observable failure path.',
'''A transfer debits one account and credits another. If the debit succeeds while the credit fails, the database has lost value. Enclose both writes in one explicit transaction. Constrain balances to remain nonnegative and make a rejected debit fail before any durable credit occurs.

The exercise transfers an integer amount from account 1 to account 2. A zero transfer leaves balances unchanged. A transfer larger than the source balance triggers the database CHECK and must leave both accounts unchanged. The local SQL host rolls back any open transaction when a statement fails, and refuses a script that ends with an open transaction. SQLx on desktop normally uses a transaction value with explicit commit and rollback behavior. Concurrency isolation, lock timeouts and retry policy need separate tests; this single-connection lab proves only the finite atomicity cases it executes.''',
'pub fn transfer_sql(amount: u32) -> String',
'''format!("BEGIN IMMEDIATE; UPDATE accounts SET balance=balance-{amount} WHERE id=1; UPDATE accounts SET balance=balance+{amount} WHERE id=2; COMMIT;")''',
'''ok("CREATE TABLE accounts(id INTEGER PRIMARY KEY,balance INTEGER NOT NULL CHECK(balance>=0)); INSERT INTO accounts VALUES(1,100),(2,20);");
ok(&solution::transfer_sql(30));same("SELECT id,balance FROM accounts ORDER BY id",&[],"SELECT 1 AS id,70 AS balance UNION ALL SELECT 2,50");
rejects(&solution::transfer_sql(71));same("SELECT id,balance FROM accounts ORDER BY id",&[],"SELECT 1 AS id,70 AS balance UNION ALL SELECT 2,50");
ok(&solution::transfer_sql(0));same("SELECT sum(balance) AS total FROM accounts",&[],"SELECT 120 AS total");
ok(&solution::transfer_sql(70));same("SELECT id,balance FROM accounts ORDER BY id",&[],"SELECT 1 AS id,0 AS balance UNION ALL SELECT 2,120");''',
[('transfer 30 from 100/20','70/50'),('transfer exceeds balance','rejected with balances unchanged'),('transfer zero','no balance change'),('transfer entire balance','0/120')],
'Return a complete BEGIN..COMMIT SQLite script transferring amount from account 1 to 2. accounts(id,balance) enforces balance>=0. Debit and credit must be atomic, including overdraw failure. Amount is a trusted u32 numeric value.',
'What should remain after a rejected overdraw?', ['Both original balances','The debit only','The credit only'],
'Atomicity means the failed transfer cannot leave one half committed.',
'Run sqlite3 ledger.db .read migrations/accounts.sql. Execute a valid BEGIN..COMMIT transfer and an overdraw script, then SELECT both balances.')

DIAG='https://docs.rs/tracing/latest/tracing/'
lab(4,'route-diag-context','Add Context Without Leaking Secrets','Redact sensitive diagnostic fields','An error should identify the operation without copying credentials into logs.',
'''A bare connection failed message loses the operation and request that failed. Add bounded structured context: operation name, request ID and a stable error category. Keep secret fields out of the event. Redacting only one capitalization of Authorization is insufficient when headers are case insensitive.

This lab preserves field order while replacing authorization, cookie, password, token and api_key values with [REDACTED], case insensitively. It does not claim that this small allowlist finds every possible secret in free text. Production code should prefer explicitly selected safe fields and never dump arbitrary request bodies or connection URLs. Diagnostic context is useful only when a person can connect it to a specific operation; a giant unstructured debug print can be harder to use than a short event with a correlation ID.''',
'pub fn safe_fields(fields: &[(&str,&str)]) -> Vec<(String,String)>',
'''fields.iter().map(|(k,v)| { let sensitive=["authorization","cookie","password","token","api_key"].contains(&k.to_ascii_lowercase().as_str()); (k.to_string(),if sensitive {"[REDACTED]".to_owned()}else{v.to_string()}) }).collect()''',
[('solution::safe_fields(&[("Authorization","bearer x"),("request_id","r1")])','vec![("Authorization".to_owned(),"[REDACTED]".to_owned()),("request_id".to_owned(),"r1".to_owned())]'),('solution::safe_fields(&[])','vec![]'),('solution::safe_fields(&[("TOKEN","x"),("api_key","y")])','vec![("TOKEN".to_owned(),"[REDACTED]".to_owned()),("api_key".to_owned(),"[REDACTED]".to_owned())]'),('solution::safe_fields(&[("operation","list")])','vec![("operation".to_owned(),"list".to_owned())]')],
'Retain field names and order; replace values for authorization,cookie,password,token,api_key with [REDACTED] using ASCII-case-insensitive key matching. Other values stay unchanged.',
'Which event is useful and safer for a failed request?', ['Operation and request ID with explicitly redacted secret fields','Every raw header and the complete body','A password is safe in logs if the request failed'],
'Failure does not make credentials safe to copy into a persistent diagnostic record.',
'Run the companion error case and inspect its request ID and operation context. Keep Authorization out of retained terminal command examples.',DIAG,mutant='fields.iter().map(|(k,v)|(k.to_string(),v.to_string())).collect()')
lab(4,'route-diag-correlation','Propagate One Request Identity','Validate a bounded correlation ID','Use the same validated ID across a request and its child operations.',
'''Async work interleaves. Two requests can emit similar messages on one thread, so thread identity alone does not connect the messages that belong together. Give an operation one request ID, propagate it through database calls and retries, and record child work under the same parent context.

An incoming ID is untrusted data. Accept only a bounded ASCII token here, using letters, digits, dash and underscore; otherwise use a generated fallback supplied by the caller. Reject line breaks so an identifier cannot inject a fake log record. Do not treat a correlation ID as authentication or an idempotency key. Clients can choose or repeat it, and tracing systems have their own full trace-context format. This exercise isolates a small application request-ID policy rather than pretending to implement W3C traceparent.''',
'pub fn request_id(incoming: Option<&str>, fallback: &str) -> String',
'''match incoming { Some(v) if !v.is_empty() && v.len()<=64 && v.bytes().all(|b|b.is_ascii_alphanumeric()||b==b'-'||b==b'_') => v.to_owned(), _=>fallback.to_owned() }''',
[('solution::request_id(Some("req_42-A"),"generated")','"req_42-A"'),('solution::request_id(None,"generated")','"generated"'),('solution::request_id(Some("evil\nrecord"),"new")','"new"'),('solution::request_id(Some("🦀"),"new")','"new"'),('solution::request_id(Some(&"a".repeat(65)),"new")','"new"'),('solution::request_id(Some(""),"new")','"new"')],
'Accept incoming IDs with 1..=64 bytes composed only of ASCII letters,digits,dash,underscore. Otherwise return the supplied fallback, which the caller guarantees is valid.',
'Does a client-supplied request ID authenticate the caller?', ['No, it is diagnostic context','Yes, a unique-looking string proves identity','It makes SQL authorization unnecessary'],
'Correlation identifies related events, not who is allowed to perform an operation.',
'Send curl -i -H "X-Request-ID: req_42" http://127.0.0.1:8080/health and follow the same ID through the diagnostic output.',DIAG,mutant='incoming.unwrap_or(fallback).to_owned()')
lab(4,'route-diag-latency','Measure the Tail, Not Just the Average','Compute an explicitly defined latency percentile','State the percentile convention and preserve the original measurements.',
'''Averages can hide slow requests. A service with many quick responses and a few multi-second waits may have an acceptable mean while some users regularly time out. Record a latency distribution and inspect tail behavior alongside throughput and error rate.

This exercise defines p95 using the nearest-rank rule: sort a copy of the positive or zero millisecond observations, choose rank ceil(0.95*n), and return that element. Return None for an empty sample. Do not mutate the caller's measurements or invent interpolated values. A percentile from a small sample has limited statistical precision; the exact calculation is not evidence that the load generator or measurement conditions were realistic. The desktop companion keeps raw samples, concurrency and toolchain identity with a before/after report.''',
'pub fn p95(samples: &[u64]) -> Option<u64>',
'''if samples.is_empty() { return None; } let mut sorted=samples.to_vec(); sorted.sort_unstable(); let n=sorted.len(); let rank=n-n/20; Some(sorted[rank-1])''',
[('solution::p95(&[1,2,3,100])','Some(100)'),('solution::p95(&[])','None'),('solution::p95(&[7])','Some(7)'),('solution::p95(&(1..=20).collect::<Vec<u64>>())','Some(19)'),('solution::p95(&[9,1,9,0])','Some(9)')],
'Return nearest-rank p95: sort a copy and choose rank ceil(0.95*n), using one-based ranks. Empty input returns None. Retain exact u64 observations.',
'Why can a good average coexist with a poor user experience?', ['Slow tail requests can be hidden by many fast ones','The average is always the slowest request','Percentiles eliminate the need for sample context'],
'A mean alone does not describe the slow tail or the measurement conditions.',
'Run python3 scripts/latency.py in the desktop companion, retain its raw samples and error count, then compare p95 before and after a change.',DIAG,mutant='samples.first().copied()')
lab(4,'route-diag-retries','Bound the Retry Budget','Retry transient failures within attempt and time limits','A retry needs a transient failure, remaining attempts and a deadline budget.',
'''Retries amplify load when a dependency is already failing. Decide whether an error is transient, cap total attempts, and stop when the proposed delay plus one minimum operation budget no longer fits the deadline. Retrying authentication failures or malformed input does not repair them.

Here failed_attempts counts attempts already made, including the one that just failed. Retry only transient failures after at least one attempt, while the count is below the total maximum. Require delay + operation_budget to fit in remaining time, using checked arithmetic so an overflow cannot create a false large budget. Jitter and exponential delay selection are separate policies. Before retrying a write, use the idempotency contract from the HTTP stage; a timing budget does not prevent duplicated effects.''',
'pub fn retry(transient: bool, failed_attempts: u32, maximum: u32, delay: u64, operation_budget: u64, remaining: u64) -> bool',
'''transient && failed_attempts>0 && failed_attempts<maximum && delay.checked_add(operation_budget).is_some_and(|cost|cost<=remaining)''',
[('solution::retry(true,1,3,10,20,30)','true'),('solution::retry(true,0,3,0,0,0)','false'),('solution::retry(false,1,3,0,0,100)','false'),('solution::retry(true,3,3,0,0,100)','false'),('solution::retry(true,1,3,u64::MAX,1,u64::MAX)','false'),('solution::retry(true,1,3,10,20,29)','false')],
'Return true only for a transient failure with 1<=failed_attempts<maximum and checked delay+operation_budget<=remaining. Overflow refuses the retry.',
'What else is needed before retrying a possibly committed write?', ['An idempotency policy','Only a longer timeout','Always retry forever until success'],
'Timeouts and budgets do not prove the previous attempt had no external effect.',
'Run python3 scripts/retry_probe.py against the desktop readiness endpoint. Stop the service and repeat; inspect the bounded attempt count and request ID. This probe retries an idempotent client GET, rather than automatically retrying service writes.',DIAG,mutant='transient')

DELIVERY='https://doc.rust-lang.org/cargo/commands/cargo-test.html'
lab(5,'route-delivery-gates','Make Checks Block Delivery','Require all declared release checks','An absent or failed required check cannot be treated as a green release.',
'''A reproducible release pipeline connects source checks to a specific revision. Formatting, compilation and tests answer different questions. A successful build does not establish that tests ran, and a test job from an older revision does not approve newer source.

The release policy requires fmt, test and build exactly once with successful results; extra unrelated checks may be present. Duplicate required records are ambiguous and should refuse delivery rather than choosing whichever result looks better. This lab models gate aggregation, while the companion workflow runs the actual commands in a clean checkout with Cargo.lock retained. The iOS terminal runs its supported Cargo profile; the desktop CI workflow exercises the server target, SQL migrations and integration requests. Keep those receipts separate instead of claiming one target qualifies the other.''',
'pub fn release_ready(checks: &[(&str,bool)]) -> bool',
'''["fmt","test","build"].iter().all(|required| { let rows:Vec<_>=checks.iter().filter(|(name,_)|name==required).collect(); rows.len()==1 && rows[0].1 })''',
[('solution::release_ready(&[("fmt",true),("test",true),("build",true)])','true'),('solution::release_ready(&[])','false'),('solution::release_ready(&[("fmt",true),("test",false),("build",true)])','false'),('solution::release_ready(&[("fmt",true),("test",true),("build",true),("test",true)])','false'),('solution::release_ready(&[("fmt",true),("test",true),("build",true),("docs",false)])','true')],
'Require exactly one successful result for each of fmt,test,build. Missing, failed or duplicate required results refuse release; unrelated checks do not affect this contract.',
'Does a successful build prove that the test job ran?', ['No, it is a separate required observation','Yes, building automatically runs every test','A missing check should default to success'],
'Compilation success and independently executed tests provide different evidence.',
'Run cargo fmt --check, cargo test and cargo build. Inspect the companion GitHub workflow for desktop integration checks.',DELIVERY,mutant='checks.iter().all(|(_,passed)|*passed)')
lab(5,'route-delivery-config','Validate Before Starting the Service','Reject invalid deployment configuration','A deployment configuration must fail before the service accepts traffic.',
'''A service can compile correctly and still fail because its deployment configuration is wrong. Parse the bind port, database address and operational limits before opening a listener. Report the failed field without echoing a password-bearing connection URL.

This lab accepts decimal ports from 1024 to 65535 and a nonempty database setting containing no whitespace. It rejects signed port syntax, surrounding whitespace and malformed numbers so accepted configuration is predictable. The database check here is intentionally syntactic; it does not prove connectivity, credentials or migration compatibility. The desktop service should perform those separate startup checks and expose readiness only after required initialization. A liveness endpoint and a readiness endpoint answer different operational questions.''',
'pub fn config(port: &str, database: &str) -> Result<u16,&\'static str>',
'''if port.is_empty() || !port.bytes().all(|b|b.is_ascii_digit()) {return Err("port");}
let n=port.parse::<u16>().map_err(|_|"port")?; if n<1024 {return Err("port");}
if database.is_empty() || database.chars().any(char::is_whitespace) {return Err("database");} Ok(n)''',
[('solution::config("8080","tasks.db")','Ok(8080)'),('solution::config("0","tasks.db")','Err("port")'),('solution::config("65536","tasks.db")','Err("port")'),('solution::config("+8080","tasks.db")','Err("port")'),('solution::config("8080","")','Err("database")'),('solution::config("8080","bad path")','Err("database")'),('solution::config("65535","db")','Ok(65535)')],
'Accept an ASCII-digit decimal port in 1024..=65535 and a nonempty database string without whitespace. Return port for port errors and database for database errors; validate the port first.',
'What does accepting a database configuration string prove?', ['Only the declared syntactic policy','That credentials and migrations work','That every future request will succeed'],
'Configuration parsing, connectivity and readiness are separate checks.',
'Start cargo serve --port 8080 --database tasks.db. Refuse an invalid port, then check /health after successful startup.',DELIVERY,mutant='Ok(8080)')
lab(5,'route-delivery-artifacts','Bind an Artifact to Its Source','Verify release identity and digest metadata','A filename or version label does not prove which bytes were tested.',
'''A release artifact should have an identity that can be compared with the tested source and the expected content digest. Reusing a mutable latest filename makes rollback and incident investigation harder. Retain the source revision, exact target, digest and verification receipt beside immutable artifact bytes.

The lab validates metadata: a full lowercase 40-hex Git object ID, a lowercase 64-hex SHA-256 digest and an exact match with an independently supplied expected digest. It does not calculate SHA-256 or prove the claim by validating string shape. The actual delivery script computes the digest from built bytes with a standard tool, then compares it before promotion. A digest detects changed bytes when the expected digest is trusted; it is not an author signature. Keep signing and provenance decisions explicit rather than calling a checksum an authenticity guarantee.''',
'pub fn artifact_matches(commit: &str, digest: &str, expected: &str) -> bool',
'''let hex=|s:&str,n:usize|s.len()==n && s.bytes().all(|b|b.is_ascii_digit()||(b'a'..=b'f').contains(&b)); hex(commit,40)&&hex(digest,64)&&hex(expected,64)&&digest==expected''',
[('solution::artifact_matches(&"a".repeat(40),&"b".repeat(64),&"b".repeat(64))','true'),('solution::artifact_matches("main",&"b".repeat(64),&"b".repeat(64))','false'),('solution::artifact_matches(&"a".repeat(40),&"b".repeat(64),&"c".repeat(64))','false'),('solution::artifact_matches(&"A".repeat(40),&"b".repeat(64),&"b".repeat(64))','false'),('solution::artifact_matches(&"a".repeat(40),"","")','false')],
'Validate lowercase hexadecimal commit(40) and digest/expected(64), then require digest==expected. This checks metadata only; actual digest computation belongs to the supplied build-byte verification step.',
'Does a well-formed SHA-256 string prove the artifact bytes match?', ['No, compute and compare the actual bytes against a trusted expected digest','Yes, every 64-character value proves integrity','A checksum automatically identifies the publisher'],
'String shape, byte integrity and publisher authenticity are different properties.',
'Run the desktop delivery script, inspect its source revision and computed artifact SHA-256, then modify an artifact copy and observe verification fail.',DELIVERY,mutant='digest==expected')
lab(5,'route-delivery-rollback','Release, Observe and Recover','Keep a known-good version until the candidate is healthy','A failed readiness check preserves the previous active version.',
'''Delivery continues after uploading bytes. A candidate can build successfully and fail a migration or readiness check in the target environment. Retain the previous active version while preparing the candidate, promote only after the required health evidence, and preserve a concrete recovery path.

The state transition in this lab receives the current version, candidate and readiness observations. Reject a blank candidate, an unchanged version or a candidate without successful required checks. On every rejection return the original active version; a partially configured candidate is not an active release. A real database migration may be irreversible, so reverting an executable is not automatically a schema rollback. Prefer compatible expand/contract changes and test recovery against actual persistent state. The capstone asks for an incident record showing the failing condition, observed data and successful recovery rather than a screenshot of a green pipeline.''',
'pub fn promote(current: &str, candidate: &str, checks_ok: bool, ready: bool) -> (String,bool)',
'''if !candidate.trim().is_empty() && candidate!=current && checks_ok && ready {(candidate.to_owned(),true)}else{(current.to_owned(),false)}''',
[('solution::promote("v1","v2",true,true)','("v2".to_owned(),true)'),('solution::promote("v1","",true,true)','("v1".to_owned(),false)'),('solution::promote("v1","v2",true,false)','("v1".to_owned(),false)'),('solution::promote("v1","v2",false,true)','("v1".to_owned(),false)'),('solution::promote("v1","v1",true,true)','("v1".to_owned(),false)')],
'Return candidate,true only for a nonblank changed candidate with checks_ok and ready both true. Every refused promotion returns current,false unchanged.',
'A candidate fails readiness. Which version remains active?', ['The previous known-good version','The failed candidate because it uploaded successfully','No version; delete the previous artifact first'],
'Upload or build success is insufficient to replace an active service.',
'Run the capstone acceptance checks, introduce a failed readiness condition, retain the old version, and document the recovery.',DELIVERY,mutant='(candidate.to_owned(),true)')

for unit,(uid,title,subtitle) in enumerate(UNITS):
 ids=[x['id'] for x in LABS if x['unit']==unit]
 assert len(ids)==4
 save(C/'units'/f'{uid}.json',{'id':uid,'parentID':'projects','order':7+unit,'level':8+unit,'title':title,'subtitle':subtitle,'lessonIDs':ids})
 if uid not in course['unitIDs']:course['unitIDs'].append(uid)
for i,record in enumerate(LABS):
 path=C/'lessons'/f'{record["id"]}.json';item=read(path)
 for offset,direction in [(-1,'previous'),(1,'next')]:
  if 0<=i+offset<len(LABS):
   neighbor=read(C/'lessons'/f'{LABS[i+offset]["id"]}.json');item['depth']['connections'].append({'direction':direction,'title':neighbor['title'],'concept':neighbor['concept']})
 save(path,item)
course.update(contentVersion='1.1.0',minimumAppVersion='1.1.8',requiredCapabilities=['workflow-terminal-v1'],subtitle='Cargo, library contracts, and the Git → CLI → HTTP → SQL → delivery route')
save(C/'course.json',course)
provenance=read(C/'provenance.json');provenance.update(contentVersion='1.1.0',editorialRevision='workflow_route_20261107');save(C/'provenance.json',provenance)
save(HERE/'lab-contracts.json',LABS)
print('Authored',len(LABS),'lessons in',len(UNITS),'units')

# The public companion is source/data only. Private solution checks remain editorial.
import shutil
companion=HERE/'companion'
first=C/'projects/route-git-review/companion'
for source in companion.rglob('*'):
 if source.is_file() and not any(part in {'target','__pycache__','.DS_Store'} for part in source.relative_to(companion).parts):
  relative=source.relative_to(companion)
  if relative.parts[0]=='local':relative=Path(*relative.parts[1:])
  target=first/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
for record in LABS:
 save(C/'projects'/record['id']/'workflow-companion.json',{'lessonID':'route-git-review','name':'task-ledger','entryFile':'src/main.rs'})
 lesson_path=C/'lessons'/f"{record['id']}.json";item=read(lesson_path)
 item['resources'].append({'title':'Task Ledger companion source (ZIP)','url':'https://crabrix.com/examples/task-ledger-route.zip'})
 save(lesson_path,item)
