"use client"
import React, { createContext, useContext, useState, ReactNode } from "react";

interface GlobalState {
  // Define your global state properties here
  user: string;
  setUser: (user: string) => void;
}

const GlobalStateContext = createContext<GlobalState | undefined>(undefined);

export const GlobalStateProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<string>("");

  return (
    <GlobalStateContext.Provider value={{ user, setUser }}>
      {children}
    </GlobalStateContext.Provider>
  );
};

export const useGlobalState = () => {
  const context = useContext(GlobalStateContext);
  if (context === undefined) {
    throw new Error("useGlobalState must be used within a GlobalStateProvider");
  }
  return context;
};