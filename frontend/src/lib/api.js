import axios from "axios";

// Same-origin first: on any preview/production domain the ingress proxies /api
// to the backend, which avoids CORS entirely. This fixes "Failed to load" when
// the site is opened via a different preview URL than the one in .env.
const host = typeof window !== "undefined" ? window.location.hostname : "";
const sameOrigin =
  host.endsWith(".emergentagent.com") || host.includes("hrdigitalservices");

export const BACKEND_URL = sameOrigin
  ? window.location.origin
  : process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API,
  withCredentials: true,
});

export default api;
