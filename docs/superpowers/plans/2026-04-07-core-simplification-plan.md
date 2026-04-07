# Core Simplification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Simplify Hermes Agent to core API-only mode - delete CLI, all channel adapters, unused tools/skills, and other non-core components.

**Architecture:** GatewayRunner with --api-only flag loads only APIServerAdapter. New `hermes serve` command starts the API server directly. All messaging platform adapters, CLI tools, and niche skills removed.

**Tech Stack:** Python 3.11, aiohttp, SQLite, OpenAI-compatible API

---

## File Map

### New Files
- `serve.py` — New `hermes serve` command entry point (root level, replaces hermes_cli/)

### Modified Files
- `gateway/run.py` — Add `api_only` parameter to GatewayRunner, skip non-api adapters
- `model_tools.py` — Remove imports of deleted tools
- `hermes` (shell script) — Add `serve` subcommand

### Deleted Directories/Files
```
cli.py
hermes_cli/
acp_adapter/
rl_cli.py
batch_runner.py
trajectory_compressor.py
tinker-atropos/
environments/
gateway/platforms/telegram.py
gateway/platforms/discord.py
gateway/platforms/slack.py
gateway/platforms/whatsapp.py
gateway/platforms/signal.py
gateway/platforms/matrix.py
gateway/platforms/mattermost.py
gateway/platforms/email.py
gateway/platforms/sms.py
gateway/platforms/dingtalk.py
gateway/platforms/feishu.py
gateway/platforms/wecom.py
gateway/platforms/homeassistant.py
gateway/platforms/webhook.py
tools/terminal_tool.py
tools/code_execution_tool.py
tools/voice_mode.py
tools/tts_tool.py
tools/transcription_tools.py
tools/image_generation_tool.py
tools/rl_training_tool.py
tools/send_message_tool.py
tools/approval.py
tools/cronjob_tools.py
tools/checkpoint_manager.py
tools/process_registry.py
tools/mixture_of_agents_tool.py
tools/memory_tool.py
tools/homeassistant_tool.py
tools/vision_tools.py
tools/browser_providers/
skills/apple/
skills/creative/
skills/domain/
skills/feeds/
skills/gaming/
skills/gifs/
skills/inference-sh/
skills/media/
skills/mlops/
skills/note-taking/
skills/research/
skills/smart-home/
skills/social-media/
optional-skills/
```

### Skills Kept
- `skills/autonomous-ai-agents/`
- `skills/productivity/`
- `skills/github/`
- `skills/data-science/`
- `skills/diagramming/`
- `skills/mcp/`

---

## Task 1: Add `--api-only` Flag to GatewayRunner

**Files:**
- Modify: `gateway/run.py`

- [ ] **Step 1: Read current GatewayRunner signature**

Run: Read `gateway/run.py` lines 460-520 to find `__init__` method.

- [ ] **Step 2: Add `api_only` parameter to GatewayRunner.__init__**

In `gateway/run.py` around line 462, find:
```python
class GatewayRunner:
    def __init__(self, config: Optional[GatewayConfig] = None):
```

Add `api_only: bool = False` parameter:
```python
class GatewayRunner:
    def __init__(self, config: Optional[GatewayConfig] = None, *, api_only: bool = False):
        self.api_only = api_only
```

- [ ] **Step 3: Find platform adapter loading code**

Run: Grep for `_load_platform_adapter` or similar in `gateway/run.py`. Around line 1540-1600 you should find imports like:
```python
from gateway.platforms.telegram import TelegramAdapter, check_telegram_requirements
from gateway.platforms.discord import DiscordAdapter, check_discord_requirements
...
```

- [ ] **Step 4: Wrap platform loading in `if not self.api_only:` block**

Wrap all platform adapter imports/loading (telegram, discord, slack, whatsapp, signal, homeassistant, email, sms, etc.) in:
```python
if not self.api_only:
    from gateway.platforms.telegram import TelegramAdapter, check_telegram_requirements
    # ... rest of imports
```

And the adapter instantiation blocks around lines 1550-1650 should also be wrapped:
```python
if not self.api_only:
    if "telegram" in enabled_platforms:
        self._adapters["telegram"] = TelegramAdapter(...)
    # ... rest of adapters
```

