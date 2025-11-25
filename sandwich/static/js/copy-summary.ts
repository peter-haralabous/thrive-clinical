/**
 * Handle copy-to-clipboard functionality for summary content
 */

function setupCopyButtons() {
  document
    .querySelectorAll<HTMLButtonElement>('.js-copy-summary')
    .forEach((button) => {
      if (button.dataset.copyListenerAttached) return;
      button.dataset.copyListenerAttached = 'true';

      button.addEventListener('click', async () => {
        const textToCopy = button.dataset.copyText;
        if (!textToCopy) return;

        try {
          await navigator.clipboard.writeText(textToCopy);
          const originalText = button.textContent;
          button.textContent = 'Copied!';
          button.disabled = true;

          setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
          }, 2000);
        } catch (err) {
          console.error('Failed to copy text:', err);
        }
      });
    });
}

// Setup on page load and after HTMX swaps
document.addEventListener('DOMContentLoaded', () => {
  setupCopyButtons();
  document.body.addEventListener('htmx:afterSwap', setupCopyButtons);
});
