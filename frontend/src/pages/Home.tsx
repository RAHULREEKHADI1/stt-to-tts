import React, { useState } from "react";
import TaskList from "../components/TaskList";
import VoiceButton from "../components/VoiceButton";
import { LayoutDashboard } from "lucide-react";

const Home: React.FC = () => {
  const [refresh, setRefresh] = useState(false);
    const handleRefresh = () => setRefresh(prev => !prev);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center">
      <nav className="w-full bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <div className="bg-indigo-600 p-2 rounded-lg">
            <LayoutDashboard className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold bg-clip-text text-transparent bg-linear-to-r from-indigo-600 to-purple-600">
            VoiceTask AI
          </span>
        </div>
      </nav>

      <main className="w-full max-w-4xl p-6 space-y-8">
        <section className="text-center pt-8">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight">
            Manage your day with <span className="text-indigo-600">Voice</span>
          </h1>
          <p className="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">
            Try saying <span className="font-mono text-sm bg-indigo-50 text-indigo-700 px-2 py-0.5 rounded italic">"Add a task to call Sarah tomorrow"</span>
          </p>
        </section>

        <div className="bg-white rounded-3xl shadow-xl shadow-indigo-100/50 p-10 border border-gray-100 flex flex-col items-center justify-center space-y-6">
          <div className="w-full max-w-sm">
            <VoiceButton onTaskUpdated={handleRefresh} />
          </div>
        </div>

        <section className="bg-white rounded-3xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="p-6 md:p-10">
            <TaskList key={refresh.toString()} />
          </div>
        </section>
      </main>

      <footer className="py-10 text-center">
        <p className="text-sm text-gray-400">
          Powered by Whisper & GPT-4o • 2026
        </p>
      </footer>
    </div>
  );
};

export default Home;