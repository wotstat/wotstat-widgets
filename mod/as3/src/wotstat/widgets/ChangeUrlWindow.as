package wotstat.widgets {
  import net.wg.infrastructure.base.AbstractWindowView;
  import net.wg.gui.components.controls.TextInput;
  import net.wg.gui.components.controls.SoundButton;
  import flash.events.MouseEvent;
  import scaleform.clik.events.InputEvent;

  public class ChangeUrlWindow extends AbstractWindowView {

    public var py_changeUrl:Function;
    public var py_cancel:Function;
    public var py_t:Function;

    private var urlInput:TextInput;
    private var applyButton:SoundButton;
    private var cnacelButton:SoundButton;

    public function ChangeUrlWindow() {
      super();
    }
    override protected function onPopulate():void {
      super.onPopulate();
      width = 401;
      height = 85;
      window.title = py_t('changeUrl.title');
      window.useBottomBtns = false;

      urlInput = addChild(App.utils.classFactory.getComponent("TextInput", TextInput, {
              width: 385,
              height: 30,
              x: 8,
              y: 10,
              defaultText: py_t('changeUrl.urlPlaceholder')
            })) as TextInput;

      urlInput.defaultTextFormat.italic = false;
      urlInput.defaultTextFormat.color = 0x959587;
      urlInput.addEventListener(InputEvent.INPUT, onInputInputHandler);

      applyButton = addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
              width: 187.5,
              height: 25,
              x: 8,
              y: 50,
              label: py_t('changeUrl.apply')
            })) as SoundButton;
      applyButton.addEventListener(MouseEvent.CLICK, onApplyButtonClick);

      cnacelButton = addChild(App.utils.classFactory.getComponent("ButtonNormal", SoundButton, {
              width: 187.5,
              height: 25,
              x: 205.5,
              y: 50,
              label: py_t('changeUrl.cancel')
            })) as SoundButton;
      cnacelButton.addEventListener(MouseEvent.CLICK, onCancelButtonClick);
    }

    private function onApplyButtonClick(event:MouseEvent):void {
      py_changeUrl(urlInput.text);
    }

    private function onCancelButtonClick(event:MouseEvent):void {
      py_cancel();
    }

    private function onInputInputHandler(event:InputEvent):void {
      applyButton.enabled = urlInput.text.length > 0;
    }

    public function as_setUrl(url:String):void {
      urlInput.text = url;
    }
  }
}