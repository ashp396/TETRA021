import axios from "axios";

const baseURL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL });

export function setToken(token: string) {
  if (typeof window !== "undefined") {
    window.localStorage.setItem("finvestorToken", token);
  }
}
 
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("finvestorToken");
}

export function clearToken() {
  if (typeof window !== "undefined") {
    window.localStorage.removeItem("finvestorToken");
  }
}

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
