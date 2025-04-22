import React, { useEffect, useState, useRef } from "react";
import { Card } from "@/components/ui/card";
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
	}, [isThinking]);

	useEffect(() => {
		if (myAppContext && myAppContext.aiInterfaceResponseText) {
      if (myAppContext.aiInterfaceResponseText.startsWith("command:")) {
        // Handle command logic here if needed
        sendMessage(myAppContext.aiInterfaceResponseText, "command");
      } else {
        sendMessage(myAppContext.aiInterfaceResponseText, "assistant");
      }
		}
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [myAppContext.aiInterfaceResponseText]);

	useEffect(() => {
		if (myAppContext && myAppContext.aiInterfaceUserText) {
			sendMessage(myAppContext.aiInterfaceUserText, "user");
		}
	// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [myAppContext.aiInterfaceUserText]);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const doExecute = (data: any) => {
    try {
      console.log(data)
			const duration = parseInt(data.time_duration);
      const filepath = data.filepath;
			const action = data.command;
			console.log(duration, filepath, action)
			processAction(action, {duration: duration, filepath:filepath})
				.then((data) => {
					setMyAppContext({...myAppContext, dataTable: data});
				})
				.catch((error) => {
					console.error("Error fetching data:", error);
					toast.error("Failed to fetch data. Please try again.");
				});
			
					
			toast(
				<pre className="mt-2 w-[340px] rounded-md bg-slate-950 p-4">
					<code className="text-black">{JSON.stringify(data)}</code>
				</pre>
			);
		} catch (error) {
			console.error("Form submission error", error);
			toast.error("Failed to submit the form. Please try again.");
		}
  };

  return (
    <Card className="w-full max-w-auto">
        <div className="p-4 flex flex-col">
        <h1 className="text-2xl font-bold mb-4">AI Interface</h1>
        <div ref={divRef} className="flex-1 overflow-y-auto space-y-2 mb-4 max-h-[300px]">
            {messages.map((msg) => (
            <div
              key={msg.id}
              className={`p-3 rounded-2xl shadow-sm max-w-[80%] ${
              msg.role === "user"
                ? "bg-blue-100 self-end text-right pl-4 ml-10"
                : "bg-gray-100 self-start text-left"
              }`}
            >
              
              {msg.data ? (
                <>
                  <div dangerouslySetInnerHTML={{ __html: msg.content }} />
                  <Button variant="outline" size="icon" onClick={() => doExecute(msg.data)}>
                    <Play />
                  </Button>
                </>
              ):
                msg.content
              }
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
    </Card>
  );
};

export default ChatInterface;
