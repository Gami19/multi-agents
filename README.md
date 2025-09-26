# FastAPI Multi-Agents

FastAPIとReactを使用したマルチエージェントAIシステム。AWS Bedrock、Azure OpenAI、ArXiv、Brave Searchなどの複数のAIサービスとツールを統合。


## 機能

### 利用可能なエージェント

- **AWS Documentation Agent**: AWS公式ドキュメントの検索・参照
- **ArXiv Agent**: arXiv論文の検索・分析
- **Brave Search Agent**: Web検索の実行

### 主要機能

- マルチエージェントアーキテクチャ
- ストリーミングレスポンス
- リアルタイムデバッグログ
- ツール使用状況の可視化
- エージェントの状態監視
- CORS対応のWeb API

## 技術スタック

### バックエンド
- **FastAPI**: 高速なPython Webフレームワーク
- **Agno**: AIエージェントフレームワーク
- **AWS Bedrock**: Claude 3.7 Sonnetモデル
- **Azure OpenAI**: GPT-4oモデル
- **MCP Tools**: Model Context Protocolツール
- **ArXiv Tools**: 論文検索ツール
- **Brave Search Tools**: Web検索ツール

### フロントエンド
- **React 19**: 最新のReactフレームワーク
- **TypeScript**: 型安全なJavaScript
- **Vite**: 高速なビルドツール
- **Tailwind CSS**: ユーティリティファーストCSS

## セットアップ

### 前提条件

- Python 3.8+
- Node.js 22+
- Vite  v7.1.7
- AWS Bedrock APIキー
- Azure OpenAI APIキー

### 環境変数の設定

`.env`ファイルを作成

```bash
# AWS Bedrock
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
```

### バックエンドの起動

```bash
cd backend
pip install -r requirements.txt
python app.py
```

サーバーは`http://localhost:8001`で起動
### フロントエンドの起動

```bash
cd frontend
npm install
npm run dev
```

フロントエンドは`http://localhost:3000`で起動

## API エンドポイント

### ヘルスチェック
- `GET /health`: エージェントの状態確認

### クエリエンドポイント
- `POST /aws_documentation/query`: AWSドキュメント検索
- `POST /arxiv/query`: arXiv論文検索
- `POST /brave_search/query`: Web検索

### リクエスト形式

```json
{
  "query": "検索したい内容"
}
```

### レスポンス形式

```json
{
  "response": "AIからの回答",
  "status": "success",
  "tools_used": ["使用されたツールのリスト"],
  "debug_info": {
    "tool_calls": ["ツール呼び出しの詳細"],
    "reasoning_steps": ["推論プロセス"],
    "token_usage": "トークン使用量"
  }
}
```

## 使用方法

1. フロントエンドにアクセス
2. 使用したいエージェントを選択
3. 質問を入力
4. AIエージェントが自動的に適切なツールを使用して回答を生成

## 開発

### デバッグモード

デバッグモードを有効にすると、以下の情報が表示される：

- ツール呼び出しの詳細
- 推論プロセス
- トークン使用量
- エラーの詳細

### ログレベル

環境変数`AGNO_LOG_LEVEL`でログレベルを設定：

- `DEBUG`: 詳細なデバッグ情報
- `INFO`: 一般的な情報
- `WARNING`: 警告
- `ERROR`: エラー

## テスト

HTTPリクエストを使用したテスト例：

```http
### AWS Documentation クエリ
POST http://localhost:8001/aws_documentation/query
Content-Type: application/json

{
  "query": "BedrockのClaude 3.7 SonnetのモデルIDは？"
}

### ArXiv クエリ
POST http://localhost:8001/arxiv/query
Content-Type: application/json

{
  "query": "最近の不確定原理について教えて"
}
```