import { useCallback, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload, Sparkles, FileAudio, X, Mic, Square } from 'lucide-react';
import { Button, Card } from '../../components/ui';
import { useAudioRecorder } from './useAudioRecorder';

interface AudioInputPanelProps {
  file: File | Blob | null;
  loading: boolean;
  error: string | null;
  onSelectFile: (file: File | Blob, name?: string) => void;
  onClearFile: () => void;
  onSubmit: () => void;
}

export function AudioInputPanel({ file, loading, error, onSelectFile, onClearFile, onSubmit }: AudioInputPanelProps) {
  const [mode, setMode] = useState<'upload' | 'record'>('upload');
  const recorder = useAudioRecorder();

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selected = acceptedFiles[0];
    if (selected) onSelectFile(selected, selected.name);
  }, [onSelectFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'audio/*': ['.mp3', '.wav', '.m4a', '.ogg', '.webm'] },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
  });

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  function useRecordedClip() {
    if (recorder.recordedBlob) {
      onSelectFile(recorder.recordedBlob, 'recording.webm');
      recorder.reset();
    }
  }

  return (
    <Card className="p-6">
      <div className="flex items-center gap-2 mb-4">
        <TabButton active={mode === 'upload'} onClick={() => setMode('upload')}>
          Upload file
        </TabButton>
        <TabButton active={mode === 'record'} onClick={() => setMode('record')}>
          Record with mic
        </TabButton>
      </div>

      {!file && mode === 'upload' && (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
            transition-colors duration-200
            ${isDragActive ? 'border-secondary-500 bg-secondary-500/10' : 'border-neutral-700 hover:border-neutral-600'}
          `}
        >
          <input {...getInputProps()} />
          <Upload className="w-10 h-10 text-neutral-500 mx-auto mb-3" />
          <p className="text-neutral-400 mb-2">
            {isDragActive ? 'Drop the audio file here...' : 'Drag & drop an audio file here'}
          </p>
          <p className="text-xs text-neutral-500">Supports MP3, WAV, M4A, OGG (max 50MB)</p>
        </div>
      )}

      {!file && mode === 'record' && (
        <div className="rounded-xl border border-neutral-700 p-8 text-center">
          <div className="flex justify-center mb-4">
            <button
              type="button"
              onClick={recorder.isRecording ? recorder.stop : recorder.start}
              className={`w-16 h-16 rounded-full flex items-center justify-center transition-colors
                ${recorder.isRecording ? 'bg-secondary-600 hover:bg-secondary-700' : 'bg-primary-600 hover:bg-primary-700'}`}
            >
              {recorder.isRecording ? <Square size={22} className="text-white" /> : <Mic size={22} className="text-white" />}
            </button>
          </div>

          {/* Level meter */}
          <div className="flex items-end justify-center gap-1 h-10 mb-3">
            {Array.from({ length: 20 }).map((_, i) => {
              const threshold = i / 20;
              const active = recorder.isRecording && recorder.level > threshold;
              return (
                <motion.div
                  key={i}
                  className="w-1.5 rounded-full"
                  style={{
                    height: `${8 + threshold * 32}px`,
                    backgroundColor: active ? '#8b5cf6' : '#3f3f46',
                  }}
                  animate={{ opacity: active ? 1 : 0.5 }}
                />
              );
            })}
          </div>

          <p className="text-sm text-neutral-400 mb-3">
            {recorder.isRecording ? 'Recording... click to stop' : 'Click the mic to start recording'}
          </p>

          {recorder.error && <p className="text-sm text-secondary-400 mb-2">{recorder.error}</p>}

          {recorder.recordedBlob && !recorder.isRecording && (
            <div className="mt-3 flex flex-col items-center gap-3">
              <audio controls src={URL.createObjectURL(recorder.recordedBlob)} className="w-full" />
              <Button size="sm" onClick={useRecordedClip}>Use this recording</Button>
            </div>
          )}
        </div>
      )}

      {file && (
        <div className="bg-neutral-800/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-secondary-500/10 flex items-center justify-center">
              <FileAudio className="w-6 h-6 text-secondary-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">
                {file instanceof File ? file.name : 'Microphone recording'}
              </p>
              <p className="text-sm text-neutral-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
            <button
              type="button"
              onClick={onClearFile}
              className="p-2 rounded-lg hover:bg-neutral-700 text-neutral-400 hover:text-white"
            >
              <X size={18} />
            </button>
          </div>
          {previewUrl && <audio controls src={previewUrl} className="w-full mt-4" />}
        </div>
      )}

      <div className="flex justify-end mt-6">
        <Button disabled={!file} loading={loading} icon={<Sparkles size={18} />} onClick={onSubmit}>
          Analyze Audio
        </Button>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="mt-4 p-3 rounded-lg bg-secondary-500/10 border border-secondary-500/30 text-secondary-400 text-sm"
        >
          {error}
        </motion.div>
      )}
    </Card>
  );
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors
        ${active ? 'bg-primary-500/20 text-primary-300 border border-primary-500/30' : 'bg-neutral-800 text-neutral-400 hover:text-neutral-200'}`}
    >
      {children}
    </button>
  );
}
