package wotstat.cef.buttons {
  import flash.display.Graphics;
  import flash.display.Loader;
  import flash.net.URLRequest;
  import flash.events.Event;
  import flash.display.LoaderInfo;
  import flash.display.Bitmap;
  import net.wg.gui.components.controls.Image;


  public class Lock extends Button {
    private const IMAGE_DATA:String = 'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAI9SURBVHgB7Zv9VcIwFMVvnQAnsBvIBqIL6AboBH4sABuAE4gb6AIiE4ATgC5AJ/D5chL/8TRt0qSlMfmdcw+HnhJebvPx2jQZOoKIBvwxZg1ZI9ZASVCwdkovrFWWZTv8B7jiI9aS7FmyxggVDj6nZhX/y1qUhZAQV461J3+Isu4QAhzohNpjAs9k8AgHeMsfc4NTN0qf6vsJK4ccHOu45wHS5D+6hWSfr2vGU5KzQVUZ16xtTTlD9I2aoBdVFS8pK1e/0bFEn1BXTccUDVEtRkd/psiKq/8ERypawhp9gGSiU8aWPMzfXMaA9FPqCI4cwZ0rzfFnH+kslyHS5EfY/Xd3kMzUysjhCdUKSlsZDklFYN5HadKn1cazSxmuXUA3H3/AP7oyczjgaoDO/R38s9Ecd0qK2jKggH8KyxiMcDUgR3f00oDgSQYgcpIBiJxkACInegMaPRRV9+HiVvQS5clQgXaywbzk2I71ypp3sprElZ9Rf5mhTajflf/FygTjLkDyAcdhH0CYc87d4d3kRJtBcIpwMH5UZmPAKcLh0vREmy5ACAjuAkZ1S4kQIicZgMhJBiBykgGInGQAIicZgMhJBiBykgGInGQAIicZgMhJBiBykgGIHBsD2ljubgvjWG0M2CAcjGO1MWCFcFiYnmizNiheSRXL406vpnaAiPHC9G0R4xagdm7coN+IBdyHVl+V4ZYwpOotcl3zrfRGDfYQNd45SnLz4hnrGHLnpytNlt+/WHvI7faNBukfiYccG1meByEAAAAASUVORK5CYII=';

    private const WIDTH:int = 18;
    private const X_OFFSET:int = 6;
    private var bitmap:Bitmap = null;

    public function Lock() {
      // bitmap = new lockImgClass() as Bitmap
      super(WIDTH, 10, drawContent);
      // var decoder:Decoder = new Base64Decoder();
    }

    private function drawContent(graphics:Graphics, size:Number, radius:Number):void {

      // graphics.beginFill(0xffffff);
      // graphics.drawRoundRect(5, 7, 8, 7, 2);
      // graphics.endFill();

      // graphics.lineStyle(1, 0xffffff);
      // graphics.drawRoundRect(7, 4, 4, 6, 6);

      // graphics.beginFill(0xffffff);
      // graphics.drawRoundRect(size * 0.3, size * 0.4, size * 0.45, size * 0.4, size * 0.1);
      // graphics.endFill();

      // graphics.lineStyle(1, 0xffffff);
      // graphics.drawRoundRect(size * 0.35, size * 0.2, size * 0.3, size * 0.4, size * 0.3);

      if (bitmap) {
        graphics.beginBitmapFill(bitmap.bitmapData);
        graphics.drawRect(0, 0, size, size);
        graphics.endFill();
      }
    }
  }
}