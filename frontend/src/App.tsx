import { useEffect, useState } from "react";
import { verifyAuth } from "./services/auth";
import LoginPage from "./views/Login";
import "./App.css";
import ChatPage from "./views/Chat";

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        await verifyAuth();
        setIsLoggedIn(true);
      } catch {
        setIsLoggedIn(false);
      } finally {
        setIsAuthLoading(false);
      }
    })();
  }, []);

  if (isAuthLoading) {
    return null;
  }
  return isLoggedIn ? (
    <ChatPage />
  ) : (
    <LoginPage onLoginSuccess={() => setIsLoggedIn(true)} />
  );
}

export default App;
