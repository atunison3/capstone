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

Automated tests were added so that important functions can be checked against their intended behavior. Testing reduces the risk that AI-assisted code drifts from what the project is supposed to do. Tests support review; they do not replace human judgment about research design or interpretation.

## Documentation example

The documentation site is a clear example of this workflow. It was **initially built with AI** after Docsify was adopted, then **reviewed extensively** against:

- the actual package and modules in the repository
- later code and configuration changes
- the intended visitor experience (data story first, then install and run, then deeper docs)

Where drafts did not match the project, they were revised by humans.

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

## Skills

Agent skills were used when generating documentation for this repository. See the [atunison3/agent-skills](https://github.com/atunison3/agent-skills) repository for the relevant `SKILL.md` definitions.

## Example AI usage

AI usage was focused on building reproducible python based analysis and improving software-engineering quality of the repository. The following examples are representative of how large language models were used on this project: short, task-focused prompts for formatting and tests, followed by human review and integration.

### Example 1 — formatting a classification map

#### Prompt 1

```text
Given a dataframe with column "NCSL Classification", convert:

"5": Strict Photo ID
"4": Strict Non-Photo ID
"3": Non-Strict Photo ID
"2": Non-Strict, Non-Photo ID
"1": No Document Required to Vote
```

#### Response 1 (excerpt)

```python
classification_map = {
    "5": "Strict Photo ID",
    "4": "Strict Non-Photo ID",
    "3": "Non-Strict Photo ID",
    "2": "Non-Strict, Non-Photo ID",
    "1": "No Document Required to Vote",
}

df["NCSL Classification"] = (
    df["NCSL Classification"]
    .astype("string")
    .map(classification_map)
)
```

### Example 2 — drafting unit tests

#### Prompt 2

```text
Write a unittest for this:

def load_fips_data(data_path: Path) -> DataFrame:
    """Loads FIPS data"""

    # Expand the data path
    data_path = expand_user(data_path)
    ...

The unittest should at minimum verify the column names, first row of data, ...
```

#### Response 2 (excerpt)

```python
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import requests

from capstone.helper_functions import load_fips_data
# ...
```

Generated test code was reviewed, adapted to the project’s test layout, and retained only where it matched intended behavior.
