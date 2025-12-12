class ListPreferences extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.columns = [];
    this.defaultSort = 'Updated (Descending)';
    this.itemsPerPage = 25;
  }

  connectedCallback() {
    this.render();
  }

  setColumns(columns) {
    this.columns = columns.map((col, index) => ({
      id: index + 1,
      name: col,
      visible: true,
    }));
    this.render();
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        * {
          box-sizing: border-box;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
          opacity: 0;
          transition: opacity 0.2s ease;
        }

        .modal-overlay.show {
          opacity: 1;
        }

        .modal {
          background: white;
          border-radius: 12px;
          max-width: 768px;
          width: 90%;
          max-height: 90vh;
          display: flex;
          flex-direction: column;
          box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
          transform: scale(0.9);
          transition: transform 0.2s ease;
        }

        .modal-overlay.show .modal {
          transform: scale(1);
        }

        .modal-header {
          padding: 24px;
          border-bottom: 1px solid rgba(11, 18, 32, 0.1);
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .modal-title {
          font-size: 20px;
          font-weight: 700;
          color: #0b1220;
          margin: 0;
          font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
        }

        .close-btn {
          background: none;
          border: none;
          cursor: pointer;
          padding: 8px;
          color: #6c757d;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          width: 40px;
          height: 40px;
          transition: background 0.2s;
        }

        .close-btn:hover {
          background: #f8f9fa;
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
          -webkit-font-feature-settings: 'liga';
          -webkit-font-smoothing: antialiased;
        }

        .modal-body {
          padding: 24px;
          overflow-y: auto;
          flex: 1;
          font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
        }

        .info-banner {
          background: #0891b2;
          color: white;
          padding: 16px;
          border-radius: 8px;
          display: flex;
          align-items: flex-start;
          gap: 12px;
          margin-bottom: 24px;
        }

        .info-banner .material-symbols-outlined {
          flex-shrink: 0;
          font-size: 24px;
        }

        .info-text {
          font-size: 14px;
          line-height: 1.5;
          margin: 0;
        }

        .section-title {
          font-size: 14px;
          font-weight: 600;
          color: #6c757d;
          margin: 0 0 8px 0;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .section-subtitle {
          font-size: 13px;
          color: #6c757d;
          margin: 0 0 12px 0;
        }

        .columns-list {
          background: #f8f9fa;
          border-radius: 8px;
          padding: 8px;
          margin-bottom: 24px;
        }

        .column-item {
          background: white;
          border: 1px solid rgba(11, 18, 32, 0.06);
          border-radius: 6px;
          padding: 12px 16px;
          margin-bottom: 8px;
          display: flex;
          align-items: center;
          gap: 12px;
          transition: box-shadow 0.2s;
          cursor: move;
        }

        .column-item:last-child {
          margin-bottom: 0;
        }

        .column-item:hover {
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .drag-handle {
          color: #adb5bd;
          cursor: move;
          font-size: 20px;
        }

        .checkbox-wrapper {
          display: flex;
          align-items: center;
        }

        .column-checkbox {
          width: 20px;
          height: 20px;
          cursor: pointer;
          accent-color: #0891b2;
        }

        .column-name {
          flex: 1;
          font-size: 14px;
          color: #0b1220;
          font-weight: 500;
        }

        .add-fields-btn {
          width: 100%;
          background: transparent;
          border: 2px dashed rgba(11, 18, 32, 0.2);
          border-radius: 8px;
          padding: 16px;
          cursor: pointer;
          font-size: 14px;
          font-weight: 600;
          color: #495057;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          transition: all 0.2s;
          margin-bottom: 24px;
        }

        .add-fields-btn:hover {
          border-color: #0891b2;
          color: #0891b2;
        }

        .form-group {
          margin-bottom: 24px;
        }

        .form-label {
          display: block;
          font-size: 14px;
          font-weight: 600;
          color: #495057;
          margin-bottom: 8px;
        }

        .form-select {
          width: 100%;
          padding: 12px 16px;
          font-size: 14px;
          color: #0b1220;
          background: white;
          border: 1px solid rgba(11, 18, 32, 0.2);
          border-radius: 8px;
          cursor: pointer;
          font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
          appearance: none;
          background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1.5L6 6.5L11 1.5' stroke='%236c757d' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
          background-repeat: no-repeat;
          background-position: right 16px center;
          padding-right: 40px;
        }

        .form-select:focus {
          outline: none;
          border-color: #0891b2;
          box-shadow: 0 0 0 3px rgba(8, 145, 178, 0.1);
        }

        .modal-footer {
          padding: 24px;
          border-top: 1px solid rgba(11, 18, 32, 0.1);
          display: flex;
          gap: 12px;
          justify-content: flex-end;
        }

        .btn {
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          border: none;
          font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial;
        }

        .btn-secondary {
          background: white;
          color: #0b1220;
          border: 1px solid rgba(11, 18, 32, 0.2);
        }

        .btn-secondary:hover {
          background: #f8f9fa;
        }

        .btn-tertiary {
          background: transparent;
          color: #6c757d;
        }

        .btn-tertiary:hover {
          background: #f8f9fa;
        }

        .btn-primary {
          background: #0891b2;
          color: white;
        }

        .btn-primary:hover {
          background: #0e7490;
        }
      </style>

      <div class="modal-overlay" id="modalOverlay">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">List Preferences</h2>
            <button class="close-btn" id="closeBtn">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>

          <div class="modal-body">
            <div class="info-banner">
              <span class="material-symbols-outlined">info</span>
              <p class="info-text">
                You have customized preferences. Click 'Reset to Defaults' to use organization defaults.
              </p>
            </div>

            <div class="columns-section">
              <h3 class="section-title">Visible Columns</h3>
              <p class="section-subtitle">Tip: Drag columns to reorder them in the table</p>

              <div class="columns-list" id="columnsList">
                ${this.columns
                  .map(
                    (col) => `
                  <div class="column-item" draggable="true" data-id="${col.id}">
                    <span class="material-symbols-outlined drag-handle">drag_indicator</span>
                    <div class="checkbox-wrapper">
                      <input
                        type="checkbox"
                        class="column-checkbox"
                        id="col-${col.id}"
                        ${col.visible ? 'checked' : ''}
                        data-id="${col.id}"
                      />
                    </div>
                    <label class="column-name" for="col-${col.id}">${col.name}</label>
                  </div>
                `
                  )
                  .join('')}
              </div>

              <button class="add-fields-btn">
                <span class="material-symbols-outlined">add</span>
                Add or edit fields
              </button>
            </div>

            <div class="form-group">
              <label class="form-label" for="defaultSort">Default Sort</label>
              <select class="form-select" id="defaultSort">
                <option value="updated-desc" ${
                  this.defaultSort === 'Updated (Descending)' ? 'selected' : ''
                }>Last Updated (Descending)</option>
                <option value="updated-asc">Last Updated (Ascending)</option>
                <option value="created-desc">Created (Descending)</option>
                <option value="created-asc">Created (Ascending)</option>
                <option value="name-asc">Name (A-Z)</option>
                <option value="name-desc">Name (Z-A)</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label" for="itemsPerPage">Items per page</label>
              <select class="form-select" id="itemsPerPage">
                <option value="10">10</option>
                <option value="25" ${this.itemsPerPage === 25 ? 'selected' : ''}>25</option>
                <option value="50">50</option>
                <option value="100">100</option>
              </select>
            </div>
          </div>

          <div class="modal-footer">
            <button class="btn btn-tertiary" id="resetBtn">Reset to Defaults</button>
            <button class="btn btn-secondary" id="cancelBtn">Cancel</button>
            <button class="btn btn-primary" id="saveBtn">Save Preferences</button>
          </div>
        </div>
      </div>
    `;

    // Attach event listeners after render
    this.attachEventListeners();
  }

  attachEventListeners() {
    const overlay = this.shadowRoot.getElementById('modalOverlay');
    const closeBtn = this.shadowRoot.getElementById('closeBtn');
    const cancelBtn = this.shadowRoot.getElementById('cancelBtn');
    const saveBtn = this.shadowRoot.getElementById('saveBtn');
    const resetBtn = this.shadowRoot.getElementById('resetBtn');

    // Close handlers
    closeBtn?.addEventListener('click', () => this.close());
    cancelBtn?.addEventListener('click', () => this.close());

    // Click outside to close
    overlay?.addEventListener('click', (e) => {
      if (e.target === overlay) {
        this.close();
      }
    });

    // Save handler
    saveBtn?.addEventListener('click', () => {
      this.savePreferences();
    });

    // Reset handler
    resetBtn?.addEventListener('click', () => {
      this.resetToDefaults();
    });

    // Drag and drop
    this.setupDragAndDrop();

    // Checkbox handlers
    const checkboxes = this.shadowRoot.querySelectorAll('.column-checkbox');
    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener('change', (e) => {
        const id = parseInt(e.target.dataset.id);
        const column = this.columns.find((col) => col.id === id);
        if (column) {
          column.visible = e.target.checked;
        }
      });
    });
  }

  setupDragAndDrop() {
    const columnsList = this.shadowRoot.getElementById('columnsList');
    const items = this.shadowRoot.querySelectorAll('.column-item');

    let draggedItem = null;

    items.forEach((item) => {
      item.addEventListener('dragstart', (e) => {
        draggedItem = item;
        item.style.opacity = '0.5';
      });

      item.addEventListener('dragend', (e) => {
        item.style.opacity = '1';
      });

      item.addEventListener('dragover', (e) => {
        e.preventDefault();
      });

      item.addEventListener('drop', (e) => {
        e.preventDefault();
        if (draggedItem !== item) {
          const allItems = [...columnsList.querySelectorAll('.column-item')];
          const draggedIndex = allItems.indexOf(draggedItem);
          const targetIndex = allItems.indexOf(item);

          if (draggedIndex < targetIndex) {
            item.after(draggedItem);
          } else {
            item.before(draggedItem);
          }

          // Update column order
          this.updateColumnOrder();
        }
      });
    });
  }

  updateColumnOrder() {
    const items = this.shadowRoot.querySelectorAll('.column-item');
    const newOrder = [];
    items.forEach((item) => {
      const id = parseInt(item.dataset.id);
      const column = this.columns.find((col) => col.id === id);
      if (column) {
        newOrder.push(column);
      }
    });
    this.columns = newOrder;
  }

  savePreferences() {
    const defaultSort = this.shadowRoot.getElementById('defaultSort').value;
    const itemsPerPage = this.shadowRoot.getElementById('itemsPerPage').value;

    const preferences = {
      columns: this.columns,
      defaultSort,
      itemsPerPage: parseInt(itemsPerPage),
    };

    this.dispatchEvent(
      new CustomEvent('preferences-saved', {
        detail: preferences,
        bubbles: true,
        composed: true,
      })
    );

    this.close();
  }

  resetToDefaults() {
    // Reset all columns to visible
    this.columns.forEach((col) => (col.visible = true));
    this.defaultSort = 'Updated (Descending)';
    this.itemsPerPage = 25;
    this.render();
    this.attachEventListeners();
  }

  open() {
    this.style.display = 'block';
    // Trigger animation
    requestAnimationFrame(() => {
      const overlay = this.shadowRoot.getElementById('modalOverlay');
      overlay?.classList.add('show');
    });
  }

  close() {
    const overlay = this.shadowRoot.getElementById('modalOverlay');
    overlay?.classList.remove('show');

    setTimeout(() => {
      this.style.display = 'none';
    }, 200);
  }
}

customElements.define('list-preferences', ListPreferences);
