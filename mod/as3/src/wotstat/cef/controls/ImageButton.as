package wotstat.cef.controls {
  import flash.display.Graphics;
  import flash.display.Bitmap;
  import net.wg.gui.components.controls.Image;
  import flash.events.Event;
  import flash.geom.Matrix;

  public class ImageButton extends Button {
    private const WIDTH:int = 18;
    private const X_OFFSET:int = 6;
    private var bitmap:Bitmap = null;
    private var image:Image = new Image();
    private var imageScale:Number;

    public function ImageButton(source:String, imageScale:Number = 15, clicked:Function = null) {
      this.imageScale = imageScale;
      super(WIDTH, 10, drawContent, clicked);

      image.addEventListener(Event.CHANGE, function(e:Event):void {
          bitmap = new Bitmap(image.bitmapData);
          redraw();
        }
      );

      image.source = source;
    }

    private function drawContent(graphics:Graphics, size:Number, radius:Number):void {

      if (bitmap) {
        const width:Number = imageScale * size;
        const offset:Number = (size - width) * 0.5;
        const scale:Number = width / bitmap.width;
        var matrix:Matrix = new Matrix();
        matrix.scale(scale, scale);
        matrix.translate(offset, offset);

        graphics.lineStyle(1, 0, 0);
        graphics.beginBitmapFill(bitmap.bitmapData, matrix, false, true);
        graphics.drawRect(offset, offset, width, width);
        graphics.endFill();
      }
    }

  }
}