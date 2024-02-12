export type BreadCrumb = {
  url: string;
  label: string;
};

export type AlertType = "success" | "error" | "warning";

export type Tab = {
  url: string;
  label: string;
  exact?: boolean;
};
