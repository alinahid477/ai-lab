import React, { useEffect, useState, useRef } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import { useAppContext } from "@/context/AppContext";
interface Message {
  id: number;
  role: "user" | "assistant";
  content: string;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const { myAppContext} = useAppContext();

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
				id: Date.now(),
				role: "user",
				content: `${textInput}`,
			};

			setMessages((prev) => [...prev, newMessage]);
			// setInput("");
			setIsThinking(true);
		}

		if (type === "assistant") {
			const assistantReply: Message = {
				id: Date.now() + 1,
				role: "assistant",
				content: `${textInput}`,
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
			sendMessage(myAppContext.aiInterfaceResponseText, "assistant");
		}
	}, [myAppContext.aiInterfaceResponseText]);

	useEffect(() => {
		if (myAppContext && myAppContext.aiInterfaceUserText) {
			sendMessage(myAppContext.aiInterfaceUserText, "user");
		}
	}, [myAppContext.aiInterfaceUserText]);

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
                {msg.content}
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