- [ ] **Step 5: Ensure APIServerAdapter loads when api_only=True**

Find where `APIServerAdapter` is loaded (around line 1638). It should already be conditionally loaded. Verify it is NOT inside the `if not self.api_only:` block — it should be loaded regardless.

- [ ] **Step 6: Commit**

```bash
git add gateway/run.py
git commit -m "feat(gateway): add api_only flag to GatewayRunner"
```

---

## Task 2: Create `hermes serve` Command

**Files:**
- Create: `serve.py` (root level)
- Modify: `hermes` (shell script)

- [ ] **Step 1: Read hermes_cli/gateway.py to understand gateway startup pattern**

Run: Read `hermes_cli/gateway.py` lines 1-100 to understand how GatewayRunner is instantiated.

- [ ] **Step 2: Create serve.py at root level**

```python
"""
Hermes API Server entry point — `hermes serve`

Starts GatewayRunner in api_only mode with only the APIServerAdapter.
"""
import argparse
import logging
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(prog="hermes serve", description="Start Hermes API Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8642, help="Port to bind (default: 8642)")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format="%(asctime)s %(name)s %(levelname)s %(message)s")

    # Set environment for api_only mode
    import os
    os.environ["HERMES_API_ONLY"] = "1"

    from gateway.run import GatewayRunner
    from gateway.config import load_gateway_config

    config = load_gateway_config()
    runner = GatewayRunner(config, api_only=True)
    runner.run()
```

- [ ] **Step 3: Update hermes shell script**

Find the `case "$1"` block in the hermes script. Add:
```shell
serve)
    exec python serve.py "$@"
    ;;
```

Before the last `*` case. The hermes script should be at the repo root.

- [ ] **Step 4: Test serve command starts**

Run: `python serve.py --help`
Expected: Help message showing --host, --port, --log-level options

- [ ] **Step 5: Commit**

```bash
git add hermes serve.py
git commit -m "feat(cli): add hermes serve command for API-only mode"
```

---

## Task 3: Remove Channel Adapters

**Files:**
- Delete: `gateway/platforms/telegram.py`
- Delete: `gateway/platforms/discord.py`
- Delete: `gateway/platforms/slack.py`
- Delete: `gateway/platforms/whatsapp.py`
- Delete: `gateway/platforms/signal.py`
- Delete: `gateway/platforms/matrix.py`
- Delete: `gateway/platforms/mattermost.py`
- Delete: `gateway/platforms/email.py`
- Delete: `gateway/platforms/sms.py`
- Delete: `gateway/platforms/dingtalk.py`
- Delete: `gateway/platforms/feishu.py`
- Delete: `gateway/platforms/wecom.py`
- Delete: `gateway/platforms/homeassistant.py`
- Delete: `gateway/platforms/webhook.py`

- [ ] **Step 1: List all platform adapter files**

Run: `ls gateway/platforms/*.py`
Confirm which ones to delete (keep: base.py, api_server.py)

- [ ] **Step 2: Delete each channel adapter file**

For each file listed above:
```bash
git rm gateway/platforms/telegram.py
git rm gateway/platforms/discord.py
# ... etc
```

- [ ] **Step 3: Verify gateway/run.py imports don't break**

