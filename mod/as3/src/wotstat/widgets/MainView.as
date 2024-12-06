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
    public var py_requestResize:Function;
    public var py_requestResolution:Function;
    public var py_moveWidget:Function;
    public var py_lockUnlockWidget:Function;
    public var py_hideShowWidget:Function;


    private var defaultLayerView:Sprite = null;
    private var topLayerView:Sprite = null;

    private var activeWidgets:Vector.<DraggableWidget> = new Vector.<DraggableWidget>();
    private var activeWidgetsByWid:Object = new Object();

    private var isInBattle:Boolean = false;

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

            if (child is IView) {
              processView(child as IView);
            }

            if (viewContainer.getChildAt(i) is BaseBattlePage) {
              defaultLayerView = new Sprite();
              (viewContainer.getChildAt(i) as IView).addChild(defaultLayerView);
              isInBattle = true;
              as_setGlobalVisible(false, LAYER.DEFAULT);
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

    private function setupWidgets():void {
      for each (var widget:DraggableWidget in activeWidgets) {
        if (widget.getLayer() == LAYER.TOP)
          topLayerView.addChild(widget);
        else
          defaultLayerView.addChild(widget);

        widget.isInBattle = isInBattle;
      }
      updateTopLayerInfo();
    }

    private function updateTopLayerInfo():void {
      for each (var widget:DraggableWidget in activeWidgets) {
        widget.setTopPlan(false);
      }

      if (activeWidgets.length > 0) {
        activeWidgets[activeWidgets.length - 1].setTopPlan(true);
      }
    }

    private function setWidgetLayer(widget:DraggableWidget, layer:String):void {
      if (!defaultLayerView || !topLayerView)
        return;

      if (layer == LAYER.TOP) {
        if (defaultLayerView.contains(widget))
          defaultLayerView.removeChild(widget);
        if (!topLayerView.contains(widget))
          topLayerView.addChild(widget);
      }
      else {
        if (topLayerView.contains(widget))
          topLayerView.removeChild(widget);
        if (!defaultLayerView.contains(widget))
          defaultLayerView.addChild(widget);
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
        isInBattle:Boolean,
        positionMode:String,
        layer:String):void {
      _log("as_createWidget [" + wid + "]: " + url + " " + width + "x" + height + " (" + x + ";" + y + ")" +
          " hidden: " + isHidden + " locked: " + isLocked + " controls: " + isControlsAlwaysHidden + " battle: " +
          isInBattle + " positionMode: " + positionMode + " layer: " + layer);

      var widget:DraggableWidget = new DraggableWidget(wid, width, height, x, y, isHidden, isLocked, isControlsAlwaysHidden, isInBattle, positionMode, layer);
      widget.addEventListener(DraggableWidget.REQUEST_RESIZE, onWidgetRequestResize);
      widget.addEventListener(DraggableWidget.REQUEST_RESOLUTION, onWidgetRequestResolution);
      widget.addEventListener(DraggableWidget.MOVE_WIDGET, onWidgetMove);
      widget.addEventListener(DraggableWidget.LOCK_WIDGET, onWidgetLockUnlock);
      widget.addEventListener(DraggableWidget.UNLOCK_WIDGET, onWidgetLockUnlock);
      widget.addEventListener(DraggableWidget.SHOW_WIDGET, onWidgetHideShow);
      widget.addEventListener(DraggableWidget.HIDE_WIDGET, onWidgetHideShow);


      activeWidgets.push(widget);
      activeWidgetsByWid[wid] = widget;
      if (defaultLayerView) {
        defaultLayerView.addChild(widget);
        updateTopLayerInfo();
      }
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

    public function as_setHangarOnly(wid:int, enabled:Boolean):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setHangarOnly(enabled);
    }

    public function as_setPositionMode(wid:int, mode:String):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setPositionMode(mode);
    }

    public function as_setPosition(wid:int, x:int, y:int):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setPosition(x, y);
    }

    public function as_setControlsVisible(isPress:Boolean):void {
      if (!isInBattle)
        return;

      for each (var widget:DraggableWidget in activeWidgets) {
        widget.setBattleInteractiveMode(isPress);
      }
    }

    public function as_setGlobalVisible(visible:Boolean, layer:String):void {
      if (layer == LAYER.TOP && topLayerView)
        topLayerView.visible = visible;
      else if (layer == LAYER.DEFAULT && defaultLayerView)
        defaultLayerView.visible = visible;
      else if (layer == 'ALL') {
        if (topLayerView)
          topLayerView.visible = visible;

        if (defaultLayerView)
          defaultLayerView.visible = visible;

      }
    }

    public function as_closeWidget(wid:int):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];

      var idx:int = activeWidgets.indexOf(widget);
      if (idx >= 0) {
        activeWidgets.splice(idx, 1);
      }

      activeWidgetsByWid[widget.wid] = null;

      if (widget.parent)
        widget.parent.removeChild(widget);

      widget.dispose();
      widget.removeEventListener(DraggableWidget.REQUEST_RESIZE, onWidgetRequestResize);
      widget.removeEventListener(DraggableWidget.REQUEST_RESOLUTION, onWidgetRequestResolution);
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

    public function as_setUnlimitedSize(wid:int, unlimited:Boolean):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setUnlimitedSize(unlimited);
    }

    public function as_setInsets(wid:int, top:Number, right:Number, bottom:Number, left:Number):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.setInsets(top, right, bottom, left);
    }

    public function as_fixPosition(wid:int):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;
      widget.fixPosition();
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

    public function as_sendToTopPlan(wid:int):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;

      var idx:int = activeWidgets.indexOf(widget);
      if (idx >= 0) {
        activeWidgets.splice(idx, 1);
        activeWidgets.push(widget);
      }

      if (!defaultLayerView)
        return;

      if (defaultLayerView.contains(widget)) {
        defaultLayerView.removeChild(widget);
      }

      defaultLayerView.addChild(widget);
      updateTopLayerInfo();
    }

    public function as_setLayer(wid:int, mode:String):void {
      var widget:DraggableWidget = activeWidgetsByWid[wid];
      if (widget == null)
        return;

      widget.setLayer(mode);
      setWidgetLayer(widget, mode);
    }

    // widget events
    private function onWidgetRequestResize(event:ResizeEvent):void {
      if (this.py_requestResize != null) {
        var widget:DraggableWidget = event.target as DraggableWidget;
        this.py_requestResize(widget.wid, event.scaleX, event.scaleY);
      }
    }

    private function onWidgetRequestResolution(event:ResizeEvent):void {
      if (this.py_requestResolution != null) {
        var widget:DraggableWidget = event.target as DraggableWidget;
        this.py_requestResolution(widget.wid, event.scaleX, event.scaleY);
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