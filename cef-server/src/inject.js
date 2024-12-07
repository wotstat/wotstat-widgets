
function wotstatWidgetSetup() {

  async function wotstatWidgetOnBodyResizeWrapper(height) {
    for (let i = 0; i < 3; i++) {
      if ('wotstatWidgetOnBodyResize' in window && typeof window.wotstatWidgetOnBodyResize === 'function') return window.wotstatWidgetOnBodyResize(height)
      await new Promise(r => setTimeout(r, 100))
      console.warn(`wotstatWidgetOnBodyResize is not defined, retrying ${i + 1}`)
    }
    console.error('wotstatWidgetOnBodyResize is not defined after 3 attempts')
  }

  async function wotstatWidgetOnFeatureFlagsChangeWrapper(flags) {
    for (let i = 0; i < 3; i++) {
      if ('wotstatWidgetOnFeatureFlagsChange' in window && typeof window.wotstatWidgetOnFeatureFlagsChange === 'function') return window.wotstatWidgetOnFeatureFlagsChange(flags)
      await new Promise(r => setTimeout(r, 100))
      console.warn(`wotstatWidgetOnFeatureFlagsChange is not defined, retrying ${i + 1}`)
    }
    console.error('wotstatWidgetOnFeatureFlagsChange is not defined after 3 attempts')
  }

  function setup() {
    const style = document.createElement('style')
    style.textContent = `
    body {
      overflow: hidden !important;
    }
  `;
    document.head.append(style)
    console.log('Injected style')

    window.isFromWotstatWidgetMod = true

    function onResize() {
      const realHeight = Math.ceil(document.body.clientHeight * devicePixelRatio);
      wotstatWidgetOnBodyResizeWrapper(realHeight)
    }

    function onHeadMutate() {
      const wotstatMeta = [...document.querySelectorAll('meta')]
        .filter(e => e.name.startsWith('wotstat-widget:'))
        .map(e => [e.name.slice(15), e.content === '' ? true : e.content])

      const metaMap = new Map(wotstatMeta)
      const getMeta = (key, defaultValue, proc) => proc && metaMap.get(key) ? proc(metaMap.get(key)) : (metaMap.get(key) ?? defaultValue)


      let insets = [0, 0, 0, 0]
      try {
        insets = getMeta('insets', [0, 0, 0, 0], t => t.split(/\s\s*/).map(e => parseFloat(e)))
        if (insets.length == 0) insets = [0, 0, 0, 0]
        if (insets.length == 1) insets = new Array(4).fill(insets[0])
        if (insets.length == 2) insets = [insets[0], insets[1], insets[0], insets[1]]
        if (insets.length == 3) insets = [insets[0], insets[1], insets[2], insets[1]]
        if (insets.length != 4) throw new Error('Invalid insets length')
      } catch (error) {
        console.warn('Failed to parse insets', error)
        insets = [0, 0, 0, 0]
      }

      wotstatWidgetOnFeatureFlagsChangeWrapper({
        autoHeight: getMeta('auto-height', false, t => t !== 'false'),
        readyToClearData: getMeta('ready-to-clear-data', false, t => t !== 'false'),
        useSniperMode: getMeta('use-sniper-mode', false, t => t !== 'false'),
        hangarOnly: getMeta('hangar-only', false, t => t !== 'false'),
        preferredTopLayer: getMeta('preferred-top-layer', false, t => t !== 'false'),
        unlimitedSize: getMeta('unlimited-size', false, t => t !== 'false'),
        insets
      })
    }

    new ResizeObserver(_ => onResize()).observe(document.body)
    new MutationObserver(_ => onHeadMutate()).observe(document.head, { childList: true, subtree: true, attributes: true });

    onResize()
    onHeadMutate()
  }

  try {
    setup()
  } catch (error) {
    console.error('Wotstat widget setup failed', error)
  }
}

window.isFromWotstatWidgetMod = true
if (document.readyState === "complete") {
  wotstatWidgetSetup();
} else {
  document.addEventListener('DOMContentLoaded', wotstatWidgetSetup);
}