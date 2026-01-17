import { useState, useEffect } from "react";
import { useApi } from "../endpoint/api-base";

export const useResults = () => {
  const { getResultsMessage, getResultsImage } = useApi()
  const [data, setData] = useState([{},""])
 
 // Funciones de AWS que haga parseado
 // Aqui 
 //

  const loadResults = async () => {
    try {
      const responseM = getResultsMessage("12345431232")
      // Agregar la funcion aqui
      setData(responseM.data); 

      const responseI = getResultsImage("12345431232")
      // Agregar la funcion aqui

      setData([responseM.data, responseI.data]);      
    } catch (error) {
        console.log(error)
    }
  };
  useEffect(() => {
    loadResults();
  }, []);


  return { data };
};
