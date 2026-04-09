const pageTitleInput = document.getElementById("page-title");
const pageUrlInput = document.getElementById("page-url");
const apiServerUrlInput = document.getElementById("api-server-url");
const apiStatusMessage = document.getElementById("api-status-message");
const apiStatusDot = document.getElementById("api-status-dot");
const apiHealthcheckButton = document.getElementById("api-healthcheck-button");
const saveStatusMessage = document.getElementById("save-status-message");
const saveButton = document.getElementById("save-button");
const cancelButton = document.getElementById("cancel-button");
const folderSelect = document.getElementById("folder-select");
const tagSelect = document.getElementById("tag-select");

const API_SERVER_URL_STORAGE_KEY = "apiServerUrl";
let apiHealthyOnLoad = false;
let savedBookmarkId = null;
let initialBookmarkCreated = false;

function setApiStatus(state, message) {
    apiStatusDot.classList.remove("dot--pending", "dot--success", "dot--error");
    apiStatusDot.classList.add(`dot--${state}`);
    apiStatusMessage.textContent = message;
}

function setSaveStatus(state, message) {
    saveStatusMessage.classList.remove(
        "save-status--success",
        "save-status--error",
    );

    if (state) {
        saveStatusMessage.classList.add(`save-status--${state}`);
    }

    saveStatusMessage.textContent = message;
}

async function readErrorMessage(response) {
    const contentType = response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {
        try {
            const data = await response.json();
            return (
                data?.detail ||
                data?.message ||
                data?.error ||
                JSON.stringify(data)
            );
        } catch {
            return null;
        }
    }

    try {
        const text = await response.text();
        return text.trim() || null;
    } catch {
        return null;
    }
}

function setPageDetails(tab) {
    if (!tab) {
        return;
    }

    if (tab.url) {
        pageUrlInput.value = tab.url;
    }

    if (tab.title) {
        pageTitleInput.value = tab.title;
    }
}

function buildBookmarkPayload() {
    return {
        url: pageUrlInput.value.trim(),
        title: pageTitleInput.value.trim(),
    };
}

async function createBookmark(baseUrl) {
    const payload = buildBookmarkPayload();

    if (!payload.url || !payload.title) {
        setSaveStatus("error", "Missing title or URL");
        return null;
    }

    const response = await fetch(new URL("/bookmarks", baseUrl), {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (response.ok) {
        const data = await response.json();
        savedBookmarkId = data.id ?? null;
        return { ok: true, status: response.status, data };
    }

    const errorMessage = await readErrorMessage(response);
    return {
        ok: false,
        status: response.status,
        errorMessage:
            errorMessage || `Create bookmark failed with status ${response.status}`,
    };
}

function setSelectOptions(select, placeholder, items) {
    select.replaceChildren();

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = placeholder;
    select.appendChild(placeholderOption);

    for (const item of items) {
        const option = document.createElement("option");
        option.value = String(item.id);
        option.textContent = item.name;
        select.appendChild(option);
    }
}

async function loadFolderAndTagOptions(baseUrl) {
    const [foldersResponse, tagsResponse] = await Promise.all([
        fetch(new URL("/folders", baseUrl)),
        fetch(new URL("/tags", baseUrl)),
    ]);

    if (!foldersResponse.ok || !tagsResponse.ok) {
        throw new Error("Failed to load folders or tags");
    }

    const [folders, tags] = await Promise.all([
        foldersResponse.json(),
        tagsResponse.json(),
    ]);

    setSelectOptions(folderSelect, "-- Select Folder --", folders);
    setSelectOptions(tagSelect, "-- Select Tag --", tags);
}

async function checkApiHealth() {
    const baseUrl = apiServerUrlInput.value.trim();
    setApiStatus("pending", "Connecting to API...");

    if (!baseUrl) {
        apiHealthyOnLoad = false;
        setApiStatus("error", "Failed to Connect to API");
        return false;
    }

    try {
        const response = await fetch(new URL("/health", baseUrl));

        if (!response.ok) {
            throw new Error(`Health check failed with status ${response.status}`);
        }

        apiHealthyOnLoad = true;
        setApiStatus("success", "Connected to API");
        if (!initialBookmarkCreated) {
            initialBookmarkCreated = true;
            const created = await createBookmark(baseUrl);

            if (created.status !== 500) {
                await loadFolderAndTagOptions(baseUrl);
            }

            if (created.ok) {
                setSaveStatus("success", "Registered");
            } else {
                setSaveStatus(
                    "error",
                    created.errorMessage || "Save failed",
                );
            }
        }
        return true;
    } catch {
        apiHealthyOnLoad = false;
        setApiStatus("error", "Failed to Connect to API");
        return false;
    }
}

async function patchBookmark(baseUrl, bookmarkId) {
    const payload = buildBookmarkPayload();

    if (!payload.url || !payload.title) {
        setSaveStatus("error", "Missing title or URL");
        return;
    }

    const response = await fetch(new URL(`/bookmarks/${bookmarkId}`, baseUrl), {
        method: "PATCH",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        const errorMessage = await readErrorMessage(response);
        throw new Error(errorMessage || `Patch bookmark failed with status ${response.status}`);
    }

    setSaveStatus("success", "Saved");
}

async function handleSaveClick() {
    setSaveStatus("", "");

    try {
        const baseUrl = apiServerUrlInput.value.trim();

        if (apiHealthyOnLoad && savedBookmarkId) {
            await patchBookmark(baseUrl, savedBookmarkId);
            savedBookmarkId = null;
        } else {
            const created = await createBookmark(baseUrl);
            if (created?.ok && created?.data?.id != null) {
                savedBookmarkId = null;
            }
        }

        window.close();
    } catch (error) {
        setSaveStatus(
            "error",
            error instanceof Error && error.message ? error.message : "Save failed",
        );
    }
}

function saveApiServerUrl() {
    chrome.storage.local.set({
        [API_SERVER_URL_STORAGE_KEY]: apiServerUrlInput.value.trim(),
    });
}

document.addEventListener("DOMContentLoaded", () => {
    cancelButton.addEventListener("click", () => {
        window.close();
    });

    apiHealthcheckButton.addEventListener("click", () => {
        checkApiHealth();
    });

    saveButton.addEventListener("click", () => {
        handleSaveClick();
    });

    apiServerUrlInput.addEventListener("input", saveApiServerUrl);

    chrome.storage.local.get([API_SERVER_URL_STORAGE_KEY], (result) => {
        if (result[API_SERVER_URL_STORAGE_KEY]) {
            apiServerUrlInput.value = result[API_SERVER_URL_STORAGE_KEY];
        }

        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            setPageDetails(tabs[0]);
        });

        setSaveStatus("", "");
        checkApiHealth();
    });
});
