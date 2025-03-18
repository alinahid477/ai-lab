"use client"
import Image from "next/image";
import { AIInputForm } from "@/components/custom/AIInputForm";
import {Terminal} from "@/components/custom/Terminal";
import { useGlobalState } from "@/context/GlobalStateContext";
import useWebSocket, { ReadyState } from 'react-use-websocket';

export default function Home() {

  const socketUrl = "ws://localhost:8765";
  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl);



  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
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
        </ol>
        <div className="grid grid-cols-4 gap-4 min-w-[200px]">
        <div className="col-span-3">
            <Terminal commands="none" username="anahid" machinename="aimachine" socketMessage={lastMessage}/>
          </div>
          <div className="col-span-1">
            <AIInputForm />
          </div>
          
        </div>
        
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
