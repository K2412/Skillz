# Command Catalog

Use these patterns to investigate repositories safely.

## Discovery

- `rg --files`
- `rg -n "<pattern>" <path>`
- `find <path> -maxdepth <n> -type f`
- `ls -la <path>`

## File inspection

- `sed -n '<start>,<end>p' <file>`
- `cat <file>`
- `wc -l <file>`

## Read-only git history

- `git status --short`
- `git rev-parse --abbrev-ref HEAD`
- `git log --oneline -- <path>`
- `git log --stat -- <path>`
- `git show <commit>`
- `git show <commit>:<path>`
- `git blame -L <start>,<end> <file>`
- `git grep -n "<pattern>"`

## Preferred search strategy

1. `rg --files` to learn the layout.
2. `rg -n` to locate symbols and call sites.
3. `git log/show/blame` to explain history and ownership.
4. Re-check with focused `rg -n` before concluding.

## Disallowed by default

Do not use these unless the user explicitly requests a workflow that needs them:

- `git reset --hard`
- `git checkout -- <path>`
- `git clean -fd`
- `git rebase`
- `git cherry-pick`
- `git commit`
- `git push --force`

If mutation is requested, acknowledge risk and prefer the least destructive option.
