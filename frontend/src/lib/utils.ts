import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function fetchData(apipath: string): Promise<any> {
  const host = "http://localhost:8000";
  const url = host + "/" + apipath;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
}


export async function processAction(action: string, paramsKeyValueObj: object): Promise<unknown> {
  let str=""
  if (action === "rawlog" || action === "logs" || action === "kafkalogs") {
    if (paramsKeyValueObj && "duration" in paramsKeyValueObj && paramsKeyValueObj["duration"]) {
      str = `getapplogs?duration=${paramsKeyValueObj["duration"]}`;
    }
    //const str="csvlogs?filepath=/tmp/myappocp_202503182148.csv&page=0&rowcount=100"
  } else if(action === "csv" || action === "csvlogs" || action === "csvlog") {
    if (paramsKeyValueObj && "filepath" in paramsKeyValueObj) {
      str = `csvlogs?filepath=${paramsKeyValueObj["filepath"]}&page=0&rowcount=100`;
    }
  } else if(action === "classify" || action === "classifycsv" || action === "classifylogs") {
    if (paramsKeyValueObj && "filepath" in paramsKeyValueObj) {
      str = `classifycsv?filepath=${paramsKeyValueObj["filepath"]}`;
    }
  } else if(action === "summarizelogs" || action === "summarize" || action === "logsummary") {
    if (paramsKeyValueObj && "filepath" in paramsKeyValueObj) {
      str = `summarize?filepath=${paramsKeyValueObj["filepath"]}`;
    }
  }
  
  if (str && str.length > 0) {
    try {
      const data = await fetchData(str)
      if(data && data.rowcount) {
        return data
      }
    } catch (error) {
      console.error("Error fetching data:", error);
      throw error;
    }
  }
}