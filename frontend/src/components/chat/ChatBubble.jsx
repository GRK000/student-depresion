import { motion } from "framer-motion";

function ChatBubble({ role, text }) {
  const isUser = role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`max-w-[85%] rounded-[22px] px-5 py-4 text-sm leading-7 shadow-soft sm:max-w-[78%] ${
          isUser
            ? "rounded-br-md bg-user-bubble text-ink"
            : "rounded-bl-md border border-border bg-white text-ink"
        }`}
      >
        {text}
      </div>
    </motion.div>
  );
}

export default ChatBubble;
