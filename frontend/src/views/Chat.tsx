import ChatCard from "../Components/Chat";
import { Image } from "primereact/image";
import { Dropdown } from "primereact/dropdown";
import { InputText } from "primereact/inputtext";
import { useState } from "react";
import { Button } from "primereact/button";

const ChatPage = () => {
  const [selectedClient, setSelectedClient] = useState(null);
  const client = [
    { name: "OpenAI", code: "openai" },
    { name: "Gemini", code: "gemini" },
  ];

  return (
    <div className="flex h-screen w-full justify-content-between align-items-center p-2 gap-1">
      <div
        className="h-full flex flex-column align-items-center justify-content-around"
        style={{ width: "25%" }}
      >
        <Image src="/temus.png" alt="logo" />
        <div className="flex flex-column align-items-center justify-content-center">
          <p className="font-bold">Select LLM Client</p>
          <Dropdown
            value={selectedClient}
            onChange={(e) => setSelectedClient(e.value)}
            options={client}
            optionLabel="name"
            placeholder="Select a Client"
            className="w-full md:w-14rem"
          />
          <Button
            size="small"
            label="Select Client"
            type="submit"
            className="mb-2 font-light mt-4"
          />
        </div>
        <div className="flex flex-column align-items-center justify-content-center">
          <p className="font-bold">Save Chat History</p>
          <div className="flex flex-column gap-2">
            <InputText
              id="filename"
              aria-describedby="filename-text"
              placeholder="chat_history.txt"
              className="w-full md:w-14rem"
            />
            <small id="filename-text">File Name </small>
          </div>
          <Button
            size="small"
            label="Save Chat"
            type="submit"
            className="mb-2 font-light mt-4"
          />
        </div>
      </div>
      <div style={{ width: "75%" }}>
        <ChatCard />
      </div>
    </div>
  );
};

export default ChatPage;
