"""
Confluence API Integration
Создание страниц, загрузка документов, вставка Mermaid диаграмм
"""
import logging
import mimetypes
import re
from typing import Optional, Dict, List
import httpx
from pathlib import Path
logger = logging.getLogger(__name__)
import base64



class ConfluenceClient:
    """
    Клиент для работы с Confluence REST API.

    Документация:
    https://developer.atlassian.com/cloud/confluence/rest/v1/intro/
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        api_token: str,
        space_key: str = "AI"
    ):
        """
        Args:
            base_url: URL Confluence (например: https://your-domain.atlassian.net)
            username: Email пользователя
            api_token: API token (https://id.atlassian.com/manage-profile/security/api-tokens)
            space_key: Ключ пространства по умолчанию
        """
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wiki/rest/api"
        self.space_key = space_key
        self.username = username
        self.api_token = api_token

        # Basic Auth
        auth_string = f"{username}:{api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

        self.headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=self.headers
        )

        logger.info(f"Confluence client initialized: {self.base_url}")

    def _auth(self):
        return base64.b64encode(f"{self.username}:{self.api_token}".encode()).decode()

    async def test_connection(self) -> bool:
        """Проверка подключения к Confluence"""
        try:
            response = await self.client.get(f"{self.api_url}/space/{self.space_key}")
            response.raise_for_status()
            logger.info(f"✅ Confluence connection OK: {self.space_key}")
            return True
        except Exception as e:
            logger.error(f"❌ Confluence connection failed: {e}")
            return False

    async def create_page(
        self,
        title: str,
        content: str,
        parent_id: Optional[str] = None,
        space_key: Optional[str] = None
    ) -> Dict:
        """
        Создать новую страницу в Confluence.

        Args:
            title: Заголовок страницы
            content: Контент в Confluence Storage Format (HTML-подобный)
            parent_id: ID родительской страницы (опционально)
            space_key: Ключ пространства (если не указан, используется дефолтный)

        Returns:
            Данные созданной страницы
        """
        space = space_key or self.space_key

        payload = {
            "type": "page",
            "title": title,
            "space": {"key": space},
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            }
        }

        if parent_id:
            payload["ancestors"] = [{"id": parent_id}]

        try:
            response = await self.client.post(
                f"{self.api_url}/content",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            page_id = data['id']
            page_url = f"{self.base_url}/wiki{data['_links']['webui']}"

            logger.info(f"✅ Page created: {title} ({page_id})")
            logger.info(f"   URL: {page_url}")

            return {
                "id": page_id,
                "title": title,
                "url": page_url,
                "data": data
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to create page: {e.response.text}")
            raise

    async def update_page(
        self,
        page_id: str,
        title: str,
        content: str,
        version: int
    ) -> Dict:
        """
        Обновить существующую страницу.

        Args:
            page_id: ID страницы
            title: Новый заголовок
            content: Новый контент
            version: Текущая версия страницы + 1

        Returns:
            Данные обновленной страницы
        """
        payload = {
            "type": "page",
            "title": title,
            "body": {
                "storage": {
                    "value": content,
                    "representation": "storage"
                }
            },
            "version": {"number": version}
        }

        try:
            response = await self.client.put(
                f"{self.api_url}/content/{page_id}",
                json=payload
            )
            response.raise_for_status()
            data = response.json()

            logger.info(f"✅ Page updated: {title} (v{version})")

            return {
                "id": page_id,
                "title": title,
                "version": version,
                "data": data
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to update page: {e.response.text}")
            raise

    async def get_page(self, page_id: str) -> Dict:
        """Получить информацию о странице"""
        try:
            response = await self.client.get(
                f"{self.api_url}/content/{page_id}",
                params={"expand": "body.storage,version"}
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Failed to get page: {e.response.text}")
            raise

    async def attach_file(self, page_id: str, filepath: str):
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(filepath)

        import mimetypes
        mime, _ = mimetypes.guess_type(file_path.name)
        mime = mime or "application/octet-stream"  # fallback

        # ❗ Удаляем content-type — httpx сам поставит multipart
        headers = {
            "Authorization": self.headers["Authorization"],
            "Accept": "application/json"
        }

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, mime)}

            r = await self.client.post(
                f"{self.base_url}/wiki/rest/api/content/{page_id}/child/attachment",
                headers=headers,
                files=files
            )

        print("ATTACH STATUS:", r.status_code)
        print("RESP:", r.text)

        if r.status_code in (200, 201):
            print("🔥 SUCCESS — FILE ATTACHED!")
            return r.json()
        else:
            raise Exception("❌ FAIL — FILE NOT ATTACHED")

    async def search_pages(
        self,
        query: str,
        space_key: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Поиск страниц в Confluence.

        Args:
            query: Поисковый запрос
            space_key: Ключ пространства (опционально)
            limit: Лимит результатов

        Returns:
            Список найденных страниц
        """
        space = space_key or self.space_key

        cql = f'type=page AND space="{space}" AND title~"{query}"'

        try:
            response = await self.client.get(
                f"{self.api_url}/content/search",
                params={
                    "cql": cql,
                    "limit": limit,
                    "expand": "version"
                }
            )
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            logger.info(f"Found {len(results)} pages for query: {query}")

            return results

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Search failed: {e.response.text}")
            raise

    async def close(self):
        """Закрыть HTTP клиент"""
        await self.client.aclose()


# ============================================================================
# MERMAID MACRO HELPER
# ============================================================================

class ConfluenceMermaidHelper:
    """Helper для вставки Mermaid диаграмм в Confluence через макрос"""

    @staticmethod
    def wrap_mermaid_macro(mermaid_code: str) -> str:
        """
        Оборачивает Mermaid код в Confluence макрос (правильный для mermaidjs!)
        """
        return f'''
    <ac:structured-macro ac:name="mermaidjs" ac:schema-version="1" data-layout="default" ac:macro-id="auto">
      <ac:parameter ac:name="theme">default</ac:parameter>
      <ac:parameter ac:name="version">2</ac:parameter>
      <ac:plain-text-body><![CDATA[{mermaid_code}]]></ac:plain-text-body>
    </ac:structured-macro>
    '''

    @staticmethod
    def create_brd_page_with_diagrams(
        title: str,
        brd_content: str,
        mermaid_diagrams: Dict[str, str]
    ) -> str:
        """
        Создает полный HTML контент для BRD страницы с диаграммами.

        Args:
            title: Заголовок страницы
            brd_content: BRD контент (может быть Markdown - конвертируем в HTML)
            mermaid_diagrams: {"process_flow": "graph TD...", "use_case": "graph TB..."}

        Returns:
            Confluence Storage Format HTML
        """
        # Конвертируем Markdown в HTML (упрощенно)
        html_content = ConfluenceMermaidHelper._markdown_to_html(brd_content)

        # Добавляем диаграммы
        diagrams_html = ""
        for diagram_name, diagram_code in mermaid_diagrams.items():
            diagrams_html += f"<h2>{diagram_name.replace('_', ' ').title()}</h2>"
            diagrams_html += ConfluenceMermaidHelper.wrap_mermaid_macro(diagram_code)
            diagrams_html += "<br/>"

        # Собираем все вместе
        full_html = f"""
<h1>{title}</h1>
<hr/>
{html_content}
<hr/>
<h1>Диаграммы</h1>
{diagrams_html}
"""

        return full_html

    @staticmethod
    def _markdown_to_html(markdown: str) -> str:
        """Простейшая конвертация Markdown в HTML"""
        html = markdown

        # Заголовки
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Жирный текст
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # Списки
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # Параграфы
        lines = html.split('\n')
        paragraphs = []
        in_list = False

        for line in lines:
            if line.strip().startswith('<li>'):
                if not in_list:
                    paragraphs.append('<ul>')
                    in_list = True
                paragraphs.append(line)
            else:
                if in_list:
                    paragraphs.append('</ul>')
                    in_list = False
                if line.strip() and not line.strip().startswith('<'):
                    paragraphs.append(f'<p>{line}</p>')
                else:
                    paragraphs.append(line)

        if in_list:
            paragraphs.append('</ul>')

        return '\n'.join(paragraphs)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_usage():
    """Пример использования"""
    import os

    # Настройки (из environment variables)
    confluence = ConfluenceClient(
        base_url=os.getenv("CONFLUENCE_URL", "https://your-domain.atlassian.net"),
        username=os.getenv("CONFLUENCE_USERNAME", "your@email.com"),
        api_token=os.getenv("CONFLUENCE_API_TOKEN", "your-api-token"),
        space_key="AI"
    )

    # Тест подключения
    connected = await confluence.test_connection()

    if connected:
        # Создаем страницу
        page = await confluence.create_page(
            title="AI Business Analyst - Test Page",
            content="<h1>Test Page</h1><p>Created by AI Assistant</p>"
        )

        print(f"Page created: {page['url']}")

    await confluence.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())