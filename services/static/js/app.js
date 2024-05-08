const menuToggle = document.querySelector('[data-menu-toggle]');
const navigation = document.getElementById('main-navigation');

function closeMenu() {
  menuToggle?.setAttribute('aria-expanded', 'false');
  navigation?.classList.remove('is-open');
}

menuToggle?.addEventListener('click', () => {
  const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
  menuToggle.setAttribute('aria-expanded', String(!isOpen));
  navigation?.classList.toggle('is-open', !isOpen);
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && menuToggle?.getAttribute('aria-expanded') === 'true') {
    closeMenu();
    menuToggle.focus();
  }
});

document.addEventListener('click', (event) => {
  if (!event.target.closest('.nav-shell')) closeMenu();
  const dismiss = event.target.closest('[data-dismiss-message]');
  if (dismiss) {
    const notice = dismiss.closest('.notice');
    const nextNotice = notice.nextElementSibling;
    notice.remove();
    (nextNotice?.querySelector('button') || document.getElementById('main-content'))?.focus();
  }
});
