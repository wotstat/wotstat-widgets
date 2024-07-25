package wotstat.cef {
  import net.wg.infrastructure.base.AbstractWindowView;
  import net.wg.gui.components.controls.TextInput;
  import net.wg.gui.components.controls.SoundButton;
  import flash.events.MouseEvent;
  import flash.text.TextFormat;
  import flash.text.TextField;
  import scaleform.clik.events.InputEvent;

  public class SettingsWindow extends AbstractWindowView {

    public var py_openWidgetsCollection:Function;
    public var py_openWidget:Function;
    public var py_openDemoWidget:Function;
    public var py_t:Function;

    private var urlInput:TextInput;
    private var addButton:SoundButton;
    private var demoButton:SoundButton;
    private var collectionButton:SoundButton;

    public function SettingsWindow() {
      super();
    }

    override protected function onPopulate():void {
      super.onPopulate();
      width = 401;
      height = 200;
      window.title = py_t('settings.title');
      window.useBottomBtns = false;

      urlInput = addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
              width: 310,
              height: 30,
              x: 8,
              y: 10,
              defaultText: py_t('settings.urlPlaceholder')
            })) as TextInput;

      urlInput.defaultTextFormat.italic = false;
      urlInput.defaultTextFormat.color = 0x959587;
      urlInput.addEventListener(InputEvent.INPUT, onInputInputHandler);

      addButton = addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
              width: 70,
              height: 25,
              x: 323,
              y: 12.5,
              label: py_t('settings.add'),
              enabled: false
            })) as SoundButton;
      addButton.addEventListener(MouseEvent.CLICK, onAddButtonClick);

      collectionButton = addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
              width: 187.5,
              height: 25,
              x: 8,
              y: 165,
              label: py_t('settings.collection')
            })) as SoundButton;
      collectionButton.addEventListener(MouseEvent.CLICK, onCollectionButtonClick);

      demoButton = addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
              width: 187.5,
              height: 25,
              x: 205.5,
              y: 165,
              label: py_t('settings.addDemo')
            })) as SoundButton;
      demoButton.addEventListener(MouseEvent.CLICK, onDemoButtonClick);


      var info:TextField = new TextField();
      info.width = 385;
      info.height = 100;
      info.x = 8;
      info.y = 50;
      info.text = py_t('settings.info');

      var format:TextFormat = new TextFormat("$FieldFont", 14, 0x959587);
      format.leading = 0;
      info.setTextFormat(format);

      info.multiline = true;
      info.wordWrap = true;
      info.selectable = false;

      addChild(info);
    }

    private function onAddButtonClick(event:MouseEvent):void {
      py_openWidget(urlInput.text);
    }

    private function onDemoButtonClick(event:MouseEvent):void {
      py_openDemoWidget();
    }

    private function onCollectionButtonClick(event:MouseEvent):void {
      py_openWidgetsCollection();
    }

    private function onInputInputHandler(event:InputEvent):void {
      addButton.enabled = urlInput.text.length > 0;
    }
  }
}