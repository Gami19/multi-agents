## backend ディレクトリ構造
```
backend/
├── app.py                      # FastAPIアプリのエントリポイント
├── config/
│   ├── __init__.py
│   ├── settings.py             # モデル設定（AWS Bedrock、Azure OpenAI）
│   └── logging_config.py       # ログ設定
├── models/
│   ├── __init__.py
│   ├── enums.py                # AgentServiceType, MultiAgentMode, AgentType
│   └── schemas.py              # QueryRequest, QueryResponse
├── services/
│   ├── __init__.py
│   ├── agent_manager.py        # AgnoAgentManagerクラス（主な管理機能）
│   ├── stream_processor.py     # stream_with_debug_logging とストリーミング処理
│   └── reasoning_service.py    # 推論関連機能（reasoning機能）
├── api/
│   ├── __init__.py
│   ├── routers.py              # エンドポイントだけに集約
│   └── middleware.py           # CORS設定
└── utils/
    ├── __init__.py
    └── helpers.py              # process_chunk, process_responseなどのユーティリティ
```