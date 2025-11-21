import { ComponentCollection } from 'survey-core';

export function registerAddressComponent() {
  // Check if already registered to avoid errors in test environments
  if (
    ComponentCollection.Instance.getCustomQuestionByName('addressautocomplete')
  ) {
    return;
  }

  ComponentCollection.Instance.add({
    name: 'addressautocomplete',
    title: 'Address',
    defaultQuestionTitle: 'Enter your address',
    elementsJSON: [
      {
        type: 'dropdown',
        name: 'suggested_addresses',
        title: 'Address',
        choicesLazyLoadEnabled: true,
        resetValueIf: '{option.filter} empty',
      },
    ],
  });
}
