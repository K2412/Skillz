/**
 * AskUserQuestion tool compatibility extension.
 *
 * Provides a Claude-style selectable question tool for skills that instruct the
 * assistant to call `AskUserQuestion` with options and descriptions.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Editor, type EditorTheme, Key, matchesKey, Text, truncateToWidth } from "@earendil-works/pi-tui";
import { Type } from "typebox";

interface OptionWithDesc {
	label: string;
	description?: string;
}

type DisplayOption = OptionWithDesc & { isOther?: boolean };

interface QuestionDetails {
	question: string;
	options: string[];
	answer: string | null;
	wasCustom?: boolean;
}

const OptionSchema = Type.Object({
	label: Type.String({ description: "Display label for this option" }),
	description: Type.Optional(Type.String({ description: "Optional explanation shown under the label" })),
});

const ParamsSchema = Type.Object({
	question: Type.String({ description: "The question to ask the user" }),
	options: Type.Array(OptionSchema, {
		description: "2-4 concrete answer options. Put the recommended option first and include '(Recommended)' in its label when appropriate.",
	}),
});

export default function askUserQuestion(pi: ExtensionAPI) {
	pi.registerTool({
		name: "AskUserQuestion",
		label: "Ask User Question",
		description:
			"Ask the user a question with selectable options. Use this when a skill requires AskUserQuestion or when user input is needed to proceed.",
		parameters: ParamsSchema,

		async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
			if (!ctx.hasUI) {
				return {
					content: [{ type: "text", text: "Error: UI not available; ask the question as numbered text instead." }],
					details: {
						question: params.question,
						options: params.options.map((option) => option.label),
						answer: null,
					} as QuestionDetails,
				};
			}

			if (params.options.length === 0) {
				return {
					content: [{ type: "text", text: "Error: No options provided" }],
					details: { question: params.question, options: [], answer: null } as QuestionDetails,
				};
			}

			const allOptions: DisplayOption[] = [...params.options, { label: "Other", description: "Type a custom answer.", isOther: true }];

			const result = await ctx.ui.custom<{ answer: string; wasCustom: boolean; index?: number } | null>(
				(tui, theme, _keybindings, done) => {
					let optionIndex = 0;
					let editMode = false;
					let cachedLines: string[] | undefined;

					const editorTheme: EditorTheme = {
						borderColor: (text) => theme.fg("accent", text),
						selectList: {
							selectedPrefix: (text) => theme.fg("accent", text),
							selectedText: (text) => theme.fg("accent", text),
							description: (text) => theme.fg("muted", text),
							scrollInfo: (text) => theme.fg("dim", text),
							noMatch: (text) => theme.fg("warning", text),
						},
					};
					const editor = new Editor(tui, editorTheme);

					editor.onSubmit = (value) => {
						const answer = value.trim();
						if (answer) {
							done({ answer, wasCustom: true });
							return;
						}

						editMode = false;
						editor.setText("");
						refresh();
					};

					function refresh() {
						cachedLines = undefined;
						tui.requestRender();
					}

					function handleInput(data: string) {
						if (editMode) {
							if (matchesKey(data, Key.escape)) {
								editMode = false;
								editor.setText("");
								refresh();
								return;
							}

							editor.handleInput(data);
							refresh();
							return;
						}

						if (matchesKey(data, Key.up)) {
							optionIndex = Math.max(0, optionIndex - 1);
							refresh();
							return;
						}

						if (matchesKey(data, Key.down)) {
							optionIndex = Math.min(allOptions.length - 1, optionIndex + 1);
							refresh();
							return;
						}

						if (matchesKey(data, Key.enter)) {
							const selected = allOptions[optionIndex];
							if (selected.isOther) {
								editMode = true;
								refresh();
								return;
							}

							done({ answer: selected.label, wasCustom: false, index: optionIndex + 1 });
							return;
						}

						if (matchesKey(data, Key.escape)) {
							done(null);
						}
					}

					function render(width: number): string[] {
						if (cachedLines) return cachedLines;

						const lines: string[] = [];
						const add = (line: string) => lines.push(truncateToWidth(line, width));

						add(theme.fg("accent", "─".repeat(width)));
						add(theme.fg("text", ` ${params.question}`));
						lines.push("");

						for (let i = 0; i < allOptions.length; i++) {
							const option = allOptions[i];
							const selected = i === optionIndex;
							const prefix = selected ? theme.fg("accent", "> ") : "  ";
							const label = `${i + 1}. ${option.label}${option.isOther && editMode ? " ✎" : ""}`;

							add(prefix + (selected ? theme.fg("accent", label) : theme.fg("text", label)));

							if (option.description) {
								add(`     ${theme.fg("muted", option.description)}`);
							}
						}

						if (editMode) {
							lines.push("");
							add(theme.fg("muted", " Your answer:"));
							for (const line of editor.render(width - 2)) {
								add(` ${line}`);
							}
						}

						lines.push("");
						add(theme.fg("dim", editMode ? " Enter to submit • Esc to go back" : " ↑↓ navigate • Enter to select • Esc to cancel"));
						add(theme.fg("accent", "─".repeat(width)));

						cachedLines = lines;
						return lines;
					}

					return {
						render,
						invalidate: () => {
							cachedLines = undefined;
						},
						handleInput,
					};
				},
			);

			const simpleOptions = params.options.map((option) => option.label);

			if (!result) {
				return {
					content: [{ type: "text", text: "User cancelled the selection" }],
					details: { question: params.question, options: simpleOptions, answer: null } as QuestionDetails,
				};
			}

			const details = {
				question: params.question,
				options: simpleOptions,
				answer: result.answer,
				wasCustom: result.wasCustom,
			} as QuestionDetails;

			// Persist human decisions so orchestrators can turn the final agreed plan
			// into durable task graphs (for example Beads parent/child work items).
			try {
				pi.appendEntry("ask-user-question-decision", {
					...details,
					answeredAt: new Date().toISOString(),
				});
			} catch {
				// Persistence is best-effort; never fail the user interaction.
			}

			return {
				content: [
					{
						type: "text",
						text: result.wasCustom ? `User wrote: ${result.answer}` : `User selected: ${result.index}. ${result.answer}`,
					},
				],
				details,
			};
		},

		renderCall(args, theme) {
			let text = theme.fg("toolTitle", theme.bold("AskUserQuestion ")) + theme.fg("muted", args.question);
			const options = Array.isArray(args.options) ? args.options : [];
			if (options.length) {
				const labels = [...options.map((option: OptionWithDesc) => option.label), "Other"];
				text += `\n${theme.fg("dim", `  Options: ${labels.map((label, index) => `${index + 1}. ${label}`).join(", ")}`)}`;
			}
			return new Text(text, 0, 0);
		},

		renderResult(result, _options, theme) {
			const details = result.details as QuestionDetails | undefined;
			if (!details) {
				const first = result.content[0];
				return new Text(first?.type === "text" ? first.text : "", 0, 0);
			}

			if (details.answer === null) {
				return new Text(theme.fg("warning", "Cancelled"), 0, 0);
			}

			if (details.wasCustom) {
				return new Text(theme.fg("success", "✓ ") + theme.fg("muted", "(other) ") + theme.fg("accent", details.answer), 0, 0);
			}

			const index = details.options.indexOf(details.answer) + 1;
			return new Text(theme.fg("success", "✓ ") + theme.fg("accent", index > 0 ? `${index}. ${details.answer}` : details.answer), 0, 0);
		},
	});
}
