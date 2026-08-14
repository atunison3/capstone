# AI statement

Artificial intelligence was used as a tool in the development of this project. It did not replace human ownership of design, intent, or final responsibility for the work.

## How AI was used

Much of the AI-assisted work consisted of ordinary software tasks a developer would otherwise type by hand: calling library APIs, wiring functions together, drafting boilerplate, and producing first-pass documentation or tests from existing code and configuration.

In other words, many generations were **built-in, routine calls**—the same kinds of operations a normal developer runs daily—rather than unsupervised invention of research claims or analysis conclusions.

## Human role

This project was:

1. **Architected by human intelligence** — research goals, package structure, modeling choices, and overall design were set by people.
2. **Shelled out with AI assistance** — scaffolding, repetitive code, and initial drafts were often generated or expanded with AI.
3. **Detailed by humans** — specifications, configuration, domain logic, and project-specific behavior were filled in and corrected by people.
4. **Reviewed by humans** — code, docs, and behavior were checked against the real repository, revisions, and project intent before being treated as finished.

## Testing

Automated tests were added so that important functions can be checked against their intended behavior. Testing is part of how we reduce the risk that AI-assisted code drifts from what the project is supposed to do. Tests support review; they do not replace human judgment about research design or interpretation.

## Documentation example

The documentation site is a clear example of this workflow. It was **initially built with AI** after the team adopted Docsify, then **reviewed extensively** against:

- the actual package and modules in the repository
- later code and configuration changes
- the intended visitor experience (data story first, then install and run, then deeper docs)

Where drafts did not match the project, humans revised them.

## What this statement is not

- It is not a claim that every line was written without tools.
- It is not a claim that AI is an author of the research findings.
- It does not transfer responsibility: the maintainers remain accountable for the software and for how results are presented.

## Summary

| Stage | Primary responsibility |
| --- | --- |
| Architecture and intent | Humans |
| Scaffolding and drafting | AI-assisted, human-directed |
| Domain detail and configuration | Humans |
| Review, revision, and release | Humans |
| Behavioral checks | Automated tests + human review |
