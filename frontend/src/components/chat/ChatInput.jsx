import { useState } from "react";
import { SendHorizonal } from "lucide-react";

import Button from "../ui/Button";
import Chip from "../ui/Chip";

function ChatInput({ suggestions = [], disabled = false, onSubmit }) {
  const [value, setValue] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!value.trim() || disabled) {
      return;
    }

    onSubmit(value);
    setValue("");
  };

  const handleSuggestion = (suggestion) => {
    if (disabled) {
      return;
    }
    onSubmit(suggestion);
    setValue("");
  };

  return (
    <div className="border-t border-border/80 px-5 pb-5 pt-4">
      <div className="mb-3 flex flex-wrap gap-2">
        {suggestions.map((suggestion) => (
          <Chip key={suggestion} onClick={() => handleSuggestion(suggestion)}>
            {suggestion}
          </Chip>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row">
        <textarea
          rows={2}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          placeholder="Escribe tu respuesta con calma..."
          className="min-h-[72px] flex-1 resize-none rounded-[22px] border border-border bg-white px-4 py-3 text-sm text-ink outline-none transition placeholder:text-muted focus:border-primary focus:ring-4 focus:ring-primary/10"
          disabled={disabled}
        />
        <Button type="submit" className="sm:self-end" disabled={disabled}>
          <SendHorizonal size={16} />
          Enviar
        </Button>
      </form>
    </div>
  );
}

export default ChatInput;
