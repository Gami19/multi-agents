from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from services.agent_manager import agent_manager
from api.middleware import setup_cors_middleware
from api.routers import setup_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションのライフサイクル管理"""
    try:
        await agent_manager.initialize_agents()
        print("🚀 Agno Multi-Agent API初期化完了")
    except Exception as e:
        print(f"❌ 起動に失敗しました: {e}")
    
    yield
    
    await agent_manager.shutdown()
    print("�� アプリケーション終了")

def create_app() -> FastAPI:
    """FastAPIアプリケーションの作成と設定"""
    app = FastAPI(
        title="Agno Multi-Agent API", 
        version="1.0.0",
        lifespan=lifespan
    )
    
    # ミドルウェアの設定
    setup_cors_middleware(app)
    
    # ルートの設定
    setup_routes(app)
    
    return app

# アプリケーションインスタンス
app = create_app()

if __name__ == "__main__":
    port = 8001
    print(f"🚀 サーバーをポート{port}で起動中...")
    uvicorn.run(app, host="0.0.0.0", port=port)