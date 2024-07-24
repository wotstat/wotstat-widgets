#include <cstring>

extern "C" {
  __declspec(dllexport) void unpremultiply_rgba(unsigned char* data, size_t length) {
    for (size_t i = 0; i < length; i+=4) {
      unsigned int r = data[i];
      unsigned int g = data[i+1];
      unsigned int b = data[i+2];
      unsigned int a = data[i+3];

      if (a == 0) {
        data[i] = 0;
        data[i+1] = 0;
        data[i+2] = 0;
        data[i+3] = 0;
      } else {
        data[i] = (unsigned char)((r * 255) / a);
        data[i+1] = (unsigned char)((g * 255) / a);
        data[i+2] = (unsigned char)((b * 255) / a);
        data[i+3] = (unsigned char)a;
      }
    }
  }
}