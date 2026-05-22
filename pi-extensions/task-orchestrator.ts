import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

type ActiveGrill = {
	originalTask: string;
	skills: string[];
	startedAt: number;
	beadsParentId?: string;
};

const SKILL_ROOT = join(homedir(), ".agents", "skills");
const INSTRUCTION_ROOT = join(homedir(), ".pi", "agent", "instructions");

const ALWAYS_INSTRUCTIONS = ["tdd"];
const DOMAIN_INSTRUCTIONS = [
	"fortify-development",
	"inertia-svelte-development",
	"laravel-best-practices",
	"laravel-docs-lookup",
	"pest-testing",
	"tailwindcss-development",
	"wayfinder-development",
];

const LATCH_PATTERNS = [
	/enough\s+(questions?|grill(?:ing)?)\b.*\b(execute|implement|build|code|do it|go)\b/i,
	/\b(stop|quit)\s+(asking|grilling)\b.*\b(execute|implement|build|code|do it|go)\b/i,
	/\b(no more|enough)\s+questions\b/i,
	/\b(execute|implement|build|code)\s+(now|it|the plan)\b/i,
	/^\s*(ok\s+)?(execute|implement|build|code|do it)\s*$/i,
	/\blet'?s\s+(execute|implement|build|code|do it)\b/i,
];

const BYPASS_PATTERNS = [
	/^\s*\/\w+/, // slash commands: /login, /reload, /model, etc.
	/^\s*!/, // user bash commands
	/^\s*(no\s*grill|skip\s*grill|bypass\s*grill)\s*[:,-]/i,
];

const NON_TASK_PATTERNS = [
	/^\s*(can|could|do|does|are|is|what|which|who|when|where|why|how)\b.*\?\s*$/i,
	/^\s*(ok\s+)?is it possible to\b/i,
	/^\s*(can|could)\s+(you|we)\b.*\?\s*$/i,
	/\bwhat (skills|tools|mcp servers|models)\b/i,
	/\b(can|could) you\b.*\b(visit|browse|open|access)\b.*\b(web|websites?|pages?|urls?)\b/i,
	/\bhow do(es)?\b.*\bwork\b/i,
];

const TASK_INTENT_PATTERNS = [
	/\b(add|build|change|create|debug|delete|edit|fix|implement|install|make|migrate|modify|refactor|remove|rename|test|update|write)\b/i,
	/\b(set up|wire up|hook up|scaffold|generate|configure|integrate)\b/i,
	/\bPR|pull request|branch|diff\b/i,
];

function stripFrontmatter(markdown: string): string {
	return markdown.replace(/^---\n[\s\S]*?\n---\n?/, "").trim();
}

function readSkill(name: string): string | undefined {
	const path = join(SKILL_ROOT, name, "SKILL.md");
	if (!existsSync(path)) return undefined;
	return stripFrontmatter(readFileSync(path, "utf8"));
}

function readInstruction(name: string): string | undefined {
	if (name === "tdd" || name === "grill-me") return readSkill(name);

	const path = join(INSTRUCTION_ROOT, `${name}.md`);
	if (!existsSync(path)) return undefined;
	return readFileSync(path, "utf8").trim();
}

function unique(values: string[]): string[] {
	return [...new Set(values)];
}

function hasAny(text: string, patterns: RegExp[]): boolean {
	return patterns.some((pattern) => pattern.test(text));
}

function shouldBypass(text: string): boolean {
	if (BYPASS_PATTERNS.some((pattern) => pattern.test(text))) return true;

	// Capability/explanation questions are not implementation tasks. Let the agent answer normally.
	// If the user asks "is it possible" / "can we", treat it as discussion even when it mentions build/make.
	if (NON_TASK_PATTERNS.some((pattern) => pattern.test(text))) {
		if (/^\s*(ok\s+)?(is it possible to|can|could)\b/i.test(text)) return true;
		if (!TASK_INTENT_PATTERNS.some((pattern) => pattern.test(text))) return true;
	}

	return false;
}

function hasLatch(text: string): boolean {
	return hasAny(text, LATCH_PATTERNS);
}

