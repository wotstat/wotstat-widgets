package wotstat.cef {

  import flash.display.Sprite;
  import flash.events.MouseEvent;
  import flash.geom.Rectangle;
  import wotstat.cef.controls.Close;
  import wotstat.cef.controls.Lock;
  import wotstat.cef.controls.Resize;
  import wotstat.cef.controls.ResizeControl;
  import flash.events.Event;
  import scaleform.clik.events.ResizeEvent;

  public class DraggableWidget extends Sprite {
    private const HANGAR_TOP_OFFSET:int = 0;
    private const HANGAR_BOTTOM_OFFSET:int = 90;

    private var imageSocket:ImageSocket;
    private var dragArea:Sprite;
    private var isDragging:Boolean = false;
    private var contentWidth:Number = 0;
    private var contentHeight:Number = 0;

    private const resizeControl:ResizeControl = new ResizeControl(40, 0, 0);

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

      var resize:Resize = new Resize();
      resize.addEventListener(MouseEvent.CLICK, onResizeButtonClick);
      addChild(resize);
      resize.x = -20;
      resize.y = 44;

      this.x = (App.appWidth - imageSocket.width) / 2;
      this.y = (App.appHeight - imageSocket.height) / 2;

      resizeControl.contentWidth = imageSocket.width;
      resizeControl.contentHeight = imageSocket.height;

      addChild(resizeControl.target);


      imageSocket.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDown);
      imageSocket.addEventListener('FRAME_RESIZE', onImageSocketResize);
      // imageSocket.addEventListener(MouseEvent.MOUSE_UP, onMouseUp);
      App.instance.addEventListener(MouseEvent.MOUSE_UP, onMouseUp);
      resizeControl.addEventListener(ResizeControl.RESIZE_MOVE, onResizeControlChange);
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

    private function onResizeButtonClick(event:MouseEvent):void {
      resizeControl.active = !resizeControl.active;
    }

    private function onImageSocketResize(event:ResizeEvent):void {
      trace("[DW] Image socket resized " + event.scaleX + "x" + event.scaleY);
      contentWidth = event.scaleX;
      contentHeight = event.scaleY;
      updateResizeControl();
    }

    private function onResizeControlChange(event:ResizeEvent):void {
      trace("[DW] Resize control changed " + event.scaleX + "x" + event.scaleY);
      imageSocket.scaleX = event.scaleX / contentWidth;
      imageSocket.scaleY = imageSocket.scaleX;
      updateResizeControl();
    }

    private function updateResizeControl():void {
      resizeControl.contentWidth = contentWidth * imageSocket.scaleX;
      resizeControl.contentHeight = contentHeight * imageSocket.scaleY;
    }
  }
}