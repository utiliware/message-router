import axios from "axios";

const API_URL = import.meta.env.VITE_API_BASE;

const headers = () => ({
  headers: {
    "Content-Type": "application/json",
  },
});

export const useApi = () => {

  const getMetrics = async () => {
    const url = `${API_URL}/grafico`
    return axios.get(url, headers)
  }

  const getResultsMessage = async (id) => {
    const url = `${API_URL}/json/${id}`
    return axios.get(url, headers)
  }
  const getResultsImage = async (id) => {
    const url = `${API_URL}/ia/${id}`
    return axios.get(url, headers)
  }


  const setMessages = async (payload) => {
    const url = `${API_URL}/send/${id}`
    return axios.get(url, payload, headers)
  }

  return {
    getResultsMessage,
    getResultsImage,
    
    getMetrics,
    setMessages
  }
}




