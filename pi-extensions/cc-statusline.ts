import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { truncateToWidth, visibleWidth } from "@earendil-works/pi-tui";
import { execFileSync } from "node:child_process";
import { basename } from "node:path";

type RuntimeState = {
	enabled: boolean;
	busy: boolean;
	phase: string;
	lastTool?: string;
	lastError?: string;
	turnCount: number;
	startedAt: number;
	lastActivityAt: number;
	gitDirty?: boolean;
	gitAheadBehind?: string;
	interval?: NodeJS.Timeout;
};

const state: RuntimeState = {
	enabled: true,
	busy: false,
	phase: "idle",
	turnCount: 0,
	startedAt: Date.now(),
	lastActivityAt: Date.now(),
};

function fmtTokens(n: number | undefined): string {
	if (!Number.isFinite(n ?? NaN)) return "0";
	const value = n ?? 0;
	if (value < 1_000) return String(value);
	if (value < 1_000_000) return `${(value / 1_000).toFixed(value < 10_000 ? 1 : 0)}k`;
	return `${(value / 1_000_000).toFixed(1)}m`;
}

function fmtMoney(n: number): string {
	if (!Number.isFinite(n) || n <= 0) return "$0";
	if (n < 0.01) return `$${n.toFixed(4)}`;
	return `$${n.toFixed(2)}`;
}

function fmtDuration(ms: number): string {
	const seconds = Math.max(0, Math.floor(ms / 1000));
	if (seconds < 60) return `${seconds}s`;
	const minutes = Math.floor(seconds / 60);
	if (minutes < 60) return `${minutes}m`;
	const hours = Math.floor(minutes / 60);
	return `${hours}h${minutes % 60}m`;
}

function markActivity(phase: string, busy = state.busy) {
	state.phase = phase;
	state.busy = busy;
	state.lastActivityAt = Date.now();
}

function refreshGit(cwd: string) {
	try {
		const status = execFileSync("git", ["status", "--porcelain=v1", "--branch"], {
			cwd,
			encoding: "utf8",
			stdio: ["ignore", "pipe", "ignore"],
			timeout: 750,
		});

		const lines = status.trim().split("\n").filter(Boolean);
		state.gitDirty = lines.some((line) => !line.startsWith("## "));

		const header = lines.find((line) => line.startsWith("## ")) ?? "";
		const ahead = header.match(/ahead (\d+)/)?.[1];
		const behind = header.match(/behind (\d+)/)?.[1];
		state.gitAheadBehind = [ahead ? `↑${ahead}` : undefined, behind ? `↓${behind}` : undefined].filter(Boolean).join(" ") || undefined;
	} catch {
		state.gitDirty = undefined;
		state.gitAheadBehind = undefined;
	}
}

function sessionUsage(ctx: any) {
	let input = 0;
	let output = 0;
	let cost = 0;

	for (const entry of ctx.sessionManager.getBranch()) {
		if (entry.type !== "message" || entry.message?.role !== "assistant") continue;
		const usage = entry.message.usage;
		input += usage?.input ?? 0;
		output += usage?.output ?? 0;
		cost += usage?.cost?.total ?? 0;
	}

	return { input, output, cost };
}

function contextText(ctx: any): string | undefined {
	try {
		const usage = ctx.getContextUsage?.();
		if (!usage) return undefined;

		const tokens = usage.tokens ?? usage.usedTokens ?? usage.inputTokens;
		const max = usage.maxTokens ?? usage.contextWindow ?? usage.limit;
		const pct = usage.percentage ?? usage.percent ?? (tokens && max ? (tokens / max) * 100 : undefined);

		if (Number.isFinite(pct)) return `${Math.round(pct)}% ctx`;
		if (Number.isFinite(tokens) && Number.isFinite(max)) return `${fmtTokens(tokens)}/${fmtTokens(max)} ctx`;
		if (Number.isFinite(tokens)) return `${fmtTokens(tokens)} ctx`;
	} catch {
		return undefined;
	}

	return undefined;
}

function joinSegments(width: number, left: string, center: string, right: string): string {
	const leftWidth = visibleWidth(left);
	const centerWidth = visibleWidth(center);
	const rightWidth = visibleWidth(right);
	const minSpaces = 2;

	if (leftWidth + centerWidth + rightWidth + minSpaces * 2 <= width) {
		const remaining = width - leftWidth - centerWidth - rightWidth;
		const first = Math.max(1, Math.floor(remaining / 2));
		const second = Math.max(1, remaining - first);
		return truncateToWidth(left + " ".repeat(first) + center + " ".repeat(second) + right, width);
	}

	if (leftWidth + rightWidth + 1 <= width) {
		return truncateToWidth(left + " ".repeat(width - leftWidth - rightWidth) + right, width);
	}

	return truncateToWidth(`${left} ${right}`, width);
}

