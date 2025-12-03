import { ComponentCollection, SvgRegistry } from 'survey-core';

export function registerMedicationComponents() {
  // Check if already registered to avoid errors in test environments
  if (
    !ComponentCollection.Instance.getCustomQuestionByName(
      'medication-multi-select',
    )
  ) {
    // Register lucide pill-bottle svg
    const pillBottleIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="var(--sjs-primary-background-500)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-pill-bottle-icon lucide-pill-bottle"><path d="M18 11h-4a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h4"/><path d="M6 7v13a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V7"/><rect width="16" height="5" x="4" y="2" rx="1"/></svg>`;
    SvgRegistry.registerIcon('icon-pill-bottle', pillBottleIcon);

    ComponentCollection.Instance.add({
      name: 'medication-multi-select',
      title: 'Medication Multi-select',
      iconName: 'icon-pill-bottle',
      questionJSON: {
        name: 'medication_multi_select',
        title: 'Select Medications',
        type: 'tagbox',
        choicesLazyLoadEnabled: true,
        resetValueIf: '{option.filter} empty',
      },
    });
  }

  if (
    !ComponentCollection.Instance.getCustomQuestionByName('medication-select')
  ) {
    const pillIcon = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="var(--sjs-primary-background-500)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-pill-icon lucide-pill"><path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7Z"/><path d="m8.5 8.5 7 7"/></svg>`;
    SvgRegistry.registerIcon('icon-pill', pillIcon);

    ComponentCollection.Instance.add({
      name: 'medication-select',
      title: 'Medication Select',
      iconName: 'icon-pill',
      questionJSON: {
        name: 'medication_select',
        title: 'Select Medication',
        type: 'dropdown',
        choicesLazyLoadEnabled: true,
        resetValueIf: '{option.filter} empty',
      },
    });
  }
}
