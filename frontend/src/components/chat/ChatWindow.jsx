import { useEffect, useRef } from "react";
import { AnimatePresence } from "framer-motion";

import ChatBubble from "./ChatBubble";
import TypingIndicator from "./TypingIndicator";

function ChatWindow({ messages, isTyping }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  return (
    <div className="flex-1 space-y-5 overflow-y-auto px-1 py-2 sm:px-2">
      {messages.map((message) => (
        <ChatBubble
          key={message.id}
          role={message.role}
          text={message.text}
        />
      ))}

      <AnimatePresence>{isTyping ? <TypingIndicator /> : null}</AnimatePresence>
      <div ref={endRef} />
    </div>
  );
}

export default ChatWindow;
