package wotstat.cef {
  import flash.display.Sprite;
  import flash.text.TextField;
  import flash.events.Event;
  import net.wg.infrastructure.base.AbstractView;
  import net.wg.infrastructure.interfaces.IView;
  import net.wg.infrastructure.events.LoaderEvent;
  import net.wg.data.Aliases;
  import net.wg.gui.lobby.hangar.Hangar;
  import net.wg.infrastructure.managers.impl.ContainerManagerBase;
  import net.wg.infrastructure.interfaces.IManagedContent;
  import net.wg.infrastructure.interfaces.ISimpleManagedContainer;
  import net.wg.data.constants.generated.LAYER_NAMES;
  import net.wg.gui.components.containers.MainViewContainer;
  import flash.display.MovieClip;
  import net.wg.gui.login.impl.LoginPage;
  import flash.display.DisplayObject;

  import flash.display.Bitmap;
  import flash.display.BitmapData;
  import flash.display.Loader;
  import flash.display.LoaderInfo;
  import flash.events.Event;
  import flash.events.ProgressEvent;
  import flash.net.Socket;
  import flash.utils.ByteArray;
  import flash.net.URLRequest;


  public class MainView extends AbstractView {


    public var py_log:Function;

    private var dragArea:Sprite = null;
    private var sprite:Sprite = null;
    private var imageSocket:ImageSocket = new ImageSocket("127.0.0.1", 30001);

    public function MainView() {
      super();
      this._log("MainView constructor", "INFO");
    }

    override protected function configUI():void {

      super.configUI();


      var viewContainer:MainViewContainer = App.containerMgr.getContainer(LAYER_NAMES.LAYER_ORDER.indexOf(LAYER_NAMES.VIEWS)) as MainViewContainer;
      if (viewContainer != null) {
        var num:int = viewContainer.numChildren;
        for (var idx:int = 0; idx < num; ++idx) {
          var view:IView = viewContainer.getChildAt(idx) as IView;
          if (view != null) {
            processView(view);
          }
        }
        var topmostView:IManagedContent = viewContainer.getTopmostView();
        if (topmostView != null) {
          viewContainer.setFocusedView(topmostView);
        }
      }

      // subscribe to container manager loader
      (App.containerMgr as ContainerManagerBase).loader.addEventListener(LoaderEvent.VIEW_LOADED, onViewLoaded, false, 0, true);
    }

    override protected function onDispose():void {
      (App.containerMgr as ContainerManagerBase).loader.removeEventListener(LoaderEvent.VIEW_LOADED, onViewLoaded);
      super.onDispose();
    }

    private function onViewLoaded(event:LoaderEvent):void {
      processView(event.view as IView);
    }

    private var hangar:Hangar = null;
    private function processView(view:IView):void {
      var alias:String = view.as_config.alias;

      if (alias == Aliases.LOBBY_HANGAR) {

        var hangarL:Hangar = view as Hangar;
        if (hangarL != null) {
          hangar = hangarL;
          sprite = new Sprite();

          sprite.graphics.beginFill(0x00ff00, 0.9);
          sprite.graphics.drawRect(0, 0, 400, 300);
          sprite.graphics.endFill();

          var disp:DisplayObject = DisplayObject(sprite);

          disp.x = 500;
          disp.y = 500;

          hangar.addChild(disp);

          var target:DisplayObject = DisplayObject(imageSocket);
          target.x = 200;
          target.y = 200;
          hangar.addChild(target);

          _log("Hangar view found", "INFO");
        }
      }
    }

    // private function onImageLoadComplete(event:Event):void {
    // var loaderInfo:LoaderInfo = LoaderInfo(event.target);
    // var bitmap:Bitmap = Bitmap(loaderInfo.content);

    // _log("Image loaded", "INFO");

    // if (sprite != null) {
    // sprite.graphics.clear();

    // sprite.graphics.beginFill(0x0000ff, 0.9);
    // sprite.graphics.drawRect(0, 0, 400, 300);
    // sprite.graphics.endFill();

    // sprite.graphics.beginBitmapFill(bitmap.bitmapData);
    // sprite.graphics.drawRect(30, 30, 340, 240);
    // sprite.graphics.endFill();

    // _log("Image drawn", "INFO");
    // }
    // }

    private function _log(msg:String, level:String = "INFO"):void {
      if (this.py_log != null) {
        this.py_log(msg, level);
      }
      else {
        DebugUtils.LOG_WARNING("[MainView][" + level + "]" + msg);
      }
    }
  }
}