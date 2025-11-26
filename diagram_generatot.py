"""
Генератор диаграмм и аналитических артефактов
Use Cases, Process Flow, User Stories, KPI
"""
import re
import json
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UseCase:
    """Use Case структура"""
    id: str
    title: str
    actor: str
    preconditions: List[str]
    main_flow: List[str]
    alternative_flows: List[str]
    postconditions: List[str]
    priority: str = "Medium"


@dataclass
class UserStory:
    """User Story"""
    id: str
    title: str
    as_a: str
    i_want: str
    so_that: str
    acceptance_criteria: List[str]
    priority: str = "Medium"
    story_points: Optional[int] = None


@dataclass
class KPI:
    """Key Performance Indicator"""
    name: str
    description: str
    target: str
    metric: str
    category: str  # Performance, Business, Usability


# ============================================================================
# MERMAID DIAGRAM GENERATOR
# ============================================================================

class MermaidGenerator:
    """Генератор Mermaid диаграмм"""

    @staticmethod
    def generate_process_flow(
        title: str,
        steps: List[Dict[str, str]],
        style: str = "LR"
    ) -> str:
        """
        Генерирует Flowchart процесса.

        Args:
            title: Название процесса
            steps: Список шагов [{"id": "A", "label": "Start", "type": "start"}, ...]
            style: Направление (LR, TD)

        Returns:
            Mermaid код
        """
        lines = [
            f"flowchart {style}",
            f"    %% {title}",
            ""
        ]

        # Добавляем узлы
        for step in steps:
            node_id = step["id"]
            label = step["label"]
            node_type = step.get("type", "process")

            # Разные типы узлов
            if node_type == "start":
                lines.append(f"    {node_id}([{label}])")
            elif node_type == "end":
                lines.append(f"    {node_id}([{label}])")
            elif node_type == "decision":
                lines.append(f"    {node_id}{{{label}}}")
            elif node_type == "subprocess":
                lines.append(f"    {node_id}[/{label}/]")
            else:
                lines.append(f"    {node_id}[{label}]")

        lines.append("")

        # Добавляем связи
        for i, step in enumerate(steps[:-1]):
            current = step["id"]
            next_step = steps[i + 1]["id"]
            label = step.get("connection_label", "")

            if label:
                lines.append(f"    {current} -->|{label}| {next_step}")
            else:
                lines.append(f"    {current} --> {next_step}")

        # Стили
        lines.extend([
            "",
            "    %% Styles",
            "    classDef startEnd fill:#90EE90,stroke:#333,stroke-width:2px",
            "    classDef process fill:#87CEEB,stroke:#333,stroke-width:2px",
            "    classDef decision fill:#FFD700,stroke:#333,stroke-width:2px",
            "    ",
            "    class A,Z startEnd",
            "    class B,C,D,E,F process"
        ])

        return "\n".join(lines)

    @staticmethod
    def generate_sequence_diagram(
        title: str,
        participants: List[str],
        interactions: List[Dict[str, str]]
    ) -> str:
        """
        Генерирует Sequence diagram.

        Args:
            title: Название
            participants: Список участников ["User", "Frontend", "Backend", "Database"]
            interactions: [{"from": "User", "to": "Frontend", "message": "Login request"}, ...]

        Returns:
            Mermaid код
        """
        lines = [
            "sequenceDiagram",
            f"    %% {title}",
            ""
        ]

        # Участники
        for p in participants:
            lines.append(f"    participant {p}")

        lines.append("")

        # Взаимодействия
        for interaction in interactions:
            from_actor = interaction["from"]
            to_actor = interaction["to"]
            message = interaction["message"]
            interaction_type = interaction.get("type", "arrow")

            if interaction_type == "arrow":
                lines.append(f"    {from_actor}->>+{to_actor}: {message}")
            elif interaction_type == "dotted":
                lines.append(f"    {from_actor}-->>-{to_actor}: {message}")
            elif interaction_type == "note":
                lines.append(f"    Note over {from_actor},{to_actor}: {message}")

        return "\n".join(lines)

    @staticmethod
    def generate_use_case_diagram(use_cases: List[UseCase]) -> str:
        """Генерирует Use Case диаграмму (упрощенная версия через flowchart)"""
        lines = [
            "graph TB",
            "    %% Use Case Diagram",
            ""
        ]

        # Актеры
        actors = list(set([uc.actor for uc in use_cases]))
        for actor in actors:
            actor_id = actor.replace(" ", "_")
            lines.append(f"    {actor_id}[/{actor}/]")

        lines.append("")

        # Use cases
        for uc in use_cases:
            uc_id = uc.id.replace("-", "_")
            lines.append(f"    {uc_id}({uc.title})")

        lines.append("")

        # Связи
        for uc in use_cases:
            actor_id = uc.actor.replace(" ", "_")
            uc_id = uc.id.replace("-", "_")
            lines.append(f"    {actor_id} --> {uc_id}")

        # Стили
        lines.extend([
            "",
            "    classDef actor fill:#FFE4B5,stroke:#333,stroke-width:2px",
            "    classDef usecase fill:#87CEEB,stroke:#333,stroke-width:2px",
            "",
            "    class " + ",".join([a.replace(" ", "_") for a in actors]) + " actor"
        ])

        return "\n".join(lines)

    @staticmethod
    def generate_kpi_dashboard(kpis: List[KPI]) -> str:
        """Генерирует KPI dashboard (через flowchart)"""
        lines = [
            "graph TD",
            "    %% KPI Dashboard",
            "",
            "    KPI[KPI Dashboard]",
            ""
        ]

        # Группируем по категориям
        categories = {}
        for kpi in kpis:
            if kpi.category not in categories:
                categories[kpi.category] = []
            categories[kpi.category].append(kpi)

        # Создаем subgraphs
        for category, category_kpis in categories.items():
            cat_id = category.replace(" ", "_")
            lines.append(f"    subgraph {cat_id}[{category}]")

            for i, kpi in enumerate(category_kpis):
                kpi_id = f"{cat_id}_{i}"
                kpi_text = f"{kpi.name}<br/>Target: {kpi.target}"
                lines.append(f"        {kpi_id}[{kpi_text}]")

            lines.append("    end")
            lines.append("")
            lines.append(f"    KPI --> {cat_id}")
            lines.append("")

        return "\n".join(lines)


