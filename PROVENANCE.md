# Source provenance

The v1 corpus was exported by executing the Swift curriculum models in
`sergii-ziborov/Crabrix` at source commit
`c38423e7503a56d6cd97e3a6c17651d5a5c33d62`.

`migration/baseline-inventory.json` is the immutable semantic fixture. It includes
the complete seven-course hierarchy, lesson writing and depth, all multiple-choice
options and feedback, Atlas verification cases and generated Rust harnesses,
starter source trees, 46 gallery projects, and 259 term pairs. No learner data,
support correspondence, credentials, or user projects were copied.

The exporter source lives in Crabrix's `migration/` directory. `tools/coursepack.py`
imports that baseline into the authoring tree. The parity report compares the
reconstructed CoursePacks with the baseline, including text and source bytes.

Publishing the checks and probes makes them inspectable. They are teaching
data, not cryptographic secrets or a trusted competitive ranking system.
