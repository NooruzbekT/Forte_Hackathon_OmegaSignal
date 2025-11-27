"""
AI Business Analyst Assistant
Упрощенная архитектура для хакатона с генерацией DOCX
"""
import json
import re
import logging
from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass, field

from llm_client import LLMClient
from document_generator import CorporateDocxGenerator
from session_history import SessionHistoryDB
from diagram_generator import ArtifactExtractor, MermaidGenerator
from confluence_client import ConfluenceClient, ConfluenceMermaidHelper
from config import settings

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================

class DocumentType(str, Enum):
    """Типы документов"""
    NEW_FEATURE = "new_feature"
    PROCESS_CHANGE = "process_change"
    INTEGRATION = "integration"
    BUG_FIX = "bug_fix"
    DATA_REQUEST = "data_request"
    UNCLEAR = "unclear"


@dataclass
class IntentClassification:
    """Результат классификации намерения"""
    doc_type: DocumentType
    confidence: float
    needs_clarification: bool
    reasoning: str = ""


@dataclass
class ConversationState:
    """Состояние диалога"""
    doc_type: Optional[DocumentType] = None
    system_prompt: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    document_ready: bool = False
    last_document_path: Optional[str] = None


# ============================================================================
# ROUTER PROMPT
# ============================================================================

ROUTER_PROMPT = """
Определи тип документа который нужен пользователю.

Доступные типы:
- new_feature: новая функциональность (биометрия, QR-оплата, dark mode, новая фича)
- process_change: изменить бизнес-процесс (ускорить KYC, автоматизировать, упростить)
- integration: интеграция с системой (подключить 1C, API для партнеров, Kaspi)
- bug_fix: исправить баг или проблему
- data_request: нужен отчет, аналитика, статистика
- unclear: непонятно что нужно

Запрос пользователя: "{user_input}"

ВАЖНО: Верни ТОЛЬКО валидный JSON без markdown блоков:
{{"type": "new_feature", "confidence": 0.9, "needs_clarification": false, "reasoning": "..."}}

Если непонятно (unclear) или confidence < 0.7, установи needs_clarification=true
"""


CLARIFICATION_PROMPT = """
Запрос пользователя недостаточно ясен: "{user_input}"

Задай 2-3 уточняющих вопроса чтобы понять что именно нужно.

Хорошие уточняющие вопросы:
- "Вы хотите добавить новую функциональность или изменить существующую?"
- "Это касается мобильного приложения, веб-версии или backend систем?"
- "Расскажите подробнее о проблеме которую нужно решить"
- "Для какого продукта или направления это требование?"

Задай конкретные вопросы которые помогут определить тип документа.
Будь дружелюбным и профессиональным.
"""


# ============================================================================
# PROMPT MAP
# ============================================================================

