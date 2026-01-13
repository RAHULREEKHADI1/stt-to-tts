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

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await API.post("/auth/signup", { email, password });
      alert("Signup successful! Login now.");
      onSignupSuccess();
      navigate('/');
    } catch {
      alert("Signup failed. That email might already be in use.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-[30%_70%] min-h-screen">
            <div className="bg-[#172026] p-8 flex flex-col justify-center items-center shadow-2xl">
        <div className="min-w-full">
          
          <div className="text-center mb-10">
            <h2 className="text-white font-bold text-2xl">Create Account</h2>
            <p className="text-[#04BFAD] text-sm mt-2">Join us and start your journey</p>
          </div>

          <form onSubmit={handleSignup} className="flex flex-col gap-8">
            <div className="flex flex-col gap-2">
              <label className="font-normal text-md text-[#04BF9D] ml-1">Email Address</label>
              <div className="relative flex items-center">
                <input
                  type="email"
                  required
                  placeholder="name@company.com"
                  className="w-full leading-12.5 pl-5 pr-12 placeholder:text-[#555555] bg-[#F1F3F6] rounded-lg outline-none focus:ring-2 focus:ring-[#06D6A0] text-gray-800"
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
                  minLength={6}
                  placeholder="••••••••"
                  className="w-full leading-12.5 pl-5 pr-12 placeholder:text-[#555555] bg-[#F1F3F6] rounded-lg outline-none focus:ring-2 focus:ring-[#06D6A0] text-gray-800"
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
                className="w-full rounded-lg py-3.25 text-md bg-[#06D6A0] text-white font-semibold flex items-center justify-center gap-2 hover:bg-[#05b88a] transition-all disabled:opacity-70 active:scale-[0.98]"
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
                className="w-full rounded-lg py-3.25 text-md border border-[#06D6A0] bg-transparent text-[#06D6A0] font-semibold hover:bg-[#06D6A0] hover:text-white transition-all flex items-center justify-center gap-2"
              >
                Already have an account? <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>
        </div>
      </div>

      <div className="bg-[#31353F] min-h-screen flex items-center justify-center">
        <div className="text-white text-center">
             <img 
               src="/imagecopy.png" 
               alt="signup_illustrator_image" 
               className="max-w-xl transition-transform duration-700 hover:scale-105" 
             />
        </div>
      </div>
      
    </div>
  );
};

export default Signup;