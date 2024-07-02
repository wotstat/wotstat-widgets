package wotstat.cef {

  import flash.display.Sprite;
  import flash.events.MouseEvent;
  import flash.geom.Rectangle;

  public class DraggableWidget extends Sprite {
    private var imageSocket:ImageSocket;
    private var dragArea:Sprite;

    private const HANGAR_TOP_OFFSET:int = 0;
    private const HANGAR_BOTTOM_OFFSET:int = 90;

    public function DraggableWidget(host:String, port:int) {
      super();

      imageSocket = new ImageSocket(host, port);
      addChild(imageSocket);
      // dragArea = new Sprite();

      // dragArea.graphics.lineStyle(1, 0xff00ff, 1);
      // dragArea.graphics.drawRect(0, 0, width / 2, height / 2);

      // addChild(dragArea);

      this.x = (App.appWidth - imageSocket.width) / 2;
      this.y = (App.appHeight - imageSocket.height) / 2;

      this.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDown);
    }

    private function onMouseDown(event:MouseEvent):void {
      trace("[DW] Mouse down " + imageSocket.width + "x" + imageSocket.height + "; " + App.appWidth + "x" + App.appHeight);
      startDrag(false, new Rectangle(
            0,
            HANGAR_TOP_OFFSET,
            App.appWidth - imageSocket.width,
            App.appHeight - imageSocket.height - HANGAR_TOP_OFFSET - HANGAR_BOTTOM_OFFSET
          ));

      parent.addEventListener(MouseEvent.MOUSE_UP, onMouseUp);
    }

    private function onMouseUp(event:MouseEvent):void {
      stopDrag();
      parent.removeEventListener(MouseEvent.MOUSE_UP, onMouseUp);
      trace("[DW] Mouse up + " + x + "x" + y);
    }
  }
}