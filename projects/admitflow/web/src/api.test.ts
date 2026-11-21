import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, request } from "./api";

function mockFetch(status: number, body: unknown) {
  vi.stubGlobal("fetch", vi.fn(async () => new Response(JSON.stringify(body), { status })));
}

afterEach(() => vi.unstubAllGlobals());

describe("request", () => {
  it("returns parsed JSON on success and sends the token", async () => {
    mockFetch(200, { status: "ok" });
    await expect(request("/health", {}, "abc")).resolves.toEqual({ status: "ok" });
    const [, init] = (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls[0];
    expect(init.headers.Authorization).toBe("Bearer abc");
  });

  it("turns API errors into readable messages", async () => {
    mockFetch(401, { error: { status: 401, detail: "Incorrect username or password" } });
    await expect(request("/auth/login")).rejects.toMatchObject({ status: 401, message: "Incorrect username or password" });
  });

  it("joins validation errors field by field", async () => {
    mockFetch(422, { error: { status: 422, detail: [{ field: "phone", message: "not a valid phone number" }] } });
    await expect(request("/leads")).rejects.toThrow("phone: not a valid phone number");
  });

  it("reports network failures clearly", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => { throw new TypeError("Failed to fetch"); }));
    const error = (await request("/health").catch((e: unknown) => e)) as ApiError;
    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(0);
  });
});
