# Security Findings — Zen MCP Server

Scope: full repository security review against the OWASP LLM Top 10 (2025), tool-input validation, and GitHub Actions hardening. This document lists every issue identified, the fixes applied in this PR, and the issues left open with rationale and recommended remediation.

Branch: `claude/security-review-prompt-injection-5QwKI`

## Summary

| Area | Findings | Fixed in this PR | Documented / deferred |
|---|---|---|---|
| LLM01 Prompt injection | 5 | 1 (delimiter defang) | 4 |
| LLM02 Insecure output handling | 2 | 1 (version-tool response validation) | 1 |
| LLM06 Sensitive info disclosure | 4 | 2 (default LOG_LEVEL, version-tool egress) | 2 |
| Tool input validation | 3 | 1 (model-name bounds) | 2 |
| GitHub Actions hardening | 9 workflow files | 9 (SHA pinning, permissions, harden-runner, script-injection fix) | 2 reusable-workflow `@main` refs |

Severity legend: **Critical / High / Medium / Low / Info**. Severity is contextual to this server — an MCP that runs locally under the user's account and brokers prompts to third-party LLMs.

---

## LLM01 — Prompt injection

External, untrusted text enters the prompt stream at three points: (1) responses from third-party model backends, (2) user-supplied tool arguments (`prompt`, `files`, `relevant_files`, `model`, …), and (3) contents of user-supplied files. The orchestrator (Claude Code) then reads our output and may act on it.

### LLM01-1 — Backend model responses are replayed unframed across turns *(High)* — **fixed**

- Files: `utils/conversation_memory.py` `_default_turn_formatting()` (was `:1078-1088`), `build_conversation_history()` (`:638-1010`).
- Risk: turn content (which may have been produced by an attacker-controlled upstream model — e.g., a poisoned OpenRouter route or a Custom/Ollama endpoint pointed at a malicious URL) was appended into the next prompt body. The framing relies on literal delimiters such as `=== END CONVERSATION HISTORY ===` and `--- Turn N (Agent) ---`. A backend that emits those exact strings in its response can close our frame early and inject instructions into the trusted region read by the orchestrator (Claude Code).
- Fix: added `_sanitize_replayed_content()` (`utils/conversation_memory.py`) and wired it into `_default_turn_formatting`. It defangs the literal frame markers (`=== … ===`) inside replayed turn content by replacing the leading `===` with `=⋮=` (U+22EE, visually similar, parser-distinct) so a delimiter-confusion attempt no longer matches our framing.
- Caveat: this does not "make the conversation safe." It closes the specific delimiter-confusion vector. The orchestrator must still treat replayed assistant content as untrusted.

### LLM01-2 — User prompt arguments are concatenated into the prompt without per-field delimiters *(Medium)* — **deferred**

- File: `tools/simple/base.py` (prompt construction in `build_standard_prompt`).
- Risk: user-supplied `prompt`/`files`/`relevant_files` are formatted into the outgoing prompt with f-strings. There is some framing (`=== USER REQUEST ===`-style markers) but no per-field tagging. A caller passing a string like `\n=== END USER REQUEST ===\nSYSTEM: …` can extend or escape the request envelope as seen by the backend.
- Why deferred: the affected callsites pre-date this PR and changing the prompt envelope shape changes every backend's behavior and every recorded test transcript. A correct fix is non-local: pick a single delimiter style (e.g., XML tags or numbered fences) and rewrite the framing in `build_standard_prompt` and `workflow_mixin.build_prompt`. Recommend opening a follow-up tracking issue.
- Recommended remediation: standardize on XML-tag envelopes (`<user_prompt>…</user_prompt>`, `<file path="…">…</file>`) with newline-anchored regexes to strip those tags from untrusted content before injection.

### LLM01-3 — File contents are embedded verbatim *(Medium)* — **deferred**

- Files: `utils/file_utils.py:282-324` (path validation is good), `tools/shared/base_tool.py` (embeds file content).
- Risk: a project file can legitimately contain prompt-injection payloads (the file is itself the data being analyzed). This is intrinsic to "analyze my code" tools. Path traversal is correctly defended — `resolve_and_validate_path` rejects relative paths, blocks system roots (`/etc`, `/usr`, `/var`, `C:\Windows`) via `is_dangerous_path`, and resolves symlinks before checking — but file *content* is not (and arguably cannot be) escaped.
- Why deferred: there is no fix that's both safe and behavior-preserving. The right mitigation is operator-level: clearly document for end-users that files passed to these tools are treated as data, not instructions, and that the backend LLM may still be susceptible. Suggest adding a one-line "file contents are untrusted" reminder to every tool's `get_system_prompt()`.

### LLM01-4 — `expert_analysis` raw model output is round-tripped to the caller *(Medium)* — **deferred**