# ============================================================================
# ARTIFACT EXTRACTOR
# ============================================================================

class ArtifactExtractor:
    """Извлечение артефактов из BRD документа"""

    @staticmethod
    def extract_use_cases(document: str) -> List[UseCase]:
        """Извлекает Use Cases из документа"""
        use_cases = []

        # Паттерн для поиска Use Case секций
        pattern = r"### UC-(\d+):\s*(.+?)\n\*\*Actor:\*\*\s*(.+?)\n\n\*\*Preconditions:\*\*\n(.*?)\n\n\*\*Main Flow:\*\*\n(.*?)(?=\n\n\*\*Alternative Flows:|$)"

        matches = re.finditer(pattern, document, re.DOTALL)

        for match in matches:
            uc_num = match.group(1)
            title = match.group(2).strip()
            actor = match.group(3).strip()
            preconditions_text = match.group(4).strip()
            main_flow_text = match.group(5).strip()

            # Парсим предусловия
            preconditions = [
                line.strip("- ").strip()
                for line in preconditions_text.split("\n")
                if line.strip().startswith("-")
            ]

            # Парсим основной флоу
            main_flow = [
                re.sub(r'^\d+\.\s*', '', line.strip())
                for line in main_flow_text.split("\n")
                if re.match(r'^\d+\.', line.strip())
            ]

            use_cases.append(UseCase(
                id=f"UC-{uc_num}",
                title=title,
                actor=actor,
                preconditions=preconditions,
                main_flow=main_flow,
                alternative_flows=[],
                postconditions=[],
                priority="High"
            ))

        return use_cases

    @staticmethod
    def extract_user_stories(document: str) -> List[UserStory]:
        """Извлекает User Stories из документа"""
        user_stories = []

        # Паттерн для User Story: "As a [role], I want [feature] so that [benefit]"
        pattern = r"As a (.+?), I want (.+?) so that (.+?)(?:\.|$)"

        matches = re.finditer(pattern, document, re.IGNORECASE)

        for i, match in enumerate(matches, 1):
            as_a = match.group(1).strip()
            i_want = match.group(2).strip()
            so_that = match.group(3).strip()

            user_stories.append(UserStory(
                id=f"US-{i:03d}",
                title=f"{as_a} wants {i_want[:30]}...",
                as_a=as_a,
                i_want=i_want,
                so_that=so_that,
                acceptance_criteria=[],
                priority="Medium"
            ))

        return user_stories

    @staticmethod
    def extract_kpis(document: str) -> List[KPI]:
        """Извлекает KPI из документа"""
        kpis = []

        # Ищем секцию Success Criteria / KPI
        kpi_pattern = r"\*\*KPI \d+:\*\*\s*(.+)"

        matches = re.finditer(kpi_pattern, document)

        for i, match in enumerate(matches, 1):
            kpi_text = match.group(1).strip()

            kpis.append(KPI(
                name=f"KPI-{i}",
                description=kpi_text,
                target="TBD",
                metric=kpi_text,
                category="Business"
            ))

        return kpis

    @staticmethod
    def extract_all_artifacts(document: str) -> Dict:
        """Извлекает все артефакты из документа"""
        return {
            "use_cases": ArtifactExtractor.extract_use_cases(document),
            "user_stories": ArtifactExtractor.extract_user_stories(document),
            "kpis": ArtifactExtractor.extract_kpis(document)
        }


# ============================================================================
# DIAGRAM SAVER
# ============================================================================

class DiagramSaver:
    """Сохранение диаграмм в файлы"""

    def __init__(self, output_dir: str = "diagrams"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def save_mermaid(self, content: str, filename: str) -> str:
        """Сохраняет Mermaid диаграмму"""
        filepath = self.output_dir / f"{filename}.mmd"
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Mermaid diagram saved: {filepath}")
        return str(filepath)

    def save_json(self, data: dict, filename: str) -> str:
        """Сохраняет JSON данные"""
        filepath = self.output_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"JSON saved: {filepath}")
        return str(filepath)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Пример генерации процесса
    mermaid = MermaidGenerator()

    process_steps = [
        {"id": "A", "label": "Start", "type": "start"},
        {"id": "B", "label": "User Login", "type": "process"},
        {"id": "C", "label": "Valid?", "type": "decision"},
        {"id": "D", "label": "Dashboard", "type": "process"},
        {"id": "E", "label": "Error", "type": "process"},
        {"id": "Z", "label": "End", "type": "end"}
    ]

    flowchart = mermaid.generate_process_flow(
        title="User Login Process",
        steps=process_steps,
        style="TD"
    )

    print(flowchart)

    # Пример генерации Use Case
    use_cases = [
        UseCase(
            id="UC-001",
            title="Login to System",
            actor="User",
            preconditions=["User has account"],
            main_flow=["Enter credentials", "Click login", "Access dashboard"],
            alternative_flows=[],
            postconditions=["User is logged in"],
            priority="Critical"
        )
    ]

    use_case_diagram = mermaid.generate_use_case_diagram(use_cases)
    print("\n" + use_case_diagram)