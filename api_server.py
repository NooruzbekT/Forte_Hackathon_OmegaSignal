"""
FastAPI Backend для AI Business Analyst
REST API + WebSocket для real-time чата
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ba_assistant import BAAssistant, create_ba_assistant


# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Запрос для chat endpoint"""
    message: str = Field(..., description="Сообщение пользователя")
    session_id: Optional[str] = Field(None, description="ID сессии (опционально)")


class ChatResponse(BaseModel):
    """Ответ от chat endpoint"""
    response: str = Field(..., description="Ответ ассистента")
    session_id: str = Field(..., description="ID сессии")
    doc_type: Optional[str] = Field(None, description="Тип документа")
    progress: float = Field(0.0, description="Прогресс создания документа (0.0-1.0)")
    document_ready: bool = Field(False, description="Готов ли документ")
    document_path: Optional[str] = Field(None, description="Путь к документу если готов")


class SessionInfo(BaseModel):
    """Информация о сессии"""
    session_id: str
    status: str
    doc_type: Optional[str] = None
    messages_count: int = 0
    progress: float = 0.0
    created_at: Optional[str] = None


class DocumentInfo(BaseModel):
    """Информация о документе"""
    filename: str
    path: str
    created: str
    size: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    llm_provider: str
    models: Dict[str, str]


# ============================================================================
# GLOBAL STATE
# ============================================================================

class AppState:
    """Глобальное состояние приложения"""
    def __init__(self):
        self.assistant: Optional[BAAssistant] = None
        self.active_websockets: Dict[str, WebSocket] = {}
        self.session_timestamps: Dict[str, datetime] = {}


app_state = AppState()


# ============================================================================
# LIFECYCLE
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    logger.info("🚀 Starting AI Business Analyst API...")

    try:
        app_state.assistant = await create_ba_assistant()
        logger.info("✅ BA Assistant initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize BA Assistant: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")

    # Закрываем все WebSocket соединения
    for ws in app_state.active_websockets.values():
        try:
            await ws.close()
        except:
            pass

    # Закрываем LLM клиент
    if app_state.assistant:
        try:
            await app_state.assistant.llm.close()
        except:
            pass


# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="AI Business Analyst API",
    description="REST API + WebSocket для AI бизнес-аналитика ForteBank",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files для документов