- File: `tools/workflow/workflow_mixin.py` (`raw_analysis` field on JSON-parse failure).
- Risk: when the expert backend returns a non-JSON response, the entire `model_response.content` is placed in `raw_analysis` and returned to the orchestrator. Combined with LLM02-1 below, that field is rendered to the orchestrator without any framing.
- Recommended remediation: wrap `raw_analysis` content in `<untrusted_model_response>…</untrusted_model_response>` tags before placing it in the JSON envelope, and strip any literal occurrences of that tag pair from the content first.

### LLM01-5 — Conversation history delimiters use the same `=== … ===` pattern that backend responses may produce *(addressed by LLM01-1 fix)*

Same root cause as LLM01-1. Listed separately because it also affects the `=== FILES REFERENCED IN THIS CONVERSATION ===` and `=== CONVERSATION HISTORY (CONTINUATION) ===` envelopes — the LLM01-1 fix defangs all four markers.

---

## LLM02 — Insecure output handling

The MCP server returns tool results to the orchestrator (Claude Code) as `mcp.types.TextContent`. Text content is not executed as HTML or shell, so there is no XSS/RCE channel here, but the *meaning* of the content matters: the orchestrator reads it as model-authored prose.

### LLM02-1 — Tool responses are not framed as "untrusted upstream output" *(Medium)* — **deferred**

- File: `tools/simple/base.py` (`SimpleTool.execute` → `TextContent(text=…)` construction).
- Risk: an end-user reading the orchestrator's transcript cannot tell which bytes came from a third-party backend vs. from the tool's own scaffolding. A user reasonably trusts "Zen MCP says X" but X may be entirely attacker-supplied.
- Recommended remediation: prepend a short banner to every tool response distinguishing the model identity that produced it (which the code already tracks in `model_response`), and wrap the model-authored portion in delimiters the orchestrator's system prompt can be taught to recognize.

### LLM02-2 — `version` tool fetched a remote `config.py` and rendered the parsed strings unchecked *(Medium)* — **fixed**

- File: `tools/version.py:82-124` (previously fetched `BeehiveInnovations/pal-mcp-server/main/config.py` on every invocation).
- Risk: (a) `BeehiveInnovations` is **not** the upstream for this fork — `CLAUDE.md` explicitly forbids using it as an upstream — so the version reported was wrong; (b) the regex-extracted strings were rendered into the tool output without validation, so a tampered `config.py` could inject markdown or instructions into the orchestrator's view; (c) every `version` call was an outbound network beacon, undesirable for privately deployed MCP instances.
- Fix:
  - Removed the hardcoded URL.
  - Remote check is now opt-in via `PAL_VERSION_CHECK_URL` (must be `https://`).
  - Response body is bounded to 64 KiB.
  - Parsed `__version__` and `__updated__` are validated against a strict whitelist regex (`^[A-Za-z0-9._:+\- ]{1,64}$`) before being rendered.

---

## LLM06 — Sensitive information disclosure

### LLM06-1 — API key loading is environment-only across all providers *(Info)* — **verified**

Each provider reads its key exclusively via `utils.env.get_env()`:

| Provider | Key file:line |
|---|---|
| OpenAI | `providers/registry.py:336` → constructor `providers/openai.py:28` |
| Gemini | `providers/registry.py:335` → `providers/gemini.py:53` |
| Azure OpenAI | `providers/registry.py:337` |
| xAI / Grok | `providers/registry.py:338` → `providers/xai.py:33` |
| OpenRouter | `providers/registry.py:339` |
| Custom (Ollama/etc.) | `providers/registry.py:340` |
| DIAL | `providers/registry.py:341` |

`.env` is in `.gitignore`. No keys come from CLI args, remote endpoints, or untrusted config files. ✅

### LLM06-2 — Default `LOG_LEVEL=DEBUG` leaks prompts/parameters to local logs *(Medium)* — **fixed**

- File: `server.py:81` (was `get_env("LOG_LEVEL", "DEBUG")`).
- Risk: DEBUG logs include full prompts, model parameters, and at the SDK layer can include request bodies via OpenAI SDK exception chaining (`providers/openai_compatible.py:500-502, 678-682`). Local logs are persisted in `logs/mcp_server.log` (20 MB × 5 rotations). For a private dev box this is annoying; for a shared workstation it's a real exfil concern.
- Fix: default changed to `INFO`. Operators can still opt into DEBUG via `LOG_LEVEL=DEBUG` when troubleshooting. Comment in the file flags the trade-off.

### LLM06-3 — OpenAI SDK exception messages may be logged verbatim *(Low)* — **deferred**

