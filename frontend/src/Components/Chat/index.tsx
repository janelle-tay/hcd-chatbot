import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { format } from "date-fns";
import { motion } from "framer-motion";
import { Button } from "primereact/button";
import { InputText } from "primereact/inputtext";

const LOREM_IPSUM_TEXT =
  "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";
const CHAT_REVEAL_SPEED = 10; // millis per character

interface ChatMessage {
  id: number;
  self: boolean;
  message: string;
  timestamp: string;
}

interface ChatResponseTextProps {
  id: number;
  text: string;
  immediate?: boolean;
  onComplete?: (id: number) => void;
  onGenerate?: () => void;
}

function ChatResponseText(props: ChatResponseTextProps) {
  const { id, text, immediate = false, onComplete, onGenerate } = props;
  const [displayText, setDisplayText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (immediate) {
      return onComplete?.(id);
    }

    const interval = setInterval(() => {
      setCurrentIndex((prevIndex) => {
        const endIndex = prevIndex + 1;
        const newText = text.substring(prevIndex, endIndex);
        setDisplayText((curr) => (curr += newText));

        if (endIndex >= text.length) {
          clearInterval(interval);
        }

        return prevIndex + 1;
      });
      onGenerate?.();
    }, CHAT_REVEAL_SPEED);

    return () => clearInterval(interval);
  }, [text, onComplete, onGenerate, immediate]);

  useEffect(() => {
    if (currentIndex >= text.length) {
      onComplete?.(id);
    }
  }, [currentIndex, text, id]);

  return immediate ? text : displayText;
}

function ChatCard() {
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const [currentChat, setCurrentChat] = useState("");
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  const onChatResponseComplete = useCallback(() => {
    setIsChatLoading(false);
  }, []);

  const onChatTextGenerate = useCallback(() => {
    if (!chatContainerRef.current) {
      return;
    }

    chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
  }, [chatContainerRef]);

  const onSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const messageId = Math.random() * Math.pow(10, 20);
    setIsChatLoading(true);
    setMessages((curr) => [
      ...curr,
      {
        id: messageId,
        self: true,
        message: currentChat,
        timestamp: new Date().toISOString(),
      },
    ]);
    setCurrentChat("");

    setTimeout(() => {
      const messageId = Math.random() * Math.pow(10, 20);
      setMessages((curr) => [
        ...curr,
        {
          id: messageId,
          self: false,
          message: LOREM_IPSUM_TEXT,
          timestamp: new Date().toISOString(),
        },
      ]);
    }, 3000);
  };

  return (
    <div
      className="surface-100 flex flex-column"
      style={{ minWidth: 400, borderRadius: "25px" }}
    >
      <div className="surface-card flex flex-column flex-1 border-round-lg border-200 border-1 border-solid">
        <div className="flex flex-1 pt-4 pl-4 pr-2">
          <div
            ref={chatContainerRef}
            className="flex flex-column w-full mt-auto overflow-y-auto pr-3"
            style={{ height: 600 }}
          >
            {messages.map(({ id, self, message, timestamp }, idx) => (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                key={String(idx)}
                className={clsx(
                  "flex flex-column",
                  self ? "align-self-start" : "align-self-end align-items-end"
                )}
              >
                <div className="flex gap-1 mb-1">
                  {self && <p className="text-xs m-0">Me</p>}
                  <p className="text-xs m-0">{format(timestamp, "HH:mm")}</p>
                </div>
                <div
                  className={clsx(
                    "py-2 px-3 border-round-lg mb-2 max-w-20rem",
                    self ? "align-self-start" : "align-self-end",
                    self ? "surface-200" : "bg-primary"
                  )}
                >
                  <p className="m-0 text-md">
                    {self ? (
                      message
                    ) : (
                      <ChatResponseText
                        id={id}
                        text={message}
                        onComplete={onChatResponseComplete}
                        onGenerate={onChatTextGenerate}
                      />
                    )}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
        <form
          onSubmit={onSubmit}
          className="surface-card border-round-lg flex align-items-center pl-4 pr-3 pb-3 pt-2 gap-2"
        >
          <InputText
            id="message"
            type="text"
            autoComplete="off"
            className="p-inputtext-sm px-3 w-full"
            placeholder="Type a message"
            value={currentChat}
            disabled={isChatLoading}
            onChange={(e) => setCurrentChat(e.target.value)}
          />
          <Button
            text
            rounded
            loading={isChatLoading}
            type="submit"
            icon="fa-solid fa-paper-plane"
            pt={{
              loadingIcon: {
                className: "text-primary",
              },
            }}
            className="h-full"
            style={{ aspectRatio: 1 }}
          />
        </form>
      </div>
    </div>
  );
}

export default ChatCard;
