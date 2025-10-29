import { LitElement, html, type TemplateResult } from 'lit';
import { Model } from 'survey-core';
import { LayeredLightPanelless } from 'survey-core/themes';

type SurveyJson = Record<string, unknown> | Array<unknown>;

export class SurveyForm extends LitElement {
  private _containerId = `survey-form-${Math.random().toString(36).slice(2, 9)}-container`;

  createRenderRoot(): HTMLElement {
    return this as unknown as HTMLElement;
  }

  render(): TemplateResult {
    return html`<div
      id="${this._containerId}"
      data-survey-container="1"
    ></div>`;
  }

  connectedCallback(): void {
    super.connectedCallback();
    this.updateComplete.then(() => this._initFromSchemaId());
  }

  /** Locate the schema script by id from `data-schema-id`. */
  private _findSchemaScriptById(): HTMLScriptElement | null {
    const attr = this.getAttribute('data-schema-id');
    if (!attr) return null;
    const el = this.ownerDocument.getElementById(
      attr,
    ) as HTMLScriptElement | null;
    if (
      el &&
      el.tagName.toLowerCase() === 'script' &&
      el.type === 'application/json'
    ) {
      return el;
    }
    return null;
  }

  static initSurvey(elementId: string, json: SurveyJson): Model {
    // Resolve the target element once and fail fast if it's missing.
    const targetEl = document.getElementById(elementId) as HTMLElement | null;
    if (!targetEl) {
      throw new Error(
        `[survey-form] initSurvey: target element not found: ${elementId}`,
      );
    }

    // SurveyJS Model expects a loosely-typed config; cast from our safer
    // SurveyJson to `any` for the library boundary.
    const model = new Model(json as any);

    // Mark the target element when rendering is complete, for E2E test hooks.
    model.onAfterRenderSurvey.add(() =>
      targetEl.setAttribute('data-survey-rendered', '1'),
    );

    // TODO(JL): create and set a Thrive specific theme
    model.applyTheme(LayeredLightPanelless);

    // Render the survey into the target element
    model.render(targetEl);

    return model;
  }

  private _initFromSchemaId(): void {
    const script = this._findSchemaScriptById();
    if (!this.id)
      this.id = `survey-form-${Math.random().toString(36).slice(2, 9)}`;

    const container = this.ownerDocument.getElementById(
      this._containerId,
    ) as HTMLElement | null;
    if (!container) throw new Error('[survey-form] container not found');

    if (!script) {
      container.textContent = 'No form data provided.';
      return;
    }

    let json: SurveyJson;
    try {
      json = JSON.parse(script.textContent || '{}') as SurveyJson;
    } catch (e) {
      container.textContent = 'Failed to load form: invalid JSON.';
      return;
    }

    SurveyForm.initSurvey(container.id, json);
  }
}
