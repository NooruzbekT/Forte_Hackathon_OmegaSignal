#!/usr/bin/env python3
"""
Скрипт запуска AI Business Analyst
"""
import sys
import os
import subprocess
import argparse
from pathlib import Path


def check_env_file():
    """Проверка наличия .env файла"""
    if not Path(".env").exists():
        print("⚠️  .env файл не найден!")
        print("Создайте .env файл на основе .env.example:")
        print("  cp .env.example .env")
        print("  nano .env  # и добавьте API ключи")
        return False
    return True


def check_directories():
    """Создание необходимых директорий"""
    dirs = ["docs", "diagrams", "logs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Директория {dir_name}/ готова")


def run_api_server(host="0.0.0.0", port=8000, reload=True):
    """Запуск FastAPI сервера"""
    print(f"\n🚀 Запуск API сервера на http://{host}:{port}")
    print("📚 API документация: http://localhost:8000/docs")
    print("🔄 Auto-reload:", "включен" if reload else "выключен")
    print("\nДля остановки нажмите Ctrl+C\n")

    cmd = [
        "uvicorn",
        "api_server:app",
        "--host", host,
        "--port", str(port),
    ]

    if reload:
        cmd.append("--reload")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 Сервер остановлен")


def run_cli():
    """Запуск CLI версии"""
    print("\n🤖 Запуск CLI ассистента\n")

    try:
        subprocess.run(["python", "main.py"])
    except KeyboardInterrupt:
        print("\n\n👋 CLI остановлен")


def run_tests():
    """Запуск тестов"""
    print("\n🧪 Запуск тестов...\n")

    # Проверка импортов
    try:
        import fastapi
        import httpx
        import pydantic
        print("✅ Все зависимости установлены")
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return

    # Проверка конфигурации
    try:
        from config import settings
        print(f"✅ Конфигурация загружена")
        print(f"   LLM Provider: {settings.LLM_PROVIDER}")
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return

    # Проверка LLM клиента
    try:
        from llm_client import create_llm_client_from_env
        client = create_llm_client_from_env()
        print(f"✅ LLM клиент создан")
        print(f"   Router model: {client.router_model}")
        print(f"   Assistant model: {client.assistant_model}")
    except Exception as e:
        print(f"❌ Ошибка LLM клиента: {e}")
        return

    print("\n✅ Все проверки пройдены!")


def main():
    parser = argparse.ArgumentParser(
        description="AI Business Analyst - Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python start.py api                  # Запустить API сервер
  python start.py api --port 8080      # API на порту 8080
  python start.py api --no-reload      # API без auto-reload
  python start.py cli                  # Запустить CLI версию
  python start.py test                 # Проверить конфигурацию
        """
    )

    parser.add_argument(
        "mode",
        choices=["api", "cli", "test"],
        help="Режим запуска: api, cli, или test"
    )

    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Хост для API сервера (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Порт для API сервера (default: 8000)"
    )

    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Отключить auto-reload для API"
    )

    args = parser.parse_args()

    # Проверки
    if not check_env_file():
        sys.exit(1)

    check_directories()

    # Запуск
    if args.mode == "api":
        run_api_server(
            host=args.host,
            port=args.port,
            reload=not args.no_reload
        )
    elif args.mode == "cli":
        run_cli()
    elif args.mode == "test":
        run_tests()


if __name__ == "__main__":
    main()