package wotstat.cef {

  import flash.display.Sprite;
  import flash.events.MouseEvent;
  import flash.geom.Rectangle;
  import wotstat.cef.buttons.Close;
  import wotstat.cef.buttons.Lock;

  public class DraggableWidget extends Sprite {
    private var imageSocket:ImageSocket;
    private var dragArea:Sprite;
    private var isDragging:Boolean = false;

    private const HANGAR_TOP_OFFSET:int = 0;
    private const HANGAR_BOTTOM_OFFSET:int = 90;

    public function DraggableWidget(host:String, port:int) {
      super();

      imageSocket = new ImageSocket(host, port);
      addChild(imageSocket);

      var close:Close = new Close();
      addChild(close);
      close.x = -20;
      close.y = 0;

      var lock:Lock = new Lock();
      addChild(lock);
      lock.x = -20;
      lock.y = 22;

      this.x = (App.appWidth - imageSocket.width) / 2;
      this.y = (App.appHeight - imageSocket.height) / 2;


      imageSocket.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDown);
      imageSocket.addEventListener(MouseEvent.MOUSE_UP, onMouseUp);
      // App.instance.addEventListener(MouseEvent.MOUSE_UP, onMouseUp);
    }

    private function onMouseDown(event:MouseEvent):void {
      if (isDragging)
        return;

      isDragging = true;
      trace("[DW] Mouse down " + imageSocket.width + "x" + imageSocket.height + "; " + App.appWidth + "x" + App.appHeight);
      startDrag(false, new Rectangle(
            0,
            HANGAR_TOP_OFFSET,
            App.appWidth - imageSocket.width,
            App.appHeight - imageSocket.height - HANGAR_TOP_OFFSET - HANGAR_BOTTOM_OFFSET
          ));
    }

    private function onMouseUp(event:MouseEvent):void {
      if (!isDragging)
        return;

      isDragging = false;
      stopDrag();
      trace("[DW] Mouse up + " + x + "x" + y);
    }
  }
}