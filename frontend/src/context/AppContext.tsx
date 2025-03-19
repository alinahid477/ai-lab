"use client"
import React, { createContext, useContext, useState, ReactNode } from "react";


// eslint-disable-next-line @typescript-eslint/no-explicit-any
const AppContext = createContext<any>(undefined);



export const AppWrapper = ({ children }: { children: ReactNode }) => {
  const [dataTable, setDataTable] = useState<object>({});

  return (
    <AppContext.Provider value={{ dataTable, setDataTable }}>
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