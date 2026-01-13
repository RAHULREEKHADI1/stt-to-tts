import React, { useRef, useState } from "react";
import API from "../api/api";
import { Mic, Square, Loader2, Volume2 } from "lucide-react";

interface Props {
  onTaskUpdated: () => void;
}
interface VoiceResponse {
  user_text: string;
  response_text: string;
  audio_url?: string;
}

const VoiceButton: React.FC<Props> = ({ onTaskUpdated }) => {
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const [recording, setRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const startRecording = async () => {
    try {
      if (!navigator.mediaDevices) {
        alert("Microphone not supported");
        return;
      }

      streamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      recorderRef.current = new MediaRecorder(streamRef.current!, {
        mimeType: "audio/webm",
      });

      chunksRef.current = [];
      recorderRef.current.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorderRef.current.onstop = sendAudio;

      recorderRef.current.start();
      setRecording(true);
    } catch (err) {
      alert("Please allow microphone access");
      console.error(err);
    }
  };

  const stopRecording = () => {
    recorderRef.current?.stop();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    setRecording(false);
  };

  const sendAudio = async () => {
    setIsProcessing(true);
    const blob = new Blob(chunksRef.current, { type: "audio/webm" });
    const formData = new FormData();
    formData.append("audio", blob, "command.webm");

    try {
      const res = await API.post<VoiceResponse>("/voice/upload", formData);
      const { audio_url } = res.data;
      
      if (audio_url) {
        const rawBackend = import.meta.env.VITE_BACKEND_URL;
        const backendBase = rawBackend.replace(/\/api\/?$/, "");
        const normalized = audio_url.startsWith("/") ? audio_url.replace(/^\/+/, "") : audio_url;
        const finalUrl = audio_url.startsWith("http") ? audio_url : `${backendBase}/${normalized}`;
        console.log(finalUrl,"final url");
        

        const audio = new Audio(finalUrl);
        audio.play();
      }

      onTaskUpdated();
    } catch {
      alert("Voice command failed. Try again.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      {recording && (
        <div className="flex gap-1 items-center justify-center h-8">
          {[...Array(5)].map((_, i) => (
            <div
              key={i}
              className="w-1 bg-red-500 rounded-full animate-bounce"
              style={{ 
                height: '100%', 
                animationDelay: `${i * 0.1}s`,
                animationDuration: '0.6s' 
              }}
            />
          ))}
        </div>
      )}

      <button
        onClick={recording ? stopRecording : startRecording}
        disabled={isProcessing}
        className={`relative group flex items-center justify-center gap-3 px-8 py-4 rounded-full font-bold text-lg transition-all duration-300 shadow-xl hover:shadow-2xl active:scale-95 disabled:opacity-80 ${
          recording
            ? "bg-red-500 text-white animate-pulse ring-4 ring-red-100"
            : "bg-linear-to-r from-indigo-600 to-purple-600 text-white hover:from-indigo-700 hover:to-purple-700"
        }`}
      >
        {isProcessing ? (
          <>
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Processing...</span>
          </>
        ) : recording ? (
          <>
            <Square className="w-6 h-6 fill-current" />
            <span>Stop Recording</span>
          </>
        ) : (
          <>
            <Mic className="w-6 h-6" />
            <span>Speak Command</span>
          </>
        )}

        {!recording && (
          <div className="absolute inset-0 rounded-full bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
      </button>
      
      {isProcessing && (
        <p className="text-sm text-indigo-600 font-medium flex items-center gap-2 animate-pulse">
          <Volume2 className="w-4 h-4" /> AI is thinking...
        </p>
      )}
    </div>
  );
};

export default VoiceButton;