<div align="center">

# Codex LB Enhanced

### 面向长对话连续性的 Codex 兼容账号池网关

<p>
  <a href="https://github.com/aafqaq/codex-lb-enhanced/actions/workflows/build-custom-image.yml"><img src="https://github.com/aafqaq/codex-lb-enhanced/actions/workflows/build-custom-image.yml/badge.svg?branch=main" alt="构建状态"></a>
  <a href="https://github.com/aafqaq/codex-lb-enhanced/releases"><img src="https://img.shields.io/github/v/release/aafqaq/codex-lb-enhanced?display_name=tag&sort=semver" alt="版本"></a>
  <a href="https://github.com/aafqaq/codex-lb-enhanced/pkgs/container/codex-lb-enhanced"><img src="https://img.shields.io/badge/GHCR-ready-9b87f5?logo=docker&logoColor=white" alt="GHCR"></a>
</p>

<p><a href="https://aafqaq.github.io/codex-lb-enhanced/">文档</a> · <a href="https://github.com/aafqaq/codex-lb-enhanced/issues">问题反馈</a> · <a href="https://github.com/aafqaq/codex-lb-enhanced/discussions">讨论</a></p>

![Codex LB Enhanced](docs/screenshots/banner.jpg)

<p><em>账号池不丢，会话不断，异常可恢复。</em></p>

</div>

> **独立发行版。** 本项目基于 [Soju06/codex-lb](https://github.com/Soju06/codex-lb) 独立维护，不是 OpenAI 或上游 Codex 的官方发布版本。上游 MIT 许可证和版权声明均予以保留。

## 项目简介

Codex LB 是 ChatGPT 账号负载均衡器：聚合多个账号、追踪用量、管理 API Key，并提供 OpenAI 兼容接口和管理仪表盘。

Codex LB Enhanced 保留原版账号池、额度统计、API Key 和路由能力，重点强化长对话连续性：上游 WebSocket 断开、额度耗尽、账号暂停、延迟重试、上下文压缩失败，以及桌面端关闭数小时后恢复，都尽可能交由程序处理。

## 与原版的区别

| 能力 | 原版 | Enhanced |
|---|---|---|
| 账号池 | 多账号负载均衡 | 保持原选择器，增加请求级故障账号排除 |
| 额度响应 | 账号池估算 | API Key 自定义额度优先，无自定义时回退账号池估算 |
| 额度耗尽 | 可能直接终止会话 | 自动遍历可用账号，池耗尽后才返回 429 |
| WebSocket | 依赖当前连接和缓存 | 首事件前可回退 HTTP，支持延迟恢复和安全重连 |
| 会话恢复 | 对账号绑定敏感 | 保留完整历史，安全时跨账号重放，不丢工具调用上下文 |
| 可观测性 | 基础请求日志 | 记录上下游事件、传输、恢复阶段和最终原因 |

增强逻辑叠加在原负载均衡器之上，不替换 API Key 鉴权、账号分配、预留额度、路由策略或普通 `/v1` 合约。

## 核心能力

<table>
<tr><td><b>账号池</b><br>多个 ChatGPT 账号负载均衡</td><td><b>用量追踪</b><br>Token、费用和历史趋势</td><td><b>API Key</b><br>按窗口、模型和用量限额</td></tr>
<tr><td><b>原生额度头</b><br>primary、secondary、monthly、credits</td><td><b>连续会话</b><br>断网、切号和延迟重试恢复</td><td><b>传输容错</b><br>WebSocket/HTTP 安全回退</td></tr>
</table>

## 快速部署

```bash
docker volume create codex-lb-enhanced-data
docker run -d --name codex-lb-enhanced \
  --restart unless-stopped \
  -e CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_AMBIGUOUS_CONTINUATION_RECOVERY_MODE=server_indefinite_recovery \
  -p 2455:2455 -p 1455:1455 \
  -v codex-lb-enhanced-data:/var/lib/codex-lb \
  ghcr.io/aafqaq/codex-lb-enhanced:1.24.5
```

打开 [localhost:2455](http://localhost:2455)，添加账号并创建 API Key。

## Codex 客户端配置

在 `~/.codex/config.toml` 中配置：

```toml
model = "gpt-5.6-sol"
model_reasoning_effort = "xhigh"
model_provider = "codex-lb-enhanced"

[model_providers.codex-lb-enhanced]
name = "openai"
base_url = "http://127.0.0.1:2455/backend-api/codex"
wire_api = "responses"
supports_websockets = true
requires_openai_auth = true
```

其他 OpenAI 兼容客户端使用 `/v1`；Codex CLI/IDE 使用 `/backend-api/codex`。

## 恢复原则

- 上游额度耗尽：记录真实额度错误，排除当前账号，继续选择下一个账号。
- 账号被暂停：首轮请求只重分配一次；有已验证完整历史时跨账号安全重放。
- 已产生可见输出：不在代理内重复生成，交给客户端使用完整历史重试。
- 无法证明上下文完整：不静默丢弃上下文，返回可恢复的官方语义并记录日志。
- 只有整个可用账号池都耗尽或不可用时，才向客户端返回最终失败。

## 配置、数据与升级

配置使用 `CODEX_LB_` 前缀或 `.env.local`，SQLite 是默认数据库，也支持 PostgreSQL。Docker 数据目录为 `/var/lib/codex-lb/`，升级前请备份命名卷并保留旧镜像标签以便回滚。

`main` 分支会通过 [GitHub Actions](.github/workflows/build-custom-image.yml) 自动构建并发布到 GHCR。文档站提供详细的鉴权、路由、数据库、Docker/Kubernetes 和故障排查说明。

## 许可证

MIT，详见 [LICENSE](LICENSE)。

