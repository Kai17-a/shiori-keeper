export const useBookmarkApi = () => {
  const config = useRuntimeConfig()
  const settingsApiBase = ref(config.public.apiBase || "http://localhost:8000")
  const apiBase = ref("http://localhost:8000")
  const defaultApiBase = "http://localhost:8000"
  const settingsPath = "/settings"
  let apiBaseLoadPromise: Promise<string> | null = null
  const buildUrl = (base: string, path: string) =>
    `${base.replace(/\/$/, "")}${path}`

  const loadApiBase = async () => {
    if (apiBaseLoadPromise) return apiBaseLoadPromise
    apiBaseLoadPromise = (async () => {
    try {
      const res = await fetch(buildUrl(settingsApiBase.value, settingsPath))
      if (!res.ok) {
        apiBase.value = defaultApiBase
        return defaultApiBase
      }
      const body = await res.json()
      apiBase.value = body.api_base_url || defaultApiBase
      settingsApiBase.value = apiBase.value
      return apiBase.value
    } catch {
      apiBase.value = defaultApiBase
      return defaultApiBase
    }
    })()
    return apiBaseLoadPromise
  }

  const saveApiBase = async (value: string) => {
    const res = await fetch(buildUrl(settingsApiBase.value, settingsPath), {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_base_url: value }),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => null)
      throw new Error(body?.detail || `HTTP ${res.status}`)
    }
    const body = await res.json()
    apiBase.value = body.api_base_url || defaultApiBase
    settingsApiBase.value = apiBase.value
    return apiBase.value
  }

  const request = async (path: string, options: Record<string, any> = {}) => {
    if (!apiBaseLoadPromise) {
      await loadApiBase()
    } else {
      await apiBaseLoadPromise
    }
    const res = await fetch(`${apiBase.value.replace(/\/$/, "")}${path}`, {
      headers: { "Content-Type": "application/json", ...(options.headers || {}) },
      ...options,
    })
    const body = await res.json().catch(() => null)
    if (!res.ok) {
      throw new Error(Array.isArray(body?.detail) ? JSON.stringify(body.detail) : body?.detail || `HTTP ${res.status}`)
    }
    return body
  }

  return { apiBase, defaultApiBase, loadApiBase, saveApiBase, request }
}
