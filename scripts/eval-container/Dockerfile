# Kit tooling, never shipped in a module: the throwaway image scripts/run-evals.py runs every eval case in
# (decision dec-0093-module-evals-with-local-receipts). It holds no secret of the host: the module's
# copy is mounted read-only, the results folder writable, and the subscription token arrives as an env file.
# The runner builds it as kit-evalbox:<version>-<hash>, the version scripts/claude-code.version pins and the
# first twelve hexadecimal digits of this file's SHA-256, so that a changed file is always built again. Its
# Debian release gives a Python at or above the floor of shared/const_gate/preflight.py, which every module's
# scripts need.
FROM node:22-trixie
ARG CLAUDE_CODE
RUN test -n "$CLAUDE_CODE" \
 && apt-get update \
 && apt-get install -y --no-install-recommends python3-yaml bubblewrap socat ripgrep \
 && rm -rf /var/lib/apt/lists/* \
 && npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE}"
# The tools the modules' scripts call, at the versions the kit's CI installs: Vale for const-language, lychee
# for const-referencing; without them a case's command stops before it does its work. Their versions are typed
# again in .github/workflows/gates.yml, which a change of either follows.
ARG TARGETARCH
RUN case "$TARGETARCH" in \
      arm64) vale=Linux_arm64; lychee=aarch64-unknown-linux-gnu ;; \
      amd64) vale=Linux_64-bit; lychee=x86_64-unknown-linux-gnu ;; \
      *) echo "no Vale and lychee for TARGETARCH '$TARGETARCH': build with BuildKit, on amd64 or arm64" >&2; exit 1 ;; \
    esac \
 && curl -fsSL "https://github.com/errata-ai/vale/releases/download/v3.23.0/vale_3.23.0_${vale}.tar.gz" \
    | tar -xz -C /usr/local/bin vale \
 && curl -fsSL "https://github.com/lycheeverse/lychee/releases/download/lychee-v0.24.2/lychee-${lychee}.tar.gz" \
    | tar -xz -C /usr/local/bin --strip-components=1 "lychee-${lychee}/lychee"
# The shell of every Bash call a case makes: bash with --norc. Claude Code runs each call as `bash -c` under
# its sandbox with a socket on stdin, which bash takes for a remote shell daemon's and so reads ~/.bashrc;
# the sandbox seals the run's home and binds /dev/null over that file, which bash may not open there, so
# without --norc every call's output opens with "/bin/bash: <home>/.bashrc: Permission denied", twice. The
# sandbox itself is unchanged; Claude Code takes the shell from CLAUDE_CODE_SHELL, which the eval passes on.
RUN mkdir -p /usr/local/lib/kit-evalbox \
 && printf '#!/bin/sh\nexec /bin/bash --norc "$@"\n' > /usr/local/lib/kit-evalbox/bash \
 && chmod 755 /usr/local/lib/kit-evalbox/bash
ENV CLAUDE_CODE_SHELL=/usr/local/lib/kit-evalbox/bash
# The names git leaves out of every repository in the image: the sandbox's placeholders. On Linux the sandbox
# holds a write denial on a protected file that does not exist yet by binding /dev/null, or an empty folder,
# over a 0-byte file it creates in the working folder for as long as each Bash call runs (sandboxing docs,
# "Protected paths" and troubleshooting), so every call of a case saw them as untracked, and `git add -A`
# failed on them. Git, in the sandbox too, reads the system config, which names this file; the sandbox itself
# is unchanged. The names are the ones Claude Code of scripts/claude-code.version places in a case's folder,
# read from the kept traces of its runs; a pin move checks them again.
RUN printf '%s\n' \
      /.bash_profile /.bashrc /.eval-artifacts /.gitconfig /.gitmodules /.idea /.mcp.json /.profile \
      /.ripgreprc /.vscode /.zprofile /.zshrc \
      /.claude/agents /.claude/commands /.claude/hooks /.claude/launch.json /.claude/loop.md \
      /.claude/output-styles /.claude/routines /.claude/scheduled_tasks.json /.claude/settings.json \
      /.claude/settings.local.json /.claude/skills /.claude/workflows \
    > /usr/local/lib/kit-evalbox/gitignore \
 && git config --system core.excludesFile /usr/local/lib/kit-evalbox/gitignore
USER node
WORKDIR /home/node
RUN git config --global user.name "Eval" && git config --global user.email "eval@example.invalid"
