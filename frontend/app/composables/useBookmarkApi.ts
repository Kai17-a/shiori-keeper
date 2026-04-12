import {
  DEFAULT_API_BASE,
  buildRequestHeaders,
  extractErrorMessage,
  getDefaultApiBase,
  parseJsonBody,
  trimTrailingSlash,
  type ApiErrorBody,
} from "~/utils/bookmarkApi";

export const useBookmarkApi = () => {
  const config = useRuntimeConfig();
  const defaultApiBase = getDefaultApiBase(config.public.apiPort);
  const apiBase = ref(
    typeof config.public.apiBaseUrl === "string" && config.public.apiBaseUrl
      ? config.public.apiBaseUrl
      : defaultApiBase,
  );

  const saveApiBase = async (value: string) => {
    apiBase.value = value || defaultApiBase;
    return apiBase.value;
  };

  const request = async <T = unknown>(path: string, options: RequestInit = {}): Promise<T> => {
    const { headers: mergedHeaders, rest } = buildRequestHeaders(options);

    const res = await fetch(`${trimTrailingSlash(apiBase.value)}${path}`, {
      headers: mergedHeaders,
      ...rest,
    });

    const body = await parseJsonBody<T>(res);
    if (!res.ok) {
      throw new Error(extractErrorMessage(res.status, body as ApiErrorBody | null));
    }

    return body as T;
  };

  return { apiBase, defaultApiBase, saveApiBase, request };
};
