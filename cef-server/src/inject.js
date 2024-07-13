
function setup() {
  const style = document.createElement('style');
  style.textContent = `
    body {
      overflow: hidden !important;
    }
  `;
  document.head.append(style);
  console.log('Injected style');


  const resizeObserver = new ResizeObserver(entries => {
    const realHeight = Math.ceil(entries[0].target.clientHeight * devicePixelRatio);
    onBodyResize(realHeight)
  })

  resizeObserver.observe(document.body);
}

if (document.readyState === "complete") {
  setup();
} else {
  document.addEventListener('DOMContentLoaded', setup);
}