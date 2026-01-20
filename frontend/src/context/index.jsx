import { createContext, useContext, useState } from "react";

const IdxContext = createContext();

export const IdxProvider = ({ children }) => {
  const [idx, setIdx] = useState(1); 
  const [messageIA, setMessageIA] = useState(null)

  return (
    <IdxContext.Provider value={{ idx, setIdx, messageIA, setMessageIA }}>
      {children}
    </IdxContext.Provider>
  );
};

export const useIdx = () => useContext(IdxContext);
