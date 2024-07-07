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
  import wotstat.cef.controls.HideShow;
  import wotstat.cef.controls.Reload;
  import wotstat.cef.controls.Close;
  import wotstat.cef.controls.Button;

  public class DraggableWidget extends Sprite {
    public static const REQUEST_RESIZE:String = "REQUEST_RESIZE";

    private const HANGAR_TOP_OFFSET:int = 0;
    private const HANGAR_BOTTOM_OFFSET:int = 90;

    private var imageSocket:ImageSocket;
    private var isDragging:Boolean = false;
    private var targetWidth:Number = 100;
    private var contentWidth:Number = 0;
    private var contentHeight:Number = 0;
    private var controlPanel:ControlsPanel;
    private var _port:int = 0;

    private var hideShowBtn:HideShow = new HideShow(onHideShowButtonClick);
    private var lockBtn:Lock = new Lock(onLockButtonClick);
    private var resizeBtn:Resize = new Resize(onResizeButtonClick);
    private var reloadBtn:Reload = new Reload(onReloadButtonClick);
    private var closeBtn:Close = new Close(onCloseButtonClick);

    private const resizeControl:ResizeControl = new ResizeControl(40, 0, 0);

    private var isContentHidden:Boolean = false;
    private var isLocked:Boolean = false;

    public function get port():int {
      return _port;
    }

    public function DraggableWidget(host:String, port:int) {
      super();
      _port = port;

      imageSocket = new ImageSocket(host, port);
      addChild(imageSocket);

      controlPanel = new ControlsPanel()
        .addButton(hideShowBtn)
        .addButton(lockBtn)
        .addButton(resizeBtn)
        .addButton(reloadBtn)
        .addButton(closeBtn);

      controlPanel.layout();

      addChild(controlPanel);
      controlPanel.y = -controlPanel.height - 3;

      this.x = (App.appWidth - imageSocket.width) / 2;
      this.y = (App.appHeight - imageSocket.height) / 2;

      resizeControl.contentWidth = imageSocket.width;
      resizeControl.contentHeight = imageSocket.height;

      addChild(resizeControl.target);

      imageSocket.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDown);
      imageSocket.addEventListener(ImageSocket.FRAME_RESIZE, onImageSocketResize);
      App.instance.addEventListener(MouseEvent.MOUSE_UP, onMouseUp);
      resizeControl.addEventListener(ResizeControl.RESIZE_MOVE, onResizeControlChange);
      resizeControl.addEventListener(ResizeControl.RESIZE_END, onReziseControlEnd);
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

      x = Math.round(x);
      y = Math.round(y);

      isDragging = false;
      stopDrag();
      trace("[DW] Mouse up + " + x + "x" + y);
    }

    private function onHideShowButtonClick(event:MouseEvent):void {
      isContentHidden = !isContentHidden;
      hideShowBtn.isShow = !isContentHidden;
      imageSocket.visible = !isContentHidden;

      for each (var value:Button in [lockBtn, resizeBtn, reloadBtn, closeBtn]) {
        value.visible = !isContentHidden;
      }

      controlPanel.layout();
    }

    private function onResizeButtonClick(event:MouseEvent):void {
      resizeControl.active = !resizeControl.active;
    }

    private function onLockButtonClick(event:MouseEvent):void {
      isLocked = !isLocked;

      if (resizeControl.active) {
        resizeControl.active = false;
      }

      for each (var value:Button in [resizeBtn, reloadBtn, closeBtn]) {
        value.visible = !isLocked;
      }

      imageSocket.hitArea = isLocked ? new Sprite() : null;
      imageSocket.mouseChildren = !isLocked;
      imageSocket.mouseEnabled = !isLocked;
    }

    private function onReloadButtonClick(event:MouseEvent):void {
      trace("[DW] Reload button clicked");
    }

    private function onCloseButtonClick(event:MouseEvent):void {
      trace("[DW] Close button clicked");
    }

    private function onImageSocketResize(event:ResizeEvent):void {
      // trace("[DW] Image socket resized " + event.scaleX + "x" + event.scaleY);
      contentWidth = event.scaleX;
      contentHeight = event.scaleY;
      updateImageScale();
      updateResizeControl();
    }

    private function onResizeControlChange(event:ResizeEvent):void {
      // trace("[DW] Resize control changed " + event.scaleX + "x" + event.scaleY);
      targetWidth = event.scaleX;
      updateImageScale();
      updateResizeControl();
    }

    private function onReziseControlEnd(event:Event):void {
      // trace("[DW] Resize control end " + targetWidth + "x" + contentWidth);
      targetWidth = Math.round(targetWidth);
      updateImageScale();
      updateResizeControl();
      dispatchEvent(new ResizeEvent(REQUEST_RESIZE, targetWidth * App.appScale, 0));
    }

    private function updateImageScale():void {
      imageSocket.scaleX = targetWidth / contentWidth;
      imageSocket.scaleY = imageSocket.scaleX;
    }

    private function updateResizeControl():void {
      resizeControl.contentWidth = contentWidth * imageSocket.scaleX;
      resizeControl.contentHeight = contentHeight * imageSocket.scaleY;
    }
  }
}