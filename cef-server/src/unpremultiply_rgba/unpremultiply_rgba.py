import ctypes

# Load the shared library (DLL)
lib = ctypes.CDLL('./unpremultiply_rgba.dll')

# Define the argument types and return type of the function
lib.unpremultiply_rgba.argtypes = [ctypes.POINTER(ctypes.c_ubyte), ctypes.c_size_t]
lib.unpremultiply_rgba.restype = None

def unpremultiply_rgba(data):
  data_ptr = (ctypes.c_ubyte * len(data)).from_buffer(data)
  lib.unpremultiply_rgba(data_ptr, len(data))

  return data
  