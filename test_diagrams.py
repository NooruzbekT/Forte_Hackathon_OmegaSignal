"""
Тестирование генератора диаграмм (исправленная версия)
"""
import asyncio
from diagram_generator import (
    MermaidGenerator,
    ArtifactExtractor,
    DiagramSaver,
    UseCase,
    UserStory,
    KPI
)
from pathlib import Path


def test_process_flow():
    """Тест 1: Process Flow диаграмма"""
    print("\n" + "="*80)
    print("🎨 Тест 1: Process Flow Diagram")
    print("="*80)

    gen = MermaidGenerator()

    # Упрощенная линейная диаграмма (по порядку)
    steps = [
        {"type": "start", "id": "start", "label": "Начало процесса"},
        {"type": "process", "id": "input", "label": "Ввод данных карты", "connection_label": ""},
        {"type": "decision", "id": "validate", "label": "Валидация данных?", "connection_label": ""},
        {"type": "process", "id": "process", "label": "Обработка платежа", "connection_label": "✓ Данные верны"},
        {"type": "subprocess", "id": "bank", "label": "Запрос в банк", "connection_label": ""},
        {"type": "decision", "id": "approved", "label": "Одобрено?", "connection_label": ""},
        {"type": "process", "id": "success", "label": "Успешная оплата", "connection_label": "✓ Да"},
        {"type": "end", "id": "end", "label": "Завершение", "connection_label": ""}
    ]

    mermaid_code = gen.generate_process_flow(
        title="Процесс обработки платежа через банковский API",
        steps=steps,
        style="TD"
    )

    # Сохраняем
    saver = DiagramSaver()
    saver.save_mermaid(mermaid_code, "payment_process_flow")

    print("✅ Process Flow сгенерирован!")
    print(f"📁 Сохранено в: diagrams/payment_process_flow.mmd")
    print(f"\n📋 Предварительный просмотр (первые 15 строк):")
    print("-"*80)
    for line in mermaid_code.split('\n')[:15]:
        print(line)
    print("-"*80)
    print(f"💡 Открой https://mermaid.live и вставь содержимое файла!")

    return mermaid_code


def test_sequence_diagram():
    """Тест 2: Sequence Diagram"""
    print("\n" + "="*80)
    print("🎨 Тест 2: Sequence Diagram")
    print("="*80)

    gen = MermaidGenerator()

    participants = ["User", "Frontend", "API", "LLM", "DocGen"]

    interactions = [
        {"from": "User", "to": "Frontend", "message": "Хочу создать BRD", "type": "arrow"},
        {"from": "Frontend", "to": "API", "message": "POST /api/chat", "type": "arrow"},
        {"from": "API", "to": "LLM", "message": "Classify intent", "type": "arrow"},
        {"from": "LLM", "to": "API", "message": "DocumentType.NEW_FEATURE", "type": "dotted"},
        {"from": "API", "to": "Frontend", "message": "Расскажите о проекте", "type": "dotted"},
        {"from": "Frontend", "to": "User", "message": "Показ ответа", "type": "dotted"},
        {"from": "User", "to": "Frontend", "message": "Система платежей...", "type": "arrow"},
        {"from": "Frontend", "to": "API", "message": "Продолжение диалога", "type": "arrow"},
        {"from": "API", "to": "LLM", "message": "Generate response", "type": "arrow"},
        {"from": "LLM", "to": "API", "message": "Уточняющие вопросы", "type": "dotted"},
        {"from": "API", "to": "DocGen", "message": "Create BRD", "type": "arrow"},
        {"from": "DocGen", "to": "API", "message": "BRD.docx", "type": "dotted"},
        {"from": "API", "to": "Frontend", "message": "Документ готов!", "type": "dotted"},
        {"from": "Frontend", "to": "User", "message": "Скачать документ", "type": "dotted"}
    ]

    mermaid_code = gen.generate_sequence_diagram(
        title="AI Business Analyst - Процесс взаимодействия",
        participants=participants,
        interactions=interactions
    )

    saver = DiagramSaver()
    saver.save_mermaid(mermaid_code, "interaction_sequence")

    print("✅ Sequence Diagram сгенерирована!")
    print(f"📁 Сохранено в: diagrams/interaction_sequence.mmd")
    print(f"\n📋 Предварительный просмотр (первые 15 строк):")
    print("-"*80)
    for line in mermaid_code.split('\n')[:15]:
        print(line)
    print("-"*80)
    print(f"💡 Открой https://mermaid.live и вставь содержимое файла!")

    return mermaid_code


