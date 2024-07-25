package wotstat.widgets.common {
  import flash.events.Event;

  public class MoveEvent extends Event {
    public static const MOVE:String = "MOVE";

    public var x:Number;
    public var y:Number;

    public function MoveEvent(type:String, x:Number, y:Number) {
      super(type);
      this.x = x;
      this.y = y;
    }

    override public function clone():Event {
      return new MoveEvent(type, x, y);
    }
  }
}