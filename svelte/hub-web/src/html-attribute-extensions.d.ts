declare global {
  type Typography =
    | "body-xlarge"
    | "body-large"
    | "body-medium"
    | "body-small"
    | "body-xsmall"
    | "label-small"
    | "label-medium"
    | "label-large"
    | "headline-medium"
    | "headline-large"
    | "display-small"
    | "display-medium"
    | "headline-small"
    | "title-small"
    | "title-medium"
    | "title-large";
  type TypographyWeight = "bold" | "default";
}

type ButtonVariant = "primary" | "outline" | "text";
type ButtonSize = "large" | "medium" | "small" | "x-small" | "xx-small";

declare module "svelte/elements" {
  export interface SvelteHTMLElements {
    "x-table": HTMLAttributes;
    "x-thead": HTMLAttributes;
    "x-tbody": HTMLAttributes;
    "x-tr": HTMLAttributes;
    "x-td": HTMLAttributes;
    "x-th": HTMLAttributes;
    "x-tloading": HTMLAttributes;
    "x-tactions": HTMLAttributes;
  }

  export interface HTMLButtonAttributes {
    variant?: ButtonVariant;
    size?: ButtonSize;
  }

  export interface HTMLAnchorAttributes {
    variant?: ButtonVariant;
    size?: ButtonSize;
  }

  export interface HTMLAttributes {
    typography?: Typography;
    weight?: TypographyWeight;
  }
}

export {};
