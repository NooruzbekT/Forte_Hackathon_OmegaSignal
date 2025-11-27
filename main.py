"""
CLI интерфейс для BA Assistant
Простой диалог через терминал с сохранением документов
"""
import logging
import asyncio
import os
from pathlib import Path
from colorama import init, Fore, Style

from config import settings
from ba_assistant import create_ba_assistant

# Colorama init (для красивого вывода)
init(autoreset=True)

# Logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_header():
    """Красивый заголовок"""
    print("\n" + "="*70)
    print(Fore.CYAN + Style.BRIGHT + "   AI BUSINESS ANALYST ASSISTANT - ForteBank Hackathon 2024")
    print("="*70 + "\n")


def print_ai(message: str):
    """Вывод сообщения от AI"""
    print(Fore.GREEN + "🤖 AI: " + Style.RESET_ALL + message + "\n")


def print_user(message: str):
    """Вывод сообщения пользователя"""
    print(Fore.BLUE + "👤 Вы: " + Style.RESET_ALL + message)


def print_status(doc_type: str, progress: float):
    """Вывод статуса"""
    progress_bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
    print(Fore.YELLOW + f"\n📊 [{progress_bar}] {int(progress*100)}% | Тип: {doc_type}\n")


def print_error(message: str):
    """Вывод ошибки"""
    print(Fore.RED + "❌ Ошибка: " + Style.RESET_ALL + message + "\n")


def print_success(message: str):
    """Вывод успеха"""
    print(Fore.GREEN + Style.BRIGHT + "✅ " + message + "\n")


def print_info(message: str):
    """Вывод информации"""
    print(Fore.CYAN + "ℹ️  " + message + "\n")


def print_help():
    """Вывод помощи"""
    print(Fore.CYAN + "\nДоступные команды:")
    print("  /reset  - начать заново")
    print("  /status - показать прогресс текущей сессии")
    print("  /docs   - список созданных документов")
    print("  /open   - открыть последний документ")
    print("  /help   - эта справка")
    print("  /exit   - выход\n")


def print_documents_list(assistant):
    """Вывод списка документов"""
    docs = assistant.doc_generator.list_documents()
    
    if not docs:
        print(Fore.YELLOW + "📂 Документов пока нет.\n")
        return None
    
    print(Fore.CYAN + Style.BRIGHT + "\n📂 Созданные документы:\n")
    print(Fore.CYAN + "-" * 70)
    
    for i, doc in enumerate(docs[:10], 1):  # Показываем последние 10
        created = doc['created'].strftime('%Y-%m-%d %H:%M:%S')
        size_kb = doc['size'] / 1024
        
        print(f"{Fore.YELLOW}{i}. {Fore.WHITE}{doc['filename']}")
        print(f"   {Fore.CYAN}Создан: {created} | Размер: {size_kb:.1f} KB")
        print(Fore.CYAN + "-" * 70)
    
    print()
    
    return docs[0]['path'] if docs else None  # Возвращаем путь к последнему


def open_document(filepath: str):
    """Открыть документ в системном редакторе"""
    try:
        import platform
        import subprocess
        
        system = platform.system()
        
        if system == 'Windows':
            os.startfile(filepath)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', filepath])
        else:  # Linux
            subprocess.run(['xdg-open', filepath])
        
        print_success(f"Документ открыт: {filepath}")
    except Exception as e:
        print_error(f"Не удалось открыть документ: {e}")
        print_info(f"Путь к файлу: {filepath}")


async def main():
    """Главная функция"""
    
    print_header()
    print(Fore.YELLOW + "Инициализация AI Assistant...")
    
    try:
        assistant = await create_ba_assistant()
        print(Fore.GREEN + "✅ AI готов к работе!\n")
    except Exception as e:
        print_error(f"Не удалось инициализировать: {e}")
        return
    
    print(Fore.CYAN + "Опишите что нужно сделать, я задам несколько вопросов")
    print(Fore.CYAN + "и создам профессиональный документ в папке 'docs/'.\n")
    print_help()
    
    session_id = "cli_session"
    last_doc_path = None  # Путь к последнему созданному документу
    
    # Главный цикл
    while True:
        try:
            # Получаем ввод от пользователя
            user_input = input(Fore.BLUE + "👤 Вы: " + Style.RESET_ALL).strip()
            
            if not user_input:
                continue
            
            # Команды
            if user_input.lower() == "/exit":
                print(Fore.YELLOW + "\n👋 До свидания!")
                break
            
            elif user_input.lower() == "/help":
                print_help()
                continue
            
            elif user_input.lower() == "/reset":
                assistant.reset_session(session_id)
                last_doc_path = None
                print(Fore.GREEN + "🔄 Сессия сброшена. Начнем заново!\n")
                continue
            
            elif user_input.lower() == "/status":
                info = assistant.get_session_info(session_id)
                if info["status"] == "no_session":
                    print(Fore.YELLOW + "❌ Нет активной сессии. Начните диалог.\n")
                else:
                    print_status(info.get("doc_type", "unknown"), info["progress"])
                    print(f"   Сообщений: {info['messages_count']}")
                    if last_doc_path:
                        print(f"   Последний документ: {Fore.GREEN}{last_doc_path}\n")
                    else:
                        print()
                continue
            
            elif user_input.lower() == "/docs":
                latest = print_documents_list(assistant)
                if latest:
                    print(Fore.CYAN + f"Используйте /open чтобы открыть последний документ\n")
                continue
            
            elif user_input.lower() == "/open":
                if last_doc_path and Path(last_doc_path).exists():
                    open_document(last_doc_path)
                else:
                    # Пробуем открыть последний из списка
                    docs = assistant.doc_generator.list_documents()
                    if docs:
                        open_document(docs[0]['path'])
                    else:
                        print(Fore.YELLOW + "📂 Нет документов для открытия.\n")
                continue
            
            # Обычное сообщение - отправляем AI
            print(Fore.YELLOW + "\n⏳ AI думает...\n")
            
            response = await assistant.process_message(
                user_message=user_input,
                session_id=session_id
            )
            
            print_ai(response)
            
            # Показываем прогресс
            info = assistant.get_session_info(session_id)
            if info["status"] == "active":
                print_status(info.get("doc_type", "unknown"), info["progress"])
                
                # Если документ готов
                if info["progress"] >= 1.0:
                    print_success("Документ готов и сохранен!")
                    
                    # Пробуем найти путь к документу в ответе
                    import re
                    match = re.search(r'`([^`]+\.docx)`', response)
                    if match:
                        last_doc_path = match.group(1)
                        print(Fore.CYAN + f"📄 Файл: {Fore.WHITE}{last_doc_path}")
                    
                    print(Fore.CYAN + "📂 Папка: " + Fore.WHITE + "docs/")
                    print()
                    print(Fore.YELLOW + "Команды:")
                    print(Fore.CYAN + "  /open  - открыть документ")
                    print(Fore.CYAN + "  /docs  - показать все документы")
                    print(Fore.CYAN + "  /reset - создать новый документ")
                    print()
        
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\n👋 Прервано пользователем. До свидания!")
            break
        
        except Exception as e:
            print_error(f"Произошла ошибка: {e}")
            logger.exception("Error in main loop")
    
    # Cleanup
    try:
        await assistant.llm.close()
    except:
        pass


if __name__ == "__main__":
    asyncio.run(main())