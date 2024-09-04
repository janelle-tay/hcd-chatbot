import apiClient from "./http";

export function login(username: string, password: string) {
  const formData = new FormData();
  formData.append("username", username);
  formData.append("password", password);
  return apiClient.post('/auth/login', formData);
}

export function verifyAuth() {
  return apiClient.post('/auth/verify');
}
