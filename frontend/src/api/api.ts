import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL,
});

export const setAuthToken = (token: string) => {
  if (token) {
    localStorage.setItem("token", token);
    API.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    localStorage.removeItem("token");
    delete API.defaults.headers.common["Authorization"];
  }
};

API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers!["Authorization"] = `Bearer ${token}`;
  return config;
});

export default API;
