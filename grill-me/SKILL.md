---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one.

Ask the questions one at a time. For EVERY question, you MUST use the AskUserQuestion tool so the user can pick from selectable options instead of typing free-text answers.

For each question:
- Generate 2-4 concrete answer options.
- Put your recommended answer first and append "(Recommended)" to its label.
- Make options mutually exclusive and specific to this plan (no generic "Option A / B").
- Keep the question text tight; put nuance in each option's description field.
- Users will always have "Other" available, so don't force a fit when the answer space is genuinely open.

If a question can be answered by exploring the codebase, explore the codebase instead of asking.
