import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import TaskList from "../components/TaskList";
import VoiceButton from "../components/VoiceButton";
import { LayoutDashboard, LogOut } from "lucide-react";


const Home: React.FC<{ onLogout: () => void }> = ({onLogout}) => {
  const [refresh, setRefresh] = useState(false);
  const navigate = useNavigate();

  const handleRefresh = () => setRefresh(prev => !prev);

  const handleLogout = () => {
    onLogout();
    navigate("/");
  };

  return (
    <div
      className="min-h-screen flex flex-col items-center bg-center bg-no-repeat bg-cover bg-fixed"
      style={{ backgroundImage: "url('/voice_command.png')" }}
    >
      <div className="absolute inset-0 bg-slate-950/40 pointer-events-none" />

      <nav className="relative w-full px-6 py-4 flex justify-between items-center sticky top-0 z-20 border-b border-white/10 backdrop-blur-md bg-white/5">
        <div className="flex items-center gap-3">
          <div className="bg-indigo-500/20 p-2.5 rounded-xl ring-1 ring-indigo-400/30">
            <LayoutDashboard className="w-5 h-5 text-indigo-300" />
          </div>
          <span className="text-xl font-bold tracking-wide text-white">
            VoiceTask <span className="text-indigo-400">AI</span>
          </span>
        </div>

        <button
          onClick={handleLogout}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-red-500/20 border border-white/10 hover:border-red-500/50 text-slate-300 hover:text-red-400 transition-all duration-200 group"
        >
          <span className="text-sm font-medium">Logout</span>
          <LogOut className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </button>
      </nav>

      <main className="relative w-full max-w-4xl p-6 space-y-10 z-10">
        <section className="text-center pt-10">
          <h1 className="text-4xl font-extrabold tracking-tight text-white drop-shadow-lg">
            Manage your day with <span className="text-indigo-400">Voice</span>
          </h1>
          <p className="mt-4 text-base text-slate-300 max-w-2xl mx-auto">
            Try saying{" "}
            <span className="font-mono text-sm bg-white/10 text-indigo-300 px-2 py-1 rounded-lg border border-white/5 italic">
              "Add a task to call Sarah tomorrow"
            </span>
          </p>
        </section>

        <div className="bg-white/5 backdrop-blur-xl rounded-3xl shadow-2xl shadow-black/40 p-10 border border-white/10 flex flex-col items-center justify-center space-y-6 transform hover:scale-[1.01] transition-transform">
          <div className="w-full max-w-sm">
            <VoiceButton onTaskUpdated={handleRefresh} />
          </div>
        </div>

        <section className="bg-slate-900/40 backdrop-blur-xl rounded-3xl shadow-xl border border-white/10 overflow-hidden">
          <div className="p-6 md:p-10">
            <TaskList key={refresh.toString()} />
          </div>
        </section>
      </main>

      <footer className="relative py-10 text-center z-10">
        <p className="text-sm text-slate-500">
          Powered by Whisper & GPT-4o • 2026
        </p>
      </footer>
    </div>
  );
};

export default Home;