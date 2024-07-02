
function setup() {
  const style = document.createElement('style');
  style.textContent = `
    body {
      overflow: hidden !important;
    }
  `;
  document.head.append(style);
  console.log('Injected style');


  const resizeObserver = new ResizeObserver(entries =>
    onBodyResize(entries[0].target.clientHeight)
  )

  resizeObserver.observe(document.body);
}

if (document.readyState === "complete") {
  setup();
} else {
  document.addEventListener('DOMContentLoaded', setup);
}