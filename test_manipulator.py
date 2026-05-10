# test_manipulator.py
"""
Упрощённые тесты для Robot Manipulator - Python interface
"""

import unittest
import sys
import os
import math

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manipulator_bridge import (
    MockManipulatorBridge,
    ManipulatorException,
    create_manipulator
)


class TestMockManipulator(unittest.TestCase):
    """Тесты для mock-версии манипулятора (без DLL)"""
    
    def setUp(self):
        """Создаём манипулятор перед каждым тестом"""
        self.manip = MockManipulatorBridge()
    
    def tearDown(self):
        """Закрываем манипулятор после каждого теста"""
        self.manip.close()
    
    def test_add_links_sequential(self):
        """Тест: добавление звеньев по порядку"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        self.manip.add_link(2, 1.0, 0.0, 0.0, 0.0)
        self.manip.add_link(3, 1.0, 0.0, 0.0, 0.0)
        
        # Проверяем, что все три звена добавлены
        self.assertEqual(len(self.manip.links), 3)
        self.assertIn(1, self.manip.links)
        self.assertIn(2, self.manip.links)
        self.assertIn(3, self.manip.links)
    
    def test_add_links_wrong_order(self):
        """Тест: добавление звеньев в неправильном порядке вызывает исключение"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        
        with self.assertRaises(ManipulatorException):
            self.manip.add_link(3, 1.0, 0.0, 0.0, 0.0)  # Пропущен ID=2
    
    def test_add_link_invalid_id(self):
        """Тест: ID меньше 1 запрещён"""
        with self.assertRaises(ValueError):
            self.manip.add_link(0, 1.0, 0.0, 0.0, 0.0)
    
    def test_add_different_types(self):
        """Тест: добавление звеньев разных типов"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        self.manip.add_gripper(2, 0.5, 0.0, 0.0, 0.0, 0.5)
        self.manip.add_camera(3, 0.3, 0.0, 0.0, 0.0, 1.2)
        
        self.assertEqual(self.manip.links[1]['type'], 'MovableLink')
        self.assertEqual(self.manip.links[2]['type'], 'Gripper')
        self.assertEqual(self.manip.links[3]['type'], 'Camera')
    
    def test_set_orientation(self):
        """Тест: установка ориентации звена"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        
        self.manip.set_orientation(1, 0.5, 0.3, 0.1)
        
        self.assertEqual(self.manip.links[1]['pitch'], 0.5)
        self.assertEqual(self.manip.links[1]['yaw'], 0.3)
        self.assertEqual(self.manip.links[1]['roll'], 0.1)
    
    def test_set_orientation_nonexistent(self):
        """Тест: ошибка при установке ориентации несуществующего звена"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        
        with self.assertRaises(RuntimeError):
            self.manip.set_orientation(99, 0.5, 0.3, 0.1)
    
    def test_gripper_operations(self):
        """Тест: операции с захватом"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        self.manip.add_gripper(2, 0.5, 0.0, 0.0, 0.0, 0.0)
        
        # Открываем захват
        self.manip.open_gripper(2, 0.8)
        self.assertEqual(self.manip.links[2]['opening_angle'], 0.8)
        
        # Закрываем захват
        self.manip.close_gripper(2)
        self.assertEqual(self.manip.links[2]['opening_angle'], 0)
    
    def test_camera_photo(self):
        """Тест: снимок камерой"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        self.manip.add_camera(2, 0.5, 0.0, 0.0, 0.0, 1.57)
        
        # Просто проверяем, что не падает
        result = self.manip.take_photo(2)
        self.assertTrue(result)
    
    def test_calculate_position_single_link_vertical(self):
        """Тест: расчёт позиции одного вертикального звена"""
        self.manip.add_link(1, 2.0, 0.0, 0.0, 0.0)
        
        x, y, z = self.manip.calculate_position(1)
        
        self.assertAlmostEqual(x, 0.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        self.assertAlmostEqual(z, 2.0, places=6)
    
    def test_calculate_position_single_link_horizontal(self):
        """Тест: расчёт позиции одного горизонтального звена"""
        self.manip.add_link(1, 1.0, math.pi/2, 0.0, 0.0)
        
        x, y, z = self.manip.calculate_position(1)
        
        self.assertAlmostEqual(x, 1.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        self.assertAlmostEqual(z, 0.0, places=6)
    
    def test_calculate_position_two_links(self):
        """Тест: расчёт позиции двух звеньев"""
        # Звено 1: вертикально вверх
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        # Звено 2: горизонтально по X
        self.manip.add_link(2, 1.0, math.pi/2, 0.0, 0.0)
        
        x, y, z = self.manip.calculate_position(2)
        
        self.assertAlmostEqual(x, 1.0, places=6)
        self.assertAlmostEqual(y, 0.0, places=6)
        self.assertAlmostEqual(z, 1.0, places=6)
    
    def test_calculate_position_with_yaw(self):
        """Тест: расчёт позиции с учётом yaw-вращения"""
        # Звено 1: длина 1.0, под углом 45° в плоскости XY
        self.manip.add_link(1, 1.0, math.pi/2, math.pi/4, 0.0)
        
        x, y, z = self.manip.calculate_position(1)
        
        expected = 1.0 / math.sqrt(2)  # ≈0.7071
        self.assertAlmostEqual(x, expected, places=6)
        self.assertAlmostEqual(y, expected, places=6)
        self.assertAlmostEqual(z, 0.0, places=6)
    
    def test_calculate_position_broken_chain(self):
        """Тест: ошибка при разорванной цепочке звеньев"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        self.manip.add_link(3, 1.0, 0.0, 0.0, 0.0)  # Пропущен ID=2
        
        with self.assertRaises(ManipulatorException):
            self.manip.calculate_position(3)
    
    def test_print_structure(self):
        """Тест: вывод структуры (просто проверяем, что не падает)"""
        self.manip.add_link(1, 1.0, 0.0, 0.0, 0.0)
        self.manip.add_gripper(2, 0.5, 0.0, 0.0, 0.0, 0.3)
        
        result = self.manip.print_structure()
        self.assertTrue(result)


class TestCreateManipulator(unittest.TestCase):
    """Тесты для фабричной функции create_manipulator"""
    
    def test_create_mock(self):
        """Тест: создание mock-манипулятора"""
        manip = create_manipulator(use_mock=True)
        self.assertIsInstance(manip, MockManipulatorBridge)
        manip.close()
    
    def test_create_real_fallback(self):
        """Тест: при отсутствии DLL происходит fallback к mock"""
        manip = create_manipulator(use_mock=False, dll_path="nonexistent.dll")
        self.assertIsInstance(manip, MockManipulatorBridge)
        manip.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
