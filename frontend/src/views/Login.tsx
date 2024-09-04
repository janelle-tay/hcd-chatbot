import React, { useRef, useState } from "react";
import { InputText } from "primereact/inputtext";
import { Password } from "primereact/password";
import { Button } from "primereact/button";
import { Toast } from "primereact/toast";
import { login } from "../services/auth";

interface LoginPageProps {
  onLoginSuccess: () => void;
}

function LoginPage(props: LoginPageProps) {
  const { onLoginSuccess } = props;
  const toastRef = useRef<Toast>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    try {
      setLoading(true);
      await login(username, password);
      onLoginSuccess?.();
    } catch (e) {
      console.log("🚀 ~ onSubmit ~ e:", e);
      toastRef.current?.show({
        severity: "error",
        summary: "Login failed",
        detail: "Please check if you have entered the correct credentials",
      });
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex align-items-center justify-content-center h-full w-full overflow-y-auto">
      <div
        className="flex flex-column align-items-center"
        style={{ minWidth: 300 }}
      >
        <form className="flex flex-column gap-2 w-full" onSubmit={onSubmit}>
          <div className="flex flex-column field">
            <label className="text-xs" htmlFor="email">
              Email
            </label>
            <InputText
              id="email"
              placeholder="Enter your email"
              aria-describedby="email-help"
              className="p-inputtext-xs text-sm"
              autoComplete="email"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="flex flex-column field mb-0">
            <label className="text-xs" htmlFor="password">
              Password
            </label>
            <Password
              id="password"
              placeholder="Enter your password"
              aria-describedby="password-help"
              inputClassName="w-full text-sm p-inputtext-xs"
              toggleMask
              feedback={false}
              pt={{
                iconField: {
                  root: "w-full",
                },
              }}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
          </div>
          <Button
            size="small"
            label="Sign in"
            type="submit"
            className="mb-2 font-light mt-4"
            loading={loading}
          />
        </form>
      </div>
      <Toast ref={toastRef} />
    </div>
  );
}

export default LoginPage;
