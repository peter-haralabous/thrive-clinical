import { LitElement, html, css, type PropertyValues } from 'lit';
import { customElement, property, query, state } from 'lit/decorators.js';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';

import { Editor } from '@tiptap/core';
import { Placeholder } from '@tiptap/extensions';
import { Markdown } from '@tiptap/markdown';
import StarterKit from '@tiptap/starter-kit';

const styles = css`
  /* Placeholder */
  wysiwyg-editor .is-editor-empty:first-child::before {
    color: #adb5bd;
    content: attr(data-placeholder);
    float: left;
    height: 0;
    pointer-events: none;
  }
`.styleSheet!;

@customElement('wysiwyg-editor')
export class WysiwygEditor extends LitElement {
  @property({ type: String }) accessor name = '';
  @property({ type: String }) accessor value = '';
  @property({ type: String }) accessor placeholder = '';

  @state() accessor _content = '';

  @query('.editor')
  accessor _container!: HTMLDivElement;

  _editor = null as Editor | null;

  attributeChangedCallback(
    name: string,
    _old: string | null,
    value: string | null,
  ): void {
    super.attributeChangedCallback(name, _old, value);
    if (name === 'value') {
      this._content = value ?? '';
    }
  }

  // Render in Light DOM to work with daisy-ui
  protected createRenderRoot() {
    const rootNode = this.getRootNode() as ShadowRoot | Document;
    if (!rootNode.adoptedStyleSheets.includes(styles)) {
      rootNode.adoptedStyleSheets.push(styles);
    }
    return this;
  }

  protected firstUpdated(_changedProperties: PropertyValues): void {
    this._editor = new Editor({
      element: this._container,
      content: this.value,
      contentType: 'markdown',
      extensions: [
        Markdown,
        StarterKit,
        Placeholder.configure({ placeholder: this.placeholder }),
      ],
      editorProps: {
        attributes: {
          class:
            'textarea textarea-bordered w-full font-mono text-sm min-h-[500px]',
        },
      },
      onUpdate: ({ editor }) => {
        this._content = editor.getMarkdown();
      },
    });
  }

  render() {
    return html`<div class="editor"></div>
      <input name="${this.name}" type="hidden" .value=${this._content} />`;
  }
}
