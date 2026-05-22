import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync } from "node:fs";
import { basename, join } from "node:path";

type ExplainMode = "diff" | "concept";

type ExplainOptions = {
	mode?: ExplainMode;
	query: string;
	base?: string;
	paths?: string;
	out?: string;
	maxFiles?: number;
};

function slugify(value: string): string {
	const slug = value
		.toLowerCase()
		.replace(/[^a-z0-9]+/g, "-")
		.replace(/^-+|-+$/g, "")
		.slice(0, 70);
	return slug || "explain";
}

function shellQuote(value: string): string {
	return `'${value.replace(/'/g, `'"'"'`)}'`;
}

function parseArgs(input: string): ExplainOptions {
	const tokens = input.match(/(?:[^\s"']+|"[^"]*"|'[^']*')+/g) ?? [];
	const positional: string[] = [];
	const options: ExplainOptions = { query: "" };

	for (const rawToken of tokens) {
		const token = rawToken.replace(/^(["'])(.*)\1$/, "$2");
		if (token === "diff" || token === "branch" || token === "commit" || token === "commits") {
			options.mode = "diff";
			continue;
		}
		if (token === "concept" || token === "topic") {
			options.mode = "concept";
			continue;
		}
		if (token.startsWith("--base=")) {
			options.base = token.slice("--base=".length);
			options.mode = "diff";
			continue;
		}
		if (token.startsWith("--paths=")) {
			options.paths = token.slice("--paths=".length);
			continue;
		}
		if (token.startsWith("--out=")) {
			options.out = token.slice("--out=".length);
			continue;
		}
		if (token.startsWith("--max-files=")) {
			const parsed = Number.parseInt(token.slice("--max-files=".length), 10);
			if (Number.isFinite(parsed) && parsed > 0) options.maxFiles = parsed;
			continue;
		}
		positional.push(token);
	}

	options.query = positional.join(" ").trim();
	if (!options.mode) {
		options.mode = /\b(diff|branch|commit|commits|PR|pull request|changed|changes)\b/i.test(input) ? "diff" : "concept";
	}

	return options;
}

function buildPrompt(ctx: any, opts: Required<Pick<ExplainOptions, "mode" | "query">> & ExplainOptions): string {
	const project = basename(ctx.cwd || process.cwd());
	const slugSource = opts.mode === "diff" ? opts.query || opts.base || "branch-diff" : opts.query;
	const outDir = opts.out || `.understand-anything/explain/${opts.mode}-${slugify(slugSource)}`;
	const maxFiles = opts.maxFiles ?? (opts.mode === "diff" ? 30 : 15);
	const graphPath = join(outDir, "knowledge-graph.json");
	const indexPath = join(outDir, "README.md");

	const common = `You are executing Pi /explain. Produce an Understand-Anything-style focused graph plus a brief index. Do not produce a long markdown walkthrough as the primary artifact.

Project: ${project}
Working directory: ${ctx.cwd}
Mode: ${opts.mode}
Output directory: ${outDir}
Focused graph path: ${graphPath}
Brief index path: ${indexPath}
Max directly analyzed files: ${maxFiles}

Output contract:
1. Create ${shellQuote(outDir)}.
2. Write ${shellQuote(graphPath)} as JSON shaped like Understand-Anything's knowledge graph:
   - project: { name, description, languages, frameworks, analyzedAt, gitCommitHash }
   - nodes[]: { id, type, name, filePath, summary, tags[], complexity, languageNotes? }
   - edges[]: { source, target, type, direction, weight }
   - layers[]: { id, name, description, nodeIds[] }
   - tour[]: { order, title, description, nodeIds[] }
3. Scope the graph to only the files/classes/functions/modules relevant to this request. Do not graph the entire application.
4. Prefer existing .understand-anything/knowledge-graph.json as source material if present. If absent, inspect files directly and still produce the focused graph.
5. Write ${shellQuote(indexPath)} as a brief index only: what the graph covers, how scope was chosen, key nodes, key edges, and how to open/use it with Understand-Anything dashboard tooling.
6. If Understand-Anything is installed and a dashboard command is obvious, mention the exact command to open the output. Otherwise tell the user the graph JSON is compatible in shape with Understand-Anything and where it lives.
7. At the end, summarize paths written and the node/edge count.

Graph quality rules:
- Include file nodes for each relevant source file.
- Include class/function/module nodes only when they are important to the concept or diff.
- Add contains edges from file nodes to class/function nodes.
- Add imports/calls/depends_on edges when supported by code evidence.
- Keep summaries concise but explanatory.
- Include a short tour ordered in the best learning/review sequence.
- Never invent a node or edge without evidence from code, git diff, or the existing knowledge graph.`;

	if (opts.mode === "diff") {
		const baseLine = opts.base ? `Use base ref: ${opts.base}` : "Auto-detect base ref: origin default branch, then dev, main, master.";
		const pathsLine = opts.paths ? `Restrict diff to paths/glob: ${opts.paths}` : "No path restriction unless the changed-file list is too broad.";
		return `${common}

Diff-specific instructions:
- ${baseLine}
- ${pathsLine}
- Resolve HEAD short SHA.
- List changed files with git diff against the base ref.
- Triage changed files to the files that matter for understanding the branch. Add up to 5 unchanged context files if needed.
- Build the focused graph around changed files plus 1-hop affected components.
- Include changed nodes and affected nodes as tags: "changed" and "affected".
- Also write ${shellQuote(join(outDir, "diff-overlay.json"))} with:
  { version, baseBranch, generatedAt, changedFiles, changedNodeIds, affectedNodeIds }.
- README should explain what changed, affected components, affected layers, risks, and reviewer checklist briefly.

Original /explain request:
${opts.query || "Explain the current branch diff."}`;
	}

	return `${common}

Concept-specific instructions:
- Concept/query: ${opts.query}
- First triage the repository file list for relevance to the concept.
- Read only the most relevant files, up to ${maxFiles}, plus small supporting context when needed.
- Build the focused graph around the concept's actual implementation flow.
- Include concept nodes when useful, but anchor them to concrete files/classes/functions with edges.
- README should briefly explain the concept, key nodes, key relationships, and recommended tour order.

Original /explain request:
${opts.query}`;
}

export default function explainCommand(pi: ExtensionAPI) {
	pi.registerCommand("explain", {
		description: "Generate a focused Understand-Anything graph for a concept or branch diff. Usage: /explain concept <topic> | /explain diff [--base=main] [--paths=glob]",
		handler: async (args, ctx) => {
			let opts = parseArgs(args);

			if (!opts.query && opts.mode === "concept") {
				if (!ctx.hasUI) {
					ctx.ui.notify("Usage: /explain concept <topic> or /explain diff [--base=main]", "warning");
					return;
				}
				const concept = await ctx.ui.input("Concept to explain:", "authorization flow, cache invalidation, checkout...");
				if (!concept?.trim()) return;
				opts.query = concept.trim();
			}

			if (!args.trim() && ctx.hasUI) {
				const mode = await ctx.ui.select("Explain what?", ["Concept", "Branch diff"]);
				if (!mode) return;
				opts.mode = mode === "Branch diff" ? "diff" : "concept";
				if (opts.mode === "concept") {
					const concept = await ctx.ui.input("Concept to explain:", "authorization flow, cache invalidation, checkout...");
					if (!concept?.trim()) return;
					opts.query = concept.trim();
				}
			}

			if (opts.mode === "diff" && !opts.query) opts.query = "current branch diff";

			const hasGraph = existsSync(join(ctx.cwd, ".understand-anything", "knowledge-graph.json"));
			ctx.ui.notify(hasGraph ? "Existing Understand-Anything graph found; generating focused graph." : "No existing Understand-Anything graph found; will inspect code directly.", "info");

			pi.sendUserMessage(buildPrompt(ctx, opts as Required<Pick<ExplainOptions, "mode" | "query">> & ExplainOptions));
		},
	});
}
