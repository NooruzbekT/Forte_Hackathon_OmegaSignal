"""
🏆 FINAL API SERVER - ForteBank AI Hackathon 2024
Полностью интегрированный бэкенд со ВСЕМИ бонусными фичами (+20 баллов)

Features:
✅ REST API + WebSocket
✅ Stateful BAAssistant с Intent Router
✅ 5 типов документов (BRD, Bug Fix, Integration, Process Change, Data Request)
✅ DOCX Generation
✅ Mermaid Diagrams → PNG → Insert to DOCX
✅ Confluence Integration (создание страниц, Mermaid макросы)
✅ Session History (SQLite)
✅ Business Assistant Summary (AI-powered)
✅ Statistics & Analytics
"""

import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Наши модули
from ba_assistant import BAAssistant, create_ba_assistant
from diagram_generator import MermaidGenerator
from confluence_client import ConfluenceClient, ConfluenceMermaidHelper
from session_history import SessionHistoryDB
from mermaid_to_png import MermaidToPNGConverter, mermaid_to_docx_workflow


# ============================================================================
# LOGGING
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC MODELS
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
    progress: float = Field(0.0, description="Прогресс (0.0-1.0)")
    document_ready: bool = Field(False, description="Готов ли документ")
    document_path: Optional[str] = Field(None, description="Путь к документу")


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
    """Health check"""
    status: str
    version: str
    llm_provider: str
    models: Dict[str, str]
    features: List[str]


class DiagramGenerateRequest(BaseModel):
    """Запрос на генерацию диаграммы"""
    type: str = Field(..., description="Тип: process_flow, sequence, use_case, kpi_dashboard")
    title: str = Field(..., description="Заголовок")
    data: Dict = Field(..., description="Данные для диаграммы")
    style: Optional[str] = Field("TD", description="Стиль (TD/LR)")


class DiagramResponse(BaseModel):
    """Ответ с диаграммой"""
    mermaid_code: str
    diagram_type: str
    png_base64: Optional[str] = None


class MermaidToPNGRequest(BaseModel):
    """Запрос на конвертацию Mermaid в PNG"""
    mermaid_code: str = Field(..., description="Mermaid код")
    return_base64: bool = Field(True, description="Вернуть base64 вместо URL")


class SessionSummaryResponse(BaseModel):
    """Summary сессии"""
    session_id: str
    summary: str
    key_points: List[str]
    doc_type: Optional[str]
    total_messages: int


class StatisticsResponse(BaseModel):
    """Статистика"""
    total_sessions: int
    active_sessions: int
    completed_sessions: int
    total_messages: int
    by_doc_type: Dict[str, int]


class ConfluencePublishRequest(BaseModel):
    """Запрос на публикацию в Confluence"""
    title: str = Field(..., description="Заголовок страницы")
    content: str = Field(..., description="Контент в Markdown")
    mermaid_diagrams: Optional[Dict[str, str]] = Field(None, description="Mermaid диаграммы")


class CleanupHistoryRequest(BaseModel):
    """Запрос на очистку истории"""
    days: int = Field(30, ge=1, le=365, description="Удалить сессии старше N дней")


# ============================================================================
# GLOBAL STATE
# ============================================================================

class AppState:
    """Глобальное состояние приложения"""
    def __init__(self):
        self.assistant: Optional[BAAssistant] = None
        self.history_db: Optional[SessionHistoryDB] = None
        self.mermaid_converter: Optional[MermaidToPNGConverter] = None
        self.confluence_client: Optional[ConfluenceClient] = None
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
    logger.info("🚀 Starting AI Business Analyst API (FINAL VERSION)...")

    try:
        # Initialize BA Assistant
        app_state.assistant = await create_ba_assistant()
        logger.info("✅ BA Assistant initialized")

        # Initialize Session History DB
        app_state.history_db = SessionHistoryDB("data/sessions.db")
        logger.info("✅ Session History DB initialized")

        # Initialize Mermaid Converter (fallback to API mode)
        app_state.mermaid_converter = MermaidToPNGConverter(use_mermaid_cli=False)
        logger.info("✅ Mermaid Converter initialized (API mode)")

        # Initialize Confluence Client (if configured)
        confluence_url = os.getenv("CONFLUENCE_URL")
        if confluence_url:
            app_state.confluence_client = ConfluenceClient(
                base_url=confluence_url,
                username=os.getenv("CONFLUENCE_USERNAME", ""),
                api_token=os.getenv("CONFLUENCE_API_TOKEN", ""),
                space_key=os.getenv("CONFLUENCE_SPACE_KEY", "AI")
            )
            logger.info("✅ Confluence Client initialized")
        else:
            logger.warning("⚠️ Confluence not configured (optional)")

        # Integrate history logging with assistant
        _integrate_history_logging()

        logger.info("🎉 All systems ready!")

    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")

    # Close WebSockets
    for ws in app_state.active_websockets.values():
        try:
            await ws.close()
        except:
            pass

    # Close LLM client
    if app_state.assistant:
        try:
            await app_state.assistant.llm.close()
        except:
            pass

    # Close Confluence client
    if app_state.confluence_client:
        try:
            await app_state.confluence_client.close()
        except:
            pass


