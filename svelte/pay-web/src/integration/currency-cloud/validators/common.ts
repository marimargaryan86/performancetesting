import { removeUndefinedValues } from "../helpers";
import type { ValidationError } from "../models/common";

export function validateEmail(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return value.match(/^.+@.+$/) ? undefined : ["Invalid email"];
}

export function validateBoolean(value?: unknown, required = true): ValidationError<boolean> {
  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return typeof value === "boolean" ? undefined : ["Invalid boolean"];
}

export function validateUUID(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return value.match(/^[A-f0-9]{8}-[A-f0-9]{4}-[A-f0-9]{4}-[A-f0-9]{4}-[A-f0-9]{12}$/)
    ? undefined
    : ["Invalid UUID"];
}

export function validateNumber(
  value?: number,
  min?: number,
  max?: number,
  required = true,
): ValidationError<string> {
  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  if (isNaN(value)) {
    return ["Invalid number"];
  }

  if (min !== undefined && value < min) {
    return [`Number is smaller than ${min}`];
  }

  if (max !== undefined && max < value) {
    return [`Number is larger than ${max}`];
  }
}

export function validateCountryCode(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return value.match(/^[A-Z]{2}$/) ? undefined : ["Invalid 2-letter country code"];
}

export function validateCurrencyCode(
  value?: string | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return value.match(/^[A-Z]{3}$/) ? undefined : ["Invalid 3-letter currency code"];
}

export function validateEnum(
  value: string | undefined | null,
  allowed: Readonly<string[]>,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return allowed.includes(value)
    ? undefined
    : [`Invalid value, must be one of [${allowed.join(", ")}]`];
}

export function validateLength(
  value?: string | null,
  minLength?: number,
  maxLength?: number,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  if (minLength !== undefined && value.length < minLength) {
    return [`Must be at least ${minLength} characters long`];
  }

  if (maxLength !== undefined && maxLength < value.length) {
    return [`Must not be more than ${maxLength} characters long`];
  }

  return undefined;
}

export function validateDate(
  value?: string | Date | null,
  required = true,
  nullable = false,
): ValidationError<string> {
  if (!nullable && value === null) {
    return ["Not nullable"];
  } else if (value === null) {
    return undefined;
  }

  if (value === undefined) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  return isNaN(new Date(value).getTime()) ? ["Invalid date"] : undefined;
}

export function validateArray(
  value: string[] | undefined,
  method: (value: string) => string[] | undefined,
  required = true,
): ValidationError<string[] | string> {
  if (!value) {
    if (required) {
      return ["Missing"];
    }

    return undefined;
  }

  const errors = value.map((item, idx) => {
    const error = method(item);

    return error
      ? {
          [idx]: error.join(", "),
        }
      : undefined;
  });

  return removeUndefinedValues(errors) as ValidationError<string[] | string>;
}
