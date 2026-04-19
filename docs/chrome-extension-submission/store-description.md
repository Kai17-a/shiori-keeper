# Chrome Web Store Description

Shiori Keeper is a browser extension for saving the page you are viewing into the Shiori Keeper app with a title, URL, and optional notes. It is designed for people who want to keep bookmarks, folders, tags, and RSS feeds in one place without losing the context of where a link came from.

Open the popup from your browser toolbar, confirm the current page title and URL, choose a folder or tags if needed, and save the bookmark to your Shiori Keeper server. The extension also lets you check the API connection, update existing entries by URL, and delete bookmarks directly from the popup.

## What Shiori Keeper Includes

- Save bookmarks with a title, URL, description, folder, and tags
- Update or delete bookmarks later
- Organize bookmarks with folders and tags
- Search and browse saved links in the main web app
- Track RSS feeds alongside bookmarks
- Configure and test a Discord webhook for RSS notifications
- View counts and recent items on the dashboard

## What the Extension Does

- Captures the current browser tab title and URL
- Stores the API server URL in `chrome.storage.local`
- Sends bookmark data to your Shiori Keeper API server
- Supports quick saving from the popup
- Provides a compact UI for editing and deleting saved bookmarks
- Verifies the API connection before saving

## Notes

- The extension is designed to work with a locally running or self-hosted Shiori Keeper server.
- Existing bookmarks are updated by URL when possible.
- Invalid URLs cannot be saved.

Shiori Keeper helps turn a growing list of saved links into an organized, searchable collection that is easy to maintain over time.

Project link: https://github.com/Kai17-a/shiori-keeper
