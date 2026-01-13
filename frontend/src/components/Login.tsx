import React, { useState } from "react";
import API, { setAuthToken } from "../api/api";
import { Mail, Lock, LogIn } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface Props {
  onLogin: () => void;
  onSwitch: () => void;
}

const Login: React.FC<Props> = ({ onLogin, onSwitch }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await API.post("/auth/login", { email, password });
      setAuthToken(res.data.token);
      onLogin();
      navigate('/home');
    } catch {
      alert("Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-[30%_70%] min-h-screen">
      
      <div className="bg-[#172026] p-8 flex flex-col justify-center items-center shadow-2xl">
        <div className="min-w-full">
          
          <div className="text-center mb-10">
            <h2 className="text-white font-bold text-2xl">Welcome Back</h2>
            <p className="text-[#04BFAD] text-sm mt-2">Login into your account</p>
          </div>

          <form onSubmit={handleLogin} className="flex flex-col gap-8">
            <div className="flex flex-col gap-2">
              <label className="font-normal text-md text-[#04BF9D] ml-1">Email Address</label>
              <div className="relative flex items-center">
                <input
                  type="email"
                  required
                  placeholder="name@company.com"
                  className="w-full leading-12.5 pl-5 pr-12 placeholder:text-[#555555] bg-[#F1F3F6] rounded-lg outline-none focus:ring-2 focus:ring-[#06D6A0]"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <div className="absolute right-0 bg-[#06D6A0] rounded-lg p-3">
                  <Mail className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <label className="font-normal text-md text-[#04BF9D] ml-1">Password</label>
              <div className="relative flex items-center">
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="w-full leading-12.5 pl-5 pr-12 placeholder:text-[#555555] bg-[#F1F3F6] rounded-lg outline-none focus:ring-2 focus:ring-[#06D6A0]"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <div className="absolute right-0 bg-[#06D6A0] rounded-lg p-3">
                  <Lock className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg py-3.25 text-md bg-[#06D6A0] text-white font-semibold flex items-center justify-center gap-2 hover:bg-[#05b88a] transition-all disabled:opacity-70"
              >
                {loading ? "Authenticating..." : (
                  <>
                    <LogIn className="w-5 h-5" />
                    Signin Now
                  </>
                )}
              </button>
            </div>

            <div className="relative flex items-center py-2">
              <div className="grow border-t border-[#C2C2C2]"></div>
              <span className="shrink mx-4 text-sm font-normal text-[#C2C2C2]">OR</span>
              <div className="grow border-t border-[#C2C2C2]"></div>
            </div>

            <div>
              <button
                type="button"
                onClick={onSwitch}
                className="w-full rounded-lg py-3.25 text-md border border-[#06D6A0] bg-transparent text-[#06D6A0] font-semibold hover:bg-[#06D6A0] hover:text-white transition-all"
              >
                Signup Now
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="bg-[#31353F] min-h-screen flex items-center justify-center">
        <div className="text-white text-center">
             <img src="/image.png" alt="login_illustrator_image" className="max-w-xl" />
        </div>
      </div>
      
    </div>
  );
};

export default Login;