(function () {
  var controls = document.querySelectorAll('[data-interest]');
  var panels = document.querySelectorAll('[data-interest-panel]');
  function selectInterest(key) {
    controls.forEach(function (button) {
      button.setAttribute('aria-pressed', String(button.dataset.interest === key));
    });
    panels.forEach(function (panel) {
      panel.hidden = panel.dataset.interestPanel !== key;
    });
  }
  controls.forEach(function (button) {
    button.addEventListener('click', function () { selectInterest(button.dataset.interest); });
  });
  // All three entries remain readable when JavaScript is unavailable.
  selectInterest('agents');
})();
