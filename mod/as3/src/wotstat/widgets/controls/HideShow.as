package wotstat.widgets.controls {
  import flash.display.Graphics;

  public class HideShow extends Button {
    private const WIDTH:int = 19;
    private const X_OFFSET:int = 6;

    private var _isShow:Boolean = true;

    public function get isShow():Boolean {
      return _isShow;
    }

    public function set isShow(value:Boolean):void {
      _isShow = value;
      redraw();
    }

    public function HideShow(clicked:Function = null) {
      super(WIDTH, 10, drawContent, clicked);
    }

    private function drawContent(graphics:Graphics, size:Number, radius:Number):void {
      graphics.lineStyle(1.5, 0xffffff);

      if (_isShow) {
        graphics.moveTo(X_OFFSET, WIDTH / 2);
        graphics.lineTo(size - X_OFFSET, WIDTH / 2);
      }
      else {
        graphics.moveTo(X_OFFSET, WIDTH / 2);
        graphics.lineTo(size - X_OFFSET, WIDTH / 2);

        graphics.moveTo(WIDTH / 2, X_OFFSET);
        graphics.lineTo(WIDTH / 2, size - X_OFFSET);
      }
    }
  }
}