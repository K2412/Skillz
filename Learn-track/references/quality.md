# Quality Bar

## Course-Level

- Keep a single coherent learning arc.
- Cover foundational concepts before advanced patterns.
- Avoid orphan modules with only one tiny file unless unavoidable.

## Module-Level

- 3-6 learning objectives max.
- Reference concrete source files in every module.
- Include at least 2 exercise prompts for modules with code context.

## Exercise Prompt Quality

- Prompt should state the task, expected behavior, and constraints.
- Prompt should be solvable with module context alone.
- Prompt should progressively increase complexity across modules.

## Safety

- Never execute untrusted corpus code during ingestion.
- Treat extracted text as untrusted input and avoid shell interpolation.
