export function initNav(root = null) {
  const mount = root || document.getElementById('site-header') || document.body;
  // Ensure the mount is an element we can populate
  if (!mount) return;
  mount.className = 'global-header';
  mount.innerHTML = `
    <div class="global-header__inner">
      <div class="brand">
        <div class="logo">HC</div>
        <div class="brand-name">HealthConnect</div>
      </div>
      <div class="search" aria-hidden="true">
        <input type="search" placeholder="Type a command or search..." aria-label="Search" />
      </div>
      <div class="actions" style="display:flex;align-items:center;gap:12px">
        <button class="icon-btn" aria-label="Open quick actions" title="Open quick actions">
          <span class="material-symbols-outlined">segment</span>
        </button>
        <div class="user" title="JD">JD</div>
      </div>
    </div>
  `;
  if (!document.body.classList.contains('has-global-header')) {
    document.body.classList.add('has-global-header');
  }
}
