package wotstat.widgets {
  import net.wg.infrastructure.base.AbstractView;
  import net.wg.infrastructure.interfaces.IView;
  import net.wg.infrastructure.events.LoaderEvent;
  import net.wg.data.Aliases;
  import net.wg.infrastructure.managers.impl.ContainerManagerBase;
  import net.wg.data.constants.generated.LAYER_NAMES;
  import net.wg.gui.components.containers.MainViewContainer;
  import net.wg.gui.battle.views.BaseBattlePage;
  import scaleform.clik.events.ResizeEvent;
  import flash.events.Event;
  import flash.utils.ByteArray;
  import flash.display.DisplayObject;
  import flash.display.Sprite;
  import wotstat.widgets.common.MoveEvent;
  import wotstat.widgets.common.LAYER;

  public class MainView extends AbstractView {

    public var py_log:Function;

    private var defaultLayerView:Sprite = null;
    private var topLayerView:Sprite = null;

    private var activeWidgets:Vector.<DraggableWidget> = new Vector.<DraggableWidget>();
    private var activeWidgetsByWid:Object = new Object();

    private var isInBattle:Boolean = false;
    private var isReadyToAdd:Boolean = false;

    public function MainView() {
      super();
    }

    override protected function configUI():void {
      super.configUI();

      topLayerView = new Sprite();
      addChild(topLayerView);

      var viewContainer:MainViewContainer = App.containerMgr.getContainer(LAYER_NAMES.LAYER_ORDER.indexOf(LAYER_NAMES.VIEWS)) as MainViewContainer;
      if (viewContainer != null && defaultLayerView == null) {

        for (var i:int = 0; i < viewContainer.numChildren; ++i) {
          var child:DisplayObject = viewContainer.getChildAt(i);

          try {

            if (child is IView)
              processView(child as IView);

            if (viewContainer.getChildAt(i) is BaseBattlePage) {
              defaultLayerView = new Sprite();
              (viewContainer.getChildAt(i) as IView).addChild(defaultLayerView);
              setupWidgets();
            }
          }
          catch (error:Error) {}
        }
      }

      (App.containerMgr as ContainerManagerBase).loader.addEventListener(LoaderEvent.VIEW_LOADED, onViewLoaded, false, 0, true);
    }

    override protected function onDispose():void {
      (App.containerMgr as ContainerManagerBase).loader.removeEventListener(LoaderEvent.VIEW_LOADED, onViewLoaded);
      for each (var widget:DraggableWidget in activeWidgets)
        widget.dispose();

      super.onDispose();
    }

    private function onViewLoaded(event:LoaderEvent):void {
      processView(event.view as IView);
    }

    private function processView(view:IView):void {
      if (view == null)
        return;

      if (view.as_config.alias == Aliases.LOBBY_HANGAR) {
        isInBattle = false;

        if (defaultLayerView == null) {
          defaultLayerView = new Sprite();
          view.addChild(defaultLayerView);
          setupWidgets();
        }
        else {
          if (defaultLayerView.parent)
            defaultLayerView.parent.removeChild(defaultLayerView);
          view.addChild(defaultLayerView);
        }
      }
    }

    private function addChildWidget(widget:DraggableWidget):void {
      topLayerView.addChild(widget);
    }

    private function setupWidgets():void {
      for each (var widget:DraggableWidget in activeWidgets) {
        addChildWidget(widget);
      }
      isReadyToAdd = true;
    }

    public function as_addWidget(wid:Number):void {
      var widget:DraggableWidget = new DraggableWidget(isInBattle, wid);
      activeWidgets.push(widget);
      activeWidgetsByWid[widget.wid] = widget;
      if (isReadyToAdd) {
        addChildWidget(widget);
      }
    }

    public function as_onFrame(wid:int, width:int, height:int, data:Array, shift:int, insets:Vector<Number):void {
      var bytes:ByteArray = Utils.decodeIntArrayAMF(data, shift);
      activeWidgetsByWid[wid].setFrame(width, height, bytes);
    }

  }
}