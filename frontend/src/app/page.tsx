"use client"
import Image from "next/image";
import { AIInputForm } from "@/components/custom/AIInputForm";
import {Terminal} from "@/components/custom/Terminal";
import { useAppContext } from "@/context/AppContext";
import useWebSocket from 'react-use-websocket';
import { useEffect, useState } from "react";
import {columns} from "@/components/custom/LogsTable/columns"
import { DataTable } from "@/components/custom/LogsTable/data-table";
import { AIInputSheet } from "@/components/custom/AIInputSheet";
import ChatInterface from "@/components/custom/ChatInterface";


export default function Home() {

  const socketUrl = "ws://localhost:8765";
  const { lastMessage } = useWebSocket(socketUrl);
  const [isToggleToForm, setIsToggleToForm] = useState(false);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [wsMessage, setWSMessage] = useState<{ data: any; timeStamp: number } | null>(null);
  
  const { myAppContext } = useAppContext();


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
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center w-full sm:items-start">
        <Image
          className="dark:invert"
          src="/next.svg"
          alt="Next.js logo"
          width={180}
          height={38}
          priority
        />
        <ol className="list-inside list-decimal text-sm/6 text-center sm:text-left font-[family-name:var(--font-geist-mono)]">
          <li className="mb-2 tracking-[-.01em]">
            Get started by editing{" "}
            <code className="bg-black/[.05] dark:bg-white/[.06] px-1 py-0.5 rounded font-[family-name:var(--font-geist-mono)] font-semibold">
              src/app/page.tsx
            </code>
            .
          </li>
          <li className="tracking-[-.01em]">
            Save and see your changes instantly.
          </li>
          <li>
              
            <AIInputSheet />
            
          </li>
        </ol>
        
        <div className="grid grid-cols-4 gap-4 w-full min-w-[200px]">
          <div className="col-span-3 min-h-[400px]">
            <Terminal commands={[]} username="anahid" machinename="aimachine" socketMessage={wsMessage || {}}/>  
          </div>
          
          
          <div className="col-span-1">
            <ChatInterface />
          </div>
        </div>
        {myAppContext.dataTable && myAppContext.dataTable.data && myAppContext.dataTable.data.length > 1 && (
          <div className="max-h-[500px] min-w-[300px] overflow-auto border border-gray-300 p-4 rounded shadow">
            {/* Render tableData content here */}
            <DataTable columns={columns} data={myAppContext.dataTable.data} />
          </div>
        )}
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
