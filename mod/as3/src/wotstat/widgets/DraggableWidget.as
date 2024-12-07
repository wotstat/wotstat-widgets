class HANGAR_INSETS {
  public static const TOP:int = 53;
  public static const BOTTOM:int = 35;
  public static const LEFT:int = 0;
  public static const RIGHT:int = 0;
}

package wotstat.widgets {

  import flash.display.Sprite;
  import flash.events.MouseEvent;
  import flash.geom.Rectangle;
  import wotstat.widgets.controls.Lock;
  import wotstat.widgets.controls.Resize;
  import wotstat.widgets.controls.ResizeControl;
  import flash.events.Event;
  import scaleform.clik.events.ResizeEvent;
  import wotstat.widgets.controls.HideShow;
  import wotstat.widgets.controls.Button;
  import flash.geom.Point;
  import flash.utils.ByteArray;
  import flash.display.Loader;
  import flash.display.Graphics;
  import flash.display.Bitmap;
  import flash.display.PixelSnapping;
  import flash.display.DisplayObject;
  import wotstat.widgets.common.MoveEvent;
  import wotstat.widgets.common.POSITION_MODE;
  import wotstat.widgets.common.LAYER;
  import wotstat.widgets.controls.Points;


  public class DraggableWidget extends Sprite {
    public static const REQUEST_RESIZE:String = "REQUEST_RESIZE";
    public static const REQUEST_RESOLUTION:String = "REQUEST_RESOLUTION";
    public static const MOVE_WIDGET:String = "MOVE_WIDGET";
    public static const LOCK_WIDGET:String = "LOCK_WIDGET";
    public static const UNLOCK_WIDGET:String = "UNLOCK_WIDGET";
    public static const HIDE_WIDGET:String = "HIDE_WIDGET";
    public static const SHOW_WIDGET:String = "SHOW_WIDGET";

    public var wid:int;
    public var isInBattle:Boolean;

    public function DraggableWidget(isInBattle:Boolean, wid:int) {
      super();
      this.wid = wid;
      this.isInBattle = isInBattle;
    }

    public function dispose():void {}
  }
}