Run: `python -c "from gateway.run import GatewayRunner; print('OK')"`
Expected: No ImportError

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(gateway): remove all channel adapters (API-only mode)"
```

---

## Task 4: Remove Deleted Tools from model_tools.py

**Files:**
- Modify: `model_tools.py`

- [ ] **Step 1: Read model_tools.py _modules list**

Run: Grep for `_modules` in `model_tools.py`
Find the list of tool modules imported.

- [ ] **Step 2: Remove deleted tool imports**

Keep imports for:
- `tools.file_operations`
- `tools.file_tools`
- `tools.web_tools`
- `tools.delegate_tool`
- `tools.mcp_tool`
- `tools.skills_tool`
- `tools.skills_hub`
- `tools.skills_guard`
- `tools.browser_tool`

Remove imports for:
- `tools.terminal_tool`
- `tools.code_execution_tool`
- `tools.voice_mode`
- `tools.tts_tool`
- `tools.transcription_tools`
- `tools.image_generation_tool`
- `tools.rl_training_tool`
- `tools.send_message_tool`
- `tools.approval`
- `tools.cronjob_tools`
- `tools.checkpoint_manager`
- `tools.process_registry`
- `tools.mixture_of_agents_tool`
- `tools.memory_tool`
- `tools.homeassistant_tool`
- `tools.vision_tools`
- `tools.rl_training_tool`

- [ ] **Step 3: Verify no import errors**

Run: `python -c "import model_tools; print('OK')"`
Expected: No ImportError

- [ ] **Step 4: Commit**

```bash
git add model_tools.py
git commit -m "feat(tools): remove deleted tools from model_tools"
```

---

## Task 5: Delete Unused Tool Files

**Files:**
- Delete: `tools/terminal_tool.py`
- Delete: `tools/code_execution_tool.py`
- Delete: `tools/voice_mode.py`
- Delete: `tools/tts_tool.py`
- Delete: `tools/transcription_tools.py`
- Delete: `tools/image_generation_tool.py`
- Delete: `tools/rl_training_tool.py`
- Delete: `tools/send_message_tool.py`
- Delete: `tools/approval.py`
- Delete: `tools/cronjob_tools.py`
- Delete: `tools/checkpoint_manager.py`
- Delete: `tools/process_registry.py`
- Delete: `tools/mixture_of_agents_tool.py`
- Delete: `tools/memory_tool.py`
- Delete: `tools/homeassistant_tool.py`
- Delete: `tools/vision_tools.py`
- Delete: `tools/rl_training_tool.py`
- Delete: `tools/browser_providers/` (directory)

- [ ] **Step 1: Verify kept tools exist**

Run: `ls tools/file_operations.py tools/web_tools.py tools/delegate_tool.py tools/mcp_tool.py tools/skills_tool.py tools/browser_tool.py`
Expected: All files exist

- [ ] **Step 2: Delete unused tool files**

```bash
git rm tools/terminal_tool.py tools/code_execution_tool.py tools/voice_mode.py tools/tts_tool.py tools/transcription_tools.py tools/image_generation_tool.py tools/rl_training_tool.py tools/send_message_tool.py tools/approval.py tools/cronjob_tools.py tools/checkpoint_manager.py tools/process_registry.py tools/mixture_of_agents_tool.py tools/memory_tool.py tools/homeassistant_tool.py tools/vision_tools.py
git rm -r tools/browser_providers/
```

- [ ] **Step 3: Verify no import errors**

Run: `python -c "import model_tools; print('OK')"`
Expected: No ImportError

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(tools): remove unused tool files"
```

---

## Task 6: Remove Deleted Skills

**Files:**
- Delete: `skills/apple/`
- Delete: `skills/creative/`
- Delete: `skills/domain/`
- Delete: `skills/feeds/`
- Delete: `skills/gaming/`
- Delete: `skills/gifs/`
- Delete: `skills/inference-sh/`
- Delete: `skills/media/`
- Delete: `skills/mlops/`
- Delete: `skills/note-taking/`
- Delete: `skills/research/`
- Delete: `skills/smart-home/`
- Delete: `skills/social-media/`
- Delete: `optional-skills/`

- [ ] **Step 1: Verify kept skills exist**

Run: `ls skills/autonomous-ai-agents skills/productivity skills/github skills/data-science skills/diagramming skills/mcp`
Expected: All directories exist

- [ ] **Step 2: Delete unused skills**

```bash
git rm -r skills/apple/ skills/creative/ skills/domain/ skills/feeds/ skills/gaming/ skills/gifs/ skills/inference-sh/ skills/media/ skills/mlops/ skills/note-taking/ skills/research/ skills/smart-home/ skills/social-media/
git rm -r optional-skills/
```

- [ ] **Step 3: Verify skills still load**

