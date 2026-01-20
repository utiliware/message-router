import { useState, useEffect } from "react";
import { useApi } from "../endpoint/api-base";
import { useIdx } from "../context";

export const useResults = () => {
  const { idx, messageIA } = useIdx()
  const { getResultsMessage, getResultsImage } = useApi();
  const [messResult, setMessResult] = useState(null); 
  const [iaResult, setIaResult] = useState(null); 
  const [loading, setLoading] = useState(true);

  const loadResults = async () => {
    setLoading(true);
    try {
      const responseM = await getResultsMessage(idx);
      const messageData = responseM?.data || null;
      setMessResult(messageData)

      const responseI = await getResultsImage(messageIA);
      const imageData = responseI?.data || null;
      setIaResult(imageData)

    } catch (error) {
      console.error("Error cargando resultados:", error);
      setMessResult(null)
      setIaResult(null)
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
      loadResults();
  }, [idx]);

  return { messResult, iaResult, loading, reload: loadResults };
};