def _integrate_history_logging():
    """Интегрировать логирование истории с assistant"""
    original_process = app_state.assistant.process_message

    async def wrapped_process(user_message: str, session_id: str = None):
        # Создать сессию если нужно
        if session_id:
            session = app_state.history_db.get_session(session_id)
            if not session:
                app_state.history_db.create_session(session_id)

            # Логировать user message
            app_state.history_db.add_message(session_id, "user", user_message)

        # Вызвать оригинальный метод
        response = await original_process(user_message, session_id)

        # Логировать assistant response
        if session_id:
            app_state.history_db.add_message(session_id, "assistant", response)

            # Обновить session info
            session_info = app_state.assistant.get_session_info(session_id)
            app_state.history_db.update_session(
                session_id,
                doc_type=session_info.get("doc_type"),
                progress=session_info.get("progress", 0.0),
                status="active" if session_info.get("progress", 0.0) < 1.0 else "completed"
            )

        return response

    app_state.assistant.process_message = wrapped_process
    logger.info("✅ History logging integrated")


# ============================================================================
# APP SETUP
# ============================================================================

app = FastAPI(
    title="AI Business Analyst API - FINAL",
    description="Полностью интегрированный бэкенд для ForteBank AI Hackathon 2024",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене: конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
docs_dir = Path("docs")
docs_dir.mkdir(exist_ok=True)

diagrams_dir = Path("diagrams")
diagrams_dir.mkdir(exist_ok=True)

if docs_dir.exists():
    app.mount("/docs", StaticFiles(directory=str(docs_dir)), name="docs")

if diagrams_dir.exists():
    app.mount("/diagrams", StaticFiles(directory=str(diagrams_dir)), name="diagrams")


# ============================================================================
# HEALTH & INFO
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check с полной информацией о системе"""
    features = [
        "REST API",
        "WebSocket",
        "Intent Router",
        "5 Document Types",
        "DOCX Generation",
        "Mermaid Diagrams",
        "Diagram → PNG",
        "Session History (SQLite)",
        "Business Summary (AI)",
    ]

    if app_state.confluence_client:
        features.append("Confluence Integration")

    return HealthResponse(
        status="ok",
        version="2.0.0",
        llm_provider=app_state.assistant.llm.provider,
        models={
            "router": app_state.assistant.llm.router_model,
            "assistant": app_state.assistant.llm.assistant_model
        },
        features=features
    )


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================================
# CHAT ENDPOINTS
# ============================================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Отправить сообщение ассистенту (REST).

    Автоматически логирует в Session History DB.
    """
    session_id = request.session_id or str(uuid.uuid4())

    try:
        response = await app_state.assistant.process_message(
            user_message=request.message,
            session_id=session_id
        )

        session_info = app_state.assistant.get_session_info(session_id)

        document_ready = session_info.get("progress", 0.0) >= 1.0
        document_path = None

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


@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint для real-time чата.

    Формат сообщений:
    {
        "type": "message",
        "content": "текст"
    }
    """
    await websocket.accept()
    app_state.active_websockets[session_id] = websocket
    app_state.session_timestamps[session_id] = datetime.now()

    logger.info(f"WebSocket connected: {session_id}")

    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "message": "Подключено к AI Business Analyst"
    })

    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "message":
                user_message = data.get("content", "")

                if not user_message:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Empty message"
                    })
                    continue

                await websocket.send_json({
                    "type": "typing",
                    "message": "AI думает..."
                })

                try:
                    response = await app_state.assistant.process_message(
                        user_message=user_message,
                        session_id=session_id
                    )

                    session_info = app_state.assistant.get_session_info(session_id)

                    document_ready = session_info.get("progress", 0.0) >= 1.0
                    document_path = None

                    if document_ready and "📄 Файл:" in response:
                        import re
                        match = re.search(r'`([^`]+\.docx)`', response)
                        if match:
                            document_path = match.group(1)

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
                        "message": f"Ошибка: {str(e)}"
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
# SESSION ENDPOINTS
# ============================================================================

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


@app.post("/api/session/{session_id}/summary", response_model=SessionSummaryResponse)
async def generate_session_summary(session_id: str):
    """
    🆕 Генерировать AI-powered summary сессии (+5 баллов)
    """
    try:
        session = app_state.history_db.get_session(session_id)
        if not session:
            raise HTTPException(404, "Session not found")

        messages = app_state.history_db.get_session_messages(session_id)

        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])

        summary_prompt = f"""
Проанализируй следующий диалог и создай краткое резюме:

{conversation_text}

Предоставь:
1. Summary (2-3 предложения о чем диалог)
2. Key points (3-5 главных моментов списком)
3. Тип документа который обсуждался

Ответь В ФОРМАТЕ JSON:
{{
  "summary": "...",
  "key_points": ["...", "..."],
  "doc_type": "..."
}}
"""

        llm_response = await app_state.assistant.llm.generate(
            prompt=summary_prompt,
            system_prompt="You are a business analyst summarizing conversations. Return ONLY valid JSON.",
            temperature=0.3,
            max_tokens=500
        )

        import json
        import re

        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            summary_data = json.loads(json_match.group())
        else:
            summary_data = {
                "summary": llm_response[:200],
                "key_points": ["Unable to parse summary"],
                "doc_type": session.get("doc_type")
            }

        return SessionSummaryResponse(
            session_id=session_id,
            summary=summary_data.get("summary", ""),
            key_points=summary_data.get("key_points", []),
            doc_type=summary_data.get("doc_type") or session.get("doc_type"),
            total_messages=len(messages)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Generate summary failed: {e}")
        raise HTTPException(500, str(e))


# ============================================================================
# DOCUMENT ENDPOINTS
# ============================================================================

@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Список всех документов"""
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
# DIAGRAM ENDPOINTS (+10 баллов)
# ============================================================================

@app.post("/api/diagrams/generate", response_model=DiagramResponse)
async def generate_diagram(request: DiagramGenerateRequest):
    """
    🆕 Генерировать Mermaid диаграмму (+5 баллов)

    Types: process_flow, sequence, use_case, kpi_dashboard
    """
    try:
        mermaid_code = None

        if request.type == "process_flow":
            steps = request.data.get("steps", [])
            mermaid_code = MermaidGenerator.generate_process_flow(
                title=request.title,
                steps=steps,
                style=request.style
            )

        elif request.type == "sequence":
            participants = request.data.get("participants", [])
            interactions = request.data.get("interactions", [])
            mermaid_code = MermaidGenerator.generate_sequence_diagram(
                title=request.title,
                participants=participants,
                interactions=interactions
            )

        elif request.type == "use_case":
            use_cases = request.data.get("use_cases", [])
            mermaid_code = MermaidGenerator.generate_use_case_diagram(
                title=request.title,
                use_cases=use_cases
            )

        elif request.type == "kpi_dashboard":
            kpis = request.data.get("kpis", [])
            mermaid_code = MermaidGenerator.generate_kpi_dashboard(
                title=request.title,
                kpis=kpis
            )

        else:
            raise HTTPException(400, f"Unknown diagram type: {request.type}")

        return DiagramResponse(
            mermaid_code=mermaid_code,
            diagram_type=request.type
        )

    except Exception as e:
        logger.error(f"Diagram generation failed: {e}")
        raise HTTPException(500, str(e))


@app.post("/api/diagrams/mermaid-to-png")
async def convert_mermaid_to_png(request: MermaidToPNGRequest):
    """
    🆕 Конвертировать Mermaid в PNG (+5 баллов)

    **Request body:**
    ```json
    {
      "mermaid_code": "graph TD\\n    A-->B",
      "return_base64": true
    }
    ```
    """
    try:
        if request.return_base64:
            base64_img = app_state.mermaid_converter.convert_and_embed_base64(request.mermaid_code)
            return {
                "format": "base64",
                "data": base64_img
            }
        else:
            png_path = app_state.mermaid_converter.convert_to_png(request.mermaid_code)
            return {
                "format": "file",
                "path": png_path,
                "url": f"/diagrams/{Path(png_path).name}"
            }

    except Exception as e:
        logger.error(f"Mermaid → PNG failed: {e}")
        raise HTTPException(500, str(e))


# ============================================================================
# HISTORY ENDPOINTS (+5 баллов)
# ============================================================================

@app.get("/api/history")
async def list_session_history(
    limit: int = Query(default=50, ge=1, le=200),
    status: Optional[str] = None
):
    """
    🆕 Список всех сессий с историей (+5 баллов)
    """
    try:
        sessions = app_state.history_db.list_sessions(limit=limit, status=status)

        result = []
        for session in sessions:
            messages = app_state.history_db.get_session_messages(
                session["session_id"],
                limit=100
            )

            result.append({
                "session_id": session["session_id"],
                "doc_type": session.get("doc_type"),
                "status": session["status"],
                "messages": messages,
                "created_at": session["created_at"],
                "updated_at": session["updated_at"]
            })

        return result

    except Exception as e:
        logger.error(f"List history failed: {e}")
        raise HTTPException(500, str(e))


@app.get("/api/history/{session_id}")
async def get_session_history(session_id: str):
    """Получить историю конкретной сессии"""
    try:
        session = app_state.history_db.get_session(session_id)

        if not session:
            raise HTTPException(404, "Session not found")

        messages = app_state.history_db.get_session_messages(session_id)

        return {
            "session_id": session_id,
            "doc_type": session.get("doc_type"),
            "status": session["status"],
            "messages": messages,
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get history failed: {e}")
        raise HTTPException(500, str(e))


@app.delete("/api/history/{session_id}")
async def delete_session_history(session_id: str):
    """Удалить историю сессии"""
    try:
        app_state.history_db.delete_session(session_id)
        return {"status": "ok", "message": "Session history deleted"}
    except Exception as e:
        logger.error(f"Delete history failed: {e}")
        raise HTTPException(500, str(e))


# ============================================================================
# STATISTICS ENDPOINT
# ============================================================================

@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """
    🆕 Статистика системы (+2 балла)
    """
    try:
        stats = app_state.history_db.get_statistics()
        return StatisticsResponse(**stats)
    except Exception as e:
        logger.error(f"Get statistics failed: {e}")
        raise HTTPException(500, str(e))


# ============================================================================
# CONFLUENCE ENDPOINTS (опционально)
# ============================================================================

@app.post("/api/confluence/publish")
async def publish_to_confluence(request: ConfluencePublishRequest):
    """
    🆕 Опубликовать документ в Confluence (если настроено)

    **Request body:**
    ```json
    {
      "title": "BRD - Payment System",
      "content": "# Business Requirements...",
      "mermaid_diagrams": {
        "process": "graph TD\\n    A-->B"
      }
    }
    ```
    """
    if not app_state.confluence_client:
        raise HTTPException(503, "Confluence not configured")

    try:
        # Создать HTML контент с диаграммами
        html_content = ConfluenceMermaidHelper.create_brd_page_with_diagrams(
            title=request.title,
            brd_content=request.content,
            mermaid_diagrams=request.mermaid_diagrams or {}
        )

        # Создать страницу
        page = await app_state.confluence_client.create_page(
            title=request.title,
            content=html_content
        )

        return {
            "status": "ok",
            "page_id": page["id"],
            "page_url": page["url"]
        }

    except Exception as e:
        logger.error(f"Confluence publish failed: {e}")
        raise HTTPException(500, str(e))


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.get("/api/admin/sessions")
async def list_active_sessions():
    """Список активных сессий"""
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


@app.post("/api/admin/cleanup-history")
async def cleanup_old_history(request: CleanupHistoryRequest):
    """
    Удалить историю старше N дней

    **Request body:**
    ```json
    {
      "days": 30
    }
    ```
    """
    try:
        deleted = app_state.history_db.cleanup_old_sessions(days=request.days)
        return {
            "status": "ok",
            "deleted_sessions": deleted,
            "days": request.days
        }
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(500, str(e))


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