# Agent Execution Rules

- **Browser Prohibition**: NEVER open a browser, use `browser_subagent`, or launch browser automation tools under any circumstance.
- **No Automated Tests / Diagnostics**: NEVER run test suites (e.g., `pytest`, `npm test`, `unittest`, `vitest`) or automated diagnostic commands unless explicitly and specifically requested by the user in the prompt.
- **No Unsolicited Dev Servers**: Do not launch dev servers, background processes, or preview environments to test or verify changes.
- **Direct Code Edits & Explanations Only**: When given a task, inspect files, apply the requested code edits directly, or provide explanations without triggering automated execution, testing, or browser verification steps.
- **Mandatory Implementation Plan Approval**: Before editing or generating any code for any feature, requirement, or execution prompt, create an interactive implementation plan artifact (`<appDataDir>\brain\<conversation-id>\implementation_plan.md`) with `RequestFeedback: true` so the user can review, comment, and approve via the interactive panel. STOP and do not edit, generate, or publish code until the user explicitly reviews and provides approval to proceed.

# Alternative Intelligence Specifications

- **Native Infographic Card**: When creating, updating, or referencing infographic generation skills in Alternative Intelligence, always use the **"Native Infographic Card"** method. In this method:
  1. Gemini outputs a structured JSON block (tagged `infographic-json`) containing visual telemetry and projections followed by the analytical write-up.
  2. Reflex parses this data into strongly-typed Pydantic models (`ChatMessage` / `RatingRow`).
  3. Reflex renders a rich, interactive native UI card (elevated podium, constructor-colored rating progress bars, qualifying grid tiers, and championship shifts).
  4. The card includes a 1-click **PNG Download** button using client-side `html2canvas` (with `data-html2canvas-ignore="true"` on UI controls and scale=2 for retina capture).
  5. The raw JSON block is sanitized and hidden from the live chat stream so users only see the visual card and analytical text.

