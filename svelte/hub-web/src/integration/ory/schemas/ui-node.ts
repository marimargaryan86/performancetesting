import {
  uiNodeTextAttributesParser,
  type UiNodeAnchorAttributesSchema,
  type UiNodeImageAttributesSchema,
  type UiNodeInputAttributesSchema,
  type UiNodeScriptAttributesSchema,
  type UiNodeTextAttributes,
  type UiNodeTextAttributesSchema,
  type UiNodeInputAttributes,
  uiNodeInputAttributesParser,
  type UiNodeImageAttributes,
  uiNodeImageAttributesParser,
  type UiNodeAnchorAttributes,
  uiNodeAnchorAttributesParser,
  type UiNodeScriptAttributes,
  uiNodeScriptAttributesParser,
} from "./ui-node-attributes";
import { uiTextParser, type UiText, type UiTextSchema } from "./ui-text";

export type UiNodeMeta = {
  label?: UiText;
};

export type UiNodeMetaSchema = {
  label?: UiTextSchema;
};

export const uiNodeMetaParser = {
  toModel: (data: UiNodeMetaSchema): UiNodeMeta => ({
    label: data.label ? uiTextParser.toModel(data.label) : undefined,
  }),
};

export type UiNodeGroup =
  | "default"
  | "password"
  | "oidc"
  | "profile"
  | "link"
  | "code"
  | "totp"
  | "lookup_secret"
  | "webauthn";

export type UiNodeType = "text" | "input" | "img" | "a" | "script";

export type UiNodeBase = {
  group: UiNodeGroup;
  messages: UiText[];
  meta: UiNodeMeta;
};

export type UiNodeBaseSchema = {
  group: UiNodeGroup;
  messages: UiTextSchema[];
  meta: UiNodeMetaSchema;
};

export const uiNodeBaseParser = {
  toModel: (data: UiNodeBaseSchema): UiNodeBase => ({
    group: data.group,
    messages: data.messages.map(uiTextParser.toModel),
    meta: uiNodeMetaParser.toModel(data.meta),
  }),
};

export type UiNodeText = UiNodeBase & {
  type: "text";
  attributes: UiNodeTextAttributes;
};

export type UiNodeTextSchema = UiNodeBaseSchema & {
  type: "text";
  attributes: UiNodeTextAttributesSchema;
};

export const uiNodeTextParser = {
  toModel: (data: UiNodeTextSchema): UiNodeText => ({
    ...uiNodeBaseParser.toModel(data),
    type: data.type,
    attributes: uiNodeTextAttributesParser.toModel(data.attributes),
  }),
};

export type UiNodeInput = UiNodeBase & {
  type: "input";
  attributes: UiNodeInputAttributes;
};

export type UiNodeInputSchema = UiNodeBaseSchema & {
  type: "input";
  attributes: UiNodeInputAttributesSchema;
};

export const uiNodeInputParser = {
  toModel: (data: UiNodeInputSchema): UiNodeInput => ({
    ...uiNodeBaseParser.toModel(data),
    type: data.type,
    attributes: uiNodeInputAttributesParser.toModel(data.attributes),
  }),
};

export type UiNodeImage = UiNodeBase & {
  type: "img";
  attributes: UiNodeImageAttributes;
};

export type UiNodeImageSchema = UiNodeBaseSchema & {
  type: "img";
  attributes: UiNodeImageAttributesSchema;
};

export const uiNodeImageParser = {
  toModel: (data: UiNodeImageSchema): UiNodeImage => ({
    ...uiNodeBaseParser.toModel(data),
    type: data.type,
    attributes: uiNodeImageAttributesParser.toModel(data.attributes),
  }),
};

export type UiNodeAnchor = UiNodeBase & {
  type: "a";
  attributes: UiNodeAnchorAttributes;
};

export type UiNodeAnchorSchema = UiNodeBaseSchema & {
  type: "a";
  attributes: UiNodeAnchorAttributesSchema;
};

export const uiNodeAnchorParser = {
  toModel: (data: UiNodeAnchorSchema): UiNodeAnchor => ({
    ...uiNodeBaseParser.toModel(data),
    type: data.type,
    attributes: uiNodeAnchorAttributesParser.toModel(data.attributes),
  }),
};

export type UiNodeScript = UiNodeBase & {
  type: "script";
  attributes: UiNodeScriptAttributes;
};

export type UiNodeScriptSchema = UiNodeBaseSchema & {
  type: "script";
  attributes: UiNodeScriptAttributesSchema;
};

export const uiNodeScriptParser = {
  toModel: (data: UiNodeScriptSchema): UiNodeScript => ({
    ...uiNodeBaseParser.toModel(data),
    type: data.type,
    attributes: uiNodeScriptAttributesParser.toModel(data.attributes),
  }),
};

export type UiNode = UiNodeText | UiNodeInput | UiNodeImage | UiNodeAnchor | UiNodeScript;

export type UiNodeSchema =
  | UiNodeTextSchema
  | UiNodeInputSchema
  | UiNodeImageSchema
  | UiNodeAnchorSchema
  | UiNodeScriptSchema;

export const uiNodeParser = {
  toModel: (data: UiNodeSchema): UiNode => {
    switch (data.type) {
      case "a":
        return uiNodeAnchorParser.toModel(data);
      case "img":
        return uiNodeImageParser.toModel(data);
      case "input":
        return uiNodeInputParser.toModel(data);
      case "script":
        return uiNodeScriptParser.toModel(data);
      case "text":
        return uiNodeTextParser.toModel(data);
      default:
        throw new Error("Unknown node type");
    }
  },
};
