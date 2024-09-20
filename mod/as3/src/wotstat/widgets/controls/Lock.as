package wotstat.widgets.controls {
  public class Lock extends DoubleStateImageButton {
    public function Lock(clicked:Function = null) {
      super(['wotstatCefAssets/LockOpen.png', 'wotstatCefAssets/Lock.png'], 0.5, clicked);
    }
  }
}