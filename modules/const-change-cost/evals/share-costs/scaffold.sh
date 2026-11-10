#!/bin/sh
# Seeds the run's working folder: a small inventory tool on its main branch, a branch of two commits ahead of
# it, both hooks of the commit log set in git's configuration, and the two commits' counts kept in the
# module's folder of the git common directory, so that the report needs no ccusage. A post-merge and a
# post-commit hook of git's own folder copy the message of HEAD, when HEAD is a merge commit, into
# merge-message.txt at the top of the work tree, which the exclude file keeps out of git and where a grader
# reads it: the eval's git is older than the one that runs hooks set in its configuration, a message is no
# file, and the post-commit hook keeps the file current after a merge concluded with --no-commit or amended.
set -e
git init -q -b main
git config user.name "Eval"
git config user.email "eval@example.invalid"
# The sandbox's placeholders: on Linux, for as long as each Bash call runs, Claude Code's sandbox holds a
# write denial on a protected file that does not exist yet with a 0-byte file in this folder. Left out of git
# here, they never stand as untracked files and `git add -A` does not fail on them; the eval gives the
# session's git no system config, so this repository's own exclude file is where they are named.
printf '%s\n' \
  /.bash_profile /.bashrc /.eval-artifacts /.gitconfig /.gitmodules /.idea /.mcp.json /.profile \
  /.ripgreprc /.vscode /.zprofile /.zshrc \
  /.claude/agents /.claude/commands /.claude/hooks /.claude/launch.json /.claude/loop.md \
  /.claude/output-styles /.claude/routines /.claude/scheduled_tasks.json /.claude/settings.json \
  /.claude/settings.local.json /.claude/skills /.claude/workflows \
  /merge-message.txt \
  >> .git/info/exclude
mkdir -p src
cat > src/inventory.py <<'END_OF_FILE'
def count_items(items: list[str]) -> int:
    """The number of items in stock."""
    return len(items)
END_OF_FILE
git add -A
git commit -q -m "Start the inventory tool"
git checkout -q -b work/report-total
cat >> src/inventory.py <<'END_OF_FILE'


def report(items: list[str]) -> str:
    return f"{count_items(items)} item(s) in stock"
END_OF_FILE
git commit -q -am "Add the stock report"
sed -i.bak "s/item(s) in stock/item(s) in stock in total/" src/inventory.py
rm -f src/inventory.py.bak
git commit -q -am "Say in total in the report"
git checkout -q main

# Both hooks of the commit log, as the setup command writes them into git's configuration. The commands are
# placeholders: no hook is needed to read the counts.
git config hook.const-change-cost-commit.command true
git config hook.const-change-cost-commit.event post-commit
git config hook.const-change-cost-merge.command true
git config hook.const-change-cost-merge.event post-merge

# The kept counts of the branch's two commits and their lines in the commit log.
logs="$(git rev-parse --git-common-dir)/const-change-cost"
mkdir -p "$logs"
session=aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa
first=$(git rev-parse work/report-total~1)
second=$(git rev-parse work/report-total)
printf '{"sha":"%s","ms":1793527205500,"session":"%s","event":"commit"}\n' "$first" "$session" >> "$logs/commits.jsonl"
printf '{"sha":"%s","ms":1793527210500,"session":"%s","event":"commit"}\n' "$second" "$session" >> "$logs/commits.jsonl"
printf '{"sha":"%s","session":"%s","input":1200,"output":340,"cache_write":5000,"cache_read":20000,"total":26540,"cost":0.0521,"replies":6,"models":{"claude-sonnet-4-5-20250929":26540},"compactions":0,"unpriced":[],"ccusage":"20.0.48","counted_ms":1793527300000}\n' "$first" "$session" >> "$logs/counts.jsonl"
printf '{"sha":"%s","session":"%s","input":800,"output":210,"cache_write":0,"cache_read":25000,"total":26010,"cost":0.0214,"replies":4,"models":{"claude-sonnet-4-5-20250929":26010},"compactions":0,"unpriced":[],"ccusage":"20.0.48","counted_ms":1793527300000}\n' "$second" "$session" >> "$logs/counts.jsonl"

for hook in post-merge post-commit; do
  cat > ".git/hooks/$hook" <<'END_OF_FILE'
#!/bin/sh
if git rev-parse -q --verify HEAD^2 >/dev/null; then
  git log -1 --format=%B HEAD > "$(git rev-parse --show-toplevel)/merge-message.txt"
fi
END_OF_FILE
  chmod +x ".git/hooks/$hook"
done
