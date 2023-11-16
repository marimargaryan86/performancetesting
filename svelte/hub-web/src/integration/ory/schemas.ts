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

export type UserRole = "reseller-user" | "reseller-admin" | "snowfall-user" | "snowfall-admin";

export type User = {
  id: string;
  email: string;
  name: string;
  role: UserRole;
};

export type UserSchema = {
  session: {
    id: string;
    active: boolean;
    expires_at: string;
    authenticated_at: string;
    authenticator_assurance_level: "aal1";
    authentication_methods: {
      method: "password";
      aal: "aal1";
      completed_at: string;
    }[];
    issued_at: string;
    identity: {
      id: string;
      schema_id: string;
      schema_url: string;
      state: "active";
      state_changed_at: string;
      traits: { email: string };
      verifiable_addresses: {
        id: string;
        value: string;
        verified: boolean;
        via: "email";
        status: "completed";
        verified_at: string;
        created_at: string;
        updated_at: string;
      }[];
      recovery_addresses: {
        id: string;
        value: string;
        via: "email";
        created_at: string;
        updated_at: string;
      }[];
      metadata_public: { role: UserRole };
      created_at: string;
      updated_at: string;
      organization_id: unknown | null;
    };
    devices: {
      id: string;
      ip_address: string;
      user_agent: "undici";
      location: string;
    }[];
  };
};

export const userParser = {
  toModel: (data: UserSchema): User => ({
    id: data.session.identity.id,
    email: data.session.identity.traits.email,
    name: "Unknown",
    role: data.session.identity.metadata_public.role,
  }),
};

export type Session = {
  id: string;
  token: string;
};

export type SessionExtended = Session & {
  user: User;
  expiresAt: Date;
};
