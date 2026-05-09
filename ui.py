"""
Robot Manipulator GUI Application
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manipulator_bridge import create_manipulator, ManipulatorException


class RobotManipulatorUI:
    """Main GUI application for Robot Manipulator"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Robot Manipulator UI")
        self.root.geometry("900x700")
        
        # Create manipulator bridge (will try DLL, fall back to mock)
        try:
            self.manipulator = create_manipulator(use_mock=False)
            self.using_mock = False
        except Exception as e:
            self.manipulator = create_manipulator(use_mock=True)
            self.using_mock = True
        
        # Store added links for display
        self.links_list = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface"""
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.build_tab = ttk.Frame(self.notebook)
        self.control_tab = ttk.Frame(self.notebook)
        self.position_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.build_tab, text="Сборка манипулятора")
        self.notebook.add(self.control_tab, text="Управление")
        self.notebook.add(self.position_tab, text="Позиция/структура")
        
        # Build tab
        self._setup_build_tab()
        
        # Control tab
        self._setup_control_tab()
        
        # Position tab
        self._setup_position_tab()
        
        # Status bar
        self.status_bar = ttk.Label(self.root, text="Готов", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        if self.using_mock:
            self._set_status("ВНИМАНИЕ: Используется эмуляция (DLL не найдена). Соберите DLL для реальной работы.", "warning")
    
    def _set_status(self, message, level="info"):
        """Set status bar message"""
        self.status_bar.config(text=message)
        if level == "error":
            self.status_bar.config(foreground="red")
        elif level == "warning":
            self.status_bar.config(foreground="orange")
        else:
            self.status_bar.config(foreground="black")
        self.root.update()
    
    def _setup_build_tab(self):
        """Setup the build tab for adding links"""
        
        # Input frame
        input_frame = ttk.LabelFrame(self.build_tab, text="Добавление звена", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Type selection
        ttk.Label(input_frame, text="Тип звена:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.link_type = tk.StringVar(value="MovableLink")
        type_combo = ttk.Combobox(input_frame, textvariable=self.link_type, 
                                  values=["MovableLink", "Gripper", "Camera"], state="readonly")
        type_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # ID
        ttk.Label(input_frame, text="ID:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.link_id = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.link_id, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Length (r)
        ttk.Label(input_frame, text="Длина r:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.link_length = tk.StringVar(value="1.0")
        ttk.Entry(input_frame, textvariable=self.link_length, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Angles
        ttk.Label(input_frame, text="Pitch (рад):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.pitch = tk.StringVar(value="0.0")
        ttk.Entry(input_frame, textvariable=self.pitch, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Yaw (рад):").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.yaw = tk.StringVar(value="0.0")
        ttk.Entry(input_frame, textvariable=self.yaw, width=10).grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Roll (рад):").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        self.roll = tk.StringVar(value="0.0")
        ttk.Entry(input_frame, textvariable=self.roll, width=10).grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Additional parameter (opening angle or FOV)
        ttk.Label(input_frame, text="Доп. параметр:").grid(row=6, column=0, sticky=tk.W, padx=5, pady=5)
        self.extra_param = tk.StringVar(value="0.0")
        self.extra_entry = ttk.Entry(input_frame, textvariable=self.extra_param, width=10)
        self.extra_entry.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        self.extra_label = ttk.Label(input_frame, text="(Для Gripper - угол раскрытия, для Camera - FOV)")
        self.extra_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Add button
        ttk.Button(input_frame, text="Добавить звено", command=self._add_link).grid(row=8, column=0, columnspan=2, pady=10)
        
        # Links list frame
        list_frame = ttk.LabelFrame(self.build_tab, text="Добавленные звенья", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.links_text = scrolledtext.ScrolledText(list_frame, height=15, width=70)
        self.links_text.pack(fill=tk.BOTH, expand=True)
        
        # Update type change handler
        def on_type_change(*args):
            link_type = self.link_type.get()
            if link_type == "MovableLink":
                self.extra_entry.config(state="disabled")
                self.extra_label.config(text="(Не используется для MovableLink)")
            else:
                self.extra_entry.config(state="normal")
                if link_type == "Gripper":
                    self.extra_label.config(text="(Для Gripper - угол раскрытия в радианах)")
                else:
                    self.extra_label.config(text="(Для Camera - угол обзора FOV в радианах)")
        
        self.link_type.trace('w', on_type_change)
        on_type_change()
    
    def _add_link(self):
        """Add a link to the manipulator"""
        try:
            link_id = int(self.link_id.get())
            if link_id < 1:
                messagebox.showerror("Ошибка", "ID звена должен быть не менее 1")
                return
            
            length = float(self.link_length.get())
            pitch = float(self.pitch.get())
            yaw = float(self.yaw.get())
            roll = float(self.roll.get())
            
            link_type = self.link_type.get()
            
            # Check if ID already exists
            for link in self.links_list:
                if link['id'] == link_id:
                    messagebox.showerror("Ошибка", f"Звено с ID {link_id} уже существует")
                    return
            
            # Check chain integrity
            if link_id > 1:
                prev_exists = False
                for link in self.links_list:
                    if link['id'] == link_id - 1:
                        prev_exists = True
                        break
                if not prev_exists:
                    messagebox.showerror("Ошибка", f"Нарушена цепочка звеньев: предыдущее звено (ID={link_id-1}) не найдено. Добавляйте звенья по порядку: 1, 2, 3...")
                    return
            
            if link_type == "MovableLink":
                self.manipulator.add_link(link_id, length, pitch, yaw, roll)
                self.links_list.append({'id': link_id, 'type': 'MovableLink', 'length': length,
                                        'pitch': pitch, 'yaw': yaw, 'roll': roll})
                self._set_status(f"Добавлено звено {link_id} (MovableLink)")
            
            elif link_type == "Gripper":
                opening_angle = float(self.extra_param.get())
                self.manipulator.add_gripper(link_id, length, pitch, yaw, roll, opening_angle)
                self.links_list.append({'id': link_id, 'type': 'Gripper', 'length': length,
                                        'pitch': pitch, 'yaw': yaw, 'roll': roll,
                                        'opening_angle': opening_angle})
                self._set_status(f"Добавлен захват {link_id} (Gripper) с углом раскрытия {opening_angle:.3f} рад")
            
            elif link_type == "Camera":
                fov = float(self.extra_param.get())
                self.manipulator.add_camera(link_id, length, pitch, yaw, roll, fov)
                self.links_list.append({'id': link_id, 'type': 'Camera', 'length': length,
                                        'pitch': pitch, 'yaw': yaw, 'roll': roll, 'fov': fov})
                self._set_status(f"Добавлена камера {link_id} (Camera) с FOV {fov:.3f} рад")
            
            # Update display
            self._update_links_display()
            
            # Clear inputs for next link (increment ID suggestion)
            if self.links_list:
                self.link_id.set(str(len(self.links_list) + 1))
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат числа: {e}")
        except ManipulatorException as e:
            messagebox.showerror("Ошибка", str(e))
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка: {e}")
    
    def _update_links_display(self):
        """Update the links display text area"""
        self.links_text.delete(1.0, tk.END)
        
        if not self.links_list:
            self.links_text.insert(tk.END, "Нет добавленных звеньев\n")
            return
        
        for link in self.links_list:
            self.links_text.insert(tk.END, f"ID {link['id']}: {link['type']}\n")
            self.links_text.insert(tk.END, f"  Длина: {link['length']:.3f}\n")
            self.links_text.insert(tk.END, f"  Ориентация: pitch={link['pitch']:.3f}, yaw={link['yaw']:.3f}, roll={link['roll']:.3f} рад\n")
            
            if link['type'] == 'Gripper':
                self.links_text.insert(tk.END, f"  Угол раскрытия: {link.get('opening_angle', 0):.3f} рад\n")
            elif link['type'] == 'Camera':
                self.links_text.insert(tk.END, f"  Угол обзора (FOV): {link.get('fov', 0):.3f} рад\n")
            
            self.links_text.insert(tk.END, "\n")
    
    def _setup_control_tab(self):
        """Setup the control tab"""
        
        # Orientation control frame
        orient_frame = ttk.LabelFrame(self.control_tab, text="Установить ориентацию", padding=10)
        orient_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(orient_frame, text="ID звена:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.orient_id = tk.StringVar()
        ttk.Entry(orient_frame, textvariable=self.orient_id, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(orient_frame, text="Pitch (рад):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.orient_pitch = tk.StringVar(value="0.0")
        ttk.Entry(orient_frame, textvariable=self.orient_pitch, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(orient_frame, text="Yaw (рад):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.orient_yaw = tk.StringVar(value="0.0")
        ttk.Entry(orient_frame, textvariable=self.orient_yaw, width=10).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(orient_frame, text="Roll (рад):").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.orient_roll = tk.StringVar(value="0.0")
        ttk.Entry(orient_frame, textvariable=self.orient_roll, width=10).grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(orient_frame, text="Установить ориентацию", command=self._set_orientation).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Gripper control frame
        gripper_frame = ttk.LabelFrame(self.control_tab, text="Управление захватом", padding=10)
        gripper_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(gripper_frame, text="ID захвата:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.gripper_id = tk.StringVar()
        ttk.Entry(gripper_frame, textvariable=self.gripper_id, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(gripper_frame, text="Угол раскрытия (рад):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.gripper_angle = tk.StringVar(value="0.0")
        ttk.Entry(gripper_frame, textvariable=self.gripper_angle, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        btn_frame = ttk.Frame(gripper_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Открыть захват", command=self._open_gripper).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Закрыть захват", command=self._close_gripper).pack(side=tk.LEFT, padx=5)
        
        # Camera control frame
        camera_frame = ttk.LabelFrame(self.control_tab, text="Управление камерой", padding=10)
        camera_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(camera_frame, text="ID камеры:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.camera_id = tk.StringVar()
        ttk.Entry(camera_frame, textvariable=self.camera_id, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(camera_frame, text="Сделать снимок", command=self._take_photo).grid(row=1, column=0, columnspan=2, pady=10)
    
    def _set_orientation(self):
        """Set orientation of a link"""
        try:
            link_id = int(self.orient_id.get())
            pitch = float(self.orient_pitch.get())
            yaw = float(self.orient_yaw.get())
            roll = float(self.orient_roll.get())
            
            self.manipulator.set_orientation(link_id, pitch, yaw, roll)
            
            # Update internal storage
            for link in self.links_list:
                if link['id'] == link_id:
                    link['pitch'] = pitch
                    link['yaw'] = yaw
                    link['roll'] = roll
                    break
            
            self._update_links_display()
            self._set_status(f"Установлена ориентация звена {link_id}: pitch={pitch:.3f}, yaw={yaw:.3f}, roll={roll:.3f} рад")
            messagebox.showinfo("Успех", f"Ориентация звена {link_id} установлена")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат: {e}")
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _open_gripper(self):
        """Open gripper"""
        try:
            gripper_id = int(self.gripper_id.get())
            angle = float(self.gripper_angle.get())
            
            self.manipulator.open_gripper(gripper_id, angle)
            
            # Update internal storage
            for link in self.links_list:
                if link['id'] == gripper_id and link['type'] == 'Gripper':
                    link['opening_angle'] = angle
                    break
            
            self._update_links_display()
            self._set_status(f"Захват {gripper_id} открыт на угол {angle:.3f} рад")
            messagebox.showinfo("Успех", f"Захват {gripper_id} открыт на угол {angle:.3f} рад")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат: {e}")
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _close_gripper(self):
        """Close gripper"""
        try:
            gripper_id = int(self.gripper_id.get())
            
            self.manipulator.close_gripper(gripper_id)
            
            # Update internal storage
            for link in self.links_list:
                if link['id'] == gripper_id and link['type'] == 'Gripper':
                    link['opening_angle'] = 0
                    break
            
            self._update_links_display()
            self._set_status(f"Захват {gripper_id} закрыт")
            messagebox.showinfo("Успех", f"Захват {gripper_id} закрыт")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат: {e}")
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _take_photo(self):
        """Take photo with camera"""
        try:
            camera_id = int(self.camera_id.get())
            
            self.manipulator.take_photo(camera_id)
            self._set_status(f"Снимок сделан камерой {camera_id}")
            messagebox.showinfo("Снимок", f"Снимок сделан камерой {camera_id} (результат в консоли)")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат: {e}")
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _setup_position_tab(self):
        """Setup the position tab"""
        
        # Position calculation frame
        pos_frame = ttk.LabelFrame(self.position_tab, text="Рассчитать позицию", padding=10)
        pos_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(pos_frame, text="ID звена:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.pos_id = tk.StringVar()
        ttk.Entry(pos_frame, textvariable=self.pos_id, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(pos_frame, text="Рассчитать позицию", command=self._calculate_position).grid(row=1, column=0, columnspan=2, pady=10)
        
        # Results display
        result_frame = ttk.LabelFrame(self.position_tab, text="Результат", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.position_text = scrolledtext.ScrolledText(result_frame, height=5, width=60)
        self.position_text.pack(fill=tk.BOTH, expand=True)
        
        # Print structure button
        ttk.Button(self.position_tab, text="Печать структуры в консоль", command=self._print_structure).pack(pady=10)
    
    def _calculate_position(self):
        """Calculate position of a link"""
        try:
            link_id = int(self.pos_id.get())
            
            x, y, z = self.manipulator.calculate_position(link_id)
            
            self.position_text.delete(1.0, tk.END)
            self.position_text.insert(tk.END, f"Координаты конца звена {link_id}:\n\n")
            self.position_text.insert(tk.END, f"  x = {x:.6f}\n")
            self.position_text.insert(tk.END, f"  y = {y:.6f}\n")
            self.position_text.insert(tk.END, f"  z = {z:.6f}\n")
            
            self._set_status(f"Рассчитана позиция звена {link_id}: ({x:.3f}, {y:.3f}, {z:.3f})")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат: {e}")
        except ManipulatorException as e:
            messagebox.showerror("Ошибка", f"Нарушена цепочка звеньев: {e}")
        except RuntimeError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def _print_structure(self):
        """Print manipulator structure to console"""
        try:
            self.manipulator.print_structure()
            self._set_status("Структура манипулятора выведена в консоль")
            messagebox.showinfo("Успех", "Структура манипулятора выведена в консоль")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def on_closing(self):
        """Handle window closing"""
        self.manipulator.close()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = RobotManipulatorUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
