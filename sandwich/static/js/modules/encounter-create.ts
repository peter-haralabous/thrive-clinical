/**
 * Patient selection and encounter form functionality
 */

export interface PatientData {
  id: string;
  name: string;
  email: string;
  dob: string;
  phn: string;
}

export class EncounterCreateController {
  private selectedPatientId: string | null = null;

  constructor() {
    this.initialize();
  }

  private initialize(): void {
    // Add event listener for clear patient button
    const clearButton = document.getElementById('clear-patient-btn');
    if (clearButton) {
      clearButton.addEventListener('click', () => this.clearSelectedPatient());
    }

    // Add event delegation for patient selection from search results
    const searchResults = document.getElementById('patient-search-results');
    if (searchResults) {
      searchResults.addEventListener('click', (e) => {
        const button = (e.target as Element).closest(
          '.patient-select-btn',
        ) as HTMLElement;
        if (button) {
          this.selectPatientFromData(button);
        }
      });
    }

    // If there's already a patient selected (form errors), show the form
    const patientField = document.querySelector(
      'input[name="patient"]',
    ) as HTMLInputElement;
    if (patientField && patientField.value) {
      const formContainer = document.getElementById('encounter-form-container');
      if (formContainer) {
        formContainer.classList.remove('hidden');
      }
    }
  }

  public selectPatient(patientData: PatientData): void {
    this.selectedPatientId = patientData.id;

    // Hide search results and show selected patient
    const searchResults = document.getElementById('patient-search-results');
    const searchInput = document.getElementById(
      'patient-search',
    ) as HTMLInputElement;
    const selectedPatientName = document.getElementById(
      'selected-patient-name',
    );
    const selectedPatient = document.getElementById('selected-patient');

    if (searchResults) {
      searchResults.innerHTML = '';
    }

    if (searchInput) {
      searchInput.value = '';
    }

    if (selectedPatientName) {
      selectedPatientName.textContent = `${patientData.name} • DOB: ${patientData.dob || 'None'} • PHN: ${patientData.phn || 'None'}`;
    }

    if (selectedPatient) {
      selectedPatient.classList.remove('hidden');
    }

    // Show the encounter form and set the patient
    const formContainer = document.getElementById('encounter-form-container');
    if (formContainer) {
      formContainer.classList.remove('hidden');
    }

    // Set the hidden patient field
    const patientField = document.querySelector(
      'input[name="patient"]',
    ) as HTMLInputElement;
    if (patientField) {
      patientField.value = patientData.id;
    }
  }

  private selectPatientFromData(element: HTMLElement): void {
    const patientData: PatientData = {
      id: element.dataset.patientId || '',
      name: element.dataset.patientName || '',
      email: element.dataset.patientEmail || '',
      dob: element.dataset.patientDob || '',
      phn: element.dataset.patientPhn || '',
    };

    this.selectPatient(patientData);
  }

  private clearSelectedPatient(): void {
    this.selectedPatientId = null;

    const selectedPatient = document.getElementById('selected-patient');
    const formContainer = document.getElementById('encounter-form-container');
    const searchInput = document.getElementById(
      'patient-search',
    ) as HTMLInputElement;

    if (selectedPatient) {
      selectedPatient.classList.add('hidden');
    }

    if (formContainer) {
      formContainer.classList.add('hidden');
    }

    if (searchInput) {
      searchInput.focus();
    }
  }

  public getSelectedPatientId(): string | null {
    return this.selectedPatientId;
  }
}

// Auto-initialize on pages with encounter create functionality
document.addEventListener('DOMContentLoaded', () => {
  // div in the encounter_create template has the data-encounter-create-page attribute
  const encounterCreatePage = document.querySelector(
    '[data-encounter-create-page]',
  );
  if (encounterCreatePage) {
    new EncounterCreateController();
  }
});
