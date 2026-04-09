export const DEFAULT_API_BASE = "http://localhost:8000";
export const SETTINGS_PATH = "/settings";

export const trimTrailingSlash = (value: string) => value.replace(/\/$/, "");

export const resolveApiBase = (
  value: unknown,
  fallback: string = DEFAULT_API_BASE,
) => {
  return typeof value === "string" && value ? value : fallback;
};

export const buildRequestHeaders = (
  options: Record<string, any> = {},
) => {
  const { headers, ...rest } = options;

  return {
    headers: {
      ...(rest.body ? { "Content-Type": "application/json" } : {}),
      ...(headers || {}),
    },
    rest,
  };
};

export const extractErrorMessage = (
  status: number,
  body: Record<string, any> | null,
) => {
  if (Array.isArray(body?.detail)) {
    return JSON.stringify(body.detail);
  }

  return body?.detail || `HTTP ${status}`;
};
