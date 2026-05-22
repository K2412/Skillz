import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { isToolCallEventType } from "@earendil-works/pi-coding-agent";
import { homedir } from "node:os";
import { resolve } from "node:path";

type BlockRule = {
	name: string;
	pattern: RegExp;
	reason: string;
};

const HOME = homedir();
const PROTECTED_PATHS = [
	resolve(HOME, ".pi", "agent", "extensions", "safety-guard.ts"),
	resolve(HOME, ".pi", "agent", "extensions", "no-push.ts"),
];

const BLOCKED_COMMANDS: BlockRule[] = [
	{
		name: "git-push",
		pattern: /(^|[;&|()\s])git\s+(?:-[^\s]+\s+)*push\b/i,
		reason: "Global no-push policy: Pi may commit locally, but must never push code.",
	},
	{
		name: "beads-dolt-push",
		pattern: /(^|[;&|()\s])bd\s+dolt\s+push\b/i,
		reason: "Global no-push policy: Pi must not push Beads/Dolt state.",
	},
	{
		name: "beads-backup-sync",
		pattern: /(^|[;&|()\s])bd\s+backup\s+sync\b/i,
		reason: "Global no-push policy: Pi must not sync Beads backups.",
	},
	{
		name: "gh-sync",
		pattern: /(^|[;&|()\s])gh\s+repo\s+sync\b/i,
		reason: "Global no-push policy: Pi must not sync repositories.",
	},
	{
		name: "rm-rf",
		pattern: /(^|[;&|()\s])(?:sudo\s+)?rm\s+(?:-[^\s]*[rR][^\s]*[fF][^\s]*|-[^\s]*[fF][^\s]*[rR][^\s]*)(?:\s|$)/i,
		reason: "Destructive action blocked: recursive forced deletion is not allowed.",
	},
	{
		name: "git-clean-force",
		pattern: /(^|[;&|()\s])git\s+clean\s+[^;&|\n]*-[^;&|\n]*[fF][^;&|\n]*[dDxX]/i,
		reason: "Destructive action blocked: forced git clean of directories/ignored files is not allowed.",
	},
	{
		name: "delete-git-dir",
		pattern: /(^|[;&|()\s])(?:sudo\s+)?rm\s+[^;&|\n]*(?:\.git|\.beads)(?:\s|\/|$)/i,
		reason: "Destructive action blocked: deleting repo metadata (.git/.beads) is not allowed.",
	},
	{
		name: "filesystem-format",
		pattern: /(^|[;&|()\s])(?:sudo\s+)?(?:mkfs|diskutil\s+erase|dd\s+[^;&|\n]*\bof=\/dev\/|shred\b|wipefs\b)/i,
		reason: "Destructive action blocked: disk/filesystem wipe commands are not allowed.",
	},
	{
		name: "permission-destruction",
		pattern: /(^|[;&|()\s])(?:sudo\s+)?chmod\s+[^;&|\n]*(?:-R\s+)?(?:000|777)\s+(?:\/|~|\.)(?:\s|$)/i,
		reason: "Destructive action blocked: broad destructive chmod is not allowed.",
	},
	{
		name: "disable-hooks",
		pattern: /(^|[;&|()\s])(?:rm|mv|chmod)\s+[^;&|\n]*(?:\.git\/hooks\/pre-push|safety-guard\.ts|no-push\.ts)/i,
		reason: "Safety policy blocked: disabling push/destructive-action guards is not allowed.",
	},
];

function isProtectedPath(path: string): boolean {
	const resolved = resolve(path.replace(/^~/, HOME));
	return PROTECTED_PATHS.some((protectedPath) => resolved === protectedPath);
}

function blockReasonForCommand(command: string): string | undefined {
	const normalized = command.replace(/\\\n/g, " ");
	for (const rule of BLOCKED_COMMANDS) {
		if (rule.pattern.test(normalized)) return `${rule.reason} [${rule.name}]`;
	}
	return undefined;
}

export default function safetyGuard(pi: ExtensionAPI) {
	pi.on("tool_call", async (event) => {
		if (isToolCallEventType("bash", event)) {
			const reason = blockReasonForCommand(event.input.command ?? "");
			if (reason) return { block: true, reason };
		}

		if (isToolCallEventType("write", event) || isToolCallEventType("edit", event)) {
			if (isProtectedPath(event.input.path)) {
				return {
					block: true,
					reason: "Safety policy blocked: the global safety guard extension cannot be modified by Pi.",
				};
			}
		}
	});

	pi.on("session_start", async (_event, ctx) => {
		ctx.ui.setStatus("safety-guard", ctx.ui.theme.fg("warning", "no-push/no-rm-rf"));
	});
}
