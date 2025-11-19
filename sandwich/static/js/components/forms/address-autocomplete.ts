import { ComponentCollection } from 'survey-core';

export function registerAddressComponent() {
  ComponentCollection.Instance.add({
    name: 'addressautocomplete',
    title: 'Address',
    defaultQuestionTitle: 'Enter your address:',
    elementsJSON: [
      {
        type: 'text',
        name: 'fullAddress',
        title: 'Address',
        placeholder: '495 Grove Street, New York, NY 10014',
      },
    ],
    onLoaded(question) {
      console.log('address.onLoaded');
      if (!question.isDesignMode) {
        console.log('Runtime mode - setting up address autocomplete');
        // TODO: Configure address autocomplete here.
      } else {
        console.log('Design mode - skipping address autocomplete setup');
      }
    },
  });
}
