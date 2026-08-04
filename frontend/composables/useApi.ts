export function useApi() {
  const config = useRuntimeConfig();
  const { accessToken } = useAuth();

  async function request<T>(path: string, options: any = {}): Promise<T> {
    const token = accessToken();
    return await $fetch<T>(path, {
      baseURL: config.public.apiBase,
      ...options,
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {}),
      },
    });
  }

  return {
    get: <T>(path: string) => request<T>(path, { method: "GET" }),
    post: <T>(path: string, body?: any) => request<T>(path, { method: "POST", body }),
    del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
  };
}
