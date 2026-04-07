# Hermes Agent 核心功能简化设计

**日期**: 2026-04-07
**状态**: 已确认

## 目标

对 Hermes Agent 进行功能删减，只保留核心能力：
- 删除 CLI 交互界面
- 保留 API Server 模式（OpenAI 兼容），支持 WebUI 接入
- 保留最常用的工具和 skills

## 保留的组件

### API Server
- `gateway/platforms/api_server.py` — OpenAI 兼容 HTTP 接口，唯一的 gateway adapter
- 端点: `/v1/chat/completions`, `/v1/responses`, `/v1/models`, `/health`
- 默认 `127.0.0.1:8642`

### Gateway 核心
| 文件 | 说明 |
|------|------|
| `gateway/run.py` | GatewayRunner — platform lifecycle |
| `gateway/session.py` | SessionStore |
| `gateway/delivery.py` | DeliveryRouter |
| `gateway/pairing.py` | PairingStore |
| `gateway/hooks.py` | HookRegistry |
| `gateway/mirror.py` | Cross-session mirroring |
| `gateway/status.py` | Token locks, process tracking |
| `gateway/channel_directory.py` | Channel registry |
| `gateway/config.py` | Platform config |
| `gateway/platforms/base.py` | BasePlatformAdapter |

### Agent 核心
| 文件 | 说明 |
|------|------|
| `run_agent.py` | AIAgent — 核心对话循环 |
| `agent/` | prompt_builder, context_compressor, auxiliary_client, model_metadata, display, skill_commands, memory_store, trajectory |
| `model_tools.py` | 工具编排 |
| `hermes_state.py` | SQLite FTS5 session store |

### 工具系统
| 文件 | 说明 |
|------|------|
| `tools/registry.py` | 工具注册中心 |
| `toolsets.py` | 工具分组 |

**保留的工具**:
- File Tools (file_operations, file_tools)
- Web Tools (web_tools)
- Delegate Tool (delegate_tool)
- MCP Tool (mcp_tool)
- Skills Tool (skills_tool, skills_hub, skills_guard)
- Browser Tool (browser_tool) — 依赖服务器上的外部浏览器

**删除的工具**:
- terminal_tool, code_execution_tool, voice_mode, tts_tool, transcription_tools, image_generation_tool, rl_training_tool, send_message_tool, approval, cronjob_tools, checkpoint_manager, process_registry, mixture_of_agents_tool, memory_tool, homeassistant_tool, vision_tools

### Skills（极简策略）
保留 6 个 bundled skills 类别:
- `skills/autonomous-ai-agents/` — Claude Code, Codex, Hermes Agent, OpenCode
- `skills/productivity/` — 生产力工具
- `skills/github/` — GitHub 集成
- `skills/data-science/` — Jupyter, pandas, numpy
- `skills/diagramming/` — Mermaid, PlantUML, Graphviz
- `skills/mcp/` — MCP 协议相关

删除: apple, creative, domain, feeds, gaming, gifs, inference-sh, media, mlops, note-taking, research, smart-home, social-media, optional-skills/

### 其他保留组件
| 组件 | 说明 |
|------|------|
| `cron/` | 任务调度 |
| `hermes_cli/plugins.py` | Plugin 系统（内存注册功能） |
| `plugins/memory/` | 9个内存后端插件 (Honcho, Mem0, SuperMemory, RetainDB, Holographic, Hindsight, ByteRover, OpenViking) |
| `mcp_serve.py` | MCP Server |

## 删除的组件

### CLI（全部删除）
- `cli.py`
- `hermes_cli/` 全部目录

### Channel Adapters（全部删除）
gateway/platforms/ 下除 `base.py`, `api_server.py` 外全部删除:
- telegram, discord, slack, whatsapp, signal, matrix, mattermost
- email, sms, dingtalk, feishu, wecom, homeassistant, webhook

### 其他（全部删除）
- `acp_adapter/` — IDE 集成
- `rl_cli.py`, `batch_runner.py`, `trajectory_compressor.py` — 研究工具
- `tinker-atropos/`, `environments/` — RL 训练环境
- `tools/browser_providers/` — 浏览器驱动（browser_tool 本身保留但依赖外部浏览器）

## 启动方式

```bash
hermes serve        # 纯 API Server 模式
```

GatewayRunner 通过 `--api-only` 或环境变量加载时只初始化 `APIServerAdapter`，跳过所有其他 channel adapters。

## 实现方案

1. 添加 `--api-only` 标志到 `gateway/run.py` 的 GatewayRunner
2. 迁移 `hermes_cli/plugins.py` 的 PluginManager 到 core 或保留在原位置（内存注册功能已足够轻量）
3. 从 `model_tools.py` 移除已删除工具的导入
4. 删除 `gateway/platforms/` 下除 `base.py` 和 `api_server.py` 外的所有 adapter
5. 删除 `skills/` 下保留类别外的所有 skills
6. 更新 `hermes` 入口脚本，支持 `serve` 子命令
