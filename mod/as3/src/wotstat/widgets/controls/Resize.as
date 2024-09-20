package wotstat.widgets.controls {
  public class Resize extends DoubleStateImageButton {
    public function Resize(clicked:Function = null) {
      super(['wotstatCefAssets/Resize.png', 'wotstatCefAssets/ResizeDisable.png'], 0.7, clicked);
    }
  }
}