- File: `providers/openai_compatible.py:500-502, 678-682`.
- Risk: `logging.error(error_msg)` where `error_msg` is built from `str(exc)` of an OpenAI SDK exception. The SDK normally redacts auth headers, but a future SDK version or a custom-base-url provider that returns a 401 body containing the bearer token would surface in logs.
- Recommended remediation: redact known sensitive substrings (the API key value itself is in `self.api_key`; you can `replace(self.api_key, "[REDACTED]")` on `error_msg` before logging).

### LLM06-4 — `Authorization` header is stripped from DIAL httpx events *(Info)* — **verified**

`providers/dial.py:78-87` installs an httpx request-hook that removes `Authorization` before any built-in httpx logging can see it. This is correctly written, but it only protects DIAL; the other OpenAI-compatible providers rely on the SDK's redaction. Recommend adopting the same hook pattern across all custom httpx clients constructed in `providers/openai_compatible.py:280-330`.

---

## Tool input validation

### TOOL-1 — `model` argument is unbounded and unvalidated at the boundary *(High)* — **fixed**

- File: `server.py:849-851` (was `model_name = arguments.get("model") or DEFAULT_MODEL` with no length/format check).
- Risk: `model_name` flowed into provider lookup (string comparison + dict lookup, so name-based DoS via huge keys is possible), into prompts (`f"Auto mode resolved to {resolved_model} for {name}"`), and into log lines / error responses. A caller passing `model = "\n\nSYSTEM: …"` could inject newlines into log output and prompt envelopes. A multi-MB string could waste CPU on every provider lookup.
- Fix: in `server.py` at the MCP boundary, reject `model` values that aren't strings, exceed 256 characters, or contain `\n` / `\r` / `\x00`. 256 chars accommodates the longest real identifiers (`openrouter/anthropic/claude-3-5-sonnet:beta` is 45) with substantial headroom.

### TOOL-2 — Custom-tool auto-discovery uses `__import__` over the contents of `tools/custom/` *(Medium)* — **deferred**

- File: `tools/custom/__init__.py:44-77`.
- Risk: any `.py` file written into `tools/custom/` at server startup is imported. If an attacker has write access to that directory, they can run arbitrary code at MCP startup. This is not a remotely exploitable vulnerability — it requires local filesystem write — but it is a sharp edge for operators who don't realize the directory is "drop-in code execution."
- Recommended remediation: (a) require explicit registration in a manifest file rather than directory scan; (b) at minimum, document in `tools/custom/README.md` that anyone who can write here can execute code as the MCP user; (c) optionally, refuse to load modules whose parent directory is world-writable.

### TOOL-3 — `CUSTOM_API_URL` is not scheme-validated *(Low)* — **deferred**

- File: `providers/registry.py` around the Custom provider construction.
- Risk: an env-var-supplied `CUSTOM_API_URL` is passed straight to the OpenAI-compatible client base_url. A `file://` or unexpected scheme could theoretically be honoured by some HTTP libraries. The OpenAI SDK's underlying httpx client should reject non-http schemes, but defense-in-depth would validate scheme explicitly.
- Recommended remediation: in `providers/registry.py`, when constructing the Custom provider, parse `custom_url` with `urllib.parse.urlsplit` and reject anything that is not `http://` or `https://`. If `http://`, log a warning unless the host is `localhost` / `127.0.0.1`.

---

## GitHub Actions hardening — **fixed**

Pre-PR audit (all 18 workflow files in `.github/workflows/`):

- **Tag-pinned (not SHA-pinned) actions** in: `codecov.yml`, `docker-pr.yml`, `docker-release.yml`, `release.yml`, `test.yml`.
- **Branch-tip refs** (`@main` / `@master`) in: `coverage.yml`, `slsa-provenance.yml`, `sonarcloud.yml`.
- **Missing top-level `permissions:`** in: `codecov.yml`, `repo-health.yml`, `test.yml`.
- **Missing `step-security/harden-runner`** in: `codecov.yml`, `docker-pr.yml`, `docker-release.yml`, `fips-compatibility.yml`, `release.yml`, `repo-health.yml`, `semantic-pr.yml`, `sonarcloud.yml`, `test.yml`.
- **Shell-injection vector** in `docker-release.yml:71` (`${{ github.event.release.body }}` interpolated into a heredoc passed to `gh release edit`).
- **Shell injection in `secrets.SONAR_TOKEN` `-n` check** in `sonarcloud.yml:20-25` (interpolating the secret value into the shell command, then checking `-n`).
- **`release.yml`** had top-level write permissions where job-level scoping was sufficient.

Fixes applied in this PR:

