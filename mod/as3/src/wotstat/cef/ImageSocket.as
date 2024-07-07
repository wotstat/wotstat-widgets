package wotstat.cef {
  import flash.display.Bitmap;
  import flash.display.Sprite;
  import flash.events.Event;
  import flash.events.IOErrorEvent;
  import flash.events.ProgressEvent;
  import flash.net.Socket;
  import flash.utils.ByteArray;
  import flash.display.Loader;
  import scaleform.clik.events.ResizeEvent;
  import flash.display.PixelSnapping;

  public class ImageSocket extends Sprite {
    public static const FRAME_RESIZE:String = "FRAME_RESIZE";

    private var socket:Socket;
    private var loader:Loader;

    private var isLoading:Boolean;

    public function ImageSocket(host:String, port:int) {
      socket = new Socket();
      loader = new Loader();
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

      addChild(loader);
    }

    public function dispose():void {
      socket.removeEventListener(Event.CONNECT, onConnect);
      socket.removeEventListener(Event.CLOSE, onClose);
      socket.removeEventListener(IOErrorEvent.IO_ERROR, onError);
      socket.removeEventListener(ProgressEvent.SOCKET_DATA, onSocketData);
      loader.contentLoaderInfo.removeEventListener(Event.COMPLETE, onImageLoadComplete);

      socket.close();
      loader.unload();
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

    private var buffer:ByteArray = new ByteArray();
    private function onSocketData(event:ProgressEvent):void {
      buffer.clear();
      socket.readBytes(buffer);
      onDataFrame(buffer);
    }


    private const HEADER_SIZE:int = 4 * 3;

    private var frameBuffer:ByteArray = new ByteArray();
    private var tempBuffer:ByteArray = new ByteArray();

    private var frameLength:int = 0;
    private var frameWidth:int = 0;
    private var frameHeight:int = 0;
    private var nextFrameLength:int = 0;
    private var nextFrameWidth:int = 0;
    private var nextFrameHeight:int = 0;
    private var headerRead:Boolean = false;

    private function onDataFrame(data:ByteArray):void {
      // trace("[IS] OnDataFrame: " + tempBuffer.length + "; " + data.length);

      if (data.length == 0)
        return;

      var hasNewFrame:Boolean = false;
      data.position = 0;

      while (data.bytesAvailable > 0) {
        // trace("[IS] Data available: " + data.bytesAvailable + "; " + headerRead + "; " + tempBuffer.length);
        if (headerRead) {
          if (tempBuffer.length + data.bytesAvailable < nextFrameLength) {
            tempBuffer.writeBytes(data, data.position);
            return;
          }

          frameBuffer.clear();
          frameBuffer.writeBytes(tempBuffer);
          frameBuffer.writeBytes(data, data.position, nextFrameLength - tempBuffer.length);
          data.position += nextFrameLength - tempBuffer.length;

          tempBuffer.clear();
          headerRead = false;
          hasNewFrame = true;
          frameWidth = nextFrameWidth;
          frameHeight = nextFrameHeight;
          frameLength = nextFrameLength;
          // trace("[IS] Image buffer read: " + frameBuffer.length + " bytes)" + ": " + bufferString(frameBuffer));
        }
        else {
          if (tempBuffer.length + data.bytesAvailable < HEADER_SIZE) {
            tempBuffer.writeBytes(data, data.position);
            return;
          }

          if (tempBuffer.length == 0) {
            nextFrameWidth = data.readInt();
            nextFrameHeight = data.readInt();
            nextFrameLength = data.readInt();
          }
          else {
            tempBuffer.writeBytes(data, data.position, HEADER_SIZE - tempBuffer.length);
            data.position += HEADER_SIZE - tempBuffer.length;

            nextFrameWidth = tempBuffer.readInt();
            nextFrameHeight = tempBuffer.readInt();
            nextFrameLength = tempBuffer.readInt();
            tempBuffer.clear();
          }
          // trace("[IS] Image header read: " + nextFrameWidth + "x" + nextFrameHeight + " (" + nextFrameLength + " bytes)");
          headerRead = true;
        }
      }

      if (hasNewFrame) {
        // trace("[IS] NEW FRAME: " + frameWidth + "x" + frameHeight + " (" + frameLength + " bytes)");
        onFrame();
      }
    }

    private var frameCount:int = 0;
    private function onFrame():void {
      var k:Number = 1 / App.appScale;
      if (loader.scaleX != k) {
        loader.scaleX = k;
        loader.scaleY = k;
      }

      loader.unload();
      loader.loadBytes(frameBuffer);
      dispatchEvent(new ResizeEvent(FRAME_RESIZE, frameWidth / App.appScale, frameHeight / App.appScale));
    }

    private function onImageLoadComplete(event:Event):void {
      // trace("[IS] Image loaded: " + loader.width + "x" + loader.height);
      (event.target.content as Bitmap).smoothing = false;
      (event.target.content as Bitmap).pixelSnapping = PixelSnapping.ALWAYS;
    }
  }
}