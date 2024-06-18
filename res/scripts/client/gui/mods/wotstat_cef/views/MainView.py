from gui.Scaleform.framework.entities.View import View
import socket
import struct
import BigWorld


class MainView(View):

  def __init__(self, *args, **kwargs):
    super(MainView, self).__init__(*args, **kwargs)
  
  def _populate(self):
    super(MainView, self)._populate()
    print('MainView._populate')
    # self.mainLoop()

  def py_log(self, msg, level):
    print('[WOTSTAT CEF FLASH][%s]: %s' % (level, msg))
    return
  

  # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # sock.bind(('localhost', 12345))
  # sock.listen(1)

  # def send_image(self, image_data):
  #   try:
  #     self.sock.sendall(struct.pack('I', len(image_data)) + image_data)
  #   except Exception as e:
  #     self.py_log('send_image error: %s' % e, 'ERROR')


  # def mainLoop(self):
  #   # read image from file
  #   with open('C:/Games/Tanki/mods/1.27.0.0/blackbuck.bmp', 'rb') as f:
  #     image_data = f.read()
  #     print('send image')
  #     self.send_image(image_data)
  #     print('sended image')
    
  #   BigWorld.callback(1, self.mainLoop)
  