def test_use_case_diagram():
    """Тест 3: Use Case Diagram"""
    print("\n" + "="*80)
    print("🎨 Тест 3: Use Case Diagram")
    print("="*80)

    gen = MermaidGenerator()

    use_cases = [
        UseCase(
            id="UC-001",
            title="Оплата через VISA",
            actor="Пользователь",
            preconditions=["Есть карта VISA", "Система доступна"],
            main_flow=[
                "Ввести данные карты",
                "Подтвердить платеж",
                "Получить результат"
            ],
            alternative_flows=["Отмена операции"],
            postconditions=["Платеж обработан"],
            priority="High"
        ),
        UseCase(
            id="UC-002",
            title="Оплата через MasterCard",
            actor="Пользователь",
            preconditions=["Есть карта MasterCard"],
            main_flow=["Ввести данные", "Оплатить"],
            alternative_flows=[],
            postconditions=["Деньги списаны"],
            priority="High"
        ),
        UseCase(
            id="UC-003",
            title="Возврат платежа",
            actor="Оператор",
            preconditions=["Платеж совершен"],
            main_flow=["Найти транзакцию", "Инициировать возврат"],
            alternative_flows=["Частичный возврат"],
            postconditions=["Деньги возвращены"],
            priority="Medium"
        )
    ]

    mermaid_code = gen.generate_use_case_diagram(use_cases)

    saver = DiagramSaver()
    saver.save_mermaid(mermaid_code, "payment_use_cases")

    print("✅ Use Case Diagram сгенерирована!")
    print(f"📁 Сохранено в: diagrams/payment_use_cases.mmd")
    print(f"\n📋 Предварительный просмотр (первые 15 строк):")
    print("-"*80)
    for line in mermaid_code.split('\n')[:15]:
        print(line)
    print("-"*80)
    print(f"💡 Открой https://mermaid.live и вставь содержимое файла!")

    return mermaid_code


def test_kpi_dashboard():
    """Тест 4: KPI Dashboard"""
    print("\n" + "="*80)
    print("🎨 Тест 4: KPI Dashboard")
    print("="*80)

    gen = MermaidGenerator()

    kpis = [
        KPI(
            name="Transaction Success Rate",
            description="Процент успешных транзакций",
            target="≥ 95%",
            metric="Успешные транзакции / Всего транзакций * 100%",
            category="Performance"
        ),
        KPI(
            name="Average Processing Time",
            description="Среднее время обработки платежа",
            target="< 2 seconds",
            metric="Сумма времени обработки / Количество транзакций",
            category="Performance"
        ),
        KPI(
            name="Revenue Growth",
            description="Рост выручки от платежей",
            target="+ 20%",
            metric="(Текущая выручка - Прошлая выручка) / Прошлая выручка * 100%",
            category="Business"
        ),
        KPI(
            name="Customer Satisfaction",
            description="Удовлетворенность пользователей",
            target="≥ 4.5/5",
            metric="Средняя оценка в опросах",
            category="Usability"
        ),
        KPI(
            name="Fraud Detection Rate",
            description="Процент выявленного мошенничества",
            target="≥ 99%",
            metric="Выявленные случаи / Всего попыток мошенничества * 100%",
            category="Security"
        )
    ]

    mermaid_code = gen.generate_kpi_dashboard(kpis)

    saver = DiagramSaver()
    saver.save_mermaid(mermaid_code, "payment_kpi_dashboard")

    print("✅ KPI Dashboard сгенерирован!")
    print(f"📁 Сохранено в: diagrams/payment_kpi_dashboard.mmd")
    print(f"\n📋 Предварительный просмотр (первые 20 строк):")
    print("-"*80)
    for line in mermaid_code.split('\n')[:20]:
        print(line)
    print("-"*80)
    print(f"💡 Открой https://mermaid.live и вставь содержимое файла!")

    return mermaid_code


