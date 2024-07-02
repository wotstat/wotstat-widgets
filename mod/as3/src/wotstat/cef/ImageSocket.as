package wotstat.cef {
  import flash.display.Bitmap;
  import flash.display.Sprite;
  import flash.events.Event;
  import flash.events.IOErrorEvent;
  import flash.events.ProgressEvent;
  import flash.net.Socket;
  import flash.utils.ByteArray;
  import flash.utils.Endian;
  import flash.display.Loader;
  import flash.display.LoaderInfo;

  public class ImageSocket extends Sprite {
    private var socket:Socket;
    private var buffer:ByteArray;
    private var bitmap:Bitmap;
    private var loader:Loader;

    private var frameLength:int;
    private var frameWidth:int;
    private var frameHeight:int;

    private var headerRead:Boolean;
    private var isLoading:Boolean;

    public function ImageSocket(host:String, port:int) {
      socket = new Socket();
      buffer = new ByteArray();
      loader = new Loader();
      buffer.endian = Endian.BIG_ENDIAN;
      headerRead = false;
      isLoading = false;

      socket.addEventListener(Event.CONNECT, onConnect);
      socket.addEventListener(Event.CLOSE, onClose);
      socket.addEventListener(IOErrorEvent.IO_ERROR, onError);
      socket.addEventListener(ProgressEvent.SOCKET_DATA, onSocketData);
      loader.contentLoaderInfo.addEventListener(Event.COMPLETE, onImageLoadComplete);

      trace("[IS] Connecting to server: " + host + ":" + port);
      socket.connect(host, port);
      trace("[IS] Connected to server: " + socket.connected);

      bitmap = new Bitmap();
      bitmap.scaleX = 1 / App.appScale;
      bitmap.scaleY = 1 / App.appScale;
      addChild(bitmap);
    }

    private function onConnect(event:Event):void {
      trace("[IS] Connected to server");
    }

    private function onClose(event:Event):void {
      trace("[IS] Connection closed");
    }

    private function onError(event:IOErrorEvent):void {
      trace("[IS] Connection error: " + event.text);
    }

    private function onSocketData(event:ProgressEvent):void {
      var bytesAvailable:uint = socket.bytesAvailable;
      var hasFrame:Boolean = false;

      try {

        while (bytesAvailable > 0) {
          if (!headerRead) {

            if (bytesAvailable >= 4 * 3) {
              frameWidth = socket.readInt();
              frameHeight = socket.readInt();
              frameLength = socket.readInt();
              headerRead = true;
              bytesAvailable -= 4 * 3;
            }
            else {
              return;
            }
          }

          if (headerRead && bytesAvailable >= frameLength) {
            hasFrame = true;
            headerRead = false;
            bytesAvailable -= frameLength;

            buffer.clear();
            socket.readBytes(buffer, 0, frameLength);
            trace("[IS] Image loaded " + frameLength + " bytes; Available: " + socket.bytesAvailable);
          }
        }

        if (!isLoading && hasFrame) {
          isLoading = true;
          loader.loadBytes(buffer);
        }
      }
      catch (error:Error) {
        trace("[IS] Error: " + error.getStackTrace());
      }
    }

    private function onImageLoadComplete(event:Event):void {
      var loaderInfo:LoaderInfo = LoaderInfo(event.target);
      var newBitmap:Bitmap = Bitmap(loaderInfo.content);

      if (bitmap.bitmapData) {
        bitmap.bitmapData.dispose();
      }

      bitmap.bitmapData = newBitmap.bitmapData;
      loader.unload();
      isLoading = false;

      var k:Number = 1 / App.appScale;
      if (bitmap.scaleX != k) {
        bitmap.scaleX = k;
        bitmap.scaleY = k;
      }

      trace("[IS] Image loaded " + bitmap.width + "x" + bitmap.height + "; " + App.appScale);
    }

  }
}