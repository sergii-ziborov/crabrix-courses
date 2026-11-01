# Algorithm Atlas corrections, 1 November 2026

This pass fixes defects found by the four-part Atlas audit: weak private test sets,
programs that did not teach their named pattern, task text that hid required
behaviour, poor quiz distractors, a `rule` field that repeated the quiz answer, and
inline-code markup. Lesson IDs, order, `exerciseKind` and `correctAnswer` positions are
unchanged, and every earlier private case stays.

## Reproduce

Run from the repository root.

```sh
python3 editorial/academy_20261101/apply_pass.py
python3 editorial/academy_20261101/prove_wrong_rejected.py
python3 editorial/academy_20261101/verify_atlas.py
python3 -m unittest discover -s tests
python3 tools/coursepack.py validate --courses courses --schema schemas
```

`apply_pass.py` reads `courses/algorithms` at commit `d4e247e` and rebuilds the files,
so running it twice gives the same result. Build output goes under
`build/academy-20261101/`. Content digests are left for the catalog step, so
`test_nested_content_digests_match_authored_values` fails for Algorithms until then.

## Files

| File | Purpose |
| --- | --- |
| `atlas_overlay.py` | `CODE`, `call` and `solve`: the 27 October pipeline plus this pass's changes |
| `programs.py` | Rust programs that replace the earlier ones |
| `adversarial.py` | New private cases, with the answer the audit stated where it stated one |
| `edits.py` | Task, idea, rule, complexity, quiz and markup text |
| `wrong_solutions.rs` | The audit's wrong solutions in the packaged `solve` shape |
| `changed-programs.json` | Patterns whose program text changed; site traces and replay packs need regenerating for these |
| `cases-added.json` | Every new case and its answer |
| `rule-rewrites.json` | Model lessons whose `rule` was reworded |
| `wrong-solution-evidence.json` | Each wrong solution against the old and the extended harness |
| `atlas-verification.json` | Standalone programs, typed fixtures, harnesses and static checks |

`academy_20261027/` is not edited. `tests/test_academy_corrections.py` now imports
`CODE` and `solve` from `atlas_overlay.py`, because new input forms and changed
programs need the new oracle.

## Limits

- Each answer comes from an independent Python oracle and from the Rust reference, and
  the two must agree. The verification also compares them with any answer the audit
  stated. Python oracles for the reworked patterns follow the same contract as the Rust
  program, so a misread contract would affect both.
- Harness runs use typed adapters for known inputs. They do not test a learner's text
  parser. Wrong solutions do parse text, so they run through the harness unmodified.
- Finite fixtures and seeded random inputs are evidence for those inputs. They do not
  prove an algorithm for all inputs or measure an asymptotic bound.
- These are desktop runs with rustc 1.99.0. Nothing here was run on an iPhone.
- `manacher`, `minimum-cover-window` and `rolling-window-statistic` still show their
  answer as a substring of the visible input (`bab` in `babad`). Only the input does this.
