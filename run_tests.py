"""
Скрипт для запуска тестов Robot Manipulator
"""

import unittest
import sys
import os

def run_all_tests():
    """Запуск всех тестов"""
    # Добавляем текущую директорию в путь
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Загружаем тесты
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')
    
    # Запускаем с подробным выводом
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Вывод статистики
    print("\n" + "="*50)
    print(f"Результаты тестирования:")
    print(f"  Выполнено: {result.testsRun}")
    print(f"  Ошибок: {len(result.errors)}")
    print(f"  Провалено: {len(result.failures)}")
    print("="*50)
    
    return result.wasSuccessful()

def run_quick_tests():
    """Запуск только быстрых основных тестов"""
    import test_manipulator
    
    # Запускаем только основные тесты (без расширенных расчётов)
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromName("test_manipulator.TestMockManipulator"))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Запуск тестов Robot Manipulator')
    parser.add_argument('--quick', action='store_true', 
                        help='Запуск только быстрых тестов')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Подробный вывод')
    
    args = parser.parse_args()
    
    if args.quick:
        success = run_quick_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
