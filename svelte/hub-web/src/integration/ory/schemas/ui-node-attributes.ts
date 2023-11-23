import { uiTextParser, type UiText, type UiTextSchema } from "./ui-text";

export type UiNodeAnchorAttributes = {
  href: string;
  id: string;
  title: UiText;
};

export type UiNodeAnchorAttributesSchema = {
  node_type: "a";
  href: string;
  id: string;
  title: UiTextSchema;
};

export const uiNodeAnchorAttributesParser = {
  toModel: (data: UiNodeAnchorAttributesSchema): UiNodeAnchorAttributes => ({
    href: data.href,
    id: data.id,
    title: uiTextParser.toModel(data.title),
  }),
};

export type UiNodeImageAttributes = {
  height: number;
  width: number;
  id: string;
  src: string;
};

export type UiNodeImageAttributesSchema = {
  node_type: "img";
  height: number;
  width: number;
  id: string;
  src: string;
};

export const uiNodeImageAttributesParser = {
  toModel: (data: UiNodeImageAttributesSchema): UiNodeImageAttributes => ({
    height: data.height,
    width: data.width,
    id: data.id,
    src: data.src,
  }),
};

export type AutocompleteType =
  | "email"
  | "tel"
  | "url"
  | "current-password"
  | "new-password"
  | "one-time-code";

export type InputType =
  | "text"
  | "password"
  | "number"
  | "checkbox"
  | "hidden"
  | "email"
  | "tel"
  | "submit"
  | "button"
  | "datetime-local"
  | "date"
  | "url";

export type UiNodeInputAttributes = {
  autocomplete?: AutocompleteType;
  disabled: boolean;
  label?: UiText;
  name: string;
  onclick?: string;
  pattern?: string;
  required: boolean;
  type: InputType;
  value?: string;
};

export type UiNodeInputAttributesSchema = {
  node_type: "input";
  autocomplete?: AutocompleteType;
  disabled: boolean;
  label?: UiTextSchema;
  name: string;
  onclick?: string;
  pattern?: string;
  required?: boolean;
  type: InputType;
  value?: unknown;
};

export const uiNodeInputAttributesParser = {
  toModel: (data: UiNodeInputAttributesSchema): UiNodeInputAttributes => ({
    autocomplete: data.autocomplete,
    disabled: data.disabled,
    label: data.label ? uiTextParser.toModel(data.label) : undefined,
    name: data.name,
    onclick: data.onclick,
    pattern: data.pattern,
    required: Boolean(data.required),
    type: data.type,
    value: data.value ? String(data.value) : undefined,
  }),
};

export type UiNodeScriptAttributes = {
  async: boolean;
  crossorigin: string;
  id: string;
  integrity: string;
  nonce: string;
  referrerPolicy: ReferrerPolicy;
  src: string;
  type: string;
};

export type UiNodeScriptAttributesSchema = {
  node_type: "script";
  async: boolean;
  crossorigin: string;
  id: string;
  integrity: string;
  nonce: string;
  referrerpolicy: ReferrerPolicy;
  src: string;
  type: string;
};

export const uiNodeScriptAttributesParser = {
  toModel: (data: UiNodeScriptAttributesSchema): UiNodeScriptAttributes => ({
    async: data.async,
    crossorigin: data.crossorigin,
    id: data.id,
    integrity: data.integrity,
    nonce: data.nonce,
    referrerPolicy: data.referrerpolicy,
    src: data.src,
    type: data.type,
  }),
};

export type UiNodeTextAttributes = {
  id: string;
  text: UiText;
};

export type UiNodeTextAttributesSchema = {
  node_type: "text";
  id: string;
  text: UiTextSchema;
};

export const uiNodeTextAttributesParser = {
  toModel: (data: UiNodeTextAttributesSchema): UiNodeTextAttributes => ({
    id: data.id,
    text: uiTextParser.toModel(data.text),
  }),
};
