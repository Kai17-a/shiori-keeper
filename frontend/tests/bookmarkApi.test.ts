import { describe, expect, it } from "vitest";

import {
  DEFAULT_API_BASE,
  buildRequestHeaders,
  extractErrorMessage,
  resolveApiBase,
  trimTrailingSlash,
} from "~/utils/bookmarkApi";

describe("bookmarkApi helpers", () => {
  it("trims only one trailing slash from an API base", () => {
    expect(trimTrailingSlash("http://localhost:8000/")).toBe("http://localhost:8000");
    expect(trimTrailingSlash("http://localhost:8000")).toBe("http://localhost:8000");
  });

  it("falls back to the default API base when config is missing", () => {
    expect(resolveApiBase(undefined)).toBe(DEFAULT_API_BASE);
    expect(resolveApiBase("https://api.example.com")).toBe("https://api.example.com");
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
    expect(extractErrorMessage(400, { detail: ["name is required"] })).toBe(
      '["name is required"]',
    );
    expect(extractErrorMessage(500, null)).toBe("HTTP 500");
  });
});
