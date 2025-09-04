import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000', // Use absolute URL to call backend directly
});

export default api;
