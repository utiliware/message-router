import { useState, useEffect, useRef } from "react";
import { useApi } from "../endpoint/api-base";
import { useIdx } from "../context";

export const useResults = () => {
  const { idx, messageIA } = useIdx();
  const { getResultsMessage, getResultsImage, getBedrockResponse } = useApi();
  const [messResult, setMessResult] = useState(null); 
  const [iaResult, setIaResult] = useState(null); 
  const [bedrockResult, setBedrockResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const lastIdxRef = useRef(null);
  const hasLoadedRef = useRef(false);

  const loadResults = async () => {
    if (!idx || idx === lastIdxRef.current) {
      return;
    }

    lastIdxRef.current = idx;
    setLoading(true);
    
    try {
      // const responseM = await getResultsMessage(idx);
      // const messageData = responseM?.data || null;
      // setMessResult(messageData);

      console.log("---------")
      console.log(messageIA)
      console.log("---------")

      const responseI = await getResultsImage(messageIA);
      const imageData = responseI?.data || null;
      setIaResult(imageData);

      const responseB = await getBedrockResponse(messageIA);
      const bedrockData = responseB?.data || null;
      setBedrockResult(bedrockData);

      hasLoadedRef.current = true;
    } catch (error) {
      console.error("Error cargando resultados:", error);
      setMessResult(null);
      setIaResult(null);
      setBedrockResult(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (idx && idx !== lastIdxRef.current) {
      loadResults();
    }
  }, [idx, messageIA]);

  return { messResult, iaResult, bedrockResult, loading, reload: loadResults };
};