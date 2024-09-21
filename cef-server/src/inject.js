
function wotstatWidgetSetup() {
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
    wotstatWidgetOnBodyResize(realHeight)
  }

  function onHeadMutate() {
    const wotstatMeta = [...document.querySelectorAll('meta')]
      .filter(e => e.name.startsWith('wotstat-widget:'))
      .map(e => [e.name.slice(15), e.content === '' ? true : e.content])

    const metaMap = new Map(wotstatMeta)
    const getMeta = (key, defaultValue, proc) => proc && metaMap.get(key) ? proc(metaMap.get(key)) : (metaMap.get(key) ?? defaultValue)

    wotstatWidgetOnFeatureFlagsChange({
      autoHeight: getMeta('auto-height', false, t => t !== 'false'),
      readyToClearData: getMeta('ready-to-clear-data', false, t => t !== 'false'),
      useSniperMode: getMeta('use-sniper-mode', false, t => t !== 'false'),
    })
  }

  new ResizeObserver(_ => onResize()).observe(document.body)
  new MutationObserver(_ => onHeadMutate()).observe(document.head, { childList: true, subtree: true, attributes: true });

  onResize()
  onHeadMutate()
}

window.isFromWotstatWidgetMod = true
if (document.readyState === "complete") {
  wotstatWidgetSetup();
} else {
  document.addEventListener('DOMContentLoaded', wotstatWidgetSetup);
}