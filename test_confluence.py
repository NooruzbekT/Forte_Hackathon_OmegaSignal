"""
Тестирование Confluence интеграции
"""
import asyncio
import os
from pathlib import Path
from confluence_client import ConfluenceClient, ConfluenceMermaidHelper
from dotenv import load_dotenv


async def test_connection():
    """Тест 1: Проверка подключения"""
    print("\n" + "=" * 80)
    print("🧪 Тест 1: Connection Test")
    print("=" * 80)

    load_dotenv()

    # Проверка переменных окружения
    required_vars = [
        "CONFLUENCE_URL",
        "CONFLUENCE_USERNAME",
        "CONFLUENCE_API_TOKEN",
        "CONFLUENCE_SPACE_KEY"
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("your-"):
            missing.append(var)
        else:
            # Показываем замаскированную версию
            if "TOKEN" in var or "PASSWORD" in var:
                display = value[:10] + "..." + value[-10:] if len(value) > 20 else "***"
            else:
                display = value
            print(f"✅ {var}: {display}")

    if missing:
        print(f"\n❌ Отсутствуют переменные окружения:")
        for var in missing:
            print(f"   - {var}")
        print(f"\n💡 Настрой их в .env файле!")
        return False

    # Подключение
    confluence = ConfluenceClient(
        base_url=os.getenv("CONFLUENCE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        api_token=os.getenv("CONFLUENCE_API_TOKEN"),
        space_key=os.getenv("CONFLUENCE_SPACE_KEY")
    )

    connected = await confluence.test_connection()

    if connected:
        print("\n✅ Подключение к Confluence успешно!")
    else:
        print("\n❌ Не удалось подключиться к Confluence")
        print("   Проверь:")
        print("   1. CONFLUENCE_URL правильный (https://your-domain.atlassian.net)")
        print("   2. CONFLUENCE_USERNAME - твой email")
        print("   3. CONFLUENCE_API_TOKEN - валидный токен")
        print("   4. CONFLUENCE_SPACE_KEY - существующий Space")

    await confluence.close()
    return connected


async def test_create_simple_page():
    """Тест 2: Создание простой страницы"""
    print("\n" + "=" * 80)
    print("🧪 Тест 2: Create Simple Page")
    print("=" * 80)

    load_dotenv()

    confluence = ConfluenceClient(
        base_url=os.getenv("CONFLUENCE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        api_token=os.getenv("CONFLUENCE_API_TOKEN"),
        space_key=os.getenv("CONFLUENCE_SPACE_KEY")
    )

    try:
        # Создаем тестовую страницу
        content = """
<h1>AI Business Analyst - Test Page</h1>
<p>Эта страница создана автоматически AI Business Analyst системой.</p>

<h2>Что это?</h2>
<p>Это тестовая страница для проверки интеграции с Confluence API.</p>

<h2>Возможности</h2>
<ul>
  <li>✅ Автоматическое создание страниц</li>
  <li>✅ Вставка Mermaid диаграмм</li>
  <li>✅ Загрузка DOCX документов</li>
  <li>✅ Генерация BRD документации</li>
</ul>

<h2>Статус</h2>
<p><strong>Тест пройден успешно! 🎉</strong></p>
"""

        page = await confluence.create_page(
            title="AI BA Test Page - " + str(asyncio.get_event_loop().time())[:10],
            content=content
        )

        print(f"✅ Страница создана!")
        print(f"   ID: {page['id']}")
        print(f"   Title: {page['title']}")
        print(f"   URL: {page['url']}")
        print(f"\n💡 Открой в браузере: {page['url']}")

        await confluence.close()
        return page

    except Exception as e:
        print(f"❌ Ошибка при создании страницы: {e}")
        await confluence.close()
        return None


async def test_page_with_mermaid():
    """Тест 3: Страница с Mermaid диаграммой"""
    print("\n" + "=" * 80)
    print("🧪 Тест 3: Page with Mermaid Diagram")
    print("=" * 80)

    load_dotenv()

    confluence = ConfluenceClient(
        base_url=os.getenv("CONFLUENCE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        api_token=os.getenv("CONFLUENCE_API_TOKEN"),
        space_key=os.getenv("CONFLUENCE_SPACE_KEY")
    )

    try:
        # Mermaid диаграмма
        mermaid_code = """
graph TD
    A[User] --> B[AI Assistant]
    B --> C[Intent Classification]
    C --> D{Document Type?}
    D -->|New Feature| E[Create BRD]
    D -->|Bug Fix| F[Create Bug Report]
    D -->|Process Change| G[Create Process Doc]
    E --> H[Generate DOCX]
    F --> H
    G --> H
    H --> I[Download]

    style A fill:#e1f5ff
    style B fill:#fff4e1
    style H fill:#e8f5e9
    style I fill:#f3e5f5
"""

        # Оборачиваем в макрос
        mermaid_macro = ConfluenceMermaidHelper.wrap_mermaid_macro(mermaid_code)

        # Создаем контент
        content = f"""
<h1>AI Business Analyst - Architecture</h1>

<p>Архитектура системы AI Business Analyst для автоматической генерации бизнес-документации.</p>

<h2>Процесс работы</h2>

{mermaid_macro}

<h2>Компоненты</h2>

<table>
  <tr>
    <th>Компонент</th>
    <th>Описание</th>
  </tr>
  <tr>
    <td><strong>User</strong></td>
    <td>Бизнес-аналитик или менеджер проекта</td>
  </tr>
  <tr>
    <td><strong>AI Assistant</strong></td>
    <td>Chatbot с LLM (Groq/Gemini)</td>
  </tr>
  <tr>
    <td><strong>Intent Classification</strong></td>
    <td>Определение типа документа</td>
  </tr>
  <tr>
    <td><strong>Document Generator</strong></td>
    <td>Генерация DOCX с корпоративным стилем</td>
  </tr>
</table>

<h2>Типы документов</h2>

<ul>
  <li>📄 <strong>Business Requirements Document (BRD)</strong> - для новых фич</li>
  <li>🐛 <strong>Bug Fix Report</strong> - для исправления багов</li>
  <li>🔄 <strong>Process Change Document</strong> - для изменения процессов</li>
  <li>🔗 <strong>Integration Specification</strong> - для интеграций</li>
  <li>📊 <strong>Data Request Document</strong> - для запросов данных</li>
</ul>
"""

        page = await confluence.create_page(
            title="AI BA Architecture - " + str(asyncio.get_event_loop().time())[:10],
            content=content
        )

        print(f"✅ Страница с Mermaid создана!")
        print(f"   ID: {page['id']}")
        print(f"   URL: {page['url']}")
        print(f"\n💡 Открой и проверь что диаграмма отображается!")

        await confluence.close()
        return page

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await confluence.close()
        return None


async def test_upload_docx():
    """Тест 4: Загрузка DOCX файла"""
    print("\n" + "=" * 80)
    print("🧪 Тест 4: Upload DOCX Attachment")
    print("=" * 80)

    load_dotenv()

    # Проверяем наличие DOCX файлов
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ Папка docs не найдена!")
        return None

    docx_files = sorted(docs_dir.glob("*.docx"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not docx_files:
        print("❌ DOCX файлы не найдены!")
        return None

    latest_doc = docx_files[0]
    print(f"📄 Загружаем: {latest_doc.name}")

    confluence = ConfluenceClient(
        base_url=os.getenv("CONFLUENCE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        api_token=os.getenv("CONFLUENCE_API_TOKEN"),
        space_key=os.getenv("CONFLUENCE_SPACE_KEY")
    )

    try:
        # Сначала создаем страницу
        content = f"""
<h1>AI Generated BRD Document</h1>

<p>Этот документ был автоматически сгенерирован системой AI Business Analyst.</p>

<h2>Информация</h2>
<ul>
  <li><strong>Файл:</strong> {latest_doc.name}</li>
  <li><strong>Дата:</strong> {latest_doc.stat().st_mtime}</li>
  <li><strong>Размер:</strong> {latest_doc.stat().st_size / 1024:.1f} KB</li>
</ul>

<p>Документ прикреплен ниже как attachment.</p>
"""

        page = await confluence.create_page(
            title="AI Generated BRD - " + str(asyncio.get_event_loop().time())[:10],
            content=content
        )

        print(f"✅ Страница создана: {page['id']}")

        # Прикрепляем DOCX
        result = await confluence.attach_file(
            page_id=page['id'],
            filepath=str(latest_doc),
        )

        print(f"✅ DOCX файл прикреплен!")
        print(f"   URL: {page['url']}")

        await confluence.close()
        return page

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await confluence.close()
        return None


async def test_full_brd_publication():
    """Тест 5: Публикация полного BRD с диаграммами"""
    print("\n" + "=" * 80)
    print("🧪 Тест 5: Full BRD Publication with Diagrams")
    print("=" * 80)

    load_dotenv()

    confluence = ConfluenceClient(
        base_url=os.getenv("CONFLUENCE_URL"),
        username=os.getenv("CONFLUENCE_USERNAME"),
        api_token=os.getenv("CONFLUENCE_API_TOKEN"),
        space_key=os.getenv("CONFLUENCE_SPACE_KEY")
    )

    try:
        # BRD контент (Markdown)
        brd_content = """
## Goal
Создать систему обработки платежей с поддержкой VISA, MasterCard и местных карт.

## Scope
- Интеграция с банковским API
- Поддержка международных платежных систем
- Безопасная обработка транзакций

## Success Criteria
**KPI 1:** Увеличение успешных платежей на 20%  
**KPI 2:** Снижение жалоб на 30%  
**KPI 3:** Расширение базы пользователей на 15%
"""

        # Mermaid диаграммы
        diagrams = {
            "Process Flow": """
graph LR
    A[User Input] --> B[Validate Card]
    B -->|Valid| C[Process Payment]
    B -->|Invalid| D[Show Error]
    C --> E[Send to Bank]
    E -->|Approved| F[Success]
    E -->|Declined| G[Decline]
            """,
            "System Architecture": """
graph TD
    U[User] --> F[Frontend]
    F --> API[API Gateway]
    API --> BA[BA Assistant]
    BA --> LLM[LLM Engine]
    BA --> DG[Doc Generator]
    DG --> S3[Storage]
            """
        }

        # Создаем полный контент
        full_content = ConfluenceMermaidHelper.create_brd_page_with_diagrams(
            title="Payment System BRD",
            brd_content=brd_content,
            mermaid_diagrams=diagrams
        )

        page = await confluence.create_page(
            title="Full BRD Example - " + str(asyncio.get_event_loop().time())[:10],
            content=full_content
        )

        print(f"✅ Полный BRD опубликован!")
        print(f"   ID: {page['id']}")
        print(f"   URL: {page['url']}")
        print(f"\n💡 Проверь что диаграммы отображаются корректно!")

        await confluence.close()
        return page

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        await confluence.close()
        return None


async def main():
    """Запуск всех тестов"""
    print("\n" + "=" * 80)
    print("🚀 ТЕСТИРОВАНИЕ CONFLUENCE INTEGRATION")
    print("=" * 80)

    # Тест 1: Подключение
    connected = await test_connection()

    if not connected:
        print("\n❌ Сначала настрой Confluence credentials в .env!")
        return

    # Тест 2: Простая страница
    await test_create_simple_page()

    # Тест 3: Страница с Mermaid
    await test_page_with_mermaid()

    # Тест 4: Загрузка DOCX
    await test_upload_docx()

    # Тест 5: Полный BRD
    await test_full_brd_publication()

    print("\n" + "=" * 80)
    print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!")
    print("=" * 80)
    print("\n💡 Проверь созданные страницы в Confluence!")


if __name__ == "__main__":
    asyncio.run(main())