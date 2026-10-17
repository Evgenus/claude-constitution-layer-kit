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
# for const-referencing; without them a case's command stops before it does its work.
ARG TARGETARCH
RUN case "$TARGETARCH" in \
      arm64) vale=Linux_arm64; lychee=aarch64-unknown-linux-gnu ;; \
      *) vale=Linux_64-bit; lychee=x86_64-unknown-linux-gnu ;; \
    esac \
 && curl -fsSL "https://github.com/errata-ai/vale/releases/download/v3.23.0/vale_3.23.0_${vale}.tar.gz" \
    | tar -xz -C /usr/local/bin vale \
 && curl -fsSL "https://github.com/lycheeverse/lychee/releases/download/lychee-v0.24.2/lychee-${lychee}.tar.gz" \
    | tar -xz -C /usr/local/bin --strip-components=1 "lychee-${lychee}/lychee"
USER node
WORKDIR /home/node
RUN git config --global user.name "Eval" && git config --global user.email "eval@example.invalid"
