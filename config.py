"""
项目级运行配置。

模块职责：
1. 提供本地开发使用的非敏感默认配置。
2. 将模型选择和请求策略从环境密钥中拆分出来。
3. 将 API key 和部署相关 endpoint 留在 `.env` 中。

设计说明：
- 敏感值应从环境变量加载。
- 这些默认值后续可以被 CLI 参数或 profile 配置覆盖。
"""

DEFAULT_LLM_PROVIDER = "deepseek"
DEFAULT_LLM_MODEL = "deepseek-v4-pro"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_EXTRA_BODY = {
    "thinking": {"type": "enabled"},
}
