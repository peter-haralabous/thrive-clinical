class PatientTimeline extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this.timeline = null;
  }

  connectedCallback() {
    this.render();
  }

  disconnectedCallback() {
    if (this.timeline) {
      this.timeline.destroy();
    }
  }

  getSampleData() {
    // Sample timeline data - can be replaced with real patient data
    const items = [
      {
        id: 1,
        content: 'Annual Physical Exam',
        start: '2024-01-15',
        type: 'point',
        className: 'encounter',
      },
      {
        id: 2,
        content: 'Lab Results - Blood Panel',
        start: '2024-01-20',
        type: 'point',
        className: 'lab',
      },
      {
        id: 3,
        content: 'Prescription - Lisinopril 10mg',
        start: '2024-01-15',
        end: '2024-12-31',
        type: 'range',
        className: 'medication',
      },
      {
        id: 4,
        content: 'Follow-up Appointment',
        start: '2024-03-15',
        type: 'point',
        className: 'encounter',
      },
      {
        id: 5,
        content: 'Flu Vaccination',
        start: '2024-02-01',
        type: 'point',
        className: 'immunization',
      },
      {
        id: 6,
        content: 'Allergy - Penicillin',
        start: '2023-06-10',
        type: 'point',
        className: 'allergy',
      },
      {
        id: 7,
        content: 'Diagnosis - Hypertension',
        start: '2023-08-20',
        end: '2024-12-31',
        type: 'range',
        className: 'condition',
      },
      {
        id: 8,
        content: 'Lab - A1C Test',
        start: '2024-04-10',
        type: 'point',
        className: 'lab',
      },
    ];

    return items;
  }

  initializeTimeline() {
    const container = this.shadowRoot.getElementById('timeline-container');
    const items = this.getSampleData();

    const options = {
      height: '600px',
      margin: {
        item: 20,
      },
      orientation: 'top',
      showCurrentTime: true,
      zoomMin: 1000 * 60 * 60 * 24 * 7, // 1 week
      zoomMax: 1000 * 60 * 60 * 24 * 365 * 5, // 5 years
      tooltip: {
        followMouse: true,
        overflowMethod: 'cap',
      },
    };

    // Initialize vis-timeline
    this.timeline = new vis.Timeline(container, items, options);
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        * {
          box-sizing: border-box;
        }

        :host {
          display: block;
          width: 100%;
          height: 100%;
        }

        .timeline-wrapper {
          width: 100%;
          height: 100%;
          padding: 24px;
          background: #ffffff;
        }

        .timeline-header {
          margin-bottom: 24px;
        }

        .timeline-header h2 {
          margin: 0 0 8px 0;
          font-size: 24px;
          font-weight: 600;
          color: #1f2937;
        }

        .timeline-header p {
          margin: 0;
          font-size: 14px;
          color: #6b7280;
        }

        .timeline-legend {
          display: flex;
          gap: 16px;
          margin-bottom: 16px;
          flex-wrap: wrap;
        }

        .legend-item {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: #4b5563;
        }

        .legend-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }

        .legend-dot.encounter {
          background: #3b82f6;
        }

        .legend-dot.lab {
          background: #8b5cf6;
        }

        .legend-dot.medication {
          background: #10b981;
        }

        .legend-dot.immunization {
          background: #f59e0b;
        }

        .legend-dot.allergy {
          background: #ef4444;
        }

        .legend-dot.condition {
          background: #ec4899;
        }

        #timeline-container {
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          background: #ffffff;
        }

        /* vis-timeline custom styling */
        #timeline-container ::ng-deep .vis-item.encounter {
          background-color: #3b82f6;
          border-color: #2563eb;
          color: white;
        }

        #timeline-container ::ng-deep .vis-item.lab {
          background-color: #8b5cf6;
          border-color: #7c3aed;
          color: white;
        }

        #timeline-container ::ng-deep .vis-item.medication {
          background-color: #10b981;
          border-color: #059669;
          color: white;
        }

        #timeline-container ::ng-deep .vis-item.immunization {
          background-color: #f59e0b;
          border-color: #d97706;
          color: white;
        }

        #timeline-container ::ng-deep .vis-item.allergy {
          background-color: #ef4444;
          border-color: #dc2626;
          color: white;
        }

        #timeline-container ::ng-deep .vis-item.condition {
          background-color: #ec4899;
          border-color: #db2777;
          color: white;
        }
      </style>

      <link rel="stylesheet" href="https://unpkg.com/vis-timeline@7.7.3/styles/vis-timeline-graph2d.min.css" />
      <script src="https://unpkg.com/vis-timeline@7.7.3/standalone/umd/vis-timeline-graph2d.min.js"></script>

      <div class="timeline-wrapper">
        <div class="timeline-header">
          <h2>Patient Timeline</h2>
          <p>View all patient health events, encounters, and milestones in chronological order</p>
        </div>

        <div class="timeline-legend">
          <div class="legend-item">
            <span class="legend-dot encounter"></span>
            <span>Encounters</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot lab"></span>
            <span>Labs</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot medication"></span>
            <span>Medications</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot immunization"></span>
            <span>Immunizations</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot allergy"></span>
            <span>Allergies</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot condition"></span>
            <span>Conditions</span>
          </div>
        </div>

        <div id="timeline-container"></div>
      </div>
    `;

    // Load vis-timeline library if not already loaded
    if (typeof vis === 'undefined') {
      const script = document.createElement('script');
      script.src =
        'https://unpkg.com/vis-timeline@7.7.3/standalone/umd/vis-timeline-graph2d.min.js';
      script.onload = () => {
        this.initializeTimeline();
      };
      document.head.appendChild(script);
    } else {
      // Library already loaded, initialize immediately
      setTimeout(() => this.initializeTimeline(), 0);
    }
  }
}

customElements.define('patient-timeline', PatientTimeline);
