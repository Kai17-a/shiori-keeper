export const DEFAULT_API_BASE = "http://localhost:8000";
export const DEFAULT_API_PORT = "8000";

export type ApiErrorBody = {
  detail?: string | string[];
};

export const trimTrailingSlash = (value: string) => value.replace(/\/+$/, "");

export const deriveBrowserApiBase = (href: string, apiPort = DEFAULT_API_PORT) => {
  const url = new URL(href);
  url.port = apiPort;
  return url.origin;
};

export const getDefaultApiBase = (apiPort = DEFAULT_API_PORT) => {
  if (typeof window !== "undefined" && typeof window.location?.href === "string") {
    return deriveBrowserApiBase(window.location.href, apiPort);
  }

  return DEFAULT_API_BASE;
};

export const buildRequestHeaders = (options: RequestInit = {}) => {
  const { headers, ...rest } = options;

  return {
    headers: {
      ...(rest.body ? { "Content-Type": "application/json" } : {}),
      ...(headers || {}),
    } satisfies HeadersInit,
    rest,
  };
};

export const extractErrorMessage = (status: number, body: ApiErrorBody | null) => {
  if (Array.isArray(body?.detail)) {
    return body.detail.join(", ");
  }

  return body?.detail || `HTTP ${status}`;
};

export const parseJsonBody = async <T>(response: Response) => {
  return response.json().catch(() => null) as Promise<T | null>;
};
