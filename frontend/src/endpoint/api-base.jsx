import axios from "axios";

// CHANGE URL
const API_URL = 'https://hnbytph7gj.execute-api.us-east-1.amazonaws.com/Prod/send';

const headers = (id = null) => {
  if (id != null) {
    return {
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "ids": `${id}` 
      }
    } 
  } else {
    return {
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json",
      }
    }
  }
};

export const useApi = () => {

  const getMetrics = async () => {
    const url = `${API_URL}/grafico`;
    return axios.get(url, headers());
  }

  const getResultsMessage = async (id) => {
    const url = `${API_URL}/sms/confirmed`;
    return axios.get(url, headers(id));
  }

  const getResultsImage = async (id) => {
    const url = `${API_URL}/ia/${id}`;
    return axios.get(url, headers());
  }

  const getBedrockResponse = async (id) => {
    const url = `${API_URL}/bedrock/${id}`;
    return axios.get(url, headers());
  }

  const sendConfirmationAndMessage = async (payload) => {
    const url = `${API_URL}/sms/contacts`; 
    return axios.post(url, payload, headers());
  }

  return {
    getResultsMessage,
    getResultsImage,
    getBedrockResponse,
    getMetrics,
    
    sendConfirmationAndMessage,
  }
}
