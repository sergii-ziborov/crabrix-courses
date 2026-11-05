#!/usr/bin/env python3
"""Qualified Cargo starters for the released app and browser WASI compiler."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent

def apply():
    for fixture in json.loads((BASE / 'portable-cargo-labs.json').read_text()):
        course, lid = fixture['course'], fixture['name']
        path = ROOT / 'courses' / course / 'lessons' / (lid + '.json')
        item = json.loads(path.read_text())
        item['exerciseKind'] = 'runnable'
        writing = item['writing']
        source = fixture['document']['files']['src/main.rs']
        writing['exampleCode'] = source
        writing['practiceCode'] = source
        paragraphs = writing['explanation'].split('\n\n')
        paragraphs = [p for p in paragraphs if not p.startswith(('Desktop Cargo profile:', 'Execution profile:', 'Local Cargo profile:', 'The visitor checks duplicate,'))]
        profile = ('Local Cargo profile: open the supplied project in Crabrix or the browser Playground. Explicitly prepare its pinned Cargo packages once on each device, then Run and Debug compile and execute on that device without a backend. The project includes Cargo.lock. The lesson question remains the completion exercise; running an unchanged demonstration does not prove a separate programming challenge.')
        if course == 'projects':
            paragraphs = [p.replace('By default, unknown struct fields are ignored; `deny_unknown_fields` rejects them.', 'Serde derive normally ignores unknown fields unless configured with `deny_unknown_fields`. This explicit visitor rejects unknown and duplicate fields itself.') for p in paragraphs]
            profile += ' This starter uses real serde 1.0.229 and serde_json 1.0.151 with explicit Serialize and Deserialize implementations. That keeps the typed round-trip, strict field policy and domain validation portable without a procedural macro. Derive can generate the same traits on a toolchain with qualified macro support; this lab does not require the experimental macro compiler.'
            writing['exampleCaption'] = 'Real Serde traits: strict typed decoding, separate domain validation and a semantic JSON round-trip.'
            paragraphs.append('The visitor checks duplicate, missing and unknown fields while Serde checks each field type. A u32 rejects negative and overflowing counts. The separate decode function bounds input size and rejects blank names. Main asserts all of those failures as well as a Unicode round-trip; a successful JSON parse alone is not evidence of domain validity.')
        else:
            profile += ' Tokio 1.54.1 is built with default-features=false and only rt/sync. The current-thread builder needs no runtime attribute macro. JoinSet, Semaphore, watch and yield_now are real Tokio APIs. This profile supplies cooperative concurrency, not native threads, sockets, OS signals or CPU parallelism.'
        paragraphs.append(profile)
        writing['explanation'] = '\n\n'.join(paragraphs)
        item['depth']['transferChallenge'] = item['depth']['transferChallenge'].replace('a desktop timer or host support', 'timer or host support outside this rt/sync profile')
        writing['task'] = writing['task'].replace('On desktop Cargo,', 'In Crabrix or the web Playground,')
        writing['task'] += ' Open the supplied local Cargo project, prepare packages, then Run or Debug it. Change inputs and examine the assertions. Answer the lesson question separately.' if 'Open the supplied local Cargo project' not in writing['task'] else ''
        path.write_text(json.dumps(item, ensure_ascii=False, indent=2)+'\n')
        folder = ROOT/'courses'/course/'projects'/lid
        folder.mkdir(parents=True,exist_ok=True)
        (folder/'project.json').write_text(json.dumps({'name':lid+'-lab','entryFile':'src/main.rs'},indent=2)+'\n')
        for name,text in fixture['document']['files'].items():
            file=folder/name;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text)
    p=ROOT/'courses/projects/lessons/dependencies.json';item=json.loads(p.read_text());w=item['writing']
    w['exampleCode']=w['exampleCode'].replace('serde = { version = "1", features = ["derive"] }','serde = "=1.0.229"\nserde_json = "=1.0.151"')
    w['explanation']='\n\n'.join(p for p in w['explanation'].split('\n\n') if not p.startswith('Execution profile:'))+'\n\nExecution profile: the Serde: Decode, Validate, Encode lesson contains the qualified, pinned Cargo project for both the app and web Playground. It uses explicit Serde traits. Enabling derive adds a procedural macro dependency and needs separately qualified macro support; downloading serde alone does not provide that capability.'
    p.write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n')
    for cid,version in [('projects','1.0.10'),('concurrency','1.0.8')]:
        p=ROOT/'courses'/cid/'course.json';c=json.loads(p.read_text());c['contentVersion']=version;p.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__': apply()
