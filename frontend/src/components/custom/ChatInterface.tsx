import React, { useEffect, useState, useRef } from "react";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";
import { toast } from "sonner"
import { useAppContext } from "@/context/AppContext";
import {processAction} from "@/lib/utils"
interface Message {
  id: string;
  role: "user" | "assistant" | "command";
  content: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: Record<string, any>;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const { myAppContext, setMyAppContext} = useAppContext();

  const [isThinking, setIsThinking] = useState(false);
  const divRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    if (divRef.current) {
      // Scroll to the bottom of the div every time the component re-renders
      divRef.current.scrollTop = divRef.current.scrollHeight;
    }
  }, [messages]);  // Trigger the effect when `messages` changes

  const sendMessage = (textInput: string, type: string) => {
    // if (!textInput.trim()) return;

		if (type === "user") {
			const newMessage: Message = {
				id: `${Date.now()}_user`,
				role: "user",
				content: `${textInput}`,
			};

			setMessages((prev) => [...prev, newMessage]);
			// setInput("");
			setIsThinking(true);
		} else if (type === "assistant") {
			const assistantReply: Message = {
				id: `${Date.now()}_assistant`,
				role: "assistant",
				content: `${textInput}`,
			};
			setMessages((prev) => [...prev, assistantReply]);
			setIsThinking(false);
		} else if (type === "command") {
      const jsonObj = JSON.parse(textInput.replace("command:", "").trim())
      const assistantReply: Message = {
        id: `${Date.now()}_command`,
        role: "command",
        content: `<b>command:</b> ${jsonObj.command}<br/><b>file:</b> ${jsonObj.filepath}<br/><b>duration:</b> ${jsonObj.time_duration}`,
        data: jsonObj,
      };
			setMessages((prev) => [...prev, assistantReply]);
			setIsThinking(false);
		} else {
      setIsThinking(false);
    }


    // setTimeout(() => {
      
    // }, 500);
  };

	useEffect(() => {
		if (isThinking) {
			setTimeout(() => {
				setIsThinking(false);
    	}, 300000);
		}
    setMyAppContext({...myAppContext, "haultTerminal": isThinking});
	}, [isThinking]);

	useEffect(() => {
		if (myAppContext && myAppContext.aiInterfaceResponseText) {
      if (myAppContext.aiInterfaceResponseText.startsWith("command:")) {
        // Handle command logic here if needed
        sendMessage(myAppContext.aiInterfaceResponseText, "command");
      } else if(myAppContext.aiInterfaceResponseText !== "clear") {
        sendMessage(myAppContext.aiInterfaceResponseText, "assistant");
      }
		}
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [myAppContext.timeStamp]);

	useEffect(() => {
		if (myAppContext && myAppContext.aiInterfaceUserText) {
			sendMessage(myAppContext.aiInterfaceUserText, "user");
		}
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [myAppContext.aiInterfaceUserText]);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const doExecute = (data: any) => {
    try {
      console.log("doExecute", data)
			const duration = parseInt(data.time_duration);
      const filepath = data.filepath;
			const action = data.command;
			processAction(myAppContext.ENVVARS.AIBACKEND_SERVER, action, {duration: duration, filepath:filepath})
				.then((data) => {
          if(typeof data === "object" && data !== null) {
            if ("action" in data) {
              if(data.action === "summarize") {
                // setMyAppContext({...myAppContext, summarydata: data});
                if ('message' in data) {
                  sendMessage(data.message as string, "assistant");
                } else {
                  console.error("Property 'message' does not exist on the data object:", data);
                  toast.error("Failed to process the response. Missing 'message' property.");
                }
              } else {
                setMyAppContext({...myAppContext, dataTable: data});
              }
              
            } else {
              throw new Error(JSON.stringify(data));
            }
          } else {
            throw new Error("fetched data from AI machine is null or undefined. ERROR: "+data);
          }
          
				})
				.catch((error) => {
					console.error("Error fetching data:", error);
					toast.error("Failed to fetch data from AI machine. Please try again." + error);
				});
			
					
			toast(
				<pre className="mt-2 w-[340px] max-h-[200px] rounded-md p-4 overflow-y-auto whitespace-pre-wrap break-words">
					<code className="text-black">{JSON.stringify(data)}</code>
				</pre>
			);
		} catch (error) {
			console.error("Execution error", error);
			toast.error("Failed execute command. Please try again.");
		}
  };

  return (
        <div className="p-4 flex flex-col">
          {/* <div className="flex p-2 dark:bg-gray-100 bg-slate-100 rounded-tl-md rounded-tr-md h-10 items-center">
            <div className="flex space-x-2 items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            </div>
            <div className="text-center w-full font-bold text-slate-400 dark:text-gray-300 -ml-9">
              AI Interface
            </div>
          </div> */}
          <div ref={divRef} className="flex-1 overflow-y-auto space-y-2 mb-4 max-h-[500px]">
              {messages.map((msg) => (
              <div
                key={msg.id}
                className={`p-5 rounded-2xl shadow-sm max-w-[80%] ${
                msg.role === "user"
                  ? "bg-blue-100 self-end text-right pl-4 ml-60"
                  : "bg-gray-100 self-start text-left"
                }`}
              >
                {msg.role !== "user" ? (
                  <div className="flex items-start space-x-2">
                    <Image
                      className="dark:invert"
                      src="/robot.svg"
                      alt="Robot logo"
                      width={54}
                      height={9}
                      priority
                    />
                    <div>
                      {msg.data ? (
                        <>
                          <div dangerouslySetInnerHTML={{ __html: msg.content }} />
                          <Button variant="outline" size="icon" onClick={() => doExecute(msg.data)}>
                            <Play />
                          </Button>
                        </>
                      ) : (
                        msg.content
                      )}
                    </div>
                  </div>
                ) : (
                  msg.data ? (
                    <>
                      <div dangerouslySetInnerHTML={{ __html: msg.content }} />
                      <Button variant="outline" size="icon" onClick={() => doExecute(msg.data)}>
                        <Play />
                      </Button>
                    </>
                  ) : (
                    msg.content
                  )
                )}
              </div>
              ))}
              {isThinking && (
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></div>
                </div>
              )}
          </div>
          {/* <Card className="p-2">
              <CardContent className="flex items-center gap-2">
              <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Type your message..."
                  onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              />
              <Button onClick={sendMessage}>
                  <Send className="w-4 h-4" />
              </Button>
              </CardContent>
          </Card> */}
        </div>
  );
};

export default ChatInterface;
