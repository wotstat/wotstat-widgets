package wotstat.cef.controls {
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
    private const MAX_WIDTH:int = 400;
    private const MIN_WIDTH:int = 105;

    private var control:Sprite;
    private var hitArea:Sprite;
    private var _active:Boolean = false;

    private var _contentWidth:Number = 0;
    private var _contentHeight:Number = 0;

    private var isDragging:Boolean = false;
    private var controlHeight:int = 0;

    public function set active(value:Boolean):void {
      _active = value;
      visible = value;
      if (!value) {
        control.stopDrag();
      }
    }

    public function get active():Boolean {
      return _active;
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
      control = new Sprite();
      control.x = x;
      control.y = y;
      controlHeight = CONTROL_HEIGHT;
      control.useHandCursor = true;
      visible = false;

      hitArea = new Sprite();
      control.addChild(hitArea);
      control.hitArea = hitArea;
      hitArea.useHandCursor = true;

      draw();

      control.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDownHandler);
      App.instance.addEventListener(MouseEvent.MOUSE_UP, onMouseUpHandler);
      App.instance.addEventListener(MouseEvent.MOUSE_MOVE, onMouseMoveHandler);

      addChild(control);
    }

    private function draw():void {
      var graphics:Graphics = control.graphics;
      graphics.clear();
      graphics.beginFill(0xffffff, 1);
      graphics.drawRoundRect(0, 0, CONTROL_WIDTH, controlHeight, 5);
      graphics.endFill();

      var hitGraphics:Graphics = hitArea.graphics;
      hitGraphics.clear();
      hitGraphics.beginFill(0xffffff, 0);
      hitGraphics.drawRect(0, 0, 20, controlHeight + 5);
      hitGraphics.endFill();

      hitArea.x = -(20 - CONTROL_WIDTH) / 2;
      hitArea.y = -2.5;
    }

    private function drawFrame():void {
      graphics.clear();
      graphics.lineStyle(1.5, 0xbbbbbb, 1, false, LineScaleMode.NORMAL, CapsStyle.ROUND, JointStyle.ROUND);
      graphics.drawRect(0, 0, control.x + CONTROL_WIDTH / 2, contentHeight);
    }

    private function onMouseDownHandler():void {
      if (!_active || isDragging) {
        return;
      }

      isDragging = true;
      control.startDrag(true, new Rectangle(MIN_WIDTH - CONTROL_WIDTH / 2 + 1, control.y, MAX_WIDTH - MIN_WIDTH, 0));
    }

    private function onMouseUpHandler():void {
      if (!isDragging) {
        return;
      }

      isDragging = false;
      control.stopDrag();
      dispatchEvent(new ResizeEvent(RESIZE_MOVE, control.x + CONTROL_WIDTH / 2, 0));
      dispatchEvent(new Event(RESIZE_END));
      resetPosition();
    }

    private function onMouseMoveHandler():void {
      if (isDragging) {
        drawFrame();
        dispatchEvent(new ResizeEvent(RESIZE_MOVE, control.x + CONTROL_WIDTH / 2, 0));
      }
    }

    private function resetPosition():void {
      if (isDragging) {
        control.stopDrag();
        control.y = _contentHeight / 2 - controlHeight / 2;
        control.startDrag(true, new Rectangle(MIN_WIDTH - CONTROL_WIDTH / 2 + 1, control.y, MAX_WIDTH - MIN_WIDTH, 0));
        return;
      }

      control.x = _contentWidth - 2.5;
      control.y = _contentHeight / 2 - controlHeight / 2;
      drawFrame();
    }

  }
}