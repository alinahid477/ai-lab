"use client"
import Image from "next/image";
import {Terminal} from "@/components/custom/Terminal";
import { useAppContext } from "@/context/AppContext";
import useWebSocket from 'react-use-websocket';
import { useEffect, useState } from "react";
import {columns} from "@/components/custom/LogsTable/columns"
import { DataTable } from "@/components/custom/LogsTable/data-table";
import { SummaryDisplayer } from "@/components/custom/SummaryDisplayer";
import { AIInputSheet } from "@/components/custom/AIInputSheet";
import ChatInterface from "@/components/custom/ChatInterface";
import AnimatedAILogo from "@/components/custom/AnimatedAILogo";

export default function Home() {

  const [socketUrl, setSocketUrl] = useState(() => 
    typeof window !== 'undefined' 
      ? `ws://${window.location.hostname}:8765` 
      : 'ws://localhost:8765'
  );

  const { myAppContext, setMyAppContext} = useAppContext();

  const [showPage, setShowPage] = useState(false);

  useEffect(() => {
    fetch('/api/env')
      .then((res) => res.json())
      .then((data) => {
        console.log('Fetched ENVVARS:', data);
        setShowPage(true)
        setSocketUrl(data.WSSERVER);
        setMyAppContext({...myAppContext, ENVVARS: {"WSSERVER":data.WSSERVER, "AIBACKEND_SERVER": data.AIBACKEND_SERVER}});
      })
      .catch((err) => {
        console.error('Error fetching runtimeValue:', err);
        //setVal(null);
      });
  }, []);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [wsMessage, setWSMessage] = useState<{ data: any; timeStamp: number } | null>(null);
  
  

  const { lastMessage } = useWebSocket(socketUrl, {
                                        shouldReconnect: () => true,
                                        reconnectAttempts: 5,
                                        reconnectInterval: 10000,
                                      });
  
  useEffect(() => {
    if (lastMessage && typeof lastMessage === 'object' && 'data' in lastMessage && 'timeStamp' in lastMessage) {
      let parsedData;
      try {
        parsedData = JSON.parse(lastMessage.data);
        if (parsedData !== null && typeof parsedData === 'object' && parsedData.type) {
          if(parsedData.type === "terminalinfo") {
            setWSMessage({ data: parsedData.data, timeStamp: lastMessage.timeStamp });
          }    
        } else {
          console.log("Parsed data is not a JSON object, it is text:", lastMessage.data);
        }  
      } catch (error) {
        console.log(error)
        console.log("Failed to parse data as JSON, treating as text:", lastMessage.data);
      }    
    }
  }, [lastMessage]);
  
  
  




  

  return (
    <div className="grid grid-rows-[5px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:pl-20 sm:pr-20 font-[family-name:var(--font-geist-sans)]">
      {/*<div className="row-start-1 self-start justify-self-start flex items-center gap-4">*/}
      <div className="row-start-1 self-start justify-self-start flex flex-col items-start gap-2 mb-8">
      <AnimatedAILogo/>
        <Image
          src="/intellilogs.png"
          alt="IntelliLogs logo"
          width={120}
          height={40}
          priority
        />
      </div>
      <main className="flex flex-col gap-[32px] row-start-2 items-center w-full sm:items-start pt-8">
        
        {showPage ? 
          <ol className="list-inside list-decimal text-sm/6 text-center sm:text-left font-[family-name:var(--font-geist-mono)]">
          
          
          <li className="mb-2 tracking-[-.01em]">
            Display: Human - AI interface
            <div className="grid grid-cols-8 gap-4 w-full min-w-[200px] shadow-md">
              <div className="col-span-1">
                <Image
                  className="dark:invert"
                  src="/robot.svg"
                  alt="Robot logo"
                  width={180}
                  height={38}
                  priority
                />
              </div>
              <div className="col-span-7 min-h-[500px]">
                <ChatInterface/>
              </div>
            </div>
            <br/>
          </li>
          <li className="tracking-[-.01em]">
            User Input: Terminal to the AI
            <div className="grid w-full min-w-[200px] min-h-[400px]">
              <Terminal commands={[]} username="human" machinename="aimachine" socketMessage={wsMessage || {}}/>  
            </div>
            <br/><br/>
          </li>
          <li className="tracking-[-.01em]">
            Display output: Tabular or Formatted data displayer
            {myAppContext.dataTable && myAppContext.dataTable.data && myAppContext.dataTable.data.length > 1 && (
              <div className="max-h-[500px] min-w-[300px] overflow-auto border border-gray-300 p-4 rounded shadow">
                {/* Render tableData content here */}
                <DataTable columns={columns} data={myAppContext.dataTable.data} />
              </div>
            )}
            {myAppContext.summarydata && (
              myAppContext.summarydata.summary ? (
                <div className="max-h-[500px] min-w-[300px] overflow-auto border border-gray-300 p-4 rounded shadow">
                  {/* Render summarize content here */}
                  <SummaryDisplayer data={myAppContext.summarydata}/>
                </div>
              ): (
                <>
                  <p className="text-red-600">
                    Error from Model. It returned empty logs summary. It shouldn&apos;t have done that. May be the model is too small to handle this many logs data.
                  </p>
                  <p>
                    Try a bigger model.
                  </p>
                </>
                
              )
            )}
          </li>

          <li className="pt-8">
             Traditional UI: &nbsp; 
            <AIInputSheet />
            &nbsp;
          </li>

        </ol>
        : <div>Loading...</div>
        }

        
        
        
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
        An AI experiment by Ali Nahid
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="mail:to(anahid@redhat.com)"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          anahid@redhat.com →
        </a>
      </footer>
    </div>
  );
}
