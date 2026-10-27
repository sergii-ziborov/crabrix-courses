#!/usr/bin/env python3
"""Write revised Atlas readings/checks from verified examples and teaching notes.

This edits authoring data only. Signing and publication are separate steps.
Lesson IDs, order, project names and correct-answer positions are retained.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from functools import lru_cache

from fixtures import call,r
from oracles import solve
from teaching import FACTS
from verify_examples import inputs,source

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]/'courses/algorithms'

@lru_cache(None)
def before(path):
    relative=path.relative_to(BASE.parents[1]).as_posix()
    return json.loads(subprocess.check_output(['git','-C',str(BASE.parents[1]),'show','52b6751:'+relative],text=True))

CONTRACT={
 'complement-lookup':'Return zero-based indexes i,j of any two distinct positions whose values sum to target. Return -1,-1 if no pair exists; either order of a valid pair is accepted.',
 'sorted-two-sum':'For sorted values, return one-based indexes of any two distinct positions summing to 17. Return -1,-1 if no pair exists.',
 'list-intersection':'Parse a_prefix, b_prefix and shared integer arrays. Build separate prefix nodes and attach both to the same shared tail. Return the first shared node value, or none when shared is empty. Equal values in separate prefixes do not identify shared nodes.',
 'reservoir-sampling':'Parse equally sized values and choices arrays. At zero-based index i, choices[i] is in 0..=i; replace the one-item reservoir exactly when choices[i] == i. Return the selected value, or none for empty arrays.',
 'monotonic-decreasing-stack':'Return the stock span for every day: the length of the consecutive block ending today whose earlier prices are no greater than today. Include today itself.',
 'imos-sweep':'Parse n and inclusive (start,end,delta) updates with nonnegative loads. Return the maximum simultaneous load over indexes 0..n-1. Add at start and subtract at end+1.',
 'binary-search-answer':'Parse positive weights and a positive days limit. Preserve input order and return the minimum daily capacity that ships all weights in at most that many days.',
 'memoization':'Parse n and return Fibonacci F(n), with F(0)=0 and F(1)=1. Teaching fixtures use n<=90 so all demonstrated u64 arithmetic fits.',
 'tabulation':'Parse n and return the number of ordered ways to climb n steps using moves of one or two. There is one empty route when n=0.',
 'matrix-exponentiation':'Parse n and return Fibonacci F(n), with F(0)=0 and F(1)=1; n<=90 in this u64 example.',
 'grid-path-dp':'Parse rows and cols. Count paths through that empty grid using right/down moves from the top-left cell to the bottom-right. A 1x1 grid has one path.',
 'permutations':'Return the number of permutations of all supplied distinct items, including one empty permutation for an empty list.',
 'gray-code':'Parse n and return n-bit binary-reflected Gray code order. For n=0 return the single code 0.',
 'n-queens':'Parse n and return the number of placements of n non-attacking queens on an n-by-n board. Count the empty placement once for n=0.',
 'miller-rabin':'Parse unsigned n and return whether it is prime. The Rust example uses deterministic unsigned-64-bit witnesses; zero and one are not prime.',
 'euclid-gcd':'Parse nonnegative a and b and return their greatest common divisor; gcd(a,0)=a and gcd(0,0)=0.',
 'sieve':'Parse n and return primes not exceeding n in ascending order, as comma-separated integers.',
 'binomial-coefficients':'Parse n and k and return n choose k. The multiplicative example bounds n<=60; return 0 when k>n.',
 'fast-power':'Parse base, exp and a positive mod; return base^exp modulo mod, including exp=0.',
 'modular-inverse':'Parse a and mod with mod>1 and gcd(a,mod)=1. Return the inverse normalized to 0..mod-1.',
 'digit-dp':'Parse bound and sum. Count integers from 0 through bound inclusive whose decimal digit sum is sum; zero has digit sum zero.',
 'rolling-fingerprint':'Parse digits in 0..9. Fold hash=(hash*10+digit)%101 from initial zero and return the final hash; leading zeros are allowed.',
 'bitmask-enumeration':'Parse values and return, in increasing order, every zero-based position mask whose selected values sum to 5.',
 'trie':'Parse words and prefix. Return how many listed words begin with that prefix, counting repeated listed words separately.',
 'aho-corasick':'Parse lowercase ASCII text and nonempty lowercase ASCII patterns. Count every pattern occurrence, including overlaps and simultaneous suffix matches.',
 'tree-rerooting':'Parse n and edges of a connected undirected tree on 0..n-1. Return the sum of distances from each vertex, in vertex order.',
 'centroid-decomposition':'Parse n and edges of a nonempty connected tree. Return its first centroid, choosing the smaller vertex index when two qualify.',
 'tree-height-balance':'Parse the compact level-order binary tree, where null omits a node. Return true exactly when every subtree has child heights differing by at most one.',
 'bst-search-insert':'Parse the level-order BST, insert 5 (equal keys go right), then return inorder values.',
 'lowest-common-ancestor':'Parse a binary tree with unique values containing both 5 and 1; return their lowest common ancestor value.',
 'tree-serialize':'Parse a compact level-order tree. Serialize preorder using comma separators and # for every missing child.',
 'sudoku':'row0 contains digits 1..9 with exactly one missing position written as a dot. Return that missing digit. The worked program demonstrates full-board backtracking on a valid 9x9 fixture; the challenge itself is this bounded row-completion case.',
 'peak-search':'Parse a nonempty array with unequal adjacent values. Return any strict peak index, treating outside endpoint values as negative infinity.',
 'priority-scheduling':'Parse unique job IDs with arrival t and positive duration d. Run the shortest available job nonpreemptively, breaking equal durations by smaller ID. Return completion order.',
 'strong-components':'Parse directed edges with vertices 0..maximum endpoint. Return SCCs with sorted members, and sort the component lists lexicographically; separate components with semicolons.',
 'selection-sort':'Sort ascending with classic selection sort and return the count of exchanges between different positions. Do not count self-swaps.',
 'prefix-sum':'Return the sum of inclusive indexes 1 through 3; input contains at least four integers.',
 'prefix-xor':'Return XOR of inclusive indexes 1 through 4; input contains at least five integers.',
 'prefix-sum-2d':'Return the sum of inclusive rows 1..2 and columns 0..1 of a rectangular matrix with at least three rows and two columns.',
 'lazy-segment-tree':'Add 3 to inclusive indexes 1..4, then return the sum of inclusive indexes 2..5. Input contains at least six integers.',
 'mo-algorithm':'Return distinct-value counts for inclusive ranges [0,3], [2,5], [0,5], in that order; input contains at least six integers.',
 'sparse-table':'Return minima for inclusive ranges [0,3], [2,5], [4,6], in that order; input contains at least seven integers.',
 'word-grid-search':'Parse a rectangular ASCII grid and word. Return whether four-neighbor moves spell the word without reusing a cell within one path.',
 'minimum-cover-window':'For ASCII text, return the shortest substring covering A, B and C; choose the earliest if lengths tie, or the empty string if no cover exists.',
 'string-frequency':'Return the first non-repeated ASCII character in source order, or none when no such character exists.',
}

COMPLEXITY={
 'group-by-key':'O(sum of L log L) letter-key sorting · O(total symbols) space',
 'kahn-topological':'O(E + V log V) with lexicographic min-heap · O(V) state',
 'graph-dfs':'O(V+E) traversal; neighbor sorting adds sum(deg log deg) · O(V+E) copied graph',
 'dfs-topological':'O(V+E) traversal; neighbor sorting adds sum(deg log deg) · O(V+E) copied graph',
 'strong-components':'O(V+E) SCC traversal; canonical report sorting adds O(V log V)',
 'a-star':'O((V+E) log V) on this finite four-neighbor grid with consistent heuristic',
 'copy-random-list':'O(n) time · O(n) separate index-arena storage',
 'three-sum':'O(n^2) time · O(n) owned sorted copy in this example',
 'activity-selection':'O(n log n) time · O(n) owned sorted copy; O(1) greedy state',
 'minimum-arrows':'O(n log n) time · O(n) owned sorted copy; O(1) greedy state',
 'quickselect':'O(n) average / O(n^2) worst time; O(log n) average / O(n) worst recursion stack',
 'suffix-array':'O(n log^2 n) comparison-sort doubling · O(n) auxiliary space',
 'suffix-automaton':'O(n log alphabet) with ordered transitions · O(n) states and transitions',
 'trie':'O(total symbols * log alphabet) with ordered child maps; O(prefix length * log alphabet) query',
 'rolling-window-statistic':'O(n) time · O(1) extra state over a borrowed slice; a stream needs an eviction buffer',
 'miller-rabin':'Seven deterministic u64 bases; O(log n) modular multiplications per base using u128 products',
 'word-break-dp':'O(n * dictionary characters) direct suffix comparisons · O(n) state',
 'longest-common-subsequence':'O(n*m) time · O(n*m) table in this example',
 'edit-distance':'O(n*m) time · O(m) row state in this example',
 'subsets':'O(n*2^n) time · O(n*2^n) materialized output',
 'binomial-coefficients':'O(min(k,n-k)) exact multiplicative steps · O(1) state',
 'imos-sweep':'O(n+q) time on discrete coordinates · O(n) space',
 'memoization':'O(n) time · O(n) memo and recursion depth',
 'tabulation':'O(n) time · O(n) table',
 'reservoir-sampling':'O(n) time · O(1) reservoir state for k=1',
 'unique-window':'O(n) time for ASCII · O(256) last-seen state',
 'hash-frequency':'O(n+m) time for lowercase ASCII · O(26) counters',
 'centroid-decomposition':'O(n log n) decomposition build · O(n) live traversal state',
 'n-queens':'O(n*n!) loose worst-case bound · O(n) search state',
}

def replace_strings(value,replacements):
    if isinstance(value,str):
        for a,b in replacements:value=value.replace(a,b)
        return value
    if isinstance(value,list):return [replace_strings(x,replacements) for x in value]
    if isinstance(value,dict):return {k:replace_strings(v,replacements) for k,v in value.items()}
    return value

def accepts(id,text,answer):
    from oracles import array,number
    if id in ['complement-lookup','sorted-two-sum']:
        try:a,b=map(int,answer.split(','))
        except ValueError:return False
        values=array(text);target=number(text,'target') if id=='complement-lookup' else 17
        if (a,b)==(-1,-1):return not any(values[i]+values[j]==target for i in range(len(values)) for j in range(i+1,len(values)))
        if id=='sorted-two-sum':a-=1;b-=1
        return 0<=a<len(values) and 0<=b<len(values) and a!=b and values[a]+values[b]==target
    if id=='peak-search':
        try:i=int(answer)
        except ValueError:return False
        a=array(text)
        return 0<=i<len(a) and (i==0 or a[i]>a[i-1]) and (i+1==len(a) or a[i]>a[i+1])
    return answer==solve(id,text)

def alternatives(id,text,expected):
    candidates=[]
    if expected in ['true','false']:candidates=['false' if expected=='true' else 'true','The valid input necessarily panics']
    elif re.fullmatch(r'-?\d+',expected):candidates=[str(int(expected)+1),str(int(expected)-1),str(int(expected)+7),'-99']
    elif re.fullmatch(r'-?\d+(?:,-?\d+)+',expected):
        a=expected.split(',');candidates=[','.join(a[1:]),','.join([str(int(a[0])+1)]+a[1:]),','.join(reversed(a)),'0,0','999,999']
    else:candidates=[expected+'0',expected[::-1],expected[:-1],'not a valid result']
    wrong=[]
    for candidate in candidates:
        if candidate not in wrong and candidate!=expected and not accepts(id,text,candidate):wrong.append(candidate)
        if len(wrong)==2:break
    while len(wrong)<2:wrong.append('No defined result despite the valid input' if not wrong else 'Every input produces the same result')
    return wrong

def display(answer):return '`'+answer+'`' if answer else 'An empty output string'

def harness(id,cases):
    checker='''fn valid(_input: &str, actual: &str, expected: &str) -> bool { actual == expected }'''
    if id in ['complement-lookup','sorted-two-sum']:
        checker='''fn valid(input: &str, actual: &str, _expected: &str) -> bool {
    let parts: Vec<_> = input.split(|c: char| !c.is_ascii_digit() && c != '-').filter(|x| !x.is_empty()).collect();
    let mut values: Vec<i64> = match parts.iter().map(|x| x.parse()).collect() { Ok(v) => v, Err(_) => return false };
    let target = TARGET;
    let pair: Vec<i64> = match actual.split(',').map(str::trim).map(str::parse).collect() { Ok(v) => v, Err(_) => return false };
    if pair.len() != 2 { return false; }
    if pair == [-1,-1] { return !(0..values.len()).any(|i| (i+1..values.len()).any(|j| values[i]+values[j] == target)); }
    let (a,b) = (pair[0]-OFFSET,pair[1]-OFFSET);
    a >= 0 && b >= 0 && a != b && (a as usize) < values.len() && (b as usize) < values.len() && values[a as usize]+values[b as usize] == target
}'''.replace('TARGET','values.pop().unwrap()' if id=='complement-lookup' else '17').replace('OFFSET','0' if id=='complement-lookup' else '1')
    elif id=='peak-search':
        checker='''fn valid(input: &str, actual: &str, _expected: &str) -> bool {
    let values: Vec<i64> = input.trim().trim_start_matches('[').trim_end_matches(']').split(',').map(|x|x.trim().parse().unwrap()).collect();
    let Ok(i) = actual.parse::<usize>() else { return false; };
    i < values.len() && (i == 0 || values[i] > values[i-1]) && (i+1 == values.len() || values[i] > values[i+1])
}'''
    entries=',\n'.join('        ('+r(c['input'])+','+r(c['expectedAnswer'])+')' for c in cases)
    return 'mod solution;\n\n'+checker+'\n\nfn main() {\n    let cases = [\n'+entries+'\n    ];\n    for (i,(input,expected)) in cases.iter().enumerate() {\n        let actual = solution::solve(input);\n        if !valid(input,&actual,expected) { eprintln!("PRIVATE CASE {} FAILED",i+1); std::process::exit(1); }\n    }\n    println!("PASS '+id+'");\n}\n'

def main():
    data=inputs();changed=[];records=[]
    for model_path in sorted((ROOT/'lessons').glob('*.model.json')):
        original=before(model_path);a=original['algorithm'];id=a['patternID'];fact=FACTS[id];texts=data[id]
        expected=solve(id,texts[0]);old_expected=a['expectedAnswer'];complexity=COMPLEXITY.get(id,a['complexity']);task=CONTRACT.get(id,a['task'])
        program=source(id,call(id,texts[0]));cases=[]
        assert len(set(texts))>=5,id
        for i,text in enumerate(texts):cases.append({'kind':'visible' if i==0 else 'boundary' if i==1 else 'adversarial','input':text,'expectedAnswer':solve(id,text)})
        cases += [{'kind':'normalisation','input':'  \n'+texts[0]+'\n  ','expectedAnswer':expected},
                  {'kind':'normalisation','input':'\n'+texts[-1]+'\n','expectedAnswer':solve(id,texts[-1])}]
        verification=harness(id,cases)
        for stage in ['model','recognize','challenge']:
            path=ROOT/'lessons'/f'algorithm.{id}.{stage}.json';lesson=before(path);old=lesson['algorithm']
            replacements=[(old['visibleInput'],texts[0]),(old['task'],task),(old['complexity'],complexity)]
            if old_expected!=expected:replacements.append(('`'+old_expected+'`','`'+expected+'`'))
            lesson=replace_strings(lesson,replacements);a=lesson['algorithm'];w=lesson['writing'];d=lesson['depth']
            teaching_input=next(text for text in texts[1:] if solve(id,text)!=expected) if stage=='challenge' else texts[0]
            teaching_answer=solve(id,teaching_input)
            teaching_program=source(id,call(id,teaching_input))
            a.update(task=task,visibleInput=texts[0],expectedAnswer=expected,complexity=complexity,rustSketch=teaching_program)
            # These positions are deliberately stable for completed native lessons.
            correct=w['correctAnswer']
            if stage=='model':question=fact['question'];answer=fact['correct'];wrong=fact['wrong'];feedback=fact['trace']
            else:
                text=texts[2] if stage=='recognize' else texts[4];answer=solve(id,text);wrong=alternatives(id,text,answer)
                question=(f'Trace {lesson["title"].split(":")[0]} on input `{text}`. Which result follows from the documented contract?' if stage=='recognize'
                          else f'Boundary check for {id}: with input `{text}`, what result should solve return?')
                feedback=f'For this input the result is {display(answer)}. '+fact['correct']+'. Compare this independent fixture with the worked trace: '+fact['trace']
                answer=display(answer);wrong=[display(x) if x not in ['The valid input necessarily panics','No defined result despite the valid input','Every input produces the same result'] else x for x in wrong]
            answers=wrong.copy();answers.insert(correct,answer)
            assert len(set(answers))==3,(id,stage,answers)
            w.update(question=question,answers=answers,feedback=feedback,correctAnswer=correct,exampleCode=teaching_program,
                     exampleCaption=f'Complete std-only {id} program for its typed teaching fixture. Parsing and output construction are separate from the core algorithm.')
            # Replace the generic command to trace with an actual transition.
            d['traceSteps']=[{'title':'Concrete transition','detail':fact['trace']},
                {'title':'Independent second fixture','detail':f'Input `{texts[2]}` produces {display(solve(id,texts[2]))}. Execute the named function in the worked program with these typed arguments, then compare its actual result with this independently computed expectation.'},
                {'title':'Boundary and contract','detail':f'Input `{texts[4]}` produces {display(solve(id,texts[4]))}. '+fact['correct']+'. The stated work bound is '+complexity+'. Count actual state changes; a successful output test alone does not prove that bound.'}]
            d['misconception']='“'+fact['wrong'][0]+'”';d['correction']=fact['correct']+'. '+fact['trace']
            d['transferChallenge']=f'Compare the visible input `{texts[0]}` with `{texts[3]}`. Predict why their results are {display(expected)} and {display(solve(id,texts[3]))}. Then change one legal value and explain whether the same invariant, '+fact['correct'].lower()+', still applies.'
            prefix=fact['trace']+'\n\n'+f'The worked program is a complete executable for this pattern. Its core function uses typed input so the state transitions remain visible. The challenge input contract is: {task} The visible fixture is `{texts[0]}` and its example result is {display(expected)}. The implementation and additional semantic fixtures were checked against an independent reference calculation. Those bounded tests establish these examples; they are not a proof for all inputs or a measurement on an iPhone.\n\nReturn a canonical String from solve: lowercase true/false for booleans; decimal integers without extra signs, leading zeros or whitespace; comma-separated sequence values and semicolon-separated groups. Whole-number medians have no decimal suffix; half medians use .5. Do not append a newline to the returned value. Preserve the explicitly named textual sentinels such as none or #. Input fixtures are bounded so the demonstrated arithmetic fits its named Rust types; satisfy the stated input preconditions before applying the algorithm.\n\n'
            if stage=='challenge':
                prefix=fact['correct']+'. The worked program demonstrates this invariant on an independent fixture, so you can study the implementation before predicting the challenge result.\n\n'+f'For teaching input `{teaching_input}`, the worked program returns {display(teaching_answer)}. Its functions are complete and use only std. Adapt the same state transitions to the visible challenge input `{texts[0]}`; predict that result before opening the answer reveal. The precise contract is: {task}\n\nReturn canonical output: lowercase booleans, decimal integers without leading zeros, comma-separated values and semicolon-separated groups, with no extra whitespace or final newline. Whole medians use integer form and half medians use .5. Textual sentinels such as none and # retain their stated meaning. String and character-grid fixtures use ASCII unless the lesson explicitly specifies Unicode scalar values.\n\n'
                other=[text for text in texts[1:] if solve(id,text)!=expected]
                d['traceSteps']=[{'title':'Pattern-specific invariant','detail':fact['correct']+'. This is the property the named implementation maintains; explain which comparison, state update or recursive return in the worked program establishes it.'},
                    {'title':'Independent typed fixture','detail':f'The worked call uses `{teaching_input}` and computes {display(teaching_answer)}. Keep parsing separate, then identify the core state before and after this call.'},
                    {'title':'Different legal case','detail':f'For `{other[-1]}`, the independently calculated result is {display(solve(id,other[-1]))}. The complexity discussion uses '+complexity+'. Verify the state invariant before reasoning about the operation count.'}]
                d['correction']=fact['correct']+'. The independent teaching fixture demonstrates this rule; predict the separate visible challenge before revealing its answer.'
                d['transferChallenge']=f'Change the independent fixture `{teaching_input}` in a legal way, then compare the result with your prediction. Explain how the same invariant applies to the separate visible challenge `{texts[0]}`.'
            old_text=w['explanation']
            paragraphs=old_text.split('\n\n')
            # Retain useful family reasoning, but remove obsolete claims about
            # a generic or incomplete sketch and replace them with exact context.
            retained=[p for p in paragraphs if not any(s in p for s in ['Now inspect the Rust sketch','Use the Rust sketch as a guide','The supplied Rust sketch'])]
            if stage != 'challenge':
                prefix += 'String and character-grid fixtures use ASCII unless the lesson explicitly specifies Unicode scalar values.\n\n'
            w['explanation']=prefix+'\n\n'.join(retained)
            w['rule']=fact['correct']+'. '+(task if stage=='challenge' else 'State the input preconditions before applying this invariant.')
            if stage=='model':w['task']='Follow the concrete trace, then change the typed fixture in the complete worked program and predict its output.';w['practiceCode']=program
            elif stage=='recognize':w['task']='Compare the visible and independent fixtures. Explain the input assumption that makes this algorithm applicable, then identify a change that would invalidate it.';w['practiceCode']=program
            else:
                starter='pub fn solve(input: &str) -> String {\n    // '+task+'\n    // Trim surrounding whitespace; implement parsing and the algorithm.\n    let _ = input;\n    todo!("implement '+id+'")\n}\n'
                w['task']=task;w['practiceCode']=starter;w['success']='The private harness prints PASS '+id+'. It checks at least five distinct semantic inputs plus surrounding-whitespace variants. Explain complexity separately; this harness does not time the algorithm.'
                check_path=ROOT/'checks'/f'algorithm.{id}.challenge.json';check=before(check_path);c=check['challenge']
                c.update(source=starter,verificationSource=verification,verificationCases=cases)
                # Semantic cases reject constant answers; broad substring bans
                # on particular return spellings can reject legitimate branches.
                c['forbiddenSourceFragments']=['todo!("implement']
                check['evidence']['forbiddenSourceFragments']=c['forbiddenSourceFragments']
                check_path.write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
            path.write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n');changed.append(lesson['id'])
        records.append({'pattern':id,'semanticInputs':len(texts),'harnessCalls':len(cases),'exampleSHA256':hashlib.sha256(program.encode()).hexdigest()})
    # Connections name current content, not stale pre-correction tasks.
    for unit_path in (ROOT/'units').glob('*.json'):
        unit=json.loads(unit_path.read_text());lessons=[json.loads((ROOT/'lessons'/f'{id}.json').read_text()) for id in unit['lessonIDs']]
        for i,lesson in enumerate(lessons):
            connections=[]
            for j,direction in [(i-1,'previous'),(i+1,'next')]:
                if 0<=j<len(lessons):connections.append({'direction':direction,'title':lessons[j]['title'],'concept':lessons[j]['concept']})
            lesson['depth']['connections']=connections
            (ROOT/'lessons'/f'{lesson["id"]}.json').write_text(json.dumps(lesson,ensure_ascii=False,indent=2)+'\n')
    (BASE/'publication-content.json').write_text(json.dumps({'changedLessons':changed,'patterns':records},indent=2)+'\n')
    print('Updated',len(changed),'lessons;',len(records),'individual examples')

if __name__=='__main__':main()
