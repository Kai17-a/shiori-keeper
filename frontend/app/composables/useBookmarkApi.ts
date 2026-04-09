import {
  DEFAULT_API_BASE,
  SETTINGS_PATH,
  buildRequestHeaders,
  extractErrorMessage,
  resolveApiBase,
  trimTrailingSlash,
} from "~/utils/bookmarkApi";

export const useBookmarkApi = () => {
  const config = useRuntimeConfig();
  const defaultApiBase = DEFAULT_API_BASE;
  const configuredBase = resolveApiBase(config.public.apiBaseUrl, defaultApiBase);
  const settingsApiBase = ref(configuredBase);
  const apiBase = ref(defaultApiBase);
  let apiBaseLoadPromise: Promise<string> | null = null;

  const loadApiBase = async () => {
    if (apiBaseLoadPromise) {
      return apiBaseLoadPromise;
    }

    apiBaseLoadPromise = (async () => {
      try {
        const res = await fetch(`${trimTrailingSlash(settingsApiBase.value)}${SETTINGS_PATH}`);
        if (!res.ok) {
          apiBase.value = defaultApiBase;
          return defaultApiBase;
        }

        const body = await res.json();
        apiBase.value = body.api_base_url || defaultApiBase;
        return apiBase.value;
      } catch {
        apiBase.value = defaultApiBase;
        return defaultApiBase;
      }
    })();

    return apiBaseLoadPromise;
  };

  const saveApiBase = async (value: string) => {
    const res = await fetch(`${trimTrailingSlash(settingsApiBase.value)}${SETTINGS_PATH}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_base_url: value }),
    });

    if (!res.ok) {
      const body = await res.json().catch(() => null);
      throw new Error(body?.detail || `HTTP ${res.status}`);
    }

    const body = await res.json();
    const nextApiBase = body.api_base_url || defaultApiBase;
    apiBase.value = nextApiBase;
    settingsApiBase.value = nextApiBase;
    return nextApiBase;
  };

  const request = async (path: string, options: Record<string, any> = {}) => {
    if (!apiBaseLoadPromise) {
      await loadApiBase();
    } else {
      await apiBaseLoadPromise;
    }

    const { headers: mergedHeaders, rest } = buildRequestHeaders(options);

    const res = await fetch(`${trimTrailingSlash(apiBase.value)}${path}`, {
      headers: mergedHeaders,
      ...rest,
    });

    const body = await res.json().catch(() => null);
    if (!res.ok) {
      throw new Error(extractErrorMessage(res.status, body));
    }

    return body;
  };

  return { apiBase, defaultApiBase, loadApiBase, saveApiBase, request };
};
