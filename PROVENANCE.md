# Source provenance

The v1 corpus was exported by executing the Swift curriculum models in
`sergii-ziborov/Crabrix` at source commit
`c38423e7503a56d6cd97e3a6c17651d5a5c33d62`.

`migration/baseline-inventory.json` is the immutable semantic fixture. It includes
the complete seven-course hierarchy, lesson writing and depth, all multiple-choice
options and feedback, Atlas verification cases and generated Rust harnesses,
starter source trees, 46 gallery projects, and 358 term pairs. No learner data,
support correspondence, credentials, or user projects were copied.

The exporter source lives in Crabrix's `migration/` directory. `tools/coursepack.py`
imports that baseline into the authoring tree. The parity report compares the
reconstructed CoursePacks with the baseline, including text and source bytes.

Examples 1.0.1 adds authored explanations to all 46 project READMEs while
preserving their Rust and Cargo source files. Four local PNG diagrams were
created with OpenAI ImageGen at the owner's request: Ferris Pixel Art,
Run-Length Encoder, Maze Pathfinder, and Mandelbrot Canvas. They are
illustrations of the accompanying text, not exact execution traces or
substitutes for the source. Their accessible descriptions and captions are in
the corresponding `project.json` files. No third-party image was imported.

Examples 1.0.2 expands every project guide with a code-specific explanation
and corrects wording that overstated a few small demonstrations. The original
Rust and Cargo source bytes, project identities, and four illustrations are
unchanged. This is a new immutable package; 1.0.1 remains available.

Publishing the checks and probes makes them inspectable. They are teaching
data, not cryptographic secrets or a trusted competitive ranking system.