function detectDomainSkills(text: string): string[] {
	const skills: string[] = [];
	const lower = text.toLowerCase();

	const laravelSignals = [
		/\blaravel\b/i,
		/\bartisan\b/i,
		/\beloquent\b/i,
		/\bmigration(s)?\b/i,
		/\bcontroller(s)?\b/i,
		/\bmodel(s)?\b/i,
		/\broute(s)?\b/i,
		/\bmiddleware\b/i,
		/\bblade\b/i,
		/\bqueue(s)?\b/i,
		/\bjob(s)?\b/i,
		/\bpolicy|policies\b/i,
		/\bform request(s)?\b/i,
		/\bvalidation\b/i,
		/\bcomposer\.(json|lock)\b/i,
		/\b(app|routes|database\/migrations|config|tests)\//i,
	];

	if (hasAny(text, laravelSignals)) {
		// TDD is always mandatory. In Laravel projects, tests should use the Pest skill.
		skills.push("laravel-docs-lookup", "laravel-best-practices", "pest-testing");
	}

	if (hasAny(text, [/\bfortify\b/i, /\bauth(entication)?\b/i, /\blogin\b/i, /\bregister|signup\b/i, /\bpassword reset\b/i, /\bverify email\b/i, /\b2fa\b/i, /\btwo[- ]factor\b/i, /app\/Actions\/Fortify\//i, /FortifyServiceProvider/i])) {
		// Fortify is Laravel-specific; pull the Laravel docs/practices/Pest stack too.
		skills.push("fortify-development", "laravel-docs-lookup", "laravel-best-practices", "pest-testing");
	}

	if (hasAny(text, [/\binertia\b/i, /\bsvelte\b/i, /\buseForm\b/, /\buseHttp\b/, /\bsetLayoutProps\b/, /\bdeferred props\b/i, /\bprefetch/i, /\brouter\b/i])) {
		// This Inertia/Svelte skill is for Laravel/Inertia apps.
		skills.push("inertia-svelte-development", "laravel-docs-lookup", "laravel-best-practices", "pest-testing");
	}

	if (hasAny(text, [/\bpest\b/i, /\bphpunit\b/i, /\btest(s|ing)?\b/i, /tests\/(Feature|Unit|Browser)\//i, /\bit\(\b/, /\bexpect\(/])) {
		skills.push("pest-testing");
	}

	if (hasAny(text, [/\btailwind\b/i, /\bresponsive\b/i, /\bdark mode\b/i, /\bgrid\b/i, /\bflex\b/i, /\bcard(s)?\b/i, /\bnavbar\b/i, /\btable\b/i, /\bform(s)?\b/i, /\bbadge(s)?\b/i, /\bspacing\b/i, /\btypography\b/i, /\bstyl(e|ing)\b/i])) {
		// Tailwind work in this setup is assumed to be Laravel app UI work.
		skills.push("tailwindcss-development", "laravel-docs-lookup", "laravel-best-practices", "pest-testing");
	}

	if (hasAny(text, [/\bwayfinder\b/i, /@\/actions/i, /@\/routes/i, /\broute function(s)?\b/i, /\bhardcoded url(s)?\b/i, /\bfrontend\b.*\bbackend\b/i, /\bbackend\b.*\bfrontend\b/i])) {
		// Wayfinder is Laravel route/controller integration.
		skills.push("wayfinder-development", "laravel-docs-lookup", "laravel-best-practices", "pest-testing");
	}

	// If the user mentions first-party Laravel frontend/form wiring, Wayfinder is often relevant.
	if (lower.includes("inertia") && hasAny(text, [/\bform(s)?\b/i, /\blink(s)?\b/i, /\broute(s)?\b/i, /\bcontroller action(s)?\b/i])) {
		skills.push("wayfinder-development");
	}

	return unique(skills.filter((skill) => DOMAIN_INSTRUCTIONS.includes(skill)));
}

function commandExists(command: string): boolean {
	try {
		execFileSync("/usr/bin/env", ["bash", "-lc", `command -v ${command}`], { stdio: "ignore", timeout: 1_000 });
		return true;
	} catch {
		return false;
	}
}

function extractBeadId(output: string): string | undefined {
	try {
		const parsed = JSON.parse(output);
		return parsed.id ?? parsed.issue?.id ?? parsed.bead?.id;
	} catch {
		return output.match(/[a-z][a-z0-9]*-[a-z0-9]+(?:\.\d+)?/i)?.[0];
	}
}

function shellQuote(value: string): string {
	return `'${value.replace(/'/g, `'"'"'`)}'`;
}

function ensureBeadsParent(cwd: string, task: string): { parentId?: string; warning?: string } {
	if (!commandExists("bd")) {
		return { warning: "Beads CLI `bd` is not installed or not on PATH. Install it, then rerun if you want automatic Beads task creation." };
	}

	try {
		if (!existsSync(join(cwd, ".beads"))) {
			execFileSync("bd", ["init", "--quiet"], { cwd, stdio: "ignore", timeout: 20_000 });
		}

		const description = `Parent task created by Pi task-orchestrator after grill/preflight acceptance.\n\nOriginal task:\n${task}`;
		const output = execFileSync("bd", ["create", task.slice(0, 180), "-t", "epic", "-p", "1", "--description", description, "--labels", "pi-orchestrator,accepted-plan", "--json"], {
			cwd,
			encoding: "utf8",
			timeout: 20_000,
		});

		return { parentId: extractBeadId(output) };
	} catch (error) {
		return { warning: `Beads setup failed: ${error instanceof Error ? error.message : String(error)}` };
	}
}

function getRecentDecisions(ctx: any, since: number): Array<{ question: string; answer: string; answeredAt?: string }> {
	try {
		return ctx.sessionManager
			.getEntries()
			.filter((entry: any) => entry.type === "custom" && entry.customType === "ask-user-question-decision")
			.map((entry: any) => entry.data ?? entry.details ?? entry)
			.filter((data: any) => data?.question && data?.answer && (!data.answeredAt || Date.parse(data.answeredAt) >= since - 5_000));
	} catch {
		return [];
	}
}

function renderDecisions(decisions: Array<{ question: string; answer: string; answeredAt?: string }>): string {
	if (decisions.length === 0) return "No persisted AskUserQuestion decisions were found in this session. Use the visible conversation context as the source of truth.";
	return decisions.map((decision, index) => `${index + 1}. ${decision.question}\n   Answer: ${decision.answer}`).join("\n");
}

function renderInstructionBundle(instructionNames: string[]): string {
	const sections = instructionNames.map((name) => {
		const content = readInstruction(name);
		if (!content) {
			const expectedPath = name === "tdd" || name === "grill-me" ? join(SKILL_ROOT, name, "SKILL.md") : join(INSTRUCTION_ROOT, `${name}.md`);
			return `## ${name}\n\n[Instruction file not found at ${expectedPath}]`;
		}
		return `## ${name}\n\n${content}`;
	});

	return sections.join("\n\n---\n\n");
}

function buildGrillPrompt(task: string, instructionNames: string[]): string {
	const grill = readSkill("grill-me") ?? "Ask focused questions one at a time before implementation.";
	const bundle = renderInstructionBundle(instructionNames);

	return `You are in mandatory preflight mode for a new task. Do not implement, edit files, run tests, or execute the plan yet.

Original task:
${task}

Mandatory grill instructions:
${grill}

Additional mandatory development instructions selected for this task:
${bundle}

Operational rules:
- Ask exactly one question at a time.
- For every question, call the AskUserQuestion tool with 2-4 concrete selectable options.
- If an answer can be discovered by reading the codebase, inspect the codebase instead of asking.
- Continue grilling until the user explicitly uses an execution latch such as "enough questions, execute", "no more questions", or "let's implement".
- Until that latch appears, do not modify files or execute the plan.
- As the plan stabilizes, identify likely child tasks and any human approval gates that should exist in Beads after acceptance.
- Always preserve TDD as a constraint for the eventual implementation.`;
}

function buildExecutionPrompt(active: ActiveGrill, latchMessage: string, decisions: Array<{ question: string; answer: string; answeredAt?: string }>, beads: { parentId?: string; warning?: string }): string {
	const combined = `${active.originalTask}\n\n${latchMessage}`;
	const skills = unique([...ALWAYS_INSTRUCTIONS, ...active.skills, ...detectDomainSkills(combined)]);
	const bundle = renderInstructionBundle(skills);

	return `The user has activated the execution latch. Stop asking preflight questions and implement the task now.

Original task:
${active.originalTask}

Latch / latest user instruction:
${latchMessage}

Persisted human decisions from AskUserQuestion:
${renderDecisions(decisions)}

Beads status:
${beads.parentId ? `Initialized/available. Parent epic: ${beads.parentId}` : `Unavailable. ${beads.warning ?? "No parent issue was created."}`}

Mandatory development instructions for execution:
${bundle}

Execution rules:
- Use TDD: write or update failing tests first when feasible, then implement, then run the relevant tests.
- Apply all relevant domain instructions above.
- If Laravel is involved, look up the official docs as instructed before non-trivial Laravel changes.
- Prefer codebase inspection over asking more questions.
- Ask a new question only if execution is impossible or unsafe without the answer.

Beads planning rules:
- Before modifying project code, convert the accepted plan into Beads tasks when `bd` is available.
- If parent epic `${beads.parentId ?? "<none>"}` exists, create child tasks under it with:
  `bd create "Child task title" -t task -p 1 --parent ${beads.parentId ?? "<parent-id>"} --description ${shellQuote("scope, acceptance criteria, and relevant decisions")} --labels "pi-orchestrator,agent-task" --json`
- Use one child per vertical TDD slice. Do not create one huge child task.
- Add dependency edges where order matters with `bd dep add <blocked-child> <blocking-child>`.
- For human approvals or irreversible decisions, create a human gate that blocks the relevant child:
  `bd gate create --type=human --blocks <child-id> --reason ${shellQuote("Human approval required before proceeding")}`
- Mark human-gated children with label `human-gate` where possible.
- Work through `bd ready --json` in dependency order.
- Do not bypass a human gate; use AskUserQuestion to get approval, then resolve/close the gate according to Beads docs.
- If Beads is unavailable, continue with an explicit task checklist in the response and tell the user what Beads setup failed.`;
}

export default function taskOrchestrator(pi: ExtensionAPI) {
	let activeGrill: ActiveGrill | undefined;

	pi.registerCommand("task-orchestrator-reset", {
		description: "Reset the mandatory grill/preflight state.",
		handler: async (_args, ctx) => {
			activeGrill = undefined;
			ctx.ui.notify("Task orchestrator state reset", "info");
		},
	});

	pi.on("session_start", async (_event, ctx) => {
		ctx.ui.setStatus("task-orchestrator", "grill+tdd");
	});

	pi.on("session_shutdown", async () => {
		activeGrill = undefined;
	});

	pi.on("input", async (event, ctx) => {
		if (event.source === "extension") return { action: "continue" };

		const text = event.text.trim();
		if (!text) return { action: "continue" };

		if (activeGrill) {
			if (hasLatch(text)) {
				const beads = ensureBeadsParent(ctx.cwd, activeGrill.originalTask);
				if (beads.parentId) activeGrill.beadsParentId = beads.parentId;
				if (beads.warning) ctx.ui.notify(beads.warning, "warning");
				const decisions = getRecentDecisions(ctx, activeGrill.startedAt);
				const prompt = buildExecutionPrompt(activeGrill, text, decisions, beads);
				activeGrill = undefined;
				ctx.ui.notify("Execution latch detected: switching from grill mode to Beads-backed implementation", "info");
				return { action: "transform", text: prompt, images: event.images };
			}

			// Let answers to the active grill pass through normally. The transformed grill prompt
			// already instructs the model not to execute until the latch appears.
			return { action: "continue" };
		}

		if (shouldBypass(text)) return { action: "continue" };
		if (hasLatch(text)) {
			ctx.ui.notify("Execution latch ignored: no active grill/preflight task is being tracked. Send the task first, or use /task-orchestrator-reset if state looks stale.", "warning");
			return { action: "handled" };
		}

		const skills = unique([...ALWAYS_INSTRUCTIONS, ...detectDomainSkills(text)]);
		activeGrill = { originalTask: text, skills, startedAt: Date.now() };

		ctx.ui.notify(`Mandatory grill preflight started (${skills.join(", ")})`, "info");
		return { action: "transform", text: buildGrillPrompt(text, skills), images: event.images };
	});
}
