# Codex LB Enhanced

这是一个独立维护的 Codex 兼容账号池网关版本。保留原 codex-lb 的仪表盘、API Key、用量统计、账号池和负载均衡能力，重点增强协议模拟、会话连续性和故障恢复。

## 为什么需要这个版本

Codex 客户端期望上游对话是长期、可恢复的。上游 websocket 意外关闭、账号额度耗尽、网络中断、手动切换账号或延迟几小时/几天后重试，都不应该让原对话失效。本版本把这些情况作为传输或路由故障处理，只要账号池中还有可用账号，就尽量恢复同一个响应和工具调用状态。

## 相比原版的增强

- 收到官方“usage limit reached”响应（包括只有文字的额度错误）时自动遍历账号池。
- 使用 Codex 原生重试边界，让官方客户端在不中断可见对话和工具状态的情况下重试。
- websocket 异常结束后持久化响应归属，后续重试或切换账号仍可继续。
- 上游 websocket 不稳定时自动回退到 HTTP。
- 模拟 Codex 官方额度响应头：配置了 API Key 独立限额时返回该限额，否则返回整个账号池的估算额度。
- 严格校验上下文压缩响应；空响应或格式异常时自动重试/切换账号，避免客户端收到 50x。
- 支持断网重连、额度切换、账号切换、延迟重试和上下文压缩后的连续会话。
- 更新检测与镜像发布地址指向本独立仓库。

额度头使用 Codex 客户端识别的 `x-codex-primary-*`、`x-codex-secondary-*` 及 credits 字段。返回的是当前 API Key 的配置额度或账号池估算，不会泄露上游账号凭据。

## 快速部署

```bash
docker volume create codex-lb-enhanced-data
docker run -d --name codex-lb-enhanced \
  --restart unless-stopped \
  -p 1455:1455 -p 2455:2455 \
  -v codex-lb-enhanced-data:/var/lib/codex-lb \
  ghcr.io/aafqaq/codex-lb-enhanced:latest
```

打开 `http://localhost:2455` 进入管理面板，然后创建 API Key 并将 Codex 客户端配置到网关的 Responses 接口。

## 开发与自动构建

后端使用 Python/FastAPI，前端使用 React。运行测试：

```bash
uv run pytest
```

`custom/resilient-streams-v1.24` 分支会由 GitHub Actions 自动构建，并发布为 `ghcr.io/aafqaq/codex-lb-enhanced:latest` 以及不可变提交标签。

## 数据与升级

请始终将 `/var/lib/codex-lb` 挂载到命名卷。更换镜像不会替换账号、API Key、用量和设置所在的数据卷。升级前请备份数据，并保留旧镜像标签以便回滚。

## 许可证

保留上游 MIT 许可证及版权声明。本仓库由 `aafqaq` 独立维护，不是上游项目的官方发布渠道。