docs_dir = Path("docs")
docs_dir.mkdir(exist_ok=True)
app.mount("/docs", StaticFiles(directory=str(docs_dir)), name="docs")


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check и информация о сервисе"""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        llm_provider=app_state.assistant.llm.provider,
        models={
            "router": app_state.assistant.llm.router_model,
            "assistant": app_state.assistant.llm.assistant_model
        }
    )


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================================
# CHAT ENDPOINTS (REST)
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Отправить сообщение ассистенту (REST).

    Используйте это для простых запросов без WebSocket.
    """
    session_id = request.session_id or str(uuid.uuid4())

    try:
        # Обработка сообщения
        response = await app_state.assistant.process_message(
            user_message=request.message,
            session_id=session_id
        )

        # Получаем информацию о сессии
        session_info = app_state.assistant.get_session_info(session_id)

        # Проверяем завершение документа
        document_ready = session_info.get("progress", 0.0) >= 1.0
        document_path = None

        # Извлекаем путь к документу из ответа если есть
        if document_ready and "📄 Файл:" in response:
            import re
            match = re.search(r'`([^`]+\.docx)`', response)
            if match:
                document_path = match.group(1)

        return ChatResponse(
            response=response,
            session_id=session_id,
            doc_type=session_info.get("doc_type"),
            progress=session_info.get("progress", 0.0),
            document_ready=document_ready,
            document_path=document_path
        )

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Получить информацию о сессии"""
    info = app_state.assistant.get_session_info(session_id)

    created_at = app_state.session_timestamps.get(session_id)
    if created_at:
        info["created_at"] = created_at.isoformat()

    return SessionInfo(session_id=session_id, **info)


@app.post("/api/session/{session_id}/reset")
async def reset_session(session_id: str):
    """Сбросить сессию"""
    app_state.assistant.reset_session(session_id)
    if session_id in app_state.session_timestamps:
        del app_state.session_timestamps[session_id]

    return {"status": "ok", "message": "Session reset", "session_id": session_id}


# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint для real-time чата.

    Сообщения в формате JSON:
    {
        "type": "message",
        "content": "текст сообщения"
    }

    Ответы:
    {
        "type": "response",
        "content": "ответ ассистента",
        "session_id": "...",
        "doc_type": "...",
        "progress": 0.5
    }
    """
    await websocket.accept()
    app_state.active_websockets[session_id] = websocket
    app_state.session_timestamps[session_id] = datetime.now()

    logger.info(f"WebSocket connected: {session_id}")

    # Отправляем welcome message
    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "message": "Подключено к AI Business Analyst"
    })

    try:
        while True:
            # Получаем сообщение
            data = await websocket.receive_json()

            if data.get("type") == "message":
                user_message = data.get("content", "")

                if not user_message:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Empty message"
                    })
                    continue

                # Отправляем индикатор "печатает"
                await websocket.send_json({
                    "type": "typing",
                    "message": "AI думает..."
                })

                try:
                    # Обрабатываем сообщение
                    response = await app_state.assistant.process_message(
                        user_message=user_message,
                        session_id=session_id
                    )

                    # Получаем информацию о сессии
                    session_info = app_state.assistant.get_session_info(session_id)

                    # Проверяем завершение документа
                    document_ready = session_info.get("progress", 0.0) >= 1.0
                    document_path = None

                    if document_ready and "📄 Файл:" in response:
                        import re
                        match = re.search(r'`([^`]+\.docx)`', response)
                        if match:
                            document_path = match.group(1)

                    # Отправляем ответ
                    await websocket.send_json({
                        "type": "response",
                        "content": response,
                        "session_id": session_id,
                        "doc_type": session_info.get("doc_type"),
                        "progress": session_info.get("progress", 0.0),
                        "document_ready": document_ready,
                        "document_path": document_path
                    })

                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Ошибка обработки: {str(e)}"
                    })

            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")

    finally:
        if session_id in app_state.active_websockets:
            del app_state.active_websockets[session_id]


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Список всех созданных документов"""
    docs = app_state.assistant.doc_generator.list_documents()

    return [
        DocumentInfo(
            filename=doc["filename"],
            path=doc["path"],
            created=doc["created"].isoformat(),
            size=doc["size"]
        )
        for doc in docs
    ]


@app.get("/api/documents/{filename}")
async def download_document(filename: str):
    """Скачать документ"""
    filepath = docs_dir / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    # Проверяем что файл в директории docs (безопасность)
    try:
        filepath.resolve().relative_to(docs_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    return FileResponse(
        path=str(filepath),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )


@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Удалить документ"""
    filepath = docs_dir / filename

    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        filepath.resolve().relative_to(docs_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    filepath.unlink()

    return {"status": "ok", "message": f"Document {filename} deleted"}


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/api/admin/sessions")
async def list_active_sessions():
    """Список активных сессий (для админки)"""
    sessions = []

    for session_id in list(app_state.assistant.states.keys()):
        info = app_state.assistant.get_session_info(session_id)

        created_at = app_state.session_timestamps.get(session_id)
        if created_at:
            info["created_at"] = created_at.isoformat()

        info["session_id"] = session_id
        info["websocket_active"] = session_id in app_state.active_websockets

        sessions.append(info)

    return sessions


@app.post("/api/admin/cleanup")
async def cleanup_old_sessions():
    """Очистить старые неактивные сессии"""
    cutoff = datetime.now().timestamp() - 3600  # 1 час
    cleaned = 0

    for session_id, timestamp in list(app_state.session_timestamps.items()):
        if timestamp.timestamp() < cutoff:
            if session_id not in app_state.active_websockets:
                app_state.assistant.reset_session(session_id)
                del app_state.session_timestamps[session_id]
                cleaned += 1

    return {
        "status": "ok",
        "cleaned_sessions": cleaned
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик ошибок"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc)
        }
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )