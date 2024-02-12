export type StatusBadgeVariant = "ok" | "warn" | "error";
export type StatusBadgeValue =
  | "confirmed"
  | "error"
  | "rejected"
  | "no-refund"
  | "refund-due"
  | "refund-issued"
  | "refund-failed"
  | "pending"
  | "submitted"
  | "succeeded"
  | "not-ticketed"
  | "cancelled"
  | "unspecified"
  | "executed"
  | "failed"
  | "completed"
  | "deleted"
  | "mixed"
  | "unknown";

export const STATUS_BADGE_MAPPING = {
  confirmed: "ok",
  completed: "ok",
  executed: "ok",
  succeeded: "ok",
  error: "error",
  rejected: "error",
  deleted: "error",
  failed: "error",
  "refund-failed": "error",
  pending: "warn",
  submitted: "warn",
  "no-refund": "warn",
  "refund-due": "warn",
  "refund-issued": "warn",
  "not-ticketed": "warn",
  mixed: "warn",
  cancelled: "warn",
  unspecified: "warn",
  unknown: "warn",
} satisfies Record<StatusBadgeValue, StatusBadgeVariant>;
