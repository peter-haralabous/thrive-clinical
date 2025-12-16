class EncounterHeader extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }

  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  static get observedAttributes() {
    return ['date', 'patient-name'];
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  get date() {
    return this.getAttribute('date') || '';
  }

  get patientName() {
    return this.getAttribute('patient-name') || '';
  }

  render() {
    this.shadowRoot.innerHTML = `
      <link
        href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"
        rel="stylesheet"
      />
      <style>
        * {
          box-sizing: border-box;
        }

        .material-symbols-outlined {
          font-family: 'Material Symbols Outlined';
          font-weight: normal;
          font-style: normal;
          font-size: 24px;
          line-height: 1;
          letter-spacing: normal;
          text-transform: none;
          display: inline-block;
          white-space: nowrap;
          word-wrap: normal;
          direction: ltr;
          font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
        }

        :host {
          display: block;
          margin-bottom: 1rem;
        }

        .encounter-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
        }

        .encounter-title {
          font-size: 1.5rem;
          line-height: 2rem;
          font-weight: 700;
          color: #1f2937;
          margin: 0;
        }

        .actions {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .send-form-btn {
          display: flex;
          flex-shrink:0;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 1rem;
          background-color: #2563eb;
          color: white;
          border: none;
          border-radius: 0.5rem;
          font-weight: 500;
          font-size: 0.875rem;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .send-form-btn:hover {
          background-color: #1d4ed8;
        }

        .send-form-btn:focus {
          outline: 2px solid #3b82f6;
          outline-offset: 2px;
        }

        .icon {
          font-size: 1.125rem;
          line-height: 1;
        }

        .menu-container {
          position: relative;
        }

        .menu-btn {
          padding: 0.5rem;
          background: transparent;
          border: none;
          border-radius: 0.5rem;
          cursor: pointer;
          color: #1f2937;
          transition: background-color 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .menu-btn:hover {
          background-color: #f3f4f6;
        }

        .menu-btn:focus {
          outline: 2px solid #3b82f6;
          outline-offset: 2px;
        }

        .menu-dropdown {
          position: absolute;
          top: calc(100% + 0.5rem);
          right: 0;
          width: 12rem;
          background-color: white;
          border-radius: 0.5rem;
          box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
          border: 1px solid #e5e7eb;
          overflow: hidden;
          z-index: 50;
          display: none;
        }

        .menu-dropdown.show {
          display: block;
        }

        .menu-item {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.625rem 1rem;
          background: transparent;
          border: none;
          text-align: left;
          font-size: 0.875rem;
          color: #1f2937;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .menu-item:hover {
          background-color: #f9fafb;
        }

        .menu-item.archive {
          color: #dc2626;
          border-top: 1px solid #e5e7eb;
        }

        .menu-item.archive:hover {
          background-color: #fef2f2;
        }

        @media (prefers-color-scheme: dark) {
          .encounter-title {
            color: white;
          }

          .menu-btn {
            color: white;
          }

          .menu-btn:hover {
            background-color: #374151;
          }

          .menu-dropdown {
            background-color: #1f2937;
            border-color: #374151;
          }

          .menu-item {
            color: #f9fafb;
          }

          .menu-item:hover {
            background-color: #111827;
          }

          .menu-item.archive {
            color: #f87171;
            border-top-color: #374151;
          }

          .menu-item.archive:hover {
            background-color: rgba(220, 38, 38, 0.2);
          }
        }
      </style>

      <div class="encounter-header">
        <h1 class="encounter-title">Encounter • ${this.date}</h1>
        <div class="actions">
          <button class="send-form-btn" id="send-form-btn">
            <span class="material-symbols-outlined icon">send</span>
            <span>Send Form</span>
          </button>
          <div class="menu-container">
            <button class="menu-btn" id="menu-btn">
              <span class="material-symbols-outlined icon">more_vert</span>
            </button>
            <div class="menu-dropdown" id="menu-dropdown">
              <button class="menu-item" id="add-note-btn">
                <span class="material-symbols-outlined icon">note_add</span>
                <span>Add Note</span>
              </button>
              <button class="menu-item archive" id="archive-btn">
                <span class="material-symbols-outlined icon">archive</span>
                <span>Archive Encounter</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  setupEventListeners() {
    const sendFormBtn = this.shadowRoot.getElementById('send-form-btn');
    const menuBtn = this.shadowRoot.getElementById('menu-btn');
    const menuDropdown = this.shadowRoot.getElementById('menu-dropdown');
    const viewPatientBtn = this.shadowRoot.getElementById('view-patient-btn');
    const addNoteBtn = this.shadowRoot.getElementById('add-note-btn');
    const archiveBtn = this.shadowRoot.getElementById('archive-btn');

    sendFormBtn.addEventListener('click', () => {
      this.dispatchEvent(
        new CustomEvent('send-form', {
          bubbles: true,
          composed: true,
          detail: { patientName: this.patientName },
        })
      );
    });

    menuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const wasOpen = menuDropdown.classList.contains('show');
      menuDropdown.classList.toggle('show');

      // If we just opened the dropdown, set up a one-time click handler
      if (!wasOpen) {
        setTimeout(() => {
          const clickOutsideHandler = (e) => {
            const path = e.composedPath();
            if (!path.includes(menuDropdown) && !path.includes(menuBtn)) {
              menuDropdown.classList.remove('show');
              document.removeEventListener('click', clickOutsideHandler);
            }
          };
          document.addEventListener('click', clickOutsideHandler);
        }, 0);
      }
    });

    viewPatientBtn.addEventListener('click', () => {
      menuDropdown.classList.remove('show');
      this.dispatchEvent(
        new CustomEvent('view-patient', {
          bubbles: true,
          composed: true,
        })
      );
    });

    addNoteBtn.addEventListener('click', () => {
      menuDropdown.classList.remove('show');
      this.dispatchEvent(
        new CustomEvent('add-note', {
          bubbles: true,
          composed: true,
        })
      );
    });

    archiveBtn.addEventListener('click', () => {
      menuDropdown.classList.remove('show');
      this.dispatchEvent(
        new CustomEvent('archive-encounter', {
          bubbles: true,
          composed: true,
        })
      );
    });
  }
}

customElements.define('encounter-header', EncounterHeader);
