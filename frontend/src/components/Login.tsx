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
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await API.post("/auth/login", { email, password });
      setAuthToken(res.data.token);
      onLogin();
      navigate('/home');
    } catch (err: any) {
      setError(err.response?.data?.message || "Invalid email or password. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[30%_70%] min-h-screen">

      <div className="bg-[#172026] p-6 sm:p-8 flex flex-col justify-center items-center shadow-2xl bg-center bg-no-repeat bg-cover bg-fixed lg:border lg:border-r-white "
        style={{ backgroundImage: "url('/voice_command.png')" }} >
        <div className="w-full max-w-md">

          <div className="text-center mb-10">
            <h2 className="text-4xl font-extrabold tracking-tight text-white drop-shadow-lg">Welcome <span className="text-indigo-400">Back</span></h2>
            <p className="text-indigo-300 font-mono text-sm mt-2">Login into your account</p>
          </div>

          <form onSubmit={handleLogin} className="flex flex-col gap-8">
            <div className="flex flex-col gap-2">
              <label className="font-normal text-md text-indigo-300 ml-1">Email Address</label>
              <div className="relative flex items-center">
                <input
                  type="email"
                  required
                  placeholder="name@company.com"
                  className="w-full leading-12.5 pl-5 pr-12 placeholder:text-[#555555] bg-[#F1F3F6] rounded-lg outline-none focus:ring-2 focus:ring-[#06D6A0]"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <div className="absolute right-2 bg-indigo-600 rounded-lg p-3">
                  <Mail className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <label className="font-normal text-md text-indigo-300 ml-1">Password</label>
              <div className="relative flex items-center">
                <input
                  type="password"
                  required
                  placeholder="••••••••"
                  className="w-full leading-12.5 pl-5 pr-12 placeholder:text-[#555555] bg-[#F1F3F6] rounded-lg outline-none focus:ring-2 focus:ring-[#06D6A0]"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <div className="absolute right-2 bg-indigo-600 rounded-lg p-3">
                  <Lock className="w-5 h-5 text-white" />
                </div>
              </div>
            </div>

            <div>
              {error && (
                <div className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 my-4 py-1 rounded-xl text-sm animate-shake">
                  {error}
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className="bg-linear-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 hover:scale-105 w-full rounded-lg py-3.25 text-md font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-70"
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
                className="bg-linear-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 hover:scale-105 w-full rounded-lg py-3.25 text-md font-semibold transition-all flex items-center justify-center gap-2"
              >
                Signup Now
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className=" min-h-screen hidden md:flex items-center justify-center bg-cover bg-no-repeat bg-center"
        style={{ backgroundImage: "url('/voice_command.png')" }} >
        <div className="text-white text-center flex flex-col gap-8 items-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-white drop-shadow-lg max-w-sm mx-auto pt-10">
            Manage your day <br />
            with <span className="text-indigo-400">Voice</span>
          </h1>

          <img src="/image.png" alt="login_illustrator_image" className="max-w-xl w-full h-auto object-contain transition-transform duration-700 hover:scale-105" />
        </div>
      </div>

    </div>
  );
};

export default Login;