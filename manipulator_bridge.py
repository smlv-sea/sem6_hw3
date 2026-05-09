"""
Bridge between Python UI and C++ RobotManipulator.dll
"""

import ctypes
import sys
import os
from typing import Optional, Tuple, List, Dict, Any


class ManipulatorException(Exception):
    """Exception for manipulator chain errors"""
    pass


class ManipulatorBridge:
    """
    Bridge class for interacting with RobotManipulator.dll
    """
    
    def __init__(self, dll_path: Optional[str] = None):
        """
        Initialize bridge and load DLL
        
        Args:
            dll_path: Path to RobotManipulator.dll (if None, search in default locations)
        """
        self.dll = None
        self.manipulator_handle = None
        self._load_dll(dll_path)
        self._init_manipulator()
    
    def _load_dll(self, dll_path: Optional[str] = None):
        """Load RobotManipulator.dll"""
        
        # Search paths for DLL
        search_paths = []
        if dll_path:
            search_paths.append(dll_path)
        
        # Default search locations
        search_paths.extend([
            os.path.join(os.path.dirname(__file__), "..", "RobotManipulator.dll"),
            os.path.join(os.path.dirname(__file__), "..", "build_objs", "RobotManipulator.dll"),
            os.path.join(os.getcwd(), "RobotManipulator.dll"),
            "RobotManipulator.dll"
        ])
        
        dll_loaded = False
        last_error = None
        
        for path in search_paths:
            try:
                if os.path.exists(path):
                    self.dll = ctypes.CDLL(path)
                    dll_loaded = True
                    print(f"Successfully loaded DLL from: {path}")
                    break
            except Exception as e:
                last_error = e
                continue
        
        if not dll_loaded:
            raise FileNotFoundError(
                f"RobotManipulator.dll not found. Searched in:\n" + 
                "\n".join(f"  - {p}" for p in search_paths) +
                f"\nLast error: {last_error}\n\n"
                "Please build the DLL first (see user manual section 2.2)"
            )
        
        # Define function signatures
        
        # rm_create_manipulator: void* -> handle
        self.dll.rm_create_manipulator.argtypes = []
        self.dll.rm_create_manipulator.restype = ctypes.c_void_p
        
        # rm_destroy_manipulator: void* -> void
        self.dll.rm_destroy_manipulator.argtypes = [ctypes.c_void_p]
        self.dll.rm_destroy_manipulator.restype = None
        
        # rm_add_link: handle, int, double, double, double, double -> int
        self.dll.rm_add_link.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double, 
                                          ctypes.c_double, ctypes.c_double, ctypes.c_double]
        self.dll.rm_add_link.restype = ctypes.c_int
        
        # rm_add_gripper: handle, int, double, double, double, double, double -> int
        self.dll.rm_add_gripper.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double,
                                             ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                             ctypes.c_double]
        self.dll.rm_add_gripper.restype = ctypes.c_int
        
        # rm_add_camera: handle, int, double, double, double, double, double -> int
        self.dll.rm_add_camera.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double,
                                           ctypes.c_double, ctypes.c_double, ctypes.c_double,
                                           ctypes.c_double]
        self.dll.rm_add_camera.restype = ctypes.c_int
        
        # rm_set_direction: handle, int, double, double, double -> int
        self.dll.rm_set_direction.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double,
                                              ctypes.c_double, ctypes.c_double]
        self.dll.rm_set_direction.restype = ctypes.c_int
        
        # rm_open_gripper: handle, int, double -> int
        self.dll.rm_open_gripper.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_double]
        self.dll.rm_open_gripper.restype = ctypes.c_int
        
        # rm_close_gripper: handle, int -> int
        self.dll.rm_close_gripper.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.dll.rm_close_gripper.restype = ctypes.c_int
        
        # rm_take_photo: handle, int -> int
        self.dll.rm_take_photo.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.dll.rm_take_photo.restype = ctypes.c_int
        
        # rm_calculate_position: handle, int, double*, double*, double* -> int
        self.dll.rm_calculate_position.argtypes = [ctypes.c_void_p, ctypes.c_int,
                                                   ctypes.POINTER(ctypes.c_double),
                                                   ctypes.POINTER(ctypes.c_double),
                                                   ctypes.POINTER(ctypes.c_double)]
        self.dll.rm_calculate_position.restype = ctypes.c_int
        
        # rm_print_structure: handle -> int
        self.dll.rm_print_structure.argtypes = [ctypes.c_void_p]
        self.dll.rm_print_structure.restype = ctypes.c_int
        
        # rm_get_last_error: void* -> char*
        self.dll.rm_get_last_error.argtypes = [ctypes.c_void_p]
        self.dll.rm_get_last_error.restype = ctypes.c_char_p
    
    def _init_manipulator(self):
        """Create manipulator instance"""
        self.manipulator_handle = self.dll.rm_create_manipulator()
        if not self.manipulator_handle:
            raise RuntimeError("Failed to create manipulator")
    
    def _check_return(self, ret_code: int, operation: str):
        """Check return code and raise exception if error"""
        if ret_code == 1:
            return True
        elif ret_code == -1:
            error_msg = self.dll.rm_get_last_error(self.manipulator_handle)
            if error_msg:
                raise ManipulatorException(f"Chain error: {error_msg.decode('utf-8')}")
            raise ManipulatorException("Chain integrity violation")
        else:
            error_msg = self.dll.rm_get_last_error(self.manipulator_handle)
            if error_msg:
                raise RuntimeError(f"{operation} failed: {error_msg.decode('utf-8')}")
            raise RuntimeError(f"{operation} failed with code {ret_code}")
    
    def add_link(self, link_id: int, length: float, pitch: float, yaw: float, roll: float) -> bool:
        """
        Add a movable link
        
        Args:
            link_id: Unique ID (>=1, must be sequential from 1)
            length: Length of link (r)
            pitch: Pitch angle in radians
            yaw: Yaw angle in radians
            roll: Roll angle in radians
        
        Returns:
            True if successful
        """
        if link_id < 1:
            raise ValueError("Link ID must be >= 1")
        
        ret = self.dll.rm_add_link(self.manipulator_handle, link_id, length, pitch, yaw, roll)
        return self._check_return(ret, "Add link")
    
    def add_gripper(self, link_id: int, length: float, pitch: float, yaw: float, roll: float,
                    opening_angle: float) -> bool:
        """
        Add a gripper link
        
        Args:
            link_id: Unique ID (>=1, must be sequential from 1)
            length: Length of link (r)
            pitch: Pitch angle in radians
            yaw: Yaw angle in radians
            roll: Roll angle in radians
            opening_angle: Gripper opening angle in radians
        
        Returns:
            True if successful
        """
        if link_id < 1:
            raise ValueError("Link ID must be >= 1")
        
        ret = self.dll.rm_add_gripper(self.manipulator_handle, link_id, length, pitch, yaw, roll,
                                      opening_angle)
        return self._check_return(ret, "Add gripper")
    
    def add_camera(self, link_id: int, length: float, pitch: float, yaw: float, roll: float,
                   field_of_view: float) -> bool:
        """
        Add a camera link
        
        Args:
            link_id: Unique ID (>=1, must be sequential from 1)
            length: Length of link (r)
            pitch: Pitch angle in radians
            yaw: Yaw angle in radians
            roll: Roll angle in radians
            field_of_view: Camera field of view in radians
        
        Returns:
            True if successful
        """
        if link_id < 1:
            raise ValueError("Link ID must be >= 1")
        
        ret = self.dll.rm_add_camera(self.manipulator_handle, link_id, length, pitch, yaw, roll,
                                     field_of_view)
        return self._check_return(ret, "Add camera")
    
    def set_orientation(self, link_id: int, pitch: float, yaw: float, roll: float) -> bool:
        """
        Set orientation of a link
        
        Args:
            link_id: ID of the link
            pitch: New pitch angle in radians
            yaw: New yaw angle in radians
            roll: New roll angle in radians
        
        Returns:
            True if successful
        """
        ret = self.dll.rm_set_direction(self.manipulator_handle, link_id, pitch, yaw, roll)
        return self._check_return(ret, "Set orientation")
    
    def open_gripper(self, gripper_id: int, opening_angle: float) -> bool:
        """
        Open gripper to specified angle
        
        Args:
            gripper_id: ID of the gripper
            opening_angle: Opening angle in radians
        
        Returns:
            True if successful
        """
        ret = self.dll.rm_open_gripper(self.manipulator_handle, gripper_id, opening_angle)
        return self._check_return(ret, "Open gripper")
    
    def close_gripper(self, gripper_id: int) -> bool:
        """
        Close gripper fully
        
        Args:
            gripper_id: ID of the gripper
        
        Returns:
            True if successful
        """
        ret = self.dll.rm_close_gripper(self.manipulator_handle, gripper_id)
        return self._check_return(ret, "Close gripper")
    
    def take_photo(self, camera_id: int) -> bool:
        """
        Take photo with camera
        
        Args:
            camera_id: ID of the camera
        
        Returns:
            True if successful
        """
        ret = self.dll.rm_take_photo(self.manipulator_handle, camera_id)
        return self._check_return(ret, "Take photo")
    
    def calculate_position(self, link_id: int) -> Tuple[float, float, float]:
        """
        Calculate end coordinates of a link in global space
        
        Args:
            link_id: ID of the link
        
        Returns:
            Tuple of (x, y, z) coordinates
        """
        x = ctypes.c_double()
        y = ctypes.c_double()
        z = ctypes.c_double()
        
        ret = self.dll.rm_calculate_position(self.manipulator_handle, link_id,
                                             ctypes.byref(x), ctypes.byref(y), ctypes.byref(z))
        self._check_return(ret, "Calculate position")
        
        return (x.value, y.value, z.value)
    
    def print_structure(self) -> bool:
        """
        Print manipulator structure to console
        
        Returns:
            True if successful
        """
        ret = self.dll.rm_print_structure(self.manipulator_handle)
        return self._check_return(ret, "Print structure")
    
    def close(self):
        """Destroy manipulator and free resources"""
        if self.manipulator_handle and self.dll:
            self.dll.rm_destroy_manipulator(self.manipulator_handle)
            self.manipulator_handle = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Mock implementation for testing without DLL
