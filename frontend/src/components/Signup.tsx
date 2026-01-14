import React, { useState } from "react";
import API from "../api/api";
import { Mail, Lock, UserPlus, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface Props {
  onSignupSuccess: () => void;
}

const Signup: React.FC<Props> = ({ onSignupSuccess }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);
    try {
      await API.post("/auth/signup", { email, password });
      setSuccess(true);
      setTimeout(() => {
        onSignupSuccess();
        navigate('/');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.message || "Signup Failed. Email already registered.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[30%_70%] min-h-screen">
      <div className="p-8 flex flex-col justify-center items-center shadow-2xl bg-center bg-no-repeat bg-cover bg-fixed lg:border lg:border-r-white "
        style={{ backgroundImage: "url('/voice_command.png')" }} >
        <div className="min-w-full max-w-md">

          <div className="text-center mb-10">
            <h2 className="text-4xl font-extrabold tracking-tight text-white drop-shadow-lg">Create <span className="text-indigo-400">Account</span></h2>
            <p className="text-indigo-300 font-mono text-sm mt-2">Join us and start your journey</p>
          </div>

          <form onSubmit={handleSignup} className="flex flex-col gap-8">
            <div className="flex flex-col gap-2">
              <label className="font-normal text-md text-indigo-300 ml-1">Email Address</label>
              <div className="relative flex items-center">
                <input
                  type="email"
                  required
                  placeholder="name@company.com"
                  className="w-full leading-12.5 pl-5 pr-12 placeholder:text-[#555555] bg-[#F1F3F6] rounded-lg outline-none focus:ring-2 focus:ring-[#06D6A0] text-gray-800"
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
                  minLength={6}
                  placeholder="••••••••"
                  className="w-full leading-12.5 pl-5 pr-12 placeholder:text-[#555555] bg-[#F1F3F6] rounded-lg outline-none focus:ring-2 focus:ring-[#06D6A0] text-gray-800"
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
              {success && (
                <div className="bg-emerald-500/10 border border-emerald-500/50 text-emerald-400 px-4 py-3 rounded-xl text-sm flex items-center gap-3 animate-in fade-in zoom-in duration-300 my-5">
                  <div className="bg-emerald-500/20 p-1 rounded-full">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <p>Account created! Redirecting to login...</p>
                </div>
              )}
              <button
                type="submit"
                disabled={loading}
                className="bg-linear-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 hover:scale-105 w-full rounded-lg py-3.25 text-md font-semibold transition-all flex items-center justify-center gap-2 disabled:opacity-70"
              >
                {loading ? "Creating account..." : (
                  <>
                    <UserPlus className="w-5 h-5" />
                    Get Started
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
                onClick={onSignupSuccess}
                className="bg-linear-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 hover:scale-105 w-full rounded-lg py-3.25 text-md font-semibold transition-all flex items-center justify-center gap-2"
              >
                Already have an account? <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className=" min-h-screen hidden md:flex items-center justify-center bg-cover bg-no-repeat bg-center"
        style={{ backgroundImage: "url('/voice_command.png')" }} >
        <div className="text-white text-center flex flex-col gap-16 items-center">
          <h1 className="text-4xl font-extrabold tracking-tight text-white drop-shadow-lg max-w-sm mx-auto">
            Manage your day <br />
            with <span className="text-indigo-400">Voice</span>
          </h1>

          <img
            src="/imagecopy.png"
            alt="signup_illustrator_image"
            className="max-w-xl w-full h-auto object-contain  transition-transform duration-700 hover:scale-105"
          />
        </div>
      </div>

    </div>
  );
};

export default Signup;