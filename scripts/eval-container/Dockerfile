# Kit tooling, never shipped in a module: the throwaway image scripts/run-evals.py --container runs the eval
# cases in (decision dec-0093-module-evals-with-local-receipts). It holds no secret of the host: the module's
# copy is mounted read-only, the results folder writable, and the subscription token arrives as an env file.
# The runner builds it as kit-evalbox:<version>, the version scripts/claude-code.version pins.
FROM node:22-bookworm
ARG CLAUDE_CODE
RUN test -n "$CLAUDE_CODE" \
 && apt-get update \
 && apt-get install -y --no-install-recommends python3-yaml bubblewrap socat ripgrep \
 && rm -rf /var/lib/apt/lists/* \
 && npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE}"
USER node
WORKDIR /home/node
RUN git config --global user.name "Eval" && git config --global user.email "eval@example.invalid"
