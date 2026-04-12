import { describe, expect, it } from "vitest";

import {
  DEFAULT_API_BASE,
  buildRequestHeaders,
  deriveBrowserApiBase,
  getDefaultApiBase,
  extractErrorMessage,
  trimTrailingSlash,
} from "../app/utils/bookmarkApi";

describe("bookmarkApi helpers", () => {
  it("trims trailing slashes from an API base", () => {
    expect(trimTrailingSlash("http://localhost:8000///")).toBe("http://localhost:8000");
    expect(trimTrailingSlash("http://localhost:8000")).toBe("http://localhost:8000");
  });

  it("derives the API base from the current browser host", () => {
    expect(deriveBrowserApiBase("http://example.com:3000/bookmarks")).toBe(
      "http://example.com:8000",
    );
    expect(deriveBrowserApiBase("http://example.com:3000/bookmarks", "9000")).toBe(
      "http://example.com:9000",
    );
    expect(deriveBrowserApiBase("https://bookmarks.example.com/settings")).toBe(
      "https://bookmarks.example.com:8000",
    );
  });

  it("uses the browser host for the default API base when available", () => {
    const originalWindow = globalThis.window;
    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: {
        location: {
          href: "http://demo.example.net:3000/folders",
        },
      },
    });

    expect(getDefaultApiBase()).toBe("http://demo.example.net:8000");
    expect(getDefaultApiBase("9000")).toBe("http://demo.example.net:9000");

    Object.defineProperty(globalThis, "window", {
      configurable: true,
      value: originalWindow,
    });
  });

  it("adds JSON content type only when a request body is present", () => {
    expect(buildRequestHeaders({})).toEqual({
      headers: {},
      rest: {},
    });

    expect(
      buildRequestHeaders({
        body: JSON.stringify({ foo: "bar" }),
        headers: { Authorization: "Bearer token" },
      }),
    ).toEqual({
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer token",
      },
      rest: {
        body: JSON.stringify({ foo: "bar" }),
      },
    });
  });

  it("normalizes error payloads into readable messages", () => {
    expect(extractErrorMessage(400, { detail: "Bad request" })).toBe("Bad request");
    expect(extractErrorMessage(400, { detail: ["name is required"] })).toBe("name is required");
    expect(extractErrorMessage(500, null)).toBe("HTTP 500");
  });
});