export default function ccStatusline(pi: ExtensionAPI) {
	function installFooter(ctx: any) {
		if (!state.enabled || !ctx.hasUI) return;

		ctx.ui.setFooter((tui: any, theme: any, footerData: any) => {
			const unsubscribeBranch = footerData?.onBranchChange?.(() => tui.requestRender()) ?? (() => {});

			return {
				dispose: unsubscribeBranch,
				invalidate() {},
				render(width: number): string[] {
					const usage = sessionUsage(ctx);
					const branch = footerData?.getGitBranch?.();
					const project = basename(ctx.cwd || process.cwd());
					const model = ctx.model ? `${ctx.model.provider}/${ctx.model.id}` : "no-model";
					const dirty = state.gitDirty === true ? "*" : "";
					const aheadBehind = state.gitAheadBehind ? ` ${state.gitAheadBehind}` : "";
					const git = branch ? ` ${branch}${dirty}${aheadBehind}` : "no-git";
					const statusIcon = state.busy ? theme.fg("accent", "●") : theme.fg("success", "✓");
					const phase = state.lastTool ? `${state.phase}:${state.lastTool}` : state.phase;
					const ctxText = contextText(ctx);
					const idleFor = fmtDuration(Date.now() - state.lastActivityAt);

					const left = `${statusIcon} ${theme.fg("text", project)} ${theme.fg("dim", git)}`;
					const centerParts = [
						`turn ${state.turnCount}`,
						phase,
						state.busy ? undefined : `idle ${idleFor}`,
					].filter(Boolean);
					const center = theme.fg(state.busy ? "accent" : "dim", centerParts.join(" · "));
					const rightParts = [
						model,
						`↑${fmtTokens(usage.input)} ↓${fmtTokens(usage.output)}`,
						fmtMoney(usage.cost),
						ctxText,
					].filter(Boolean);
					const right = theme.fg("dim", rightParts.join(" · "));

					return [joinSegments(width, left, center, right)];
				},
			};
		});
	}

	pi.registerCommand("statusline", {
		description: "Toggle the cc-statusline-style footer extension.",
		handler: async (args, ctx) => {
			const value = args.trim().toLowerCase();
			if (value === "on") state.enabled = true;
			else if (value === "off") state.enabled = false;
			else state.enabled = !state.enabled;

			if (state.enabled) {
				installFooter(ctx);
				ctx.ui.notify("Statusline enabled", "info");
			} else {
				ctx.ui.setFooter(undefined);
				ctx.ui.notify("Statusline disabled", "info");
			}
		},
	});

	pi.on("session_start", async (_event, ctx) => {
		state.startedAt = Date.now();
		state.lastActivityAt = Date.now();
		state.turnCount = 0;
		state.lastTool = undefined;
		state.lastError = undefined;
		markActivity("idle", false);
		refreshGit(ctx.cwd);
		installFooter(ctx);

		if (state.interval) clearInterval(state.interval);
		state.interval = setInterval(() => {
			refreshGit(ctx.cwd);
			// Reinstalling the footer is a simple, reliable way to request a redraw
			// across Pi versions without depending on an internal requestRender API.
			installFooter(ctx);
		}, 10_000);
	});

	pi.on("session_shutdown", async (_event, ctx) => {
		if (state.interval) clearInterval(state.interval);
		state.interval = undefined;
		ctx.ui.setFooter(undefined);
	});

	pi.on("model_select", async (_event, ctx) => {
		markActivity("model", false);
		installFooter(ctx);
	});

	pi.on("agent_start", async (_event, ctx) => {
		state.turnCount = 0;
		state.lastTool = undefined;
		markActivity("thinking", true);
		refreshGit(ctx.cwd);
	});

	pi.on("turn_start", async (_event, _ctx) => {
		state.turnCount += 1;
		state.lastTool = undefined;
		markActivity("turn", true);
	});

	pi.on("tool_execution_start", async (event, _ctx) => {
		state.lastTool = event.toolName;
		markActivity("tool", true);
	});

	pi.on("tool_execution_end", async (event, ctx) => {
		state.lastTool = event.toolName;
		state.lastError = event.isError ? event.toolName : undefined;
		markActivity(event.isError ? "tool-error" : "tool-done", true);
		if (["bash", "edit", "write"].includes(event.toolName)) refreshGit(ctx.cwd);
	});

	pi.on("agent_end", async (_event, ctx) => {
		state.lastTool = undefined;
		markActivity("idle", false);
		refreshGit(ctx.cwd);
	});
}
