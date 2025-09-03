import axios from 'axios';

const api = axios.create({
  baseURL: '/', // Use a relative path to work with the Vite proxy
});

export default api;
