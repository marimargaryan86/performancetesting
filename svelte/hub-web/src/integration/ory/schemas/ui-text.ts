export type UiText = {
  context?: object;
  id: number;
  text: string;
  type: "info" | "error" | "success";
};

export type UiTextSchema = {
  context?: object;
  id: number;
  text: string;
  type: "info" | "error" | "success";
};

export const uiTextParser = {
  toModel: (data: UiTextSchema): UiText => ({
    context: data.context,
    id: data.id,
    text: data.text,
    type: data.type,
  }),
};
