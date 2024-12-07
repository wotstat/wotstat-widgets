class HANGAR_INSETS {
  public static const TOP:int = 53;
  public static const BOTTOM:int = 35;
  public static const LEFT:int = 0;
  public static const RIGHT:int = 0;
}

package wotstat.widgets {

  import flash.display.Sprite;
  import flash.events.MouseEvent;
  import flash.geom.Rectangle;
  import wotstat.widgets.controls.Lock;
  import wotstat.widgets.controls.Resize;
  import wotstat.widgets.controls.ResizeControl;
  import flash.events.Event;
  import scaleform.clik.events.ResizeEvent;
  import wotstat.widgets.controls.HideShow;
  import wotstat.widgets.controls.Button;
  import flash.geom.Point;
  import flash.utils.ByteArray;
  import flash.display.Loader;
  import flash.display.Graphics;
  import flash.display.Bitmap;
  import flash.display.PixelSnapping;
  import flash.display.DisplayObject;
  import wotstat.widgets.common.MoveEvent;
  import wotstat.widgets.common.POSITION_MODE;
  import wotstat.widgets.common.LAYER;
  import wotstat.widgets.controls.Points;


  public class DraggableWidget extends Sprite {
    public static const REQUEST_RESIZE:String = "REQUEST_RESIZE";
    public static const REQUEST_RESOLUTION:String = "REQUEST_RESOLUTION";
    public static const MOVE_WIDGET:String = "MOVE_WIDGET";
    public static const LOCK_WIDGET:String = "LOCK_WIDGET";
    public static const UNLOCK_WIDGET:String = "UNLOCK_WIDGET";
    public static const HIDE_WIDGET:String = "HIDE_WIDGET";
    public static const SHOW_WIDGET:String = "SHOW_WIDGET";

    private const HANGAR_HEADER_HEIGHT:int = 35;

    private var _wid:int = 0;

    private var hideShowBtn:HideShow = new HideShow();
    private var lockBtn:Lock = new Lock(onLockButtonClick);
    private var resizeBtn:Resize = new Resize(onResizeButtonClick);
    private var contextMenuBtn:Points = new Points(showContextMenu);

    private var controlPanel:ControlsPanel = new ControlsPanel();
    private var allowInteraction:Boolean = true;
    private const resizeControl:ResizeControl = new ResizeControl(0, 0);

    // Target width by resize control in POINTS
    private var targetWidth:Number = -1;
    private var targetHeight:Number = -1;

    private var hideShowButtonDownPosition:Point = null;
    private var isDragging:Boolean = false;
    private var isContentHidden:Boolean = false;
    private var isReadyToClearData:Boolean = false;
    private var isControlsAlwaysHidden:Boolean = false;
    private var isTopPlan:Boolean = false;
    private var hangarOnly:Boolean = false;
    private var layer:String = LAYER.DEFAULT;
    private var positionMode:String = POSITION_MODE.SAME;
    private var unlimitedSize:Boolean = false;
    private var insets:Object = {
        'top': 0,
        'right': 0,
        'bottom': 0,
        'left': 0
      };
    private var _isLocked:Boolean = false;
    private var lastInterfaceScale:Number = 0;

    // CONTENT == Browser Image in real PIXELS
    private var contentWidth:Number = 0;
    private var contentHeight:Number = 0;
    private var content:Sprite = new Sprite();
    private var loader:Loader = new Loader();
    private var dragArea:Sprite = new Sprite();

    public var isInBattle:Boolean = false;

    private function get insetHorizontalOffset():Number {
      return targetWidth / (1 - insets.left / 100 - insets.right / 100) - targetWidth;
    }

    private function get insetVerticalOffset():Number {
      return (targetWidth + insetHorizontalOffset) * (insets.top + insets.bottom) / 100;
    }

    private function get targetContentWidth():Number {
      if (targetWidth < 0)
        return Math.round(targetWidth * App.appScale);
      return Math.round((targetWidth + insetHorizontalOffset) * App.appScale);
    }

    private function get targetContentHeight():Number {
      if (targetHeight < 0)
        return Math.round(targetHeight * App.appScale);
      return Math.round((targetHeight + insetVerticalOffset) * App.appScale);
    }

    public function get wid():int {
      return _wid;
    }

    public function get isLocked():Boolean {
      return _isLocked;
    }

    public function get isHidden():Boolean {
      return isContentHidden;
    }

    public function DraggableWidget(wid:int, width:int, height:int, x:int, y:int,
        isHidden:Boolean,
        isLocked:Boolean,
        isControlsAlwaysHidden:Boolean,
        isInBattle:Boolean,
        positionMode:String,
        layer:String):void {
      super();
      name = "DraggableWidget_" + wid;
      content.name = "Content_" + wid;
      controlPanel.name = "ControlPanel_" + wid;
      loader.name = "WidgetContentLoader_" + wid;
      this.positionMode = positionMode;
      this.layer = layer;

      _wid = wid;
      this.isInBattle = isInBattle;

      addChild(dragArea);
      addChild(content);
      content.addChild(loader);

      controlPanel
        .addButton(hideShowBtn)
        .addButton(lockBtn)
        .addButton(resizeBtn)
        .addButton(contextMenuBtn)
        .layout();

      addChild(controlPanel);
      controlPanel.y = -controlPanel.height - 3;

      var hitAreaSprite:Sprite = new Sprite();
      addChild(hitAreaSprite);
      hitArea = hitAreaSprite;

      content.mouseEnabled = false;
      content.mouseChildren = false;

      targetWidth = width;
      if (height > 0)
        targetHeight = height;

      var localPosition:Point = globalToLocalPosition(x, y);
      this.x = x >= 0 ? localPosition.x : (App.appWidth - width) / 2;
      this.y = y >= 0 ? localPosition.y : (App.appHeight - height - 100) / 2;

      addChild(resizeControl);

      dragArea.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDown);
      App.instance.addEventListener(MouseEvent.MOUSE_DOWN, onAppMouseDown);
      App.instance.addEventListener(MouseEvent.MOUSE_UP, onAppMouseUp);
      App.instance.addEventListener(MouseEvent.MOUSE_MOVE, onAppMouseMove);
      App.instance.addEventListener(Event.RESIZE, onAppResize);
      resizeControl.addEventListener(ResizeControl.RESIZE_MOVE, onResizeControlChange);
      resizeControl.addEventListener(ResizeControl.RESIZE_END, onResizeControlEnd);
      loader.contentLoaderInfo.addEventListener(Event.COMPLETE, onLoaderComplete);
      hideShowBtn.addEventListener(MouseEvent.MOUSE_DOWN, onHideShowButtonMouseDown);

      setHidden(isHidden);
      setLocked(isLocked);
      setControlsAlwaysHidden(isControlsAlwaysHidden);
      updateControlsVisibility();
    }

    public function dispose():void {
      dragArea.removeEventListener(MouseEvent.MOUSE_DOWN, onMouseDown);
      App.instance.removeEventListener(MouseEvent.MOUSE_DOWN, onAppMouseDown);
      App.instance.removeEventListener(MouseEvent.MOUSE_UP, onAppMouseUp);
      App.instance.removeEventListener(MouseEvent.MOUSE_MOVE, onAppMouseMove);
      resizeControl.removeEventListener(ResizeControl.RESIZE_MOVE, onResizeControlChange);
      resizeControl.removeEventListener(ResizeControl.RESIZE_END, onResizeControlEnd);
      loader.contentLoaderInfo.removeEventListener(Event.COMPLETE, onLoaderComplete);
      hideShowBtn.removeEventListener(MouseEvent.MOUSE_DOWN, onHideShowButtonMouseDown);

      for each (var btn:Button in [hideShowBtn, lockBtn, resizeBtn, contextMenuBtn]) {
        btn.dispose();
      }

      loader.unload();
    }

    public function setFrame(width:uint, height:uint, data:ByteArray):void {

      if (width != targetContentWidth && !resizeControl.isResizing) {
        trace("[DW] Skip frame with width " + width + "!=" + targetContentWidth);
        return;
      }

      loader.unload();
      loader.loadBytes(data);

      contentWidth = width;
      contentHeight = height;

      updateImageScale();
      updateResizeControl();
    }

    public function setResizeMode(full:Boolean):void {
      trace("[DW] Set resize mode " + full);
      resizeControl.fullResize = full;
      if (!full)
        targetHeight = -1;
      dispatchEvent(new ResizeEvent(REQUEST_RESOLUTION, targetContentWidth, targetContentHeight));
      dispatchEvent(new ResizeEvent(REQUEST_RESIZE, targetWidth, targetHeight));
    }

    public function setHangarOnly(value:Boolean):void {
      hangarOnly = value;
    }

    public function setBattleInteractiveMode(isVisible:Boolean):void {
      setResizing(false);
      allowInteraction = isVisible;
      updateControlsVisibility();

      if (!isVisible) {
        stopDrag();
        isDragging = false;
        App.contextMenuMgr.hide();
      }
    }

    public function onInterfaceScaleChanged(scale:Number):void {
      if (resizeControl.fullResize) {
        content.scaleX = 1 / App.appScale;
        content.scaleY = 1 / App.appScale;
        updateImagePosition();
      }

      updateImageScale();
      updateResizeControl();

      dispatchEvent(new ResizeEvent(REQUEST_RESOLUTION, targetContentWidth, targetContentHeight));
      dispatchEvent(new ResizeEvent(REQUEST_RESIZE, targetWidth, targetHeight));

      if (lastInterfaceScale != 0)
        fixPosition();

      lastInterfaceScale = scale;

    }

    public function setResizing(enabled:Boolean):void {
      if (resizeControl.active == enabled)
        return;

      resizeControl.active = enabled;
      resizeBtn.state = enabled ? 1 : 0;
    }

    public function setLocked(value:Boolean):void {
      if (_isLocked == value)
        return;

      _isLocked = value;

      setResizing(false);
      lockBtn.state = isLocked ? 1 : 0;
      dragArea.mouseEnabled = !_isLocked;
      updateButtonsVisibility();
    }

    public function setUnlimitedSize(value:Boolean):void {
      this.unlimitedSize = value;
      resizeControl.unlimitedSize = value;
    }

    public function setInsets(top:Number, right:Number, bottom:Number, left:Number):void {
      this.insets = {
          'left': left,
          'top': top,
          'right': right,
          'bottom': bottom
        };

      trace("[DW] Set insets " + top + "x" + right + "x" + bottom + "x" + left);
      dispatchEvent(new ResizeEvent(REQUEST_RESOLUTION, targetContentWidth, targetContentHeight));
      updateImageScale();
      updateImagePosition();
    }

    public function setReadyToClearData(value:Boolean):void {
      isReadyToClearData = value;
    }

    public function setControlsAlwaysHidden(value:Boolean):void {
      setResizing(false);
      isControlsAlwaysHidden = value;
      updateControlsVisibility();
    }

    public function setTopPlan(value:Boolean):void {
      isTopPlan = value;
    }

    public function setLayer(value:String):void {
      var global:Point = globalPosition();

      layer = value;

      var localPosition:Point = globalToLocalPosition(global.x, global.y);
      x = localPosition.x;
      y = localPosition.y;

      trace("[DW] Set layer");
      fixPosition();
    }

    public function getLayer():String {
      return layer;
    }

    public function setPositionMode(mode:String):void {
      positionMode = mode;
    }

    public function setPosition(x:int, y:int):void {
      this.x = x;
      this.y = y;

      trace("[DW] Set position");
      fixPosition();
    }

    private function setHidden(value:Boolean):void {
      if (isContentHidden == value)
        return;

      isContentHidden = value;
      hideShowBtn.isShow = !value;
      content.visible = !value;
      dragArea.visible = !value;

      setResizing(false);
      setControlsAlwaysHidden(false);

      updateButtonsVisibility();
    }

    private function onLoaderComplete(event:Event):void {
      (loader.content as Bitmap).pixelSnapping = PixelSnapping.ALWAYS;
      (loader.content as Bitmap).smoothing = false;
    }

    private function showContextMenu(event:MouseEvent):void {
      var ctx:Object = {
          'wid': _wid,
          'isLocked': _isLocked,
          'isInResizing': resizeControl.active,
          'isReadyToClearData': isReadyToClearData,
          'isHidden': isContentHidden,
          'isInBattle': isInBattle,
          'isControlsAlwaysHidden': isControlsAlwaysHidden,
          'isTopPlan': isTopPlan,
          'layer': layer,
          'positionMode': positionMode,
          'hangarOnly': hangarOnly
        };

      App.contextMenuMgr.show('WOTSTAT_WIDGET_CONTEXT_MENU', null, ctx);
    }

    private function onMouseDown(event:MouseEvent):void {
      if (isDragging || !allowInteraction)
        return;

      if (!event.buttonDown) {
        showContextMenu(event);
        return;
      }

      isDragging = true;
      startDrag(false, getDraggingRectangle(!isHidden, isInBattle));
    }

    private function onAppMouseDown(event:MouseEvent):void {
      if (event.buttonDown)
        return;

      if (isInBattle && !(allowInteraction && isControlsAlwaysHidden))
        return;

      if (!isInBattle && !(isLocked && !isHidden))
        return;

      var stageX:Number = event.stageX / App.appScale;
      var stageY:Number = event.stageY / App.appScale;
      if (!dragArea.getBounds(App.instance.stage).contains(stageX, stageY))
        return;

      var clickPoint:Point = new Point(event.stageX, event.stageY);
      var objectsUnderPoint:Array = stage.getObjectsUnderPoint(clickPoint);

      if (objectsUnderPoint.length == 0)
        return;

      var topMostObject:DisplayObject = objectsUnderPoint[objectsUnderPoint.length - 1];
      if (topMostObject == this || this.contains(topMostObject))
        showContextMenu(event);

    }

    private function onAppMouseMove(event:MouseEvent):void {
      if (!allowInteraction)
        return;

      if (hideShowButtonDownPosition != null) {
        var dx:Number = event.stageX - hideShowButtonDownPosition.x;
        var dy:Number = event.stageY - hideShowButtonDownPosition.y;

        if (Math.sqrt(dx * dx + dy * dy) > 5 && isContentHidden && !_isLocked) {
          hideShowButtonDownPosition = null;
          isDragging = true;
          x += dx;
          y += dy;
          startDrag(false, getDraggingRectangle(!isHidden, isInBattle));
        }
      }
    }

    private function onAppMouseUp(event:MouseEvent):void {
      if (!allowInteraction)
        return;

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

      var position:Point = globalPosition();
      dispatchEvent(new MoveEvent(MOVE_WIDGET, position.x, position.y));
    }

    private function onHideShowButtonMouseDown(event:MouseEvent):void {
      hideShowButtonDownPosition = new Point(event.stageX, event.stageY);
    }

    private function onHideShowButtonClick():void {
      setHidden(!isContentHidden);
      dispatchEvent(isContentHidden ? new Event(HIDE_WIDGET) : new Event(SHOW_WIDGET));
    }

    private function onResizeButtonClick(event:MouseEvent):void {
      setResizing(!resizeControl.active);
    }

    private function onLockButtonClick(event:MouseEvent):void {
      setLocked(!_isLocked);
      dispatchEvent(_isLocked ? new Event(UNLOCK_WIDGET) : new Event(LOCK_WIDGET));
    }

    private function updateButtonsVisibility():void {
      for each (var value:Button in [resizeBtn, contextMenuBtn]) {
        value.visible = !isContentHidden && !_isLocked;
      }

      lockBtn.visible = !isContentHidden;
      controlPanel.layout();
    }

    private function updateControlsVisibility():void {
      var visible:Boolean = !isControlsAlwaysHidden && (allowInteraction || !isInBattle);

      controlPanel.visible = visible;
      controlPanel.mouseEnabled = visible;
      controlPanel.mouseChildren = visible;
    }

    private function onResizeControlChange(event:ResizeEvent):void {
      trace("[DW] Resize control changed " + event.scaleX + "x" + event.scaleY);
      targetWidth = event.scaleX;
      targetHeight = event.scaleY;
      updateImageScale();
      updateResizeControl();
    }

    private function onResizeControlEnd(event:Event):void {
      targetWidth = Math.round(targetWidth);
      targetHeight = Math.round(targetHeight);
      trace("[DW] Resize control end " + targetWidth + "x" + targetHeight);
      updateImageScale();

      resizeControl.contentWidth = targetWidth;
      resizeControl.contentHeight = targetHeight >= 0 ?
        targetHeight :
        contentHeight * content.scaleY - insetVerticalOffset;

      dispatchEvent(new ResizeEvent(REQUEST_RESOLUTION, targetContentWidth, targetContentHeight));
      dispatchEvent(new ResizeEvent(REQUEST_RESIZE, targetWidth, targetHeight));
    }

    private function globalPosition():Point {
      var position:Point = new Point(x, y);

      if (layer == LAYER.DEFAULT && !isInBattle) {
        position.x += HANGAR_INSETS.LEFT;
        position.y += HANGAR_INSETS.TOP;
      }

      return position;
    }

    private function globalToLocalPosition(x:Number, y:Number):Point {
      var position:Point = new Point(x, y);

      if (layer == LAYER.DEFAULT && !isInBattle) {
        position.x -= HANGAR_INSETS.LEFT;
        position.y -= HANGAR_INSETS.TOP;
      }

      return position;
    }

    private function onAppResize(event:Event):void {
      if (isDragging) {
        stopDrag();
        isDragging = false;
      }

      trace("[DW] App resize");
      fixPosition();
    }

    private function getDraggingRectangle(full:Boolean, battle:Boolean = false):Rectangle {

      var isTopLayer:Boolean = layer == LAYER.TOP;
      var controlOffset:int = controlPanel.height + 2;
      var right:Number = App.appWidth - dragArea.width;
      var bottom:Number = App.appHeight - dragArea.height;
      var cRight:Number = App.appWidth - controlPanel.height;
      var cBottom:Number = App.appHeight - controlPanel.height;

      trace("[DW] Get dragging rectangle " + App.appWidth + "x" + App.appHeight + " " + dragArea.width + "x" + dragArea.height);

      if (full && isTopLayer)
        return new Rectangle(0, 0, right, bottom);

      if (!full && isTopLayer)
        return new Rectangle(0, controlOffset, cRight, cBottom);

      if (full && !battle)
        return new Rectangle(0, 0, right, bottom - HANGAR_INSETS.BOTTOM - HANGAR_INSETS.TOP);

      if (!full && !battle)
        return new Rectangle(
            0,
            HANGAR_HEADER_HEIGHT + controlOffset,
            cRight,
            cBottom - HANGAR_HEADER_HEIGHT - HANGAR_INSETS.BOTTOM - HANGAR_INSETS.TOP
          );

      if (full && battle)
        return new Rectangle(0, 0, right, bottom);

      if (!full && battle)
        return new Rectangle(0, controlOffset, cRight, cBottom);

      return new Rectangle(0, 0, App.appWidth, App.appHeight);
    }

    public function fixPosition():void {
      x = Math.round(x);
      y = Math.round(y);

      var oldX:Number = x;
      var oldY:Number = y;

      var rect:Rectangle = getDraggingRectangle(!isHidden, isInBattle);

      if (x < rect.x)
        x = rect.x;
      if (y < rect.y)
        y = rect.y;
      if (x > rect.width + rect.x)
        x = rect.width + rect.x;
      if (y > rect.height + rect.y)
        y = rect.height + rect.y;

      if (x != oldX || y != oldY) {
        trace("[DW] Fix position to " + x + "x" + y + " from " + oldX + "x" + oldY + " in " + rect);
        var position:Point = globalPosition();
        dispatchEvent(new MoveEvent(MOVE_WIDGET, position.x, position.y));
      }
    }


    private function updateImagePosition():void {
      loader.x = -Math.round(contentWidth * insets.left / 100);
      loader.y = -Math.round(contentWidth * insets.top / 100);
    }

    private function updateImageScale():void {
      if (!resizeControl.fullResize) {
        var k:Number = (targetWidth + insetHorizontalOffset) / contentWidth;
        content.scaleX = k;
        content.scaleY = k;
        updateImagePosition();
      }

      if (contentWidth == 0 || contentHeight == 0)
        return;

      var scaledWidth:Number = targetWidth;
      var scaledHeight:Number = targetHeight > 0 ?
        targetHeight :
        targetWidth *
        (contentHeight * content.scaleY - insetVerticalOffset) /
        (contentWidth * content.scaleX - insetHorizontalOffset);

      if (dragArea.width != scaledWidth || dragArea.height != scaledHeight) {
        var graphics:Graphics = dragArea.graphics;
        graphics.clear();
        graphics.beginFill(0x00ffff, 0);
        graphics.drawRect(0, 0, scaledWidth, scaledHeight);
        graphics.endFill();
      }

      updateImagePosition();

    }

    private function updateResizeControl():void {
      resizeControl.contentWidth = contentWidth * content.scaleX - insetHorizontalOffset;
      resizeControl.contentHeight = contentHeight * content.scaleY - insetVerticalOffset;
    }
  }
}