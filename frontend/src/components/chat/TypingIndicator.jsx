import { motion } from "framer-motion";

function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
      className="flex justify-start"
    >
      <div className="inline-flex items-center gap-1 rounded-full border border-border bg-white px-4 py-3 shadow-soft">
        {[0, 1, 2].map((dot) => (
          <motion.span
            key={dot}
            className="h-2 w-2 rounded-full bg-primary/70"
            animate={{ y: [0, -4, 0], opacity: [0.45, 1, 0.45] }}
            transition={{
              duration: 1,
              repeat: Infinity,
              ease: "easeInOut",
              delay: dot * 0.15,
            }}
          />
        ))}
      </div>
    </motion.div>
  );
}

export default TypingIndicator;
