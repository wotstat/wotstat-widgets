package wotstat.cef.controls {
  import flash.display.Sprite;
  import flash.events.EventDispatcher;
  import flash.display.Graphics;
  import flash.geom.Rectangle;
  import flash.events.Event;
  import flash.events.MouseEvent;
  import net.wg.data.constants.Cursors;
  import scaleform.clik.events.ResizeEvent;

  public class ResizeControl extends EventDispatcher {
    public static const RESIZE_MOVE:String = "RESIZE_MOVE";
    public static const RESIZE_END:String = "RESIZE_END";

    private const CONTROL_WIDTH:int = 5;

    private var _height:int = 0;
    private var _target:Sprite;
    private var _hitArea:Sprite;
    private var _active:Boolean = false;
    private var isDragging:Boolean = false;

    private var _contentWidth:Number = 0;
    private var _contentHeight:Number = 0;


    public function get height():int {
      return _height;
    }

    public function set height(value:int):void {
      _height = value;
      draw();
    }

    public function get target():Sprite {
      return _target;
    }

    public function set active(value:Boolean):void {
      _active = value;
      _target.visible = value;
      if (!value) {
        _target.stopDrag();
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
      if (_height != targetHeight) {
        _height = targetHeight;
        draw();
      }
      resetPosition();
    }



    public function ResizeControl(height:int, x:Number, y:Number) {
      _target = new Sprite();
      _target.x = x;
      _target.y = y;
      _height = height;
      _target.visible = false;
      _target.useHandCursor = true;

      _hitArea = new Sprite();
      _target.addChild(_hitArea);
      _target.hitArea = _hitArea;

      draw();

      _target.addEventListener(MouseEvent.MOUSE_DOWN, onMouseDownHandler);
      App.instance.addEventListener(MouseEvent.MOUSE_UP, onMouseUpHandler);
      App.instance.addEventListener(MouseEvent.MOUSE_MOVE, onMouseMoveHandler);
    }

    private function draw():void {
      var graphics:Graphics = _target.graphics;
      graphics.clear();
      graphics.beginFill(0xffffff, 1);
      graphics.drawRoundRect(0, 0, CONTROL_WIDTH, _height, 5);
      graphics.endFill();

      var hitGraphics:Graphics = _hitArea.graphics;
      hitGraphics.clear();
      hitGraphics.beginFill(0xffffff, 0);
      hitGraphics.drawRect(0, 0, 20, height + 5);
      hitGraphics.endFill();

      _hitArea.x = -(20 - CONTROL_WIDTH) / 2;
      _hitArea.y = -2.5;
    }

    private function onMouseDownHandler():void {
      if (!_active || isDragging) {
        return;
      }

      isDragging = true;
      _target.startDrag(true, new Rectangle(80, _target.y, 320, 0));
    }

    private function onMouseUpHandler():void {
      if (!isDragging) {
        return;
      }

      isDragging = false;
      _target.stopDrag();
      dispatchEvent(new ResizeEvent(RESIZE_MOVE, _target.x + CONTROL_WIDTH / 2, 0));
      dispatchEvent(new Event(RESIZE_END));
      resetPosition();
    }

    private function onMouseMoveHandler():void {
      if (isDragging) {
        dispatchEvent(new ResizeEvent(RESIZE_MOVE, _target.x + CONTROL_WIDTH / 2, 0));
      }
    }

    private function resetPosition():void {
      if (isDragging) {
        _target.stopDrag();
        _target.y = _contentHeight / 2 - _height / 2;
        _target.startDrag(true, new Rectangle(80, _target.y, 320, 0));
        return;
      }

      _target.x = _contentWidth - 2.5;
      _target.y = _contentHeight / 2 - _height / 2;
    }

  }
}