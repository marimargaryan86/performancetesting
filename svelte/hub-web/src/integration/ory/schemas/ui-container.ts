import { uiNodeParser, type UiNode, type UiNodeGroup, type UiNodeSchema } from "./ui-node";
import { uiTextParser, type UiText, type UiTextSchema } from "./ui-text";

export type UiContainerMethod = "GET" | "POST" | "PATCH" | "PUT" | "DELETE";

export type UiContainer = {
  action: string;
  messages: UiText[];
  method: UiContainerMethod;
  groups: { [key in UiNodeGroup]?: UiNode[] };
};

export type UiContainerSchema = {
  action: string;
  messages?: UiTextSchema[];
  method: UiContainerMethod;
  nodes: UiNodeSchema[];
};

export const uiContainerParser = {
  toModel: (data: UiContainerSchema): UiContainer => {
    const groups: { [key in UiNodeGroup]?: UiNode[] } = {};

    data.nodes.forEach((node) => {
      const group = groups[node.group] ?? [];
      group.push(uiNodeParser.toModel(node));
      groups[node.group] = group;
    });

    return {
      action: data.action,
      messages: data.messages?.map(uiTextParser.toModel) ?? [],
      method: data.method,
      groups,
    };
  },
};
