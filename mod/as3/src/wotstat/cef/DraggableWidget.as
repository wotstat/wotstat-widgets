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
  import flash.geom.Point;
  import flash.utils.ByteArray;
  import flash.display.Loader;
  import flash.display.Graphics;

  public class DraggableWidget extends Sprite {
    public static const REQUEST_RESIZE:String = "REQUEST_RESIZE";
    public static const REQUEST_RELOAD:String = "REQUEST_RELOAD";
    public static const REQUEST_CLOSE:String = "REQUEST_CLOSE";

    private const HANGAR_TOP_OFFSET:int = 0;
    private const HANGAR_BOTTOM_OFFSET:int = 90;

    private var _uuid:int = 0;

    private var hideShowBtn:HideShow = new HideShow();
    private var lockBtn:Lock = new Lock(onLockButtonClick);
    private var resizeBtn:Resize = new Resize(onResizeButtonClick);
    private var reloadBtn:Reload = new Reload(onReloadButtonClick);
    private var closeBtn:Close = new Close(onCloseButtonClick);

    private var controlPanel:ControlsPanel = new ControlsPanel();
    private const resizeControl:ResizeControl = new ResizeControl(0, 0);

    // Target width by resize control in POINTS
    private var targetWidth:Number = 0;

    private var hideShowButtonDownPosition:Point = null;
    private var isDragging:Boolean = false;
    private var isContentHidden:Boolean = false;
    private var isLocked:Boolean = false;

    // CONTENT == Browser Image in readl PIXELS
    private var contentWidth:Number = 0;
    private var contentHeight:Number = 0;
    private var content:Sprite = new Sprite();
    private var loader:Loader = new Loader();

    public function get uuid():int {
      return _uuid;
    }

    public function DraggableWidget(uuid:int, width:int, height:int) {
      super();
      _uuid = uuid;

      addChild(content);
      content.addChild(loader);

      controlPanel
        .addButton(hideShowBtn)
        .addButton(lockBtn)
        .addButton(resizeBtn)
        .addButton(reloadBtn)
        .addButton(closeBtn)
        .layout();

      addChild(controlPanel);
      controlPanel.y = -controlPanel.height - 3;
      hitArea = controlPanel;

      targetWidth = width / App.appScale;

      this.x = (App.appWidth - targetWidth) / 2;
      this.y = (App.appHeight - height / App.appScale - 100) / 2;
      contentWidth = width;
      contentHeight = height;

      addChild(resizeControl);

      content.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDown);
      App.instance.addEventListener(MouseEvent.MOUSE_UP, onMouseUp);
      App.instance.addEventListener(MouseEvent.MOUSE_MOVE, onMouseMove);
      resizeControl.addEventListener(ResizeControl.RESIZE_MOVE, onResizeControlChange);
      resizeControl.addEventListener(ResizeControl.RESIZE_END, onReziseControlEnd);

      hideShowBtn.addEventListener(MouseEvent.MOUSE_DOWN, onHideShowButtonMouseDown);

      updateImageScale();
    }

    public function setFrame(width:uint, height:uint, data:ByteArray):void {

      if (width != targetWidth * App.appScale && !resizeControl.isResizing) {
        trace("[DW] Skip frame with width " + width + "!=" + targetWidth * App.appScale);
        return;
      }

      loader.unload();
      loader.loadBytes(data);

      contentWidth = width;
      contentHeight = height;

      updateImageScale();
      updateResizeControl();
    }

    public function dispose():void {
      loader.removeEventListener(MouseEvent.MOUSE_DOWN, onMouseDown);
      App.instance.removeEventListener(MouseEvent.MOUSE_UP, onMouseUp);
      App.instance.removeEventListener(MouseEvent.MOUSE_MOVE, onMouseMove);
      resizeControl.removeEventListener(ResizeControl.RESIZE_MOVE, onResizeControlChange);
      resizeControl.removeEventListener(ResizeControl.RESIZE_END, onReziseControlEnd);

      for each (var btn:Button in [hideShowBtn, lockBtn, resizeBtn, reloadBtn, closeBtn]) {
        btn.dispose();
      }

      loader.unload();
    }

    private function onMouseDown(event:MouseEvent):void {
      if (isDragging)
        return;

      isDragging = true;
      startDrag(false, new Rectangle(
            0,
            HANGAR_TOP_OFFSET,
            App.appWidth - content.width,
            App.appHeight - content.height - HANGAR_TOP_OFFSET - HANGAR_BOTTOM_OFFSET
          ));
    }

    private function onMouseMove(event:MouseEvent):void {
      if (hideShowButtonDownPosition != null) {
        var dx:Number = event.stageX - hideShowButtonDownPosition.x;
        var dy:Number = event.stageY - hideShowButtonDownPosition.y;

        if (Math.sqrt(dx * dx + dy * dy) > 10 && isContentHidden && !isLocked) {
          hideShowButtonDownPosition = null;
          isDragging = true;
          startDrag(false, new Rectangle(
                0,
                HANGAR_TOP_OFFSET + controlPanel.height + 3,
                App.appWidth - loader.width,
                App.appHeight - loader.height - HANGAR_TOP_OFFSET - HANGAR_BOTTOM_OFFSET
              ));
        }
      }
    }

    private function onMouseUp(event:MouseEvent):void {

      if (hideShowButtonDownPosition != null) {
        hideShowButtonDownPosition = null;

        if (event.target == hideShowBtn) {
          onHideShowButtonClick();
        }
      }

      if (!isDragging)
        return;

      x = Math.round(x);
      y = Math.round(y);

      isDragging = false;
      stopDrag();
    }

    private function onHideShowButtonMouseDown(event:MouseEvent):void {
      hideShowButtonDownPosition = new Point(event.stageX, event.stageY);
    }

    private function onHideShowButtonClick():void {
      isContentHidden = !isContentHidden;
      hideShowBtn.isShow = !isContentHidden;
      content.visible = !isContentHidden;

      if (resizeControl.active) {
        resizeControl.active = false;
      }

      updateButtonsVisibility();
    }

    private function onResizeButtonClick(event:MouseEvent):void {
      resizeControl.active = !resizeControl.active;
    }

    private function onLockButtonClick(event:MouseEvent):void {
      isLocked = !isLocked;

      if (resizeControl.active) {
        resizeControl.active = false;
      }

      content.mouseEnabled = !isLocked;
      content.mouseChildren = !isLocked;
      updateButtonsVisibility();
    }

    private function updateButtonsVisibility():void {
      for each (var value:Button in [resizeBtn, reloadBtn, closeBtn]) {
        value.visible = !isContentHidden && !isLocked;
      }

      lockBtn.visible = !isContentHidden;
      controlPanel.layout();
    }

    private function onReloadButtonClick(event:MouseEvent):void {
      dispatchEvent(new Event(REQUEST_RELOAD));
    }

    private function onCloseButtonClick(event:MouseEvent):void {
      dispatchEvent(new Event(REQUEST_CLOSE));
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
      var k:Number = targetWidth / contentWidth;
      content.scaleX = k;
      content.scaleY = k;

      if (content.width != contentWidth / App.appScale || content.height != contentHeight / App.appScale) {
        var graphics:Graphics = content.graphics;
        graphics.clear();
        graphics.beginFill(0x000000, 0);
        graphics.drawRect(0, 0, contentWidth, contentHeight);
        graphics.endFill();
      }
    }

    private function updateResizeControl():void {
      resizeControl.contentWidth = contentWidth * content.scaleX;
      resizeControl.contentHeight = contentHeight * content.scaleY;
    }
  }
}