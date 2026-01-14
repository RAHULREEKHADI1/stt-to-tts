import React, { useState, useRef } from "react";
import API from "../api/api";
import { Upload, Loader2, Volume2, FileAudio, AlertCircle } from "lucide-react";

interface Props {
  onTaskUpdated: () => void;
}

interface VoiceResponse {
  user_text: string;
  response_text: string;
  audio_url?: string;
}

const VoiceButton: React.FC<Props> = ({ onTaskUpdated }) => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedExtensions = [".mp3", ".wav", ".webm"];
  const allowedMimeTypes = ["audio/mpeg", "audio/wav", "audio/webm", "audio/mp3"];

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setError(null); 

    if (!file) return;

    const isAcceptedType = allowedMimeTypes.includes(file.type) || 
                           allowedExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

    if (!isAcceptedType) {
      setError("Please upload a valid .mp3, .wav, or .webm file.");
      if (fileInputRef.current) fileInputRef.current.value = "";
      return;
    }

    await uploadAudio(file);
    
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const uploadAudio = async (file: File) => {
  setIsProcessing(true);
  setError(null);

  const formData = new FormData();
  formData.append("audio", file);

  try {
    const res = await API.post<VoiceResponse>("/voice/upload", formData);
    const { audio_url } = res.data;

    if (audio_url) {
      const rawBackend = import.meta.env.VITE_BACKEND_URL;
      const backendBase = rawBackend.replace(/\/api\/?$/, "");

      const normalized = audio_url.startsWith("/")
        ? audio_url.replace(/^\/+/, "")
        : audio_url;

      const finalUrl = audio_url.startsWith("http")
        ? `${audio_url}?t=${Date.now()}`
        : `${backendBase}/${normalized}?t=${Date.now()}`;

      await new Promise((resolve) => setTimeout(resolve, 5000));

      const audio = new Audio(finalUrl);

      audio.oncanplaythrough = () => {
        audio.play().catch(console.error);
      };

      audio.onerror = () => {
        setError("Audio failed to load.");
      };
    }

    onTaskUpdated();
  } catch (err: any) {
    setError(
      err?.response?.data?.error ||
      err?.response?.data?.message ||
      "Upload failed. Please try again."
    );
    console.error(err);
  } finally {
    setIsProcessing(false);
  }
};

  return (
    <div className="flex flex-col items-center gap-4 w-full">
      <input
        type="file"
        accept=".mp3,audio/mpeg,.wav,audio/wav,.webm,audio/webm"
        className="hidden"
        ref={fileInputRef}
        onChange={handleFileChange}
      />

      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        disabled={isProcessing}
        className={`relative group flex items-center justify-center gap-3 px-8 py-4 rounded-full font-bold text-lg transition-all duration-300 shadow-xl hover:shadow-2xl active:scale-95 disabled:opacity-80 
          bg-linear-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700 hover:scale-105`}
      >
        {isProcessing ? (
          <>
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Processing...</span>
          </>
        ) : (
          <>
            <Upload className="w-6 h-6" />
            <span>Upload Command</span>
          </>
        )}
      </button>

      <div className="h-6 flex items-center justify-center">
        {error ? (
          <p className="text-sm text-red-500 font-medium flex items-center gap-2 animate-in fade-in slide-in-from-top-1">
            <AlertCircle className="w-4 h-4" /> {error}
          </p>
        ) : isProcessing ? (
          <p className="text-sm text-indigo-600 font-medium flex items-center gap-2 animate-pulse">
            <Volume2 className="w-4 h-4" /> AI is analyzing audio...
          </p>
        ) : (
          <p className="text-xs text-gray-400 flex items-center gap-1">
            <FileAudio className="w-3 h-3" /> MP3, WAV, or WebM
          </p>
        )}
      </div>
    </div>
  );
};

export default VoiceButton;