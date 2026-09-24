/* Guide controls. Reading and navigation work without JavaScript or analytics. */
(() => {
  const track = (name, data) => {
    try {
      const sent = window.umami?.track(name, data);
      sent?.catch?.(() => {});
    } catch (_) { /* Analytics must never interfere with the guide. */ }
  };

  document.querySelectorAll('.code-block').forEach((block, index) => {
    if (!navigator.clipboard?.writeText) return;
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', `Copy command block ${index + 1}`);
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(block.querySelector('code').textContent);
        button.textContent = 'Copied';
        document.getElementById('copy-status').textContent = 'Commands copied.';
        track('Copy command', {
          guide: document.body.dataset.guide,
          block: index + 1,
          section: block.dataset.section,
        });
      } catch (_) {
        button.textContent = 'Select to copy';
        document.getElementById('copy-status').textContent = 'Could not copy. Select the commands and copy them manually.';
      }
      setTimeout(() => { button.textContent = 'Copy'; }, 2000);
    });
    block.append(button);
  });
})();
