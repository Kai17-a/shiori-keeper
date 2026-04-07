const form = document.getElementById("bookmark-form")
const titleInput = document.getElementById("title")
const urlInput = document.getElementById("url")
const descriptionInput = document.getElementById("description")
const apiBaseInput = document.getElementById("api-base")
const folderSelect = document.getElementById("folder")
const tagsSelect = document.getElementById("tags")
const status = document.getElementById("status")
const prefillButton = document.getElementById("prefill")
const DEFAULT_API_BASE = "http://localhost:8001"
const SETTINGS_PATH = "/settings"

const setStatus = (text) => {
  status.textContent = text
  status.dataset.state = "info"
}

const setErrorStatus = (text) => {
  status.textContent = text
  status.dataset.state = "error"
}

const setSuccessStatus = (text) => {
  status.textContent = text
  status.dataset.state = "success"
}

const storageGet = (keys) =>
  new Promise((resolve, reject) => {
    if (!chrome.storage?.local) {
      reject(new Error("chrome.storage.local is unavailable."))
      return
    }
    chrome.storage.local.get(keys, resolve)
  })

const storageSet = (items) =>
  new Promise((resolve, reject) => {
    if (!chrome.storage?.local) {
      reject(new Error("chrome.storage.local is unavailable."))
      return
    }
    chrome.storage.local.set(items, resolve)
  })

const normalizeBase = (value) => (value || DEFAULT_API_BASE).replace(/\/$/, "")

const fillFromActiveTab = async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true })
    if (!tab) {
      setErrorStatus("No active tab found.")
      return
    }
    titleInput.value = tab.title || ""
    urlInput.value = tab.url || ""
    setSuccessStatus("Captured the current tab.")
  } catch (error) {
    setErrorStatus(error.message || "Failed to read the active tab.")
  }
}

const loadOptions = async () => {
  const base = normalizeBase(apiBaseInput.value)
  const [foldersRes, tagsRes] = await Promise.all([
    fetch(`${base.replace(/\/$/, "")}/folders`),
    fetch(`${base.replace(/\/$/, "")}/tags`),
  ])
  if (!foldersRes.ok) throw new Error(`Failed to load folders: HTTP ${foldersRes.status}`)
  if (!tagsRes.ok) throw new Error(`Failed to load tags: HTTP ${tagsRes.status}`)
  const folders = await foldersRes.json()
  const tags = await tagsRes.json()

  folderSelect.innerHTML = '<option value="">No folder</option>'
  for (const folder of folders) {
    const option = document.createElement("option")
    option.value = String(folder.id)
    option.textContent = folder.name
    folderSelect.appendChild(option)
  }

  tagsSelect.innerHTML = '<option value="">No tag</option>'
  for (const tag of tags) {
    const option = document.createElement("option")
    option.value = String(tag.id)
    option.textContent = tag.name
    tagsSelect.appendChild(option)
  }
}

const loadApiBase = async () => {
  try {
    const res = await fetch(`${DEFAULT_API_BASE.replace(/\/$/, "")}${SETTINGS_PATH}`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const body = await res.json()
    const apiBase = normalizeBase(body.api_base_url)
    apiBaseInput.value = apiBase
    await storageSet({ apiBase })
    return apiBase
  } catch {
    const { apiBase } = await storageGet({ apiBase: DEFAULT_API_BASE })
    const fallback = normalizeBase(apiBase)
    apiBaseInput.value = fallback
    return fallback
  }
}

const postBookmark = async (payload) => {
  const base = normalizeBase(apiBaseInput.value)
  const res = await fetch(`${base}/bookmarks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const body = await res.json().catch(() => null)
    throw new Error(body?.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

const attachTags = async (bookmarkId, tagIds) => {
  const base = normalizeBase(apiBaseInput.value)
  for (const tagId of tagIds) {
    const res = await fetch(`${base}/bookmarks/${bookmarkId}/tags`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tag_id: Number(tagId) }),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => null)
      throw new Error(body?.detail || `HTTP ${res.status}`)
    }
  }
}

prefillButton.addEventListener("click", fillFromActiveTab)

form.addEventListener("submit", async (event) => {
  event.preventDefault()
  const payload = {
    title: titleInput.value.trim(),
    url: urlInput.value.trim(),
    description: descriptionInput.value.trim() || null,
    folder_id: folderSelect.value ? Number(folderSelect.value) : null,
  }
  try {
    const created = await postBookmark(payload)
    const selectedTag = tagsSelect.value
    if (created?.id && selectedTag) {
      await attachTags(created.id, [selectedTag])
    }
    setSuccessStatus("Bookmark saved to the DB.")
    window.close()
  } catch (error) {
    setErrorStatus(error.message || "Failed to save to the DB.")
  }
})

Promise.all([loadApiBase(), fillFromActiveTab()])
  .then(loadOptions)
  .catch((error) => setErrorStatus(error.message || "Failed to initialize popup."))
