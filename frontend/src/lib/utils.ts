import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export async function fetchData(AIBACKEND_SERVER: string, apipath: string): Promise<any> {
  const host = AIBACKEND_SERVER || "http://localhost:8000";
  const url = host + "/" + apipath;
  try {
    const response = await fetch(url);
    if (!response.ok) {
      const contentType = response.headers.get('content-type');
      let errorBody;

      if (contentType && contentType.includes('application/json')) {
        const json = await response.json();
        errorBody = JSON.stringify(json);
      } else {
        errorBody = await response.text();
      }

      // Include body in error
      throw new Error(`HTTP ${response.status}: ${response.statusText} --> ${errorBody}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching data:", error);
    throw error;
  }
}


export async function processAction(AIBACKEND_SERVER:string, action: string, paramsKeyValueObj: object): Promise<unknown> {
  let str=""
  let theaction=""
  if (action === "rawlog" || action === "logs" || action === "kafkalogs") {
    if (paramsKeyValueObj && "duration" in paramsKeyValueObj && paramsKeyValueObj["duration"]) {
      str = `getapplogs?duration=${paramsKeyValueObj["duration"]}`;
      theaction="getapplogs"
    }
    //const str="csvlogs?filepath=/tmp/myappocp_202503182148.csv&page=0&rowcount=100"
  } else if(action === "csv" || action === "csvlogs" || action === "csvlog") {
    if (paramsKeyValueObj && "filepath" in paramsKeyValueObj) {
      str = `csvlogs?filepath=${paramsKeyValueObj["filepath"]}&page=0&rowcount=100`;
      theaction="csvlogs"
    }
  } else if(action === "classify" || action === "classifycsv" || action === "classifylogs") {
    if (paramsKeyValueObj && "filepath" in paramsKeyValueObj) {
      str = `classifycsv?filepath=${paramsKeyValueObj["filepath"]}`;
      theaction="classifycsv"
    }
  } else if(action === "summarizelogs" || action === "summarize" || action === "logsummary") {
    if (paramsKeyValueObj && "filepath" in paramsKeyValueObj) {
      str = `summarize?filepath=${paramsKeyValueObj["filepath"]}`;
      theaction="summarize"
    }
  } else if (action === "listfiles") {
    if (Object.keys(paramsKeyValueObj).length === 0) {
      str = `listfiles`;
      theaction="listfiles"
    }
  } else if (action === "truncatecsv") {
    if (paramsKeyValueObj && "filepath" in paramsKeyValueObj && "totalrows" in paramsKeyValueObj) {
      str = `truncatecsv?filepath=${paramsKeyValueObj["filepath"]}&totalrows=${paramsKeyValueObj["totalrows"]}`;
      if ("skiprows" in paramsKeyValueObj && paramsKeyValueObj.skiprows) {
        str += `&skiprows=${paramsKeyValueObj["skiprows"]}`;
      }
      theaction="truncatecsv"
    }
  } else if (action === "downloadcsv" || action === "downloadfile") {
    if (paramsKeyValueObj && "filepath" in paramsKeyValueObj) {
      str = `downloadfile?filepath=${paramsKeyValueObj["filepath"]}`;
      theaction="downloadfile"
    }
  }
  
  if (str && str.length > 0) {
    try {
      const data = await fetchData(AIBACKEND_SERVER, str)      
      if(data && (data.rowcount || /summarize\?/i.test(str))) {
        return {...data, action: theaction}
      } else {
        return data;
      }
    } catch (error) {
      console.error(error)
      console.error("Error fetching data:", error);
      throw error;
    }
  }
}