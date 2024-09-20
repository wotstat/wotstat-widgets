package wotstat.widgets.controls {
  public class DoubleStateImageButton extends ImageButton {
    private var currentState:int = 0;
    private var states:Array = [];

    public function get state():int {
      return currentState;
    }

    public function set state(value:int):void {
      currentState = value;
      if (currentState < 0)
        currentState = 0;
      else if (currentState >= states.length)
        currentState = states.length - 1;

      image.source = states[currentState];
    }

    public function DoubleStateImageButton(states:Array, imageScale:Number = 0.5, clicked:Function = null) {
      this.states = states;
      super(states[0], imageScale, clicked);
    }
  }
}