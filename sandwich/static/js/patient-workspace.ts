/**
 * Patient workspace functionality - mobile navigation, panel resizing, chat form, file upload
 */

const MOBILE_BREAKPOINT = 1024; // Tailwind's lg breakpoint

// Panel IDs
const enum PanelId {
  Left = 'left-panel',
  Right = 'right-panel',
  Chat = 'mobile-chat-view',
}

// Resize handle IDs
const enum ResizeHandleId {
  Left = 'left-resize-handle',
  Right = 'right-resize-handle',
}

// View names for mobile navigation
const enum View {
  Records = 'records',
  Chat = 'chat',
  Feed = 'feed',
}

// LocalStorage keys for panel widths
const enum StorageKey {
  LeftPanelWidth = 'leftPanelWidth',
  RightPanelWidth = 'rightPanelWidth',
}

let lastActivePanel = View.Chat;

function getPanelForElement(element: Element): View | null {
  const leftPanel = document.getElementById(PanelId.Left);
  const chatPanel = document.getElementById(PanelId.Chat);
  const rightPanel = document.getElementById(PanelId.Right);

  if (leftPanel?.contains(element)) return View.Records;
  if (chatPanel?.contains(element)) return View.Chat;
  if (rightPanel?.contains(element)) return View.Feed;
  return null;
}

function setActiveView(viewName: View): void {
  lastActivePanel = viewName;
  const container = document.getElementById('panels-container');
  if (!container) return;

  container.setAttribute('data-active-view', viewName);

  if (window.innerWidth < MOBILE_BREAKPOINT) {
    const leftPanel = document.getElementById(PanelId.Left);
    const chatPanel = document.getElementById(PanelId.Chat);
    const rightPanel = document.getElementById(PanelId.Right);

    // Hide all panels
    [leftPanel, chatPanel, rightPanel].forEach(panel => {
      panel?.classList.add('hidden');
      panel?.classList.remove('flex', 'flex-1', 'w-full');
    });

    // Show active panel
    const panelMap: Record<View, HTMLElement | null> = {
      [View.Records]: leftPanel,
      [View.Chat]: chatPanel,
      [View.Feed]: rightPanel,
    };
    const activePanel = panelMap[viewName];
    activePanel?.classList.remove('hidden');
    activePanel?.classList.add('flex', 'flex-1', 'w-full');
  }

  // Update mobile nav styles
  document.querySelectorAll('.mobile-nav-item').forEach(item => {
    const itemView = (item as HTMLElement).dataset.view;
    const label = item.querySelector('span');
    const isActive = itemView === viewName;

    item.classList.toggle('text-base-content/60', !isActive);
    item.classList.toggle('text-primary', isActive);
    label?.classList.toggle('font-bold', isActive);
  });
}

function handleResize(): void {
  if (window.innerWidth < MOBILE_BREAKPOINT) {
    let viewToShow = lastActivePanel || View.Chat;
    if (!lastActivePanel) {
      const path = window.location.pathname;
      if (path.includes('/records') || path.includes('/repository')) viewToShow = View.Records;
      else if (path.includes('/feed')) viewToShow = View.Feed;
    }
    setActiveView(viewToShow);
  } else {
    // Desktop: show all panels
    const panelIds = [PanelId.Left, PanelId.Chat, PanelId.Right];
    panelIds.forEach(id => {
      const panel = document.getElementById(id);
      panel?.classList.remove('hidden', 'w-full');
      panel?.classList.add('flex');
    });
  }
}

function initMobileNavigation(): void {
  const panelsContainer = document.getElementById('panels-container');
  if (panelsContainer) {
    const handlePanelInteraction = (e: Event): void => {
      const panel = getPanelForElement(e.target as Element);
      if (panel) lastActivePanel = panel;
    };
    panelsContainer.addEventListener('click', handlePanelInteraction);
    panelsContainer.addEventListener('focusin', handlePanelInteraction);
  }

  document.querySelectorAll('.mobile-nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      const view = (item as HTMLElement).dataset.view as View;
      setActiveView(view);
    });
  });

  if (window.innerWidth < MOBILE_BREAKPOINT) {
    setActiveView(lastActivePanel);
  }

  window.addEventListener('resize', handleResize);
  handleResize();
}

