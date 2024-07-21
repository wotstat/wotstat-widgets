package wotstat.cef {
  import flash.display.Sprite;
  import wotstat.cef.controls.Button;

  public class ControlsPanel extends Sprite {

    private var gap:int;
    private var buttons:Vector.<Button> = new Vector.<Button>();

    public function ControlsPanel(height:int = 19, gap:int = 3) {
      this.gap = gap;
      super();
    }

    public function addButton(btn:Button):ControlsPanel {
      buttons.push(btn);
      addChild(btn);
      return this;
    }

    public function layout():void {
      var x:int = 0;
      for each (var btn:Button in buttons) {
        if (btn.visible) {
          btn.x = x;
          x += btn.width + gap;
        }
      }
    }
  }
}