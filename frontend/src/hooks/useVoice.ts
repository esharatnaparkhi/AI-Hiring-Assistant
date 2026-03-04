"use client";

import { useState, useRef, useCallback } from "react";
import { transcribeAudio, synthesizeSpeech } from "@/lib/api";

export function useVoice(sessionId: string) {
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const startRecording = useCallback(async () => {
    if (recording) return;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    chunksRef.current = [];
    recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
    recorder.start();
    mediaRef.current = recorder;
    setRecording(true);
  }, [recording]);

  const stopAndTranscribe = useCallback((): Promise<string> => {
    return new Promise((resolve) => {
      if (!mediaRef.current) { resolve(""); return; }
      mediaRef.current.onstop = async () => {
        setRecording(false);
        setTranscribing(true);
        const blob = new Blob(chunksRef.current, { type: "audio/wav" });
        const text = await transcribeAudio(sessionId, blob);
        setTranscribing(false);
        resolve(text);
      };
      mediaRef.current.stop();
      mediaRef.current.stream.getTracks().forEach((t) => t.stop());
    });
  }, [sessionId]);

  const speak = useCallback(async (text: string) => {
    if (!text) return;
    setSpeaking(true);
    const url = await synthesizeSpeech(sessionId, text);
    if (url) {
      audioRef.current = new Audio(url);
      audioRef.current.onended = () => {
        URL.revokeObjectURL(url);
        setSpeaking(false);
      };
      audioRef.current.onerror = () => setSpeaking(false);
      await audioRef.current.play().catch(() => setSpeaking(false));
    } else {
      setSpeaking(false);
    }
  }, [sessionId]);

  const stopSpeaking = useCallback(() => {
    audioRef.current?.pause();
    setSpeaking(false);
  }, []);

  return { recording, transcribing, speaking, startRecording, stopAndTranscribe, speak, stopSpeaking };
}
