export interface ResponseErrorSchema {
  errors: {
    status: string;
    detail: string;
    title?: string;
    code?: string;
    source?: {
      pointer: string;
    };
  }[];
}
