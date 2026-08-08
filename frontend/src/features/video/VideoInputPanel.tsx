import { useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { Upload, Sparkles, FileVideo, X } from 'lucide-react';
import { Button, Card } from '../../components/ui';

interface VideoInputPanelProps {
  file: File | null;
  loading: boolean;
  error: string | null;
  onSelectFile: (file: File) => void;
  onClearFile: () => void;
  onSubmit: () => void;
}

export function VideoInputPanel({ file, loading, error, onSelectFile, onClearFile, onSubmit }: VideoInputPanelProps) {
  const onDrop = useCallback((acceptedFiles: File[]) => {
    const selected = acceptedFiles[0];
    if (selected) onSelectFile(selected);
  }, [onSelectFile]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'video/*': ['.mp4', '.webm', '.mov', '.avi'] },
    maxFiles: 1,
    maxSize: 100 * 1024 * 1024,
  });

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file]);

  return (
    <Card className="p-6">
      <label className="block text-sm font-medium text-neutral-300 mb-4">Upload video file</label>

      {!file ? (
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
            transition-colors duration-200
            ${isDragActive ? 'border-primary-500 bg-primary-500/10' : 'border-neutral-700 hover:border-neutral-600'}
          `}
        >
          <input {...getInputProps()} />
          <Upload className="w-10 h-10 text-neutral-500 mx-auto mb-3" />
          <p className="text-neutral-400 mb-2">
            {isDragActive ? 'Drop the video file here...' : 'Drag & drop a video file here'}
          </p>
          <p className="text-xs text-neutral-500">Supports MP4, WebM, MOV, AVI (max 100MB)</p>
        </div>
      ) : (
        <div className="bg-neutral-800/50 rounded-xl p-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-primary-500/10 flex items-center justify-center">
              <FileVideo className="w-6 h-6 text-primary-400" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">{file.name}</p>
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
          {previewUrl && <video controls src={previewUrl} className="w-full mt-4 rounded-lg" />}
        </div>
      )}

      <div className="flex justify-end mt-6">
        <Button disabled={!file} loading={loading} icon={<Sparkles size={18} />} onClick={onSubmit}>
          Analyze Video
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
