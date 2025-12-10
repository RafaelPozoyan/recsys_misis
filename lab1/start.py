"""
Стартовый скрипт для быстрого запуска приложения.

Проверяет наличие зависимостей и запускает GUI приложение.
"""

import sys
import subprocess
from typing import List, Optional
from pathlib import Path


def check_python_version() -> bool:
    """
    Что я делаю?
        Проверяю версию Python.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        bool: True если версия >= 3.9, False иначе.
    """
    if sys.version_info >= (3, 9):
        print(f"✅ Python версия: {sys.version.split()[0]} - OK")
        return True
    else:
        print(f"❌ Python версия: {sys.version.split()[0]}")
        print("   Требуется Python 3.9 или выше")
        return False


def check_env_file() -> bool:
    """
    Что я делаю?
        Проверяю наличие файла .env.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        bool: True если файл существует, False иначе.
    """
    env_path: Path = Path(".env")
    
    if env_path.exists():
        print("✅ Файл .env найден")
        return True
    else:
        print("❌ Файл .env не найден!")
        print("   Инструкции:")
        print("   1. Скопируйте .env.example в .env")
        print("   2. Откройте .env")
        print("   3. Вставьте ваш API токен вместо your_hf_token_here")
        print("   4. Сохраните файл")
        return False


def check_requirements() -> bool:
    """
    Что я делаю?
        Проверяю установленные зависимости.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        bool: True если все зависимости установлены, False иначе.
    """
    required_packages: List[str] = ["requests", "dotenv", "PyQt6"]
    missing_packages: List[str] = []
    
    for package in required_packages:
        try:
            __import__(package.lower())
            print(f"✅ {package} установлен")
        except ImportError:
            print(f"❌ {package} не установлен")
            missing_packages.append(package)
    
    if missing_packages:
        print("\n❌ Отсутствуют зависимости!")
        print("   Установите их:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def check_required_files() -> bool:
    """
    Что я делаю?
        Проверяю наличие всех необходимых файлов проекта.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        bool: True если все файлы найдены, False иначе.
    """
    required_files: List[str] = [
        "text_summarizer.py",
        "gui_app.py",
        "examples.py",
        "requirements.txt",
        "README.md"
    ]
    
    missing_files: List[str] = []
    
    for file in required_files:
        file_path: Path = Path(file)
        if file_path.exists():
            print(f"✅ {file} найден")
        else:
            print(f"❌ {file} не найден")
            missing_files.append(file)
    
    return len(missing_files) == 0


def main() -> None:
    """
    Что я делаю?
        Проверяю систему и запускаю приложение.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        Ничего.
    """
    print("=" * 80)
    print("🚀 СТАРТЕР ПРИЛОЖЕНИЯ СУММАРИЗАТОРА ТЕКСТА")
    print("=" * 80)
    
    print("\n🔍 ПРОВЕРКА СИСТЕМЫ:\n")
    
    # Проверки
    checks: List[tuple[str, callable]] = [
        ("Python версия", check_python_version),
        ("Файлы проекта", check_required_files),
        ("Зависимости", check_requirements),
        ("Конфигурация", check_env_file)
    ]
    
    all_passed: bool = True
    
    for check_name, check_func in checks:
        try:
            result: bool = check_func()
            if not result:
                all_passed = False
        except Exception as err:
            print(f"❌ Ошибка при проверке {check_name}: {str(err)}")
            all_passed = False
        
        print()
    
    # Результат
    print("=" * 80)
    
    if all_passed:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("\n🚀 Запуск приложения...\n")
        
        try:
            # Импортируем и запускаем приложение
            from gui_app import main as run_gui
            run_gui()
        except Exception as err:
            print(f"❌ Ошибка при запуске приложения: {str(err)}")
            print("\nПопробуйте запустить вручную:")
            print("   python gui_app.py")
    else:
        print("❌ ПРОВЕРКИ НЕ ПРОЙДЕНЫ!")
        print("\nПожалуйста, исправьте ошибки и попробуйте снова.")
        print("\nДля помощи прочитайте:")
        print("   - README.md (основная документация)")
        print("   - INSTALLATION.md (инструкции установки)")
        print("   - CHEATSHEET.md (краткая шпаргалка)")
    
    print("=" * 80)


if __name__ == "__main__":
    main()
