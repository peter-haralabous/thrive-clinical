import { ComponentCollection, Question } from 'survey-core';

export function registerAddressComponent() {
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
