(() => {
  const visible = document.querySelector('#overlay-visible');
  const form = document.querySelector('#overlay-form');
  const hide = document.querySelector('#overlay-hide');
  if (!visible || !form || !hide) return;
  visible.addEventListener('change', () => {
    if (visible.checked) form.requestSubmit();
    else hide.click();
  });
})();