Run: `python -c "from tools.skills_tool import get_skills; print(len(get_skills()), 'skills loaded')"`
Expected: Count of remaining skills (should be ~6)

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(skills): remove unused skills (keep 6 core categories)"
```

---

## Task 7: Remove hermes_cli/ Directory

**Files:**
- Delete: `hermes_cli/` (entire directory)
- Modify: `hermes` (shell script — update entry point)

- [ ] **Step 1: Check what hermes_cli files exist**

Run: `ls hermes_cli/`
Confirm all files to be deleted vs kept (we need to keep the plugin context/memory registration functionality if it's in hermes_cli/plugins.py)

- [ ] **Step 2: Verify plugin system is needed**

The memory plugins in `plugins/memory/*` use `ctx.register_memory_provider()` which comes from `hermes_cli/plugins.py`. If we delete hermes_cli entirely, we need to either:
- Move `plugins.py` core logic to core (agent/memory_provider.py or similar)
- Or make memory plugins self-registering

Check if `agent/memory_provider.py` exists and has the `MemoryProvider` ABC:
Run: `ls agent/memory_provider.py`
If exists, memory plugins import from there directly (not from hermes_cli.plugins).

- [ ] **Step 3: Check memory plugin imports**

Run: `head -30 plugins/memory/honcho/__init__.py`
Look for `from hermes_cli.plugins import` or `from agent.memory_provider import`

- [ ] **Step 4: Delete hermes_cli**

If memory plugins import from `agent.memory_provider`, safe to delete hermes_cli:
```bash
git rm -r hermes_cli/
```

- [ ] **Step 5: Update hermes shell script**

After hermes_cli deletion, the hermes script's default case (`*`) calls `python -m hermes_cli.main` which will fail. Update the default case to delegate to `python serve.py`:
```shell
*)
    exec python serve.py "$@"
    ;;
```

Note: The `serve)` case was already added in Task 2 and should remain unchanged.

Actually since hermes_cli is deleted, we need a new serve module location. Create `serve.py` at root or in a new `core/` directory.

**Alternative approach (if hermes_cli/plugins.py is needed):**
Move `hermes_cli/plugins.py` to `core/plugins.py` before deleting hermes_cli. Update memory plugin imports accordingly.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(cli): remove hermes_cli directory"
```

---

## Task 8: Remove Other Deleted Components

**Files:**
- Delete: `acp_adapter/`
- Delete: `rl_cli.py`
- Delete: `batch_runner.py`
- Delete: `trajectory_compressor.py`
- Delete: `tinker-atropos/`
- Delete: `environments/`
- Delete: `cli.py`

- [ ] **Step 1: Delete each component**

```bash
git rm -r acp_adapter/
git rm rl_cli.py batch_runner.py trajectory_compressor.py
git rm -r tinker-atropos/ environments/
git rm cli.py
```

- [ ] **Step 2: Verify gateway still works**

Run: `python -c "from gateway.run import GatewayRunner; print('OK')"`
Expected: No ImportError

- [ ] **Step 3: Commit**

```bash
git commit -m "feat: remove research/IDE components (acp, rl, cli)"
```

---

## Task 9: Update pyproject.toml / Dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Read current dependencies**

Run: Grep for dependencies in pyproject.toml related to deleted features (telegram, discord, slack, etc.)

- [ ] **Step 2: Remove unused dependencies**

Channels, CLI tools, etc. may have specific dependencies. Remove any that are no longer needed. Be conservative — only remove if clearly only used by deleted features.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: remove unused dependencies from pyproject.toml"
```

---

## Task 10: Integration Test

- [ ] **Step 1: Run quick test suite**

Run: `python -m pytest tests/test_model_tools.py -v`
Expected: All tests pass

- [ ] **Step 2: Test hermes serve starts**

Run: `timeout 5 python -m hermes_cli.serve --help || true`
Expected: Help message (timeout kills it after 5s)

- [ ] **Step 3: Verify no orphan imports**

Run: `python -c "import gateway.run; import model_tools; import agent; print('All OK')"`
Expected: All imports succeed

- [ ] **Step 4: Final commit if all passes**

```bash
git add -A
git commit -m "feat: core simplification complete — API-only mode"
```

---

## Self-Review Checklist

Before claiming done, verify:

1. **Spec coverage**: Each item in the design spec has a corresponding task
2. **No placeholders**: All steps have actual code/commands, no "TBD" or "TODO"
3. **Type consistency**: Method names match across tasks (e.g., `GatewayRunner.__init__` signature)
4. **Test verification**: Each task includes verification steps
5. **Import errors**: After deletions, core imports still work
