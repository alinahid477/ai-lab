"use client"
import React, { createContext, useContext, useState, ReactNode } from "react";


// eslint-disable-next-line @typescript-eslint/no-explicit-any
const AppContext = createContext<any>(undefined);



export const AppWrapper = ({ children }: { children: ReactNode }) => {
  const [myAppContext, setMyAppContext] = useState<object>({});

  return (
    <AppContext.Provider value={{ myAppContext, setMyAppContext }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error("useGlobalState must be used within a GlobalStateProvider");
  }
  return context;
};