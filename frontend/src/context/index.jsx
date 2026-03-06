import { createContext, useContext, useState } from "react";

const IdxContext = createContext();

export const IdxProvider = ({ children }) => {
  const [idx, setIdx] = useState(1);
  const [messageIA, setMessageIA] = useState(null);
  const [wsImageUrl, setWsImageUrl] = useState(null);

  return (
    <IdxContext.Provider value={{ idx, setIdx, messageIA, setMessageIA, wsImageUrl, setWsImageUrl }}>
      {children}
    </IdxContext.Provider>
  );
};

export const useIdx = () => useContext(IdxContext);
