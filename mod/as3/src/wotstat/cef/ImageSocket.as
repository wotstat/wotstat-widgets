package wotstat.cef {
  import flash.display.Bitmap;
  import flash.display.BitmapData;
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
    private var imageLength:int;
    private var headerRead:Boolean;
    private var bitmap:Bitmap;
    private var loader:Loader;
    private var isLoading:Boolean;

    private var width:int;
    private var height:int;

    public function ImageSocket(host:String, port:int, width:int, height:int) {
      socket = new Socket();
      buffer = new ByteArray();
      loader = new Loader();
      buffer.endian = Endian.BIG_ENDIAN;
      headerRead = false;
      isLoading = false;

      this.width = width;
      this.height = height;

      socket.addEventListener(Event.CONNECT, onConnect);
      socket.addEventListener(Event.CLOSE, onClose);
      socket.addEventListener(IOErrorEvent.IO_ERROR, onError);
      socket.addEventListener(ProgressEvent.SOCKET_DATA, onSocketData);
      loader.contentLoaderInfo.addEventListener(Event.COMPLETE, onImageLoadComplete);

      trace("[IS] Connecting to server: " + host + ":" + port);
      socket.connect(host, port);
      trace("[IS] Connected to server: " + socket.connected);

      bitmap = new Bitmap();
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
      if (socket.bytesAvailable > 0) {
        if (!headerRead) {
          // Read the header (assuming the first 4 bytes indicate the length of the image data)
          if (socket.bytesAvailable >= 4) {
            imageLength = socket.readInt();
            headerRead = true;
          }
          else {
            return;
          }
        }

        if (headerRead && socket.bytesAvailable >= imageLength) {
          socket.readBytes(buffer, 0, imageLength);
          trace("[IS] Image loaded " + imageLength + " bytes; Available: " + socket.bytesAvailable);

          if (!isLoading) {
            isLoading = true;
            loader.loadBytes(buffer);
          }

          buffer.clear();
          headerRead = false;
        }
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

      bitmap.width = width / 2;
      bitmap.height = height / 2;

      // this.hitTestPoint()
    }

  }
}