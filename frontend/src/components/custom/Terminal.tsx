// https://github.com/token-ed/react-terminal-emulator-ui/blob/main/demo/app.tsx
// https://token-ed.github.io/react-terminal-emulator-ui/

"use client"
import { time } from "console";
import React, { useEffect, useRef, useState } from "react";
import { set } from "react-hook-form";
import { TypeAnimation } from "react-type-animation";


export interface Command {
  command: string;
  result?: React.ReactNode;
  sideEffect?: () => void;
}

// interface Props {
//   commands: Array<Command>;
//   userName: string;
//   machineName: string;
//   initialFeed?: string;
//   onCommandNotFound?: (cmd: string) => string;
//   disableClearCommand?: boolean;
// }

interface TerminalProps {
  commands: string;
  machinename: string;
  username: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  socketMessage?: { [key: string]: any },
  initialFeed?: string;
}

const getPrompt = (line: React.ReactNode, index: number): React.ReactNode => {
  if (index % 2 === 0 && typeof line === "string") {
        const parts = line.split(" ");
        const prompt = parts[0];
        const command = parts.slice(1).join(" ");

        const promptParts = prompt.split("@");
        const userName = promptParts[0];
        const machineName = promptParts[1];

        const machineNameOnly = machineName.slice(0, -3);
        return (
        <div className="flex" key={index}>
            <span className="dark:text-green-500/80 text-green-800 font-bold">{userName}</span>
            <span className="dark:text-gray-300 text-gray-700">@</span>
            <span className="dark:text-blue-500/80 text-blue-800 font-bold">{machineNameOnly}</span>:
            <span className="dark:text-yellow-500/80 text-orange-800 font-bold">~</span>
            <span className="dark:text-red-500/80 text-red-800 font-bold">$</span>&nbsp;
            <span>{command}</span>
        </div>
        );
    }
    return <div key={index}>{line}</div>;
};