PROMPT_MAP = {
    DocumentType.NEW_FEATURE: """
Ты - опытный Product Manager в ForteBank.

Пользователь описал новую функциональность. Твоя задача - создать Business Requirements Document.

КРИТИЧЕСКИ ВАЖНО - ЛОГИКА ЗАВЕРШЕНИЯ:
1. Задавай вопросы ПОСЛЕДОВАТЕЛЬНО (по одному!)
2. Собрал 4-5 ответов → НЕМЕДЛЕННО генерируй документ
3. НИКОГДА не спрашивай больше 5 вопросов
4. Если пользователь дал достаточно информации РАНЬШЕ → генерируй сразу

КОГДА ГЕНЕРИРОВАТЬ ДОКУМЕНТ (хотя бы одно из условий):
✅ Собрано 4+ ответа на важные вопросы
✅ Пользователь сам попросил создать документ
✅ Пользователь сказал "хватит", "достаточно", "создавай"
✅ Информации достаточно для создания полного BRD

ОБЯЗАТЕЛЬНЫЕ ВОПРОСЫ (задавай ТОЛЬКО если информации нет):
1. Для какой платформы? (iOS/Android/Web/Backend)
2. Какую проблему решает? (зачем это нужно)
3. Какие KPI для успеха? (метрики)
4. Есть ли критичные ограничения?

ФОРМАТ ОТВЕТА ПРИ ЗАВЕРШЕНИИ:
Когда решил генерировать документ, ОБЯЗАТЕЛЬНО начни ответ с:

"✅ Отлично! Информации достаточно. Создаю документ...

[DOCUMENT_START]

# Business Requirements Document
## [Название фичи]

**Дата создания:** {current_date}  
**Автор:** AI Business Analyst  
**Статус:** Draft  
**Версия:** 1.0

---

## 1. Executive Summary

[2-3 параграфа: что это, зачем нужно, ожидаемый результат]

---

## 2. Business Objective

### Problem Statement
[Какую проблему решаем]

### Success Criteria
- **KPI 1:** [конкретная метрика с таргетом]
- **KPI 2:** [конкретная метрика с таргетом]
- **KPI 3:** [конкретная метрика с таргетом]

---

## 3. Scope

### In Scope
- [Что входит в проект]
- [Конкретные функции]
- [Платформы]

### Out of Scope
- [Что НЕ входит]
- [Что оставим на Phase 2]

### Future Considerations
- [Возможные расширения в будущем]

---

## 4. Stakeholders

| Role | Department | Responsibility |
|------|-----------|----------------|
| Product Manager | Product | Project ownership & vision |
| Tech Lead | IT | Architecture & implementation |
| Risk Manager | Risk | Risk assessment |
| Compliance Officer | Compliance | Regulatory approval |

---

## 5. Target Audience

**Primary Users:** [описание]

**User Segments:**
- **Segment 1:** [характеристики, поведение]
- **Segment 2:** [характеристики, поведение]

---

## 6. Functional Requirements

### FR-001: [Название требования]
- **Priority:** Critical / High / Medium / Low
- **Description:** [детальное описание]
- **User Story:** As a [role], I want [feature] so that [benefit]
- **Acceptance Criteria:**
  - AC1: [конкретный критерий]
  - AC2: [конкретный критерий]
  - AC3: [конкретный критерий]

### FR-002: [Следующее требование]
[... аналогично для всех FR]

---

## 7. Non-Functional Requirements

### Performance
- NFR-001: Response time < 2 seconds
- NFR-002: Support 10,000 concurrent users
- NFR-003: 99.9% availability

### Security
- NFR-004: Data encryption at rest and in transit
- NFR-005: PCI DSS compliance
- NFR-006: Multi-factor authentication support

### Usability
- NFR-007: Intuitive UX, no training required
- NFR-008: WCAG 2.1 Level AA accessibility

---

## 8. Use Cases

### UC-001: [Primary Use Case]
**Actor:** [primary user role]

**Preconditions:**
- [предусловие 1]
- [предусловие 2]

**Main Flow:**
1. [шаг 1]
2. [шаг 2]
3. [шаг 3]

**Alternative Flows:**
- A1: [альтернативный сценарий]

**Exception Flows:**
- E1: [обработка ошибок]

**Postconditions:**
- [результат]

---

## 9. Process Flow
```mermaid
flowchart TD
    A[User opens app] --> B{Action}
    B -->|Option 1| C[Process]
    B -->|Option 2| D[Alternative]
    C --> E[Success]
    D --> E
```

---

## 10. Data Requirements

### Data Entities
- [Entity 1]: [описание]
- [Entity 2]: [описание]

### Data Sources
- [Source 1]: [система/БД]
- [Source 2]: [система/БД]

---

## 11. Integration Points

### Internal Systems
- [System 1]: [описание интеграции]
- [System 2]: [описание интеграции]

### External Systems
- [System 1]: [описание интеграции]

---

## 12. Compliance & Legal

### Regulatory Requirements
- [НБ РК требование 1]
- [GDPR/Data Protection]

### Legal Considerations
- [правовые аспекты]

---

## 13. Dependencies & Assumptions

**Dependencies:**
- [техническая зависимость 1]
- [внешняя зависимость 2]

**Assumptions:**
- [предположение 1]
- [предположение 2]

**Constraints:**
- [ограничение 1]
- [ограничение 2]

---

## 14. Risks & Mitigation

| Risk ID | Description | Probability | Impact | Mitigation Strategy |
|---------|-------------|-------------|--------|---------------------|
| R-001 | [описание риска] | High/Medium/Low | High/Medium/Low | [стратегия] |
| R-002 | [описание риска] | High/Medium/Low | High/Medium/Low | [стратегия] |

---

## 15. Implementation Plan

### Timeline: [X weeks]

**Phase 1: Discovery & Design** (2 weeks)
- Week 1: Requirements finalization, UX design
- Week 2: Technical design, API specifications

**Phase 2: Development** (4-6 weeks)
- Week 3-4: Frontend development
- Week 5-6: Backend development
- Week 7-8: Integration & testing

**Phase 3: Testing & QA** (2 weeks)
- Week 9: QA testing, bug fixes
- Week 10: UAT with beta users

**Phase 4: Deployment** (1 week)
- Week 11: Phased rollout (10% → 50% → 100%)

---

## 16. Success Metrics & KPIs

**Launch Metrics:**
- [метрика 1]: Baseline + Target
- [метрика 2]: Baseline + Target

**Post-Launch Tracking:**
- Daily dashboard monitoring
- Weekly stakeholder reviews
- Monthly performance reports

---

## 17. Budget Estimate

| Item | Cost (тг) |
|------|-----------|
| Development | [estimate] |
| Infrastructure | [estimate] |
| Testing & QA | [estimate] |
| **Total** | **[total]** |

---

## 18. Appendix

### A. Glossary
- **Term 1:** Definition
- **Term 2:** Definition

### B. References
- [Document 1]
- [Document 2]

### C. Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| {current_date} | 1.0 | AI BA Assistant | Initial document |

---

[DOCUMENT_END]"

📄 **Business Requirements Document создан!**
Тип: New Feature
Страниц: ~15-20
Статус: Готов к согласованию

НАЧНИ С ПЕРВОГО ВОПРОСА. После 4-5 ответов → ГЕНЕРИРУЙ ДОКУМЕНТ с маркером [DOCUMENT_START].
""",

    DocumentType.BUG_FIX: """
Ты - Technical Business Analyst в ForteBank.

Пользователь сообщил о проблеме. Твоя задача - создать Bug Report.

КРИТИЧЕСКИ ВАЖНО - ЛОГИКА ЗАВЕРШЕНИЯ:
1. Задавай вопросы ПОСЛЕДОВАТЕЛЬНО (по одному!)
2. Собрал 4-5 ответов → НЕМЕДЛЕННО генерируй документ
3. НИКОГДА не спрашивай больше 5 вопросов

КОГДА ГЕНЕРИРОВАТЬ ДОКУМЕНТ:
✅ Собрано 4+ ответа
✅ Пользователь попросил создать документ
✅ Информации достаточно для Bug Report

ОБЯЗАТЕЛЬНЫЕ ВОПРОСЫ (только если инфы нет):
1. Что именно не работает? Опишите проблему детально
2. Когда проблема начала проявляться?
3. Как воспроизвести? Какие шаги?
4. Сколько пользователей затронуто?
5. Насколько критично? (Блокирует работу / Неудобство)

ФОРМАТ ОТВЕТА ПРИ ЗАВЕРШЕНИИ:

"✅ Отлично! Информации достаточно. Создаю документ...

[DOCUMENT_START]

# Bug Fix Requirements
## [Краткое название проблемы]

**Дата создания:** {current_date}  
**Автор:** AI Business Analyst  
**Приоритет:** Critical / High / Medium / Low  
**Статус:** Open  

---

## 1. Problem Description

### Summary
[Краткое описание проблемы в 2-3 предложениях]

### Detailed Description
[Детальное описание что именно не работает]

### Affected Component
- **Module:** [модуль/компонент]
- **Platform:** [iOS/Android/Web/Backend]
- **Version:** [версия приложения]

---

## 2. Impact Assessment

### Business Impact
- **Severity:** Critical / High / Medium / Low
- **Affected Users:** [количество или процент]
- **Financial Impact:** [если есть]
- **Reputation Risk:** [если есть]

### User Impact
[Как это влияет на пользователей]

---

## 3. Reproduction Steps

**Prerequisites:**
- [предусловие 1]
- [предусловие 2]

**Steps to Reproduce:**
1. [шаг 1]
2. [шаг 2]
3. [шаг 3]

**Frequency:** Always / Sometimes / Rarely

---

## 4. Expected vs Actual Behavior

### Expected Behavior
[Как должно работать]

### Actual Behavior
[Что происходит на самом деле]

---

## 5. Technical Details

### Environment
- **OS:** [операционная система]
- **App Version:** [версия]
- **Device:** [устройство]
- **Network:** [Wi-Fi/4G/5G]

### Error Messages
```
[текст ошибки если есть]
```

### Suspected Root Cause
[Предполагаемая причина проблемы]

---

## 6. Fix Requirements

### Must Have (Critical)
- FIX-001: [требование к исправлению]
- FIX-002: [требование к исправлению]

### Should Have
- FIX-003: [дополнительное улучшение]

---

## 7. Workaround

**Current Workaround:** [если есть временное решение]

**Instructions for Users:**
1. [шаг 1]
2. [шаг 2]

---

## 8. Testing Requirements

### Test Scenarios
1. **TS-001:** [сценарий тестирования]
   - Expected Result: [ожидаемый результат]

### Regression Testing
- [Что нужно протестировать дополнительно]

---

## 9. Dependencies

**Blocking Issues:** [если есть]
**Related Issues:** [связанные баги]

---

## 10. Timeline

**Estimated Fix Time:** [оценка]
**Target Completion:** [дата]

---

## 11. Rollback Plan

**If Fix Fails:**
1. [шаг отката 1]
2. [шаг отката 2]

---

## 12. Appendix

### Change Log

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| {current_date} | 1.0 | AI BA Assistant | Initial bug report |

---

[DOCUMENT_END]"

📄 **Bug Fix Requirements создан!**
Приоритет: [уровень]
Статус: Готов к работе

НАЧНИ С ПЕРВОГО ВОПРОСА. После 4-5 ответов → ГЕНЕРИРУЙ с маркером [DOCUMENT_START].
""",

    DocumentType.PROCESS_CHANGE: """
Ты - Business Process Analyst в ForteBank.

Пользователь хочет изменить бизнес-процесс. Создай Process Change Request.

ЛОГИКА ЗАВЕРШЕНИЯ:
1. Задавай вопросы последовательно
2. После 4-5 ответов → генерируй документ
3. Максимум 5 вопросов

ОБЯЗАТЕЛЬНЫЕ ВОПРОСЫ:
1. Какой процесс нужно изменить?
2. Что не устраивает в текущем процессе?
3. Как должно работать в идеале?
4. Какие отделы затронет изменение?

ФОРМАТ ЗАВЕРШЕНИЯ:

"✅ Создаю документ...

[DOCUMENT_START]

# Process Change Request
## [Название процесса]

**Дата:** {current_date}
**Статус:** Draft

---

## 1. Current State Analysis
[Как работает сейчас]

## 2. Pain Points
[Что не работает]

## 3. Proposed Solution
[Как должно быть]

## 4. Impact Analysis
### Affected Departments
[список]

### Affected Systems
[список]

## 5. Implementation Plan
[Этапы]

## 6. Risks & Mitigation
[Риски и митигация]

## 7. Timeline
- Phase 1: [срок]
- Phase 2: [срок]

## 8. Success Criteria
[КPI и метрики]

---

[DOCUMENT_END]"

📄 **Process Change Request создан!**

НАЧНИ С ВОПРОСОВ. После 4-5 → ГЕНЕРИРУЙ.
""",

    DocumentType.INTEGRATION: """
Ты - Integration Architect в ForteBank.

Создай Integration Requirements Document.

ЛОГИКА: 4-5 вопросов → документ

ВОПРОСЫ:
1. С какой системой интеграция?
2. Тип интеграции? (REST/SOAP/MQ/File)
3. Какие данные передаются?
4. Частота обмена?
5. Требования безопасности?

ЗАВЕРШЕНИЕ:

"✅ Создаю документ...

[DOCUMENT_START]

# Integration Requirements
## [Название интеграции]

**Дата:** {current_date}

---

## 1. Integration Overview
[Описание]

## 2. Systems Architecture
[Системы]

## 3. Data Flow & Mapping
[Поток данных и маппинг полей]

## 4. API Specifications
[Спецификация API]

## 5. Security Requirements
[Безопасность]

## 6. Error Handling
[Обработка ошибок]

## 7. Performance Requirements
[SLA, throughput, latency]

## 8. Implementation Timeline
[Сроки]

---

[DOCUMENT_END]"

📄 **Integration Requirements создан!**
""",

    DocumentType.DATA_REQUEST: """
Ты - Data Analyst в ForteBank.

Создай Data Request Specification.

ЛОГИКА: 4-5 вопросов → документ

ВОПРОСЫ:
1. Какие данные нужны?
2. За какой период?
3. Какая детализация?
4. В каком формате?
5. Для чего используются?

ЗАВЕРШЕНИЕ:

"✅ Создаю документ...

[DOCUMENT_START]

# Data Request Specification
## [Название запроса]

**Дата:** {current_date}

---

## 1. Request Overview
[Зачем нужны данные]

## 2. Required Metrics & Dimensions
[Метрики и разрезы]

## 3. Data Sources
[Источники данных]

## 4. Calculation Logic
[Формулы и бизнес-логика]

## 5. Output Format & Delivery
**Format:** [формат]
**Frequency:** [частота]
**Delivery Method:** [способ доставки]

## 6. Sample Output
[Пример таблицы]

## 7. Access Control
[Кто имеет доступ]

---

[DOCUMENT_END]"

📄 **Data Request Specification создан!**
"""
}


