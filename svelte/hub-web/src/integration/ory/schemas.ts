export type LoginForm = {
  id: string;
  elements: {
    type: "text" | "a" | "img" | "input" | "script";
    attributes: {
      label?: string;
      name: string;
      value: string;
      type:
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
    };
  }[];
};

export type LoginFormSchema = {
  id: string;
  ui: {
    nodes: {
      attributes: {
        node_type: "text" | "a" | "img" | "input" | "script";
        type:
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
        name: string;
        value?: string;
      };
      meta: { label?: { text: string } };
    }[];
  };
};

export const loginFormParser = {
  toModel: (data: LoginFormSchema): LoginForm => ({
    id: data.id,
    elements: data.ui.nodes.map((item) => ({
      type: item.attributes.node_type,
      attributes: {
        name: item.attributes.name,
        type: item.attributes.type,
        value: item.attributes.value ?? "",
        label: item.meta.label?.text,
      },
    })),
  }),
};

export type OrySessionSchema = {
  expires_at: string;
  identity: {
    id: string;
    traits: {
      email: string;
    };
  };
};
