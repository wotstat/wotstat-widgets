package wotstat.widgets {
  import net.wg.infrastructure.base.AbstractWindowView;
  import net.wg.gui.components.controls.TextInput;
  import net.wg.gui.components.controls.SoundButton;
  import flash.events.MouseEvent;
  import flash.text.TextFormat;
  import flash.text.TextField;
  import scaleform.clik.events.InputEvent;
  import flash.display.Sprite;

  public class SettingsWindow extends AbstractWindowView {

    public var py_openWidgetsCollection:Function;
    public var py_openWidget:Function;
    public var py_openDemoWidget:Function;
    public var py_openUnpackError:Function;
    public var py_t:Function;

    private var urlInput:TextInput;
    private var addButton:SoundButton;
    private var demoButton:SoundButton;
    private var collectionButton:SoundButton;
    private var showUnpackErrorButton:SoundButton;

    private var normalState:Sprite = new Sprite();
    private var textState:Sprite = new Sprite();
    private var textStateText:TextField = new TextField();

    public function SettingsWindow() {
      super();
    }

    private function setVisible(sprite:Sprite, value:Boolean):void {
      sprite.visible = value;
      sprite.mouseEnabled = value;
      sprite.mouseChildren = value;
    }

    override protected function onPopulate():void {
      super.onPopulate();
      width = 401;
      height = 200;
      window.title = py_t('settings.title');
      window.useBottomBtns = false;


      addChild(normalState);
      addChild(textState);

      setVisible(normalState, false);
      setVisible(textState, false);

      {
        urlInput = normalState.addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
                width: 310,
                height: 30,
                x: 8,
                y: 10,
                defaultText: py_t('settings.urlPlaceholder')
              })) as TextInput;

        urlInput.defaultTextFormat.italic = false;
        urlInput.defaultTextFormat.color = 0x959587;
        urlInput.addEventListener(InputEvent.INPUT, onInputInputHandler);

        addButton = normalState.addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
                width: 70,
                height: 25,
                x: 323,
                y: 12.5,
                label: py_t('settings.add'),
                enabled: false
              })) as SoundButton;
        addButton.addEventListener(MouseEvent.CLICK, onAddButtonClick);

        collectionButton = normalState.addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
                width: 187.5,
                height: 25,
                x: 8,
                y: 165,
                label: py_t('settings.collection')
              })) as SoundButton;
        collectionButton.addEventListener(MouseEvent.CLICK, onCollectionButtonClick);

        demoButton = normalState.addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
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

        var infoFormat:TextFormat = new TextFormat("$FieldFont", 14, 0x959587);
        infoFormat.leading = 0;
        info.setTextFormat(infoFormat);
        info.multiline = true;
        info.wordWrap = true;
        info.selectable = false;

        normalState.addChild(info);
      }

      {
        textStateText.width = 385;
        textStateText.height = 150;
        textStateText.x = 8;
        textStateText.y = 8;
        textStateText.text = 'Text State';

        textStateText.multiline = true;
        textStateText.wordWrap = true;
        textStateText.selectable = false;
        textStateText.mouseEnabled = false;

        textState.addChild(textStateText);

        showUnpackErrorButton = textState.addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
                width: 187.5,
                height: 25,
                x: 106,
                y: 165,
                label: py_t('settings.showUnpackError')
              })) as SoundButton;

        showUnpackErrorButton.addEventListener(MouseEvent.CLICK, onShowUnpackErrorButtonClick);
        showUnpackErrorButton.visible = false;
      }
    }

    public function as_setNormalState():void {
      normalState.visible = true;
      setVisible(normalState, true);
      setVisible(textState, false);
    }

    public function as_setTextState(text:String):void {
      textStateText.htmlText = text;

      setVisible(normalState, false);
      setVisible(textState, true);
    }

    public function as_showUnpackErrorButton():void {
      showUnpackErrorButton.visible = true;
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

    private function onShowUnpackErrorButtonClick(event:MouseEvent):void {
      py_openUnpackError();
    }

    private function onInputInputHandler(event:InputEvent):void {
      addButton.enabled = urlInput.text.length > 0;
    }
  }
}