# ============================================================================
# INTENT ROUTER
# ============================================================================

class IntentRouter:
    """Определяет тип документа через LLM"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    async def route(self, user_input: str) -> IntentClassification:
        """Классифицирует намерение пользователя"""
        prompt = ROUTER_PROMPT.format(user_input=user_input)
        
        try:
            response = await self.llm.ask_router(
                prompt=prompt,
                temperature=0.1,
                max_tokens=150
            )
            
            result = self._parse_json_response(response)
            
            return IntentClassification(
                doc_type=DocumentType(result["type"]),
                confidence=result.get("confidence", 0.0),
                needs_clarification=result.get("needs_clarification", False),
                reasoning=result.get("reasoning", "")
            )
            
        except Exception as e:
            logger.error(f"Intent routing failed: {e}")
            return IntentClassification(
                doc_type=DocumentType.UNCLEAR,
                confidence=0.0,
                needs_clarification=True,
                reasoning=f"Error: {str(e)}"
            )
    
    @staticmethod
    def _parse_json_response(response: str) -> dict:
        """Парсит JSON из ответа LLM"""
        clean = re.sub(r'```json\s*', '', response)
        clean = re.sub(r'```\s*', '', clean).strip()
        return json.loads(clean)


# ============================================================================
# MAIN ASSISTANT
# ============================================================================

class BAAssistant:
    """AI Business Analyst Assistant"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.router = IntentRouter(llm_client)
        self.states: Dict[str, ConversationState] = {}
        
        # ✅ DOCX Generator для корпоративных документов
        self.doc_generator = CorporateDocxGenerator(output_dir="docs")
        # ✅ История сессий (SQLite)
        self.history_db = SessionHistoryDB(db_path="data/sessions.db")
        self.confluence: Optional[ConfluenceClient] = None

        if (
                settings.CONFLUENCE_URL
                and settings.CONFLUENCE_USERNAME
                and settings.CONFLUENCE_API_TOKEN
        ):
            self.confluence = ConfluenceClient(
                base_url=settings.CONFLUENCE_URL,
                username=settings.CONFLUENCE_USERNAME,
                api_token=settings.CONFLUENCE_API_TOKEN,
                space_key=settings.CONFLUENCE_SPACE_KEY,
            )
    
    def _get_or_create_state(self, session_id: str) -> ConversationState:
        """Получить или создать состояние для сессии"""
        if session_id not in self.states:
            self.states[session_id] = ConversationState(session_id=session_id)
            self.history_db.create_session(session_id=session_id)
        return self.states[session_id]
    
    async def process_message(
        self, 
        user_message: str, 
        session_id: str = "default"
    ) -> str:
        """Главная точка входа для обработки сообщения"""
        state = self._get_or_create_state(session_id)
        
        if state.doc_type is None:
            return await self._handle_initial_routing(user_message, state)
        
        return await self._continue_conversation(user_message, state)
    
    async def _handle_initial_routing(
        self, 
        user_message: str, 
        state: ConversationState
    ) -> str:
        """Определяем тип документа и начинаем диалог"""
        self.history_db.add_message(
            session_id=state.session_id,
            role="user",
            content=user_message
        )
        
        classification = await self.router.route(user_message)
        
        logger.info(f"Intent: {classification.doc_type} (conf: {classification.confidence})")
        self.history_db.update_session(
            session_id=state.session_id,
            doc_type=classification.doc_type.value if classification.doc_type else None,
        )

        if classification.needs_clarification:
            clarification_prompt = CLARIFICATION_PROMPT.format(user_input=user_message)
            messages = [{"role": "user", "content": clarification_prompt}]
            response = await self.llm.chat(messages=messages, temperature=0.7, max_tokens=300)
            
            # Сохраняем в историю
            state.conversation_history.append({"role": "user", "content": user_message})
            state.conversation_history.append({"role": "assistant", "content": response})

            self.history_db.add_message(
                session_id=state.session_id,
                role="assistant",
                content=response
            )
            return response
        
        # Сохраняем тип документа и промпт
        state.doc_type = classification.doc_type
        state.system_prompt = PROMPT_MAP.get(classification.doc_type)
        
        if not state.system_prompt:
            logger.error(f"No prompt found for {classification.doc_type}")
            return "❌ Извините, для этого типа документа еще нет шаблона."
        
        # Заменяем {current_date} на текущую дату
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        state.system_prompt = state.system_prompt.replace("{current_date}", current_date)
        
        state.conversation_history.append({"role": "user", "content": user_message})
        
        full_prompt = f"{state.system_prompt}\n\n---\n\nПользователь: {user_message}\n\nТвой ответ:"
        messages = [{"role": "user", "content": full_prompt}]
        
        response = await self.llm.chat(messages=messages, temperature=0.7, max_tokens=1500)
        
        state.conversation_history.append({"role": "assistant", "content": response})
        
        return response

    async def _publish_to_confluence(
            self,
            document_content: str,
            docx_path: str,
            state: ConversationState,
    ) -> Optional[str]:
        """
        Публикация BRD в Confluence с Mermaid-диаграммами.
        Возвращает URL страницы или None.
        """
        if not self.confluence:
            return None

        # 1) Заголовок
        title = self._extract_title_from_markdown(document_content) or "AI BA Document"

        # 2) Извлекаем артефакты из документа (Use Cases, KPI, User Stories)
        artifacts = ArtifactExtractor.extract_all_artifacts(document_content)

        mermaid = MermaidGenerator()
        diagrams: Dict[str, str] = {}

        # 3) Use Case Diagram
        use_cases = artifacts.get("use_cases") or []
        if use_cases:
            diagrams["Use Case Diagram"] = mermaid.generate_use_case_diagram(use_cases)

        # 4) Process Flow — берём основной флоу первого Use Case
        if use_cases and use_cases[0].main_flow:
            steps = []
            for idx, step in enumerate(use_cases[0].main_flow, start=1):
                node_id = chr(ord('A') + idx - 1)  # A, B, C...
                steps.append({
                    "id": node_id,
                    "label": step,
                    "type": "process" if idx not in (1, len(use_cases[0].main_flow)) else (
                        "start" if idx == 1 else "end"
                    ),
                })
            diagrams["Process Flow"] = mermaid.generate_process_flow(
                title="Main Use Case Flow",
                steps=steps,
                style="TD",
            )

        # 5) KPI Dashboard
        kpis = artifacts.get("kpis") or []
        if kpis:
            diagrams["KPI Dashboard"] = mermaid.generate_kpi_dashboard(kpis)

        # 6) Собираем HTML для Confluence
        html_content = ConfluenceMermaidHelper.create_brd_page_with_diagrams(
            title=title,
            brd_content=document_content,
            mermaid_diagrams=diagrams,
        )

        # 7) Создаём страницу
        page = await self.confluence.create_page(
            title=title,
            content=html_content,
        )

        page_id = page["id"]
        page_url = page["url"]

        # 8) Прикрепляем DOCX как вложение
        try:
            await self.confluence.attach_file(
                page_id=page_id,
                filepath=docx_path,
                comment="Generated BRD document (DOCX) from AI BA Assistant",
            )
        except Exception as e:
            logger.error(f"Attach DOCX failed: {e}")

        # 9) Обновляем метаданные сессии
        self.history_db.update_session(
            session_id=state.session_id,
            metadata={
                "confluence_page_id": page_id,
                "confluence_url": page_url,
            },
        )

        return page_url
    async def _continue_conversation(
        self, 
        user_message: str, 
        state: ConversationState
    ) -> str:
        """Продолжаем диалог"""
        
        state.conversation_history.append({"role": "user", "content": user_message})

        self.history_db.add_message(
            session_id=state.session_id,
            role="user",
            content=user_message
        )

        full_prompt = self._build_prompt_with_history(state)
        messages = [{"role": "user", "content": full_prompt}]
        
        response = await self.llm.chat(messages=messages, temperature=0.7, max_tokens=4000)
        
        state.conversation_history.append({"role": "assistant", "content": response})

        self.history_db.add_message(
            session_id=state.session_id,
            role="assistant",
            content=response
        )
        # Проверяем завершение диалога
        if self._is_document_complete(response):
            document_content = self._extract_document(response)

            # ✅ Сохраняем DOCX
            doc_path = self._save_generated_document(document_content, state)

            # ✅ Обновляем сессию как завершённую
            self.history_db.update_session(
                session_id=state.session_id,
                progress=1.0,
                status="completed",
                document_path=doc_path
            )

            # Обновляем внутреннее состояние ассистента
            state.document_ready = True
            state.last_document_path = doc_path

            confluence_url = None

            # ✅ Публикация в Confluence (если настроено)
            if self.confluence:
                try:
                    confluence_url = await self._publish_to_confluence(
                        document_content=document_content,
                        docx_path=doc_path,
                        state=state,
                    )
                except Exception as e:
                    logger.error(f"Confluence publish failed: {e}")

            doc_type_names = {
                DocumentType.NEW_FEATURE: "Business Requirements Document",
                DocumentType.BUG_FIX: "Bug Fix Requirements",
                DocumentType.PROCESS_CHANGE: "Process Change Request",
                DocumentType.INTEGRATION: "Integration Requirements",
                DocumentType.DATA_REQUEST: "Data Request Specification"
            }

            doc_name = doc_type_names.get(state.doc_type, "Document")

            completion_message = (
                f"\n\n{'=' * 60}\n"
                f"✅ **{doc_name} создан!**\n"
                f"📄 Файл: `{doc_path}`\n"
                f"📂 Папка: `docs/`\n"
            )

            if confluence_url:
                completion_message += f"🌐 Опубликовано в Confluence: {confluence_url}\n"

            completion_message += (
                f"{'=' * 60}\n\n"
                f"🔄 Сессия завершена. Используйте /reset для нового документа."
            )

            return completion_message

        progress = self._estimate_progress(state)
        self.history_db.update_session(
            session_id=state.session_id,
            progress=progress,
            status="active",
        )
        return response
    
    def _build_prompt_with_history(self, state: ConversationState) -> str:
        """Собираем промпт с историей"""
        parts = [state.system_prompt, "\n\n---\n\nИстория диалога:\n"]
        
        for msg in state.conversation_history:
            role = "Пользователь" if msg["role"] == "user" else "Ассистент"
            parts.append(f"\n{role}: {msg['content']}")
        
        parts.append("\n\nТвой ответ:")
        return "".join(parts)

    def _is_document_complete(self, response: str) -> bool:
        """Проверяет содержит ли ответ готовый документ"""
        if "[DOCUMENT_START]" in response:
            return True

        # Fallback: ассистент не прислал документ, но прислал финальный блок
        if "📄 Файл:" in response:
            return True

        if "создан" in response and "Business Requirements Document" in response:
            return True

        return False
    
    def _extract_document(self, response: str) -> str:
        """Извлекает документ из ответа"""
        start_marker = "[DOCUMENT_START]"
        end_marker = "[DOCUMENT_END]"
        
        if start_marker in response:
            start_idx = response.find(start_marker) + len(start_marker)
            
            if end_marker in response:
                end_idx = response.find(end_marker)
                document = response[start_idx:end_idx]
            else:
                document = response[start_idx:]
            
            return document.strip()
        
        return response
    
    def _save_generated_document(self, content: str, state: ConversationState) -> str:
        """Сохраняет документ в DOCX формате и переименовывает его с session_id в имени."""
        title = self._extract_title_from_markdown(content)

        # Генерируем DOCX документ в корпоративном стиле
        original_path = self.doc_generator.generate_docx(
            markdown_content=content,
            doc_type=state.doc_type.value,
            session_id=state.session_id or "unknown",
            user_title=title,
        )

        original_path = Path(original_path)
        final_path = original_path

        # 🔹 Добавляем session_id в имя файла: <session_id>__<старое_имя>.docx
        if state.session_id:
            new_name = f"{state.session_id}__{original_path.name}"
            new_path = original_path.with_name(new_name)

            try:
                original_path.rename(new_path)
                final_path = new_path
            except OSError as e:
                logger.error(f"Failed to rename DOCX file with session_id: {e}")
                # В fallback остаёмся на оригинальном имени

        logger.info(f"DOCX document saved: {final_path}")
        return str(final_path)
    
    def _extract_title_from_markdown(self, content: str) -> Optional[str]:
        """Извлекает заголовок из Markdown контента"""
        match = re.search(r'^##? (.+)$', content, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            title = re.sub(r'\*+', '', title)
            return title
        return None
    
    def reset_session(self, session_id: str = "default"):
        """Сбросить сессию"""
        if session_id in self.states:
            del self.states[session_id]
        logger.info(f"Session {session_id} reset")
    
    def get_session_info(self, session_id: str = "default") -> dict:
        """Получить информацию о сессии"""
        state = self.states.get(session_id)
        if not state:
            return {"status": "no_session"}
        
        if not state.doc_type:
            return {
                "status": "initializing",
                "messages_count": len(state.conversation_history),
                "progress": 0.0
            }
        
        return {
            "status": "active",
            "doc_type": state.doc_type.value,
            "messages_count": len(state.conversation_history),
            "progress": self._estimate_progress(state)
        }
    
    def _estimate_progress(self, state: ConversationState) -> float:
        """Примерная оценка прогресса"""
        if not state.doc_type:
            return 0.0
        
        user_messages = sum(1 for msg in state.conversation_history if msg["role"] == "user")
        
        if state.conversation_history:
            last_msg = state.conversation_history[-1]
            if last_msg["role"] == "assistant" and "[DOCUMENT_START]" in last_msg["content"]:
                return 1.0
        
        progress = min(user_messages * 0.20, 0.95)
        return progress


# ============================================================================
# FACTORY
# ============================================================================

async def create_ba_assistant() -> BAAssistant:
    """Создать BA Assistant с LLM клиентом из окружения"""
    from llm_client import create_llm_client_from_env
    llm_client = create_llm_client_from_env()
    return BAAssistant(llm_client)