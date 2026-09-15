# Agent Execution Rules

- **Browser Prohibition**: NEVER open a browser, use `browser_subagent`, or launch browser automation tools under any circumstance.
- **No Automated Tests / Diagnostics**: NEVER run test suites (e.g., `pytest`, `npm test`, `unittest`, `vitest`) or automated diagnostic commands unless explicitly and specifically requested by the user in the prompt.
- **No Unsolicited Dev Servers**: Do not launch dev servers, background processes, or preview environments to test or verify changes.
- **Direct Code Edits & Explanations Only**: When given a task, inspect files, apply the requested code edits directly, or provide explanations without triggering automated execution, testing, or browser verification steps.
