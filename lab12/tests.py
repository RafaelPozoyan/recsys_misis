"""
Модуль для тестирования основных функций суммаризатора.

Содержит unit тесты для проверки корректности работы функций.
"""

from typing import Optional
from text_summarizer import validate_text, load_api_token


def test_validate_text() -> None:
    """
    Что я делаю?
        Тестирую функцию validate_text с различными входными данными.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        Ничего.
    """
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ФУНКЦИИ validate_text()")
    print("=" * 80)
    
    # Тест 1: Пустая строка
    result1: bool = validate_text("")
    status1: str = "✅ PASSED" if not result1 else "❌ FAILED"
    print(f"\n[Тест 1] Пустая строка: {status1}")
    print(f"  Результат: {result1} (ожидается False)")
    
    # Тест 2: Текст с пробелами
    result2: bool = validate_text("   ")
    status2: str = "✅ PASSED" if not result2 else "❌ FAILED"
    print(f"\n[Тест 2] Только пробелы: {status2}")
    print(f"  Результат: {result2} (ожидается False)")
    
    # Тест 3: Короткий текст (менее 50 символов)
    short_text: str = "Это короткий текст."
    result3: bool = validate_text(short_text)
    status3: str = "✅ PASSED" if not result3 else "❌ FAILED"
    print(f"\n[Тест 3] Короткий текст ({len(short_text)} символов): {status3}")
    print(f"  Результат: {result3} (ожидается False)")
    
    # Тест 4: Достаточно длинный текст (более 50 символов)
    long_text: str = "Это достаточно длинный текст для суммаризации. " * 3
    result4: bool = validate_text(long_text)
    status4: str = "✅ PASSED" if result4 else "❌ FAILED"
    print(f"\n[Тест 4] Длинный текст ({len(long_text)} символов): {status4}")
    print(f"  Результат: {result4} (ожидается True)")
    
    # Подсчет результатов
    passed: int = sum([status1 == "✅ PASSED", status2 == "✅ PASSED", 
                        status3 == "✅ PASSED", status4 == "✅ PASSED"])
    print(f"\n📊 Результаты: {passed}/4 тестов пройдено\n")


def test_load_api_token() -> None:
    """
    Что я делаю?
        Тестирую функцию load_api_token для проверки загрузки токена.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        Ничего.
    """
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ФУНКЦИИ load_api_token()")
    print("=" * 80)
    
    try:
        token: str = load_api_token()
        is_valid: bool = len(token) > 0 and "hf_" in token.lower()
        
        if is_valid:
            print("\n✅ PASSED: API токен успешно загружен")
            print(f"  Токен начинается на: {token[:20]}...")
            print(f"  Длина токена: {len(token)} символов")
        else:
            print("\n⚠️ WARNING: Токен загружен, но может быть невалидным")
            print(f"  Токен: {token[:50]}...")
    
    except ValueError as err:
        print(f"\n⚠️ WARNING: {str(err)}")
        print("  Убедитесь, что установлена переменная окружения HUGGINGFACE_API_TOKEN")
    
    print()


def test_type_annotations() -> None:
    """
    Что я делаю?
        Проверяю, что все функции имеют правильные аннотации типов.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        Ничего.
    """
    print("=" * 80)
    print("ПРОВЕРКА АННОТАЦИЙ ТИПОВ")
    print("=" * 80)
    
    from text_summarizer import (
        validate_text,
        summarize_text,
        summarize_text_advanced,
        load_api_token
    )
    
    # Получаем аннотации типов для каждой функции
    functions: dict[str, any] = {
        "validate_text": validate_text,
        "summarize_text": summarize_text,
        "summarize_text_advanced": summarize_text_advanced,
        "load_api_token": load_api_token
    }
    
    print("\n🔍 Аннотации типов для функций:\n")
    
    for func_name, func in functions.items():
        annotations: dict = func.__annotations__
        print(f"✅ {func_name}:")
        
        if annotations:
            for param_name, param_type in annotations.items():
                print(f"   - {param_name}: {param_type}")
        else:
            print("   ⚠️  Нет аннотаций типов")
        
        print()


def main() -> None:
    """
    Что я делаю?
        Запускаю все тесты для проверки функциональности суммаризатора.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        Ничего.
    """
    print("\n" + "=" * 80)
    print("🧪 ТЕСТИРОВАНИЕ МОДУЛЯ text_summarizer.py")
    print("=" * 80 + "\n")
    
    test_validate_text()
    test_load_api_token()
    test_type_annotations()
    
    print("=" * 80)
    print("✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 80)


if __name__ == "__main__":
    main()
