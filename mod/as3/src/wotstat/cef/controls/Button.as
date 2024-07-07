package wotstat.cef.controls {
  import flash.display.SimpleButton;
  import flash.events.MouseEvent;

  public class Button extends SimpleButton {
    private const border:uint = 0xffffff4d;

    private var clickFunction:Function;

    public function Button(width:Number, corner:Number = 10, drawContent:Function = null, clickFunction:Function = null) {
      downState = new ButtonDisplayState(0x6969694a, border, width, corner, drawContent);
      overState = new ButtonDisplayState(0xffffff1a, border, width, corner, drawContent);
      upState = new ButtonDisplayState(0x6969690f, border, width, corner, drawContent);
      hitTestState = new ButtonDisplayState(0x00000000, border, width, corner);
      useHandCursor = true;
      if (clickFunction != null) {
        this.clickFunction = clickFunction;
        addEventListener(MouseEvent.CLICK, clickFunction);
      }
    }

    public function dispose():void {
      removeEventListener(MouseEvent.CLICK, clickFunction);
    }

    public function redraw():void {
      ButtonDisplayState(downState).draw();
      ButtonDisplayState(overState).draw();
      ButtonDisplayState(upState).draw();
      ButtonDisplayState(hitTestState).draw();
    }
  }
}


import flash.display.Sprite;

class ButtonDisplayState extends Sprite {
  private var background:uint;
  private var border:uint;
  private var size:Number;
  private var radius:Number;
  private var drawContent:Function;

  public function ButtonDisplayState(background:uint, border:uint, size:Number, radius:Number = 10, drawContent:Function = null) {
    this.background = background;
    this.border = border;
    this.size = size;
    this.radius = radius;
    this.drawContent = drawContent;
    draw();
  }

  function draw():void {
    graphics.clear();
    graphics.beginFill(background >>> 8, Number(background & 0xFF) / 255);
    graphics.lineStyle(1.5, border >>> 8, Number(border & 0xFF) / 255);
    graphics.drawRoundRect(0, 0, size, size, radius);
    graphics.endFill();

    if (drawContent != null)
      drawContent(graphics, size, radius);
  }
}