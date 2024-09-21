package wotstat.widgets {
  import net.wg.infrastructure.base.AbstractView;
  import net.wg.infrastructure.interfaces.IView;
  import net.wg.infrastructure.events.LoaderEvent;
  import net.wg.data.Aliases;
  import net.wg.infrastructure.managers.impl.ContainerManagerBase;
  import net.wg.data.constants.generated.LAYER_NAMES;
  import net.wg.gui.components.containers.MainViewContainer;
  import scaleform.clik.events.ResizeEvent;
  import flash.events.Event;
  import flash.utils.ByteArray;
  import net.wg.gui.battle.views.BaseBattlePage;
  import flash.display.DisplayObject;
  import wotstat.widgets.common.MoveEvent;

  public class MainView extends AbstractView {

    public var py_log:Function;
    public var py_requestResize:Function;
    public var py_moveWidget:Function;
    public var py_lockUnlockWidget:Function;
    public var py_hideShowWidget:Function;


    private var targetView:IView = null;
    private var activeWidgets:Vector.<DraggableWidget> = new Vector.<DraggableWidget>();
    private var activeWidgetsByWid:Object = new Object();

    private var isInBattle:Boolean = false;
    private var isGlovalVisible:Boolean = true;

    public function MainView() {
      super();
    }

    override protected function configUI():void {
      super.configUI();

      var viewContainer:MainViewContainer = App.containerMgr.getContainer(LAYER_NAMES.LAYER_ORDER.indexOf(LAYER_NAMES.VIEWS)) as MainViewContainer;
      if (viewContainer != null) {

        for (var i:int = 0; i < viewContainer.numChildren; ++i) {
          var child:DisplayObject = viewContainer.getChildAt(i);

          try {

            if (child is IView) {
              processView(child as IView);
            }

            if (viewContainer.getChildAt(i) is BaseBattlePage) {
              targetView = viewContainer.getChildAt(i) as IView;
              isInBattle = true;
              as_setGlobalVisible(false);
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
      for each (var widget:DraggableWidget in activeWidgets) {
        widget.dispose();
      }
      super.onDispose();
    }

    private function onViewLoaded(event:LoaderEvent):void {
      processView(event.view as IView);
    }

    private function processView(view:IView):void {
      if (view == null)
        return;

      if (view.as_config.alias == Aliases.LOBBY_HANGAR) {
        targetView = view;
        isInBattle = false;
        setupWidgets();
      }
    }

    private function setupWidgets():void {
      for each (var widget:DraggableWidget in activeWidgets) {
        targetView.addChild(widget);
        widget.isInBattle = isInBattle;
        widget.visible = isGlovalVisible;
      }
    }

    private function _log(msg:String, level:String = "INFO"):void {
      if (this.py_log != null) {
        this.py_log(msg, level);
      }
      else {
        DebugUtils.LOG_WARNING("[MainView][" + level + "]" + msg);
      }
    }

    public function as_createWidget(wid:int, url:String, width:int, height:int, x:int, y:int,
        isHidden:Boolean,
        isLocked:Boolean,
        isControlsAlwaysHidden:Boolean,
        isInBattle:Boolean):void {
      _log("as_createWidget [" + wid + "]: " + url + " " + width + "x" + height + " (" + x + ";" + y + ")" +
          " hidden: " + isHidden + " locked: " + isLocked + " controls: " + isControlsAlwaysHidden + " battle: " + isInBattle);

      var widget:DraggableWidget = new DraggableWidget(wid, width, height, x, y, isHidden, isLocked, isControlsAlwaysHidden, isInBattle);
      widget.addEventListener(DraggableWidget.REQUEST_RESIZE, onWidgetRequestResize);
      widget.addEventListener(DraggableWidget.MOVE_WIDGET, onWidgetMove);
      widget.addEventListener(DraggableWidget.LOCK_WIDGET, onWidgetLockUnlock);
      widget.addEventListener(DraggableWidget.UNLOCK_WIDGET, onWidgetLockUnlock);
      widget.addEventListener(DraggableWidget.SHOW_WIDGET, onWidgetHideShow);
      widget.addEventListener(DraggableWidget.HIDE_WIDGET, onWidgetHideShow);


      activeWidgets.push(widget);
      activeWidgetsByWid[wid] = widget;
      if (targetView)
        targetView.addChild(widget);
    }

    public function as_setInterfaceScale(scale:Number):void {
      for each (var widget:DraggableWidget in activeWidgets) {
        widget.onInterfaceScaleChanged(scale);
      }
    }

    public function as_onFrame(wid:int, width:int, height:int, data:Array, shift:int):void {
      var bytes:ByteArray = Utils.decodeIntArrayAMF(data, shift);

      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;

      widget.setFrame(width, height, bytes);
    }

    public function as_setResizeMode(wid:int, full:Boolean):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setResizeMode(full);
    }

    public function as_setControlPressed(isPress:Boolean):void {
      if (!isInBattle)
        return;

      for each (var widget:DraggableWidget in activeWidgets) {
        widget.setBattleInteractiveMode(isPress);
      }
    }

    public function as_setGlobalVisible(visible:Boolean):void {
      isGlovalVisible = visible;
      for each (var widget:DraggableWidget in activeWidgets) {
        widget.visible = visible;
      }
    }

    public function as_closeWidget(wid:int):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];

      var idx:int = activeWidgets.indexOf(widget);
      if (idx >= 0) {
        activeWidgets.splice(idx, 1);
      }

      activeWidgetsByWid[widget.wid] = null;

      targetView.removeChild(widget);
      widget.dispose();
      widget.removeEventListener(DraggableWidget.REQUEST_RESIZE, onWidgetRequestResize);
      widget.removeEventListener(DraggableWidget.MOVE_WIDGET, onWidgetMove);
      widget.removeEventListener(DraggableWidget.LOCK_WIDGET, onWidgetLockUnlock);
      widget.removeEventListener(DraggableWidget.UNLOCK_WIDGET, onWidgetLockUnlock);
      widget.removeEventListener(DraggableWidget.SHOW_WIDGET, onWidgetHideShow);
      widget.removeEventListener(DraggableWidget.HIDE_WIDGET, onWidgetHideShow);
    }

    // context menu events
    public function as_setResizing(wid:int, enabled:Boolean):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setResizing(enabled);
    }

    public function as_setLocked(wid:int, locked:Boolean):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setLocked(locked);
    }

    public function as_setReadyToClearData(wid:int, enabled:Boolean):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setReadyToClearData(enabled);
    }

    public function as_setControlsAlwaysHidden(wid:int, enabled:Boolean):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setControlsAlwaysHidden(enabled);
    }

    // widget events
    private function onWidgetRequestResize(event:ResizeEvent):void {
      if (this.py_requestResize != null) {
        var widget:DraggableWidget = event.target as DraggableWidget;
        this.py_requestResize(widget.wid, event.scaleX, event.scaleY);
      }
    }

    private function onWidgetMove(event:MoveEvent):void {
      if (this.py_moveWidget != null) {
        var widget:DraggableWidget = event.target as DraggableWidget;
        this.py_moveWidget(widget.wid, event.x, event.y);
      }
    }

    private function onWidgetLockUnlock(event:Event):void {
      if (this.py_lockUnlockWidget != null) {
        var widget:DraggableWidget = event.target as DraggableWidget;
        this.py_lockUnlockWidget(widget.wid, widget.isLocked);
      }
    }

    private function onWidgetHideShow(event:Event):void {
      if (this.py_hideShowWidget != null) {
        var widget:DraggableWidget = event.target as DraggableWidget;
        this.py_hideShowWidget(widget.wid, widget.isHidden);
      }
    }
  }
}