function initChatForm(): void {
  const chatPanel = document.getElementById(PanelId.Chat);
  if (!chatPanel) return;

  const chatMessages = chatPanel.querySelector('#chat-messages') as HTMLElement;
  const chatInput = chatPanel.querySelector('textarea');
  const chatSubmit = chatPanel.querySelector('#button-id-submit');
  const chatUserMessageTemplate = chatPanel.querySelector('#user-message-template') as HTMLTemplateElement;

  if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;

  chatSubmit?.addEventListener('htmx:beforeRequest', (event) => {
    const message = chatInput?.value.trim();
    if (message) {
      const clone = document.importNode(chatUserMessageTemplate.content, true);
      clone.querySelector('.user-message-content')!.textContent = message;
      chatMessages?.appendChild(clone);
      chatInput!.value = '';
      chatInput?.focus();
    } else {
      event.preventDefault();
    }
  });

  const chatAttach = document.getElementById('chat-attach');
  const uploadForm = document.getElementById('global-upload-form') as HTMLFormElement;
  const fileInput = uploadForm?.querySelector('input');
  chatAttach?.addEventListener('click', () => fileInput?.click());
}

function initFileUpload(): void {
  const hoverIndicator = document.getElementById('global-upload-hover');
  const uploadForm = document.getElementById('global-upload-form') as HTMLFormElement;
  const fileInput = uploadForm?.querySelector('input');

  if (!hoverIndicator || !uploadForm || !fileInput) return;

  window.addEventListener('dragover', (e) => {
    e.preventDefault();
    hoverIndicator.classList.add('border-primary', 'bg-base-300/50');
    hoverIndicator.classList.remove('border-transparent');
  });

  window.addEventListener('dragleave', (e) => {
    e.preventDefault();
    hoverIndicator.classList.remove('border-primary', 'bg-base-300/50');
    hoverIndicator.classList.add('border-transparent');
  });

  window.addEventListener('drop', (e) => {
    e.preventDefault();
    hoverIndicator.classList.remove('border-primary', 'bg-base-300/50');
    hoverIndicator.classList.add('border-transparent');

    const files = e.dataTransfer?.files;
    if (!files?.length) return;

    const validFiles = Array.from(files).filter(file =>
      ['application/pdf', 'text/plain'].includes(file.type)
    );

    if (validFiles.length < files.length) {
      alert('Unsupported file type. Please upload a PDF or plain text file.');
      return;
    }

    const dataTransfer = new DataTransfer();
    validFiles.forEach(file => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
    uploadForm.requestSubmit();
  });

  fileInput.addEventListener('change', () => uploadForm.requestSubmit());
}

function getExpandedPanel(panelId: PanelId): HTMLElement | null {
  const container = document.getElementById(panelId);
  if (!container) return null;
  return container.querySelector('.panel-expanded');
}

function initPanelResizing(): void {
  // Drag-to-resize state (shared across all panels)
  let isResizing = false;
  let currentPanelId: PanelId | null = null;
  let startX = 0;
  let startWidth = 0;

  const startResize = (e: MouseEvent, panelId: PanelId): void => {
    const expandedPanel = getExpandedPanel(panelId);
    if (!expandedPanel || expandedPanel.classList.contains('hidden')) return;

    isResizing = true;
    currentPanelId = panelId;
    startX = e.clientX;
    startWidth = parseInt(window.getComputedStyle(expandedPanel).width);
    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    e.preventDefault();
  };

  const resize = (e: MouseEvent): void => {
    if (!isResizing || !currentPanelId) return;

    const expandedPanel = getExpandedPanel(currentPanelId);
    if (!expandedPanel || expandedPanel.classList.contains('hidden')) return;

    const delta = currentPanelId === PanelId.Right ? (startX - e.clientX) : (e.clientX - startX);
    const newWidth = Math.max(240, Math.min(1200, startWidth + delta));

    // Set width directly on .panel-expanded (matches original working code)
    expandedPanel.style.width = newWidth + 'px';
  };

  const stopResize = (): void => {
    if (!isResizing) return;

    isResizing = false;
    document.body.style.cursor = '';
    document.body.style.userSelect = '';

    // Save widths to localStorage from .panel-expanded elements
    const leftExpanded = getExpandedPanel(PanelId.Left);
    const rightExpanded = getExpandedPanel(PanelId.Right);

    if (leftExpanded && leftExpanded.style.width) {
      localStorage.setItem(StorageKey.LeftPanelWidth, leftExpanded.style.width);
    }
    if (rightExpanded && rightExpanded.style.width) {
      localStorage.setItem(StorageKey.RightPanelWidth, rightExpanded.style.width);
    }

    currentPanelId = null;
  };

  // Attach global mouse handlers once
  document.addEventListener('mousemove', resize);
  document.addEventListener('mouseup', stopResize);

  // Apply saved panel widths from localStorage to .panel-expanded elements
  const applyPanelWidths = (): void => {
    const leftExpanded = getExpandedPanel(PanelId.Left);
    const rightExpanded = getExpandedPanel(PanelId.Right);

    // Only apply widths on desktop
    if (window.innerWidth >= MOBILE_BREAKPOINT) {
      const savedLeftWidth = localStorage.getItem(StorageKey.LeftPanelWidth);
      const savedRightWidth = localStorage.getItem(StorageKey.RightPanelWidth);

      if (leftExpanded && !leftExpanded.classList.contains('hidden') && savedLeftWidth) {
        leftExpanded.style.width = savedLeftWidth;
      }
      if (rightExpanded && !rightExpanded.classList.contains('hidden') && savedRightWidth) {
        rightExpanded.style.width = savedRightWidth;
      }
    } else {
      // On mobile, clear width styles
      if (leftExpanded) leftExpanded.style.width = '';
      if (rightExpanded) rightExpanded.style.width = '';
    }
  };

  // Function to setup a panel's resize handle (called on init and after HTMX swaps)
  const setupResizeHandle = (panelId: PanelId): void => {
    const handleId = panelId === PanelId.Left ? ResizeHandleId.Left : ResizeHandleId.Right;
    const handle = document.getElementById(handleId);

    if (!handle) return;

    // Remove old listener by cloning
    const newHandle = handle.cloneNode(true) as HTMLElement;
    handle.parentNode?.replaceChild(newHandle, handle);

    // Attach mousedown listener
    newHandle.addEventListener('mousedown', (e) => startResize(e, panelId));
  };

  // Setup both panels initially
  setupResizeHandle(PanelId.Left);
  setupResizeHandle(PanelId.Right);
  applyPanelWidths();

  // Apply panel widths on window resize (to handle desktop <-> mobile transitions)
  window.addEventListener('resize', () => {
    applyPanelWidths();
  });

  // After ANY HTMX swap, apply panel widths (matches original working implementation)
  document.body.addEventListener('htmx:afterSwap', (): void => {
    // Apply panel widths after a small delay (matches original working code)
    setTimeout(() => {
      applyPanelWidths();
    }, 0);
  });
}

function initHTMXHandlers(): void {
  document.body.addEventListener('htmx:afterSettle', (event: Event): void => {
    const detail = (event as CustomEvent).detail;
    if (!detail?.target) return;

    const swapTarget = detail.target;
    const triggeringElement = detail.elt;

    if (window.innerWidth < MOBILE_BREAKPOINT) {
      const targetId = swapTarget.id || '';
      let activePanel: View | null = null;

      if (triggeringElement) {
        activePanel = getPanelForElement(triggeringElement);
      }

      if (!activePanel) {
        if (targetId === PanelId.Left || swapTarget.closest?.(`#${PanelId.Left}`)) {
          activePanel = View.Records;
        } else if (targetId === PanelId.Chat || swapTarget.closest?.(`#${PanelId.Chat}`)) {
          activePanel = View.Chat;
        } else if (targetId === PanelId.Right || swapTarget.closest?.(`#${PanelId.Right}`)) {
          activePanel = View.Feed;
        }
      }

      if (targetId === 'modal-container' || swapTarget.closest?.('#modal-container')) {
        requestAnimationFrame(() => setActiveView(lastActivePanel));
        return;
      }

      if (activePanel) {
        lastActivePanel = activePanel;
        requestAnimationFrame(() => setActiveView(lastActivePanel));
      }
    }
  });
}

export function initPatientWorkspace(): void {
  const chatPanel = document.getElementById(PanelId.Chat);
  if (!chatPanel) return; // Not on patient workspace page

  initMobileNavigation();
  initChatForm();
  initFileUpload();
  initPanelResizing();
  initHTMXHandlers();
}
