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

declare module "svelte/elements" {
  export interface HTMLButtonAttributes {
    variant?: "primary" | "outline" | "text";
    size?: "large" | "medium" | "small" | "x-small" | "xx-small";
  }

  export interface HTMLAttributes {
    typography?: Typography;
    weight?: TypographyWeight;
  }
}

export {};