class MockManipulatorBridge:
    """
    Mock bridge for testing when DLL is not available
    """
    
    def __init__(self):
        self.links = {}
        self.next_id = 1
        print("WARNING: Using mock manipulator (no DLL). For real use, build RobotManipulator.dll")
    
    def add_link(self, link_id: int, length: float, pitch: float, yaw: float, roll: float) -> bool:
        if link_id != self.next_id:
            raise ManipulatorException(f"Chain violation: expected ID {self.next_id}, got {link_id}")
        self.links[link_id] = {'type': 'MovableLink', 'length': length, 'pitch': pitch, 'yaw': yaw, 'roll': roll}
        self.next_id += 1
        print(f"Added MovableLink {link_id}: length={length}, angles=({pitch}, {yaw}, {roll})")
        return True
    
    def add_gripper(self, link_id: int, length: float, pitch: float, yaw: float, roll: float,
                    opening_angle: float) -> bool:
        if link_id != self.next_id:
            raise ManipulatorException(f"Chain violation: expected ID {self.next_id}, got {link_id}")
        self.links[link_id] = {'type': 'Gripper', 'length': length, 'pitch': pitch, 'yaw': yaw, 'roll': roll,
                               'opening_angle': opening_angle}
        self.next_id += 1
        print(f"Added Gripper {link_id}: length={length}, angles=({pitch}, {yaw}, {roll}), opening={opening_angle}")
        return True
    
    def add_camera(self, link_id: int, length: float, pitch: float, yaw: float, roll: float,
                   field_of_view: float) -> bool:
        if link_id != self.next_id:
            raise ManipulatorException(f"Chain violation: expected ID {self.next_id}, got {link_id}")
        self.links[link_id] = {'type': 'Camera', 'length': length, 'pitch': pitch, 'yaw': yaw, 'roll': roll,
                               'fov': field_of_view}
        self.next_id += 1
        print(f"Added Camera {link_id}: length={length}, angles=({pitch}, {yaw}, {roll}), FOV={field_of_view}")
        return True
    
    def set_orientation(self, link_id: int, pitch: float, yaw: float, roll: float) -> bool:
        if link_id not in self.links:
            raise RuntimeError(f"Link {link_id} not found")
        self.links[link_id]['pitch'] = pitch
        self.links[link_id]['yaw'] = yaw
        self.links[link_id]['roll'] = roll
        print(f"Set orientation of link {link_id}: ({pitch}, {yaw}, {roll})")
        return True
    
    def open_gripper(self, gripper_id: int, opening_angle: float) -> bool:
        if gripper_id not in self.links or self.links[gripper_id]['type'] != 'Gripper':
            raise RuntimeError(f"Gripper {gripper_id} not found")
        self.links[gripper_id]['opening_angle'] = opening_angle
        print(f"Opened gripper {gripper_id} to {opening_angle} rad")
        return True
    
    def close_gripper(self, gripper_id: int) -> bool:
        if gripper_id not in self.links or self.links[gripper_id]['type'] != 'Gripper':
            raise RuntimeError(f"Gripper {gripper_id} not found")
        self.links[gripper_id]['opening_angle'] = 0
        print(f"Closed gripper {gripper_id}")
        return True
    
    def take_photo(self, camera_id: int) -> bool:
        if camera_id not in self.links or self.links[camera_id]['type'] != 'Camera':
            raise RuntimeError(f"Camera {camera_id} not found")
        print(f"[Camera {camera_id}] Photo taken! (FOV: {self.links[camera_id]['fov']:.3f} rad)")
        return True
    
    def calculate_position(self, link_id: int) -> Tuple[float, float, float]:
        if link_id not in self.links:
            raise RuntimeError(f"Link {link_id} not found")
        
        # Simulate forward kinematics calculation
        import math
        
        x, y, z = 0.0, 0.0, 0.0
        
        for lid in range(1, link_id + 1):
            if lid not in self.links:
                raise ManipulatorException(f"Chain broken: link {lid} missing")
            
            link = self.links[lid]
            r = link['length']
            pitch = link['pitch']
            yaw = link['yaw']
            
            dx = r * math.cos(yaw) * math.sin(pitch)
            dy = r * math.sin(yaw) * math.sin(pitch)
            dz = r * math.cos(pitch)
            
            x += dx
            y += dy
            z += dz
        
        print(f"Calculated position for link {link_id}: ({x:.3f}, {y:.3f}, {z:.3f})")
        return (x, y, z)
    
    def print_structure(self) -> bool:
        print("\n=== Manipulator Structure ===")
        for lid, link in sorted(self.links.items()):
            print(f"  [{lid}] {link['type']}: length={link['length']:.3f}, "
                  f"angles=({link['pitch']:.3f}, {link['yaw']:.3f}, {link['roll']:.3f})")
            if 'opening_angle' in link:
                print(f"       gripper opening: {link['opening_angle']:.3f} rad")
            if 'fov' in link:
                print(f"       camera FOV: {link['fov']:.3f} rad")
        print("=============================\n")
        return True
    
    def close(self):
        self.links.clear()
        self.next_id = 1
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_manipulator(use_mock: bool = False, dll_path: Optional[str] = None):
    """
    Factory function to create manipulator bridge
    
    Args:
        use_mock: If True, use mock implementation (for testing without DLL)
        dll_path: Path to DLL file (ignored if use_mock=True)
    
    Returns:
        Manipulator bridge instance
    """
    if use_mock:
        return MockManipulatorBridge()
    
    try:
        return ManipulatorBridge(dll_path)
    except FileNotFoundError as e:
        print(f"\n{e}")
        print("\nFalling back to mock implementation...")
        return MockManipulatorBridge()
