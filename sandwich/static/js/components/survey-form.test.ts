import { describe, it, expect, beforeEach, vi } from 'vitest';

import { SurveyForm } from './survey-form';

describe('SurveyForm custom element', () => {
  // Note: tests asserting survey-core internals / render calls rely
  // on E2E Playwright tests elsewhere since they depend on browser
  // behavior.

  beforeEach(() => {
    // Ensure custom element isn't registered between tests
    if (!customElements.get('survey-form')) {
      // Register the element for jsdom tests. This is idempotent across runs.
      customElements.define('survey-form', SurveyForm as any);
    }
  });

  it('shows friendly error when JSON invalid', async () => {
    const el = new SurveyForm();
    // Place the script in the document and reference it by id via data-schema-id
    const script = document.createElement('script');
    script.type = 'application/json';
    script.id = 'form_schema';
    script.textContent = '{invalid-json}';
    document.body.appendChild(script);

    el.setAttribute('data-schema-id', 'form_schema');
    document.body.appendChild(el);

    // Manually trigger connected lifecycle in JSDOM and allow the microtask tick
    el.connectedCallback();
    await new Promise((resolve) => setTimeout(resolve, 0));

    // Container was created but it shows the error message
    const container = el.querySelector('[data-survey-container]');
    expect(container).toBeTruthy();
    expect(container?.textContent).toContain('Failed to load form');

    document.body.removeChild(el);
    document.body.removeChild(script);
  });

  it('shows message when no data-schema-id script present', async () => {
    const el = new SurveyForm();
    // No script in the document and no data-schema-id -> should show the helper message
    document.body.appendChild(el);

    el.connectedCallback();
    await new Promise((r) => setTimeout(r, 0));

    // Container was created but it shows the no data message
    const container = el.querySelector('[data-survey-container]');
    expect(container).toBeTruthy();
    expect(container?.textContent).toContain('No form data provided.');

    document.body.removeChild(el);
  });

  it('initSurvey throws when target not found', () => {
    expect(() =>
      SurveyForm.initSurvey('non-existent-id', { title: 'x' }),
    ).toThrow(/\[survey-form\] initSurvey: target element not found/);
  });

  it('throws when the internal container element is missing', () => {
    const el = new SurveyForm();
    const script = document.createElement('script');
    script.type = 'application/json';
    script.id = 'form_schema';
    script.textContent = JSON.stringify({ title: 'x' });
    document.body.appendChild(script);

    el.setAttribute('data-schema-id', 'form_schema');

    expect(() => (el as any)._initFromSchemaId()).toThrow(
      /\[survey-form\] container not found/,
    );

    document.body.removeChild(script);
  });

  it('normal flow: loads and calls render', async () => {
    const el = new SurveyForm();
    const script = document.createElement('script');
    script.type = 'application/json';
    script.id = 'form_schema';
    script.textContent = JSON.stringify({ title: 'Test Survey' });
    document.body.appendChild(script);

    el.setAttribute('data-schema-id', 'form_schema');
    document.body.appendChild(el);

    // Spy on the render method of the SurveyJS Model prototype
    const renderSpy = vi.spyOn(
      (await import('survey-core')).Model.prototype,
      'render',
    );

    el.connectedCallback();
    await new Promise((r) => setTimeout(r, 0));

    // No explosions here

    expect(renderSpy).toHaveBeenCalled();

    document.body.removeChild(el);
    document.body.removeChild(script);
  });
});