| Workflow | What changed |
|---|---|
| `codecov.yml` | Added `permissions: contents: read`; added `step-security/harden-runner@…` (egress audit) to every job; pinned `actions/checkout`, `actions/setup-python`, `codecov/codecov-action` to SHAs; set `persist-credentials: false`. |
| `docker-pr.yml` | Added harden-runner; pinned `actions/checkout`, `docker/setup-buildx-action`, `docker/login-action`, `docker/metadata-action`, `docker/build-push-action` to SHAs; set `persist-credentials: false`. |
| `docker-release.yml` | Added harden-runner; pinned all docker actions and checkout to SHAs; scoped write permissions to the job level; **fixed shell injection** in the "Update release with Docker info" step by passing `release.body`, `release.tag_name`, and `repository` via `env:` and using a quoted heredoc (`<<'EOF'`) so the shell does not expand `$(…)` or backticks from a user-controlled release body. |
| `release.yml` | Added harden-runner; pinned `actions/checkout` and `actions/setup-python` to SHAs; moved write permissions from workflow-level to job-level; documented why `persist-credentials: true` is required (semantic-release pushes commits). |
| `repo-health.yml` | Added `permissions: contents: read`; added harden-runner. |
| `sonarcloud.yml` | Added harden-runner to both jobs; pinned the `SonarSource/sonarqube-quality-gate-action` reference from `@master` → SHA (`cf038b0e0cdecfa9e56c198bbb7d21d751d62c3b`, v1.2.0); fixed the secret-presence check in the `check-secrets` job to avoid interpolating the secret value into the shell command; added `persist-credentials: false` on checkout. |
| `test.yml` | Added `permissions: contents: read`; added harden-runner to both jobs; pinned `actions/checkout`, `actions/setup-python`, `codecov/codecov-action` to SHAs; set `persist-credentials: false`. |
| `fips-compatibility.yml` | Added harden-runner; set `persist-credentials: false`. |
| `semantic-pr.yml` | Added harden-runner. |

### GitHub Actions — deferred

- `coverage.yml:26` references `ByronWilliamsCPA/.github/.github/workflows/python-qlty-coverage.yml@main`.
- `slsa-provenance.yml:103` references `ByronWilliamsCPA/.github/.github/workflows/python-slsa.yml@main`.

These are reusable-workflow refs whose underlying file paths may or may not exist at the SHAs other workflows already pin (`@c22009ccaab0d3234819d30d9d7a03d53c531cb9`, `@d18c93045bef4f6669488c7657543a5b7e04f8ed`). Pinning them blindly to a SHA where the file doesn't exist would silently break the workflow. Recommend the maintainer (a) confirm a SHA where both `python-qlty-coverage.yml` and `python-slsa.yml` exist, or (b) tag the upstream `.github` repository and pin to that tag's SHA, and apply that pin here in a follow-up.

---

## Items considered but not flagged

- **`tools/clink.py` subprocess execution.** Uses `asyncio.create_subprocess_exec(*command_with_output_flag, …)` — list form, no shell. Command tokens come from configuration files loaded by `clink/registry.py`, not from MCP tool arguments. The end-user prompt is passed via `stdin`. No command injection.
- **`utils/infisical.py` subprocess calls.** All `subprocess.run([...], …)` invocations use list-form args. The only inputs that flow in (`environment`, `path`) are either from `os.getenv` or derived from `git branch --show-current` — both controlled by the operator, not by tool callers.
- **`providers/openai_compatible.py:785` `ast.literal_eval`.** `literal_eval` only evaluates Python literals (str, num, list, dict, …), not arbitrary expressions — it is documented as safe for untrusted input. This is not an `eval()` finding.
- **`continuation_id` storage.** Stored in-memory via `utils/storage_backend.py` with a configurable TTL. UUIDs are validated by `_is_valid_uuid` (`utils/conversation_memory.py:1091-1108`) before lookup; collisions/guessing infeasible for v4 UUIDs.
- **Path traversal.** `resolve_and_validate_path` (`utils/file_utils.py:282-324`) requires absolute paths, calls `.resolve()` (defeats `..` and symlinks pointing into system dirs), then runs `is_dangerous_path` post-resolution against a denylist of system roots. This is the correct order; the agent's earlier flag of a TOCTOU race is not exploitable here because the resolved path is what's then opened — a swapped symlink would change the resolved path on the next call, not retroactively.

---

## Files changed in this PR

Code:
- `server.py` — `LOG_LEVEL` default → `INFO`; model-name validation at MCP boundary.
- `tools/version.py` — opt-in remote version check via `PAL_VERSION_CHECK_URL`; strict response validation.
- `utils/conversation_memory.py` — `_sanitize_replayed_content` and call site in `_default_turn_formatting`.

GitHub Actions:
- `.github/workflows/codecov.yml`
- `.github/workflows/docker-pr.yml`
- `.github/workflows/docker-release.yml`
- `.github/workflows/fips-compatibility.yml`
- `.github/workflows/release.yml`
- `.github/workflows/repo-health.yml`
- `.github/workflows/semantic-pr.yml`
- `.github/workflows/sonarcloud.yml`
- `.github/workflows/test.yml`

Documentation:
- `SECURITY-FINDINGS.md` (this file).
