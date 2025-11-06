import { SurveyCreator } from 'survey-creator-js';

document.addEventListener('DOMContentLoaded', () => {
  const creatorOptions = {
    autoSaveEnabled: true,
    collapseOnDrag: true,
  };

  const creator = new SurveyCreator(creatorOptions);
  const creatorContainer = document.getElementById('form-builder-container');
  if (creatorContainer) {
    creator.render(creatorContainer);
  }
});
