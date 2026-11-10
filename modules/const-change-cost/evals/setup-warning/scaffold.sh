#!/bin/sh
# Seeds the run's working folder: a small inventory tool on its main branch whose git configuration lacks both
# hooks of the commit log, so that the start line of the plugin names them.
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
  >> .git/info/exclude
cat > README.md <<'END_OF_FILE'
# Inventory

A small tool that counts the items in stock. It can recieve a list of item names and print how many
there are.
END_OF_FILE
git add -A
git commit -q -m "Start the inventory tool"
