import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

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
  if (action === "rawlog") {
    // const str="getapplogs?duration="+logDuration
    const str="csvlogs?filepath=/tmp/myappocp_202503182148.csv&page=0&rowcount=100"
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