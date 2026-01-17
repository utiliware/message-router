import { useState, useEffect } from "react";
import { useApi } from "../endpoint/api-base";

export const useMetrics = () => {
  const { getMetrics } = useApi()
  const [data, setData] = useState([])
 
 // Funciones de AWS que haga parseado
 // Aqui 
 //

  const loadMetrics = async () => {
    try {
      const response = getMetrics()
      // Agregar la funcion aqui
      setData(response.data); 
      
    } catch (error) {
        console.log(error)
    }
  };
  useEffect(() => {
    loadMetrics();
  }, []);


  return { data };
};