def test_artifact_extraction():
    """Тест 5: Извлечение артефактов из BRD"""
    print("\n" + "="*80)
    print("🎨 Тест 5: Artifact Extraction")
    print("="*80)

    # Читаем последний созданный BRD
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("❌ Папка docs не найдена! Пропускаем тест.")
        return None

    docx_files = sorted(docs_dir.glob("*.docx"), key=lambda x: x.stat().st_mtime, reverse=True)

    if not docx_files:
        print("❌ DOCX файлы не найдены! Пропускаем тест.")
        return None

    latest_doc = docx_files[0]
    print(f"📄 Извлекаем артефакты из: {latest_doc.name}")

    # Читаем документ
    try:
        from docx import Document
        doc = Document(latest_doc)
        text = '\n'.join([p.text for p in doc.paragraphs])

        # Извлекаем артефакты
        extractor = ArtifactExtractor()
        artifacts = extractor.extract_all_artifacts(text)

        print(f"\n✅ Извлечено:")
        print(f"   📋 Use Cases: {len(artifacts['use_cases'])}")
        print(f"   📝 User Stories: {len(artifacts['user_stories'])}")
        print(f"   📊 KPIs: {len(artifacts['kpis'])}")

        # Сохраняем в JSON
        saver = DiagramSaver()
        saver.save_json(artifacts, "extracted_artifacts")

        print(f"\n📁 Сохранено в: diagrams/extracted_artifacts.json")

        # Показываем первые результаты
        if artifacts['use_cases']:
            uc = artifacts['use_cases'][0]
            print(f"\n📋 Пример Use Case:")
            print(f"   ID: {uc.id}")
            print(f"   Title: {uc.title}")
            print(f"   Actor: {uc.actor}")

        if artifacts['kpis']:
            kpi = artifacts['kpis'][0]
            print(f"\n📊 Пример KPI:")
            print(f"   Name: {kpi.name}")
            print(f"   Target: {kpi.target}")
            print(f"   Category: {kpi.category}")

        return artifacts

    except Exception as e:
        print(f"❌ Ошибка при чтении документа: {e}")
        return None


def main():
    """Запуск всех тестов"""
    print("\n" + "="*80)
    print("🚀 ТЕСТИРОВАНИЕ DIAGRAM GENERATOR")
    print("="*80)

    # Создаем папку для диаграмм
    Path("diagrams").mkdir(exist_ok=True)

    try:
        # Запускаем тесты
        test_process_flow()
        test_sequence_diagram()
        test_use_case_diagram()
        test_kpi_dashboard()
        test_artifact_extraction()

        print("\n" + "="*80)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("="*80)
        print("\n📁 Результаты сохранены в папке: diagrams/")
        print("\n💡 Как просмотреть диаграммы:")
        print("   1. Открой https://mermaid.live")
        print("   2. Скопируй содержимое .mmd файлов")
        print("   3. Вставь в редактор - увидишь визуализацию!")
        print("\n   Или используй VS Code с расширением 'Mermaid Preview'")

        print("\n📋 Созданные файлы:")
        diagrams_dir = Path("diagrams")
        if diagrams_dir.exists():
            for file in sorted(diagrams_dir.glob("*")):
                size_kb = file.stat().st_size / 1024
                print(f"   ✓ {file.name} ({size_kb:.1f} KB)")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()