const pageTitleInput = document.getElementById("page-title");
const pageUrlInput = document.getElementById("page-url");
const apiServerUrlInput = document.getElementById("api-server-url");
const apiStatusMessage = document.getElementById("api-status-message");
const apiStatusDot = document.getElementById("api-status-dot");
const cancelButton = document.getElementById("cancel-button");

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

async function checkApiHealth() {
    const baseUrl = apiServerUrlInput.value.trim();

    if (!baseUrl) {
        apiStatusDot.classList.remove("dot--success");
        apiStatusDot.classList.add("dot--error");
        apiStatusMessage.textContent = "Failed to Connect to API";
        return;
    }

    try {
        const response = await fetch(new URL("/health", baseUrl));

        if (!response.ok) {
            throw new Error(`Health check failed with status ${response.status}`);
        }

        apiStatusDot.classList.remove("dot--error");
        apiStatusDot.classList.add("dot--success");
    } catch {
        apiStatusDot.classList.remove("dot--success");
        apiStatusDot.classList.add("dot--error");
        apiStatusMessage.textContent = "Failed to Connect to API";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    cancelButton.addEventListener("click", () => {
        window.close();
    });

    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        setPageDetails(tabs[0]);
    });

    checkApiHealth();
});
