package wotstat.widgets.controls {
  import flash.display.Sprite;
  import flash.display.Graphics;
  import flash.geom.Rectangle;
  import flash.events.Event;
  import flash.events.MouseEvent;
  import scaleform.clik.events.ResizeEvent;
  import flash.display.CapsStyle;
  import flash.display.JointStyle;
  import flash.display.LineScaleMode;

  public class ResizeControl extends Sprite {
    public static const RESIZE_MOVE:String = "RESIZE_MOVE";
    public static const RESIZE_END:String = "RESIZE_END";

    private const CONTROL_WIDTH:int = 5;
    private const CONTROL_HEIGHT:int = 40;
    private const FULL_CONTROL_SIZE:int = 15;
    private const MAX_WIDTH:int = 400;
    private const MIN_WIDTH:int = 110;

    private var _active:Boolean = false;

    private var verticalControl:Sprite = new Sprite();
    private var verticalHitArea:Sprite = new Sprite();

    private var fullControl:Sprite = new Sprite();
    private var fullHitArea:Sprite = new Sprite();

    private var _fullResize:Boolean = false;
    private var _contentWidth:Number = 0;
    private var _contentHeight:Number = 0;

    private var isDragging:Boolean = false;
    private var controlHeight:int = 0;

    public function set active(value:Boolean):void {
      _active = value;
      visible = value;
      if (!value) {
        verticalControl.stopDrag();
      }
    }

    public function get active():Boolean {
      return _active;
    }

    public function get fullResize():Boolean {
      return _fullResize;
    }

    public function set fullResize(value:Boolean):void {
      _fullResize = value;
      verticalControl.visible = !_fullResize;
      fullControl.visible = _fullResize;
    }

    public function get contentWidth():Number {
      return _contentWidth;
    }

    public function set contentWidth(value:Number):void {
      _contentWidth = value;
      resetPosition();
    }

    public function get contentHeight():Number {
      return _contentHeight;
    }

    public function set contentHeight(value:Number):void {
      _contentHeight = value;
      var targetHeight:Number = Math.max(15, Math.min(40, value - 20));
      if (controlHeight != targetHeight) {
        controlHeight = targetHeight;
        draw();
      }
      resetPosition();
    }

    public function get isResizing():Boolean {
      return isDragging;
    }

    public function ResizeControl(x:Number, y:Number) {

      controlHeight = CONTROL_HEIGHT;

      verticalControl.addChild(verticalHitArea);
      verticalControl.hitArea = verticalHitArea;

      fullControl.addChild(fullHitArea);
      fullControl.hitArea = fullHitArea;

      draw();

      fullControl.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDownHandler);
      verticalControl.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDownHandler);
      App.instance.addEventListener(MouseEvent.MOUSE_UP, onMouseUpHandler);
      App.instance.addEventListener(MouseEvent.MOUSE_MOVE, onMouseMoveHandler);

      addChild(verticalControl);
      addChild(fullControl);
      visible = false;

      verticalControl.visible = false;
      fullControl.visible = false;
    }

    private function draw():void {
      var vGraph:Graphics = verticalControl.graphics;
      vGraph.clear();
      vGraph.beginFill(0xffffff, 1);
      vGraph.drawRoundRect(0, 0, CONTROL_WIDTH, controlHeight, 5);
      vGraph.endFill();

      var hGraph:Graphics = verticalHitArea.graphics;
      hGraph.clear();
      hGraph.beginFill(0xffffff, 0);
      hGraph.drawRect(0, 0, 20, controlHeight + 5);
      hGraph.endFill();

      verticalHitArea.x = -(20 - CONTROL_WIDTH) / 2;
      verticalHitArea.y = -2.5;

      var fGraph:Graphics = fullControl.graphics;
      fGraph.clear();
      fGraph.lineStyle(5, 0xffffff, 1, false, LineScaleMode.NORMAL, CapsStyle.ROUND, JointStyle.ROUND);
      fGraph.moveTo(-FULL_CONTROL_SIZE, 0);
      fGraph.lineTo(0, 0);
      fGraph.lineTo(0, -FULL_CONTROL_SIZE);

      var fhGraph:Graphics = fullHitArea.graphics;
      fhGraph.clear();
      fhGraph.beginFill(0xffffff, 0);
      fhGraph.drawRect(-FULL_CONTROL_SIZE - 5, -10, FULL_CONTROL_SIZE + 15, 20);
      fhGraph.drawRect(-10, -FULL_CONTROL_SIZE - 5, 20, FULL_CONTROL_SIZE - 5);
      fhGraph.endFill();
    }

    private function drawFrame():void {
      graphics.clear();
      graphics.lineStyle(1.5, 0xbbbbbb, 1, false, LineScaleMode.NORMAL, CapsStyle.ROUND, JointStyle.ROUND);
      if (_fullResize)
        graphics.drawRect(0, 0, fullControl.x, fullControl.y);
      else
        graphics.drawRect(0, 0, verticalControl.x + CONTROL_WIDTH / 2, contentHeight);
    }

    private function onMouseDownHandler():void {
      if (!_active || isDragging) {
        return;
      }

      isDragging = true;
      if (_fullResize)
        fullControl.startDrag(true, new Rectangle(MIN_WIDTH, 50, 500, 500));
      else
        verticalControl.startDrag(true, new Rectangle(MIN_WIDTH - CONTROL_WIDTH / 2 + 1, verticalControl.y, MAX_WIDTH - MIN_WIDTH, 0));
    }

    private function onMouseUpHandler():void {
      if (!isDragging) {
        return;
      }

      isDragging = false;

      if (_fullResize) {
        fullControl.stopDrag();
        dispatchEvent(new ResizeEvent(RESIZE_MOVE, fullControl.x, fullControl.y));
      }
      else {
        verticalControl.stopDrag();
        dispatchEvent(new ResizeEvent(RESIZE_MOVE, verticalControl.x + CONTROL_WIDTH / 2, -1));
      }
      dispatchEvent(new Event(RESIZE_END));
      resetPosition();
    }

    private function onMouseMoveHandler():void {
      if (isDragging) {
        drawFrame();
        if (_fullResize) {
          dispatchEvent(new ResizeEvent(RESIZE_MOVE, fullControl.x, fullControl.y));
        }
        else
          dispatchEvent(new ResizeEvent(RESIZE_MOVE, verticalControl.x + CONTROL_WIDTH / 2, -1));

      }
    }

    private function resetPosition():void {
      if (isDragging) {
        if (!_fullResize) {
          verticalControl.stopDrag();
          verticalControl.y = _contentHeight / 2 - controlHeight / 2;
          verticalControl.startDrag(true, new Rectangle(MIN_WIDTH - CONTROL_WIDTH / 2 + 1, verticalControl.y, MAX_WIDTH - MIN_WIDTH, 0));
        }
      }
      else {
        verticalControl.x = _contentWidth - 2.5;
        verticalControl.y = _contentHeight / 2 - controlHeight / 2;

        fullControl.x = _contentWidth;
        fullControl.y = _contentHeight;
      }

      drawFrame();
    }

  }
}