const formatTimestamp = (timestamp: number): string => {
  // const totalSeconds = timestamp;

  // const hours = Math.floor(totalSeconds / 3600) % 24; // Modulo 24 to keep it within a day's range
  // const minutes = Math.floor((totalSeconds % 3600) / 60);
  // const seconds = Math.floor(totalSeconds % 60);
  // const milliseconds = Math.floor((totalSeconds % 1) * 1000); // Extract milliseconds

  // const pad = (num: number) => num.toString().padStart(2, "0");
  // const padMs = (num: number) => num.toString().padStart(3, "0"); // Milliseconds should have 3 digits

  // const formattedTime = `${pad(hours)}:${pad(minutes)}:${pad(seconds)}.${padMs(milliseconds)}`;

  // return formattedTime;
  const now = new Date();

  const pad = (num: number) => num.toString().padStart(2, "0");

  const formattedTime = `${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;

  return formattedTime;
}

export function Terminal({ commands, machinename, username, initialFeed = "AI Terminal to display the processing outputs.", socketMessage, }: TerminalProps 
    // onCommandNotFound = (cmd: string) => `'${cmd}': command  not found.`,
    //disableClearCommand,
  ) {
    const trimmedUserName = username.replaceAll(" ", "").toLowerCase();
    const trimmedMachineName = machinename.replaceAll(" ", "").toLowerCase();
  
    // const allCommands: Array<Command> = disableClearCommand
    //   ? commands
    //   : [...commands, { command: "clear" }];
    const [output, setOutput] = useState<Array<React.ReactNode | undefined>>([]);
    const [focused, setFocused] = useState(true);
    const [currentLine, setCurrentLine] = useState<string>("");
    const [lastMessageData, setLastMessageData] = useState<string>("");
    const wrapperRef = useRef<HTMLInputElement>(null);
    const inputRef = useRef<HTMLInputElement>(null);
    const caretRef = useRef<HTMLDivElement>(null);
    const hiddenSpanRef = useRef<HTMLSpanElement>(null);
  
    const setCaretPosition = () => {
      const caretPosition = inputRef.current?.value.length || 0;
      setTimeout(() => {
        if (inputRef && inputRef.current) {
          inputRef.current.selectionStart = caretPosition;
          inputRef.current.selectionEnd = caretPosition;
        }
      }, 0);
    };
  
    const handleCommand = (event: React.KeyboardEvent<HTMLInputElement>) => {
      if (event.key == "Backspace")
        return setCurrentLine(currentLine.substring(0, currentLine?.length));
      if (event.key === "Enter") {
        // processCommand(currentLine);
        return setCurrentLine("");
      }
    };
  
    const handleInput = (event: React.ChangeEvent<HTMLInputElement>) => {
      event.preventDefault();
      // if (!ignoredKeys.includes(event.currentTarget.value)) {
      //   setCaretPosition();
      //   setCurrentLine(event.currentTarget.value);
      // }
      setCaretPosition();
      setCurrentLine(event.currentTarget.value);
    };
  
    // const processCommand = (cmd: string) => {
    //   const newOutput = [...output, `${trimmedUserName}@${trimmedMachineName}:~$ ${cmd}`];
    //   const foundCommand = allCommands.find((command) => command.command === cmd);
  
    //   if (!foundCommand) {
    //     newOutput.push(onCommandNotFound(cmd));
    //   } else {
    //     if (!disableClearCommand && foundCommand.command === "clear") return setOutput([]);
    //     if (foundCommand.result) newOutput.push(foundCommand.result);
    //     if (foundCommand.sideEffect) foundCommand.sideEffect();
    //   }
  
    //   setOutput(newOutput);
    // };
  
    useEffect(() => {
      if (wrapperRef.current) {
        wrapperRef.current.scrollTo({
          top: wrapperRef.current.scrollHeight,
          behavior: "smooth",
        });
      }
    }, [output]);
  
    useEffect(() => {
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }, []);


    

    useEffect(() => {
      if (socketMessage) {
        const txt = socketMessage.data;
        const newOutput = [...output, `${trimmedUserName}@${trimmedMachineName}:~$ ${formatTimestamp(socketMessage.timeStamp)}`];
        newOutput.push(txt);
        setOutput(newOutput);
      }
    }, [socketMessage]);
  
    // Update the caret position
    useEffect(() => {
      if (inputRef.current && caretRef.current && hiddenSpanRef.current) {
        const valueLength = inputRef.current?.value.length;
        const textBeforeCaret = currentLine.slice(0, valueLength || 0);
        hiddenSpanRef.current.textContent = textBeforeCaret;
        caretRef.current.style.left = `${hiddenSpanRef.current.offsetWidth}px`; // Adjust to fit input width
      }
    }, [currentLine]);
  
    const handleFocusInput = () => {
      setFocused(true);
      if (inputRef.current) {
        inputRef.current.focus();
      }
    };
  
    const handleBlur = () => {
      setFocused(false);
    };
  
    

    return (
      <div
        className="flex flex-col text-black dark:text-white bg-[#afafaf96] dark:bg-[#300924] rounded-md w-full h-full font-mono"
        onFocus={handleFocusInput}
        onBlur={handleBlur}
        tabIndex={1}>
        <div className="flex p-2 dark:bg-gray-700 bg-slate-600 rounded-tl-md rounded-tr-md h-10 items-center">
          <div className="flex space-x-2 items-center">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
          </div>
          <div className="text-center w-full font-bold text-slate-400 dark:text-gray-300 -ml-9">
            AI Terminal
          </div>
        </div>
        <div className="overflow-y-auto pt-4 px-2 max-h-[400px]" ref={wrapperRef}>
          <TypeAnimation speed={90} cursor={false} sequence={[initialFeed]} />
          {output.map(getPrompt)}
          <div className="flex relative">
            <span>
              <span className="dark:text-green-500/80 text-green-800 font-bold ">
                {trimmedUserName}
              </span>
              <span className="dark:text-gray-300 text-gray-700 font-bold">@</span>
              <span className="dark:text-blue-500/80 text-blue-800 font-bold">
                {trimmedMachineName}
              </span>
            </span>
            :<span className="dark:text-yellow-500/80 text-orange-800 font-bold">~</span>
            <span className="dark:text-red-500/80 text-red-800 font-bold">$</span>&nbsp;
            {/* <div className="flex-grow relative">
              <span id="hiddenSpan" className="invisible fixed" ref={hiddenSpanRef} />
              <input
                ref={inputRef}
                className="fixed -z-10 w-0 h-0 opacity-0"
                value={currentLine}
                onKeyDown={handleCommand}
                onInput={handleInput}
                autoComplete="off"
                autoCapitalize="none"
                autoCorrect="off"
                dir="ltr"
                type="text"
              />
              <div className="flex">
                <span>{currentLine}</span>
                {focused ? (
                  <div
                    ref={caretRef}
                    className="absolute top-0 h-full bg-slate-800 dark:bg-white w-[10px] animate-caret-blink"
                  />
                ) : null}
              </div>
            </div> */}
          </div>
        </div>
      </div>
    );
  }
