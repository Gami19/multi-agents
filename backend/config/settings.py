"""アプリケーション設定管理"""
import os
from agno.models.aws import AwsBedrock
from agno.models.azure import AzureOpenAI
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

def get_aws_model() -> AwsBedrock:
    """AWS Bedrockモデルの設定を取得"""
    return AwsBedrock(
        id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        aws_region="us-west-2",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

def get_azure_model() -> AzureOpenAI:
    """Azure OpenAIモデルの設定を取得"""
    return AzureOpenAI(
        id="gpt-4o",
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

def get_brave_api_key() -> str:
    """Brave APIキーを取得"""
    return os.getenv("BRAVE_API_KEY")

def get_environment_config():
    """環境設定の取得"""
    return {
        "aws_region": "us-west-2",
        "model_id_aws": "us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        "model_id_azure": "gpt-4o",
        "cors_origins": ["http://localhost:3000"],
        "server_port": 8001,
        "server_host": "0.0.0.0"
    }