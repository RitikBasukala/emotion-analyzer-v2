import { motion } from 'framer-motion';
import { Video } from 'lucide-react';
import { Card } from '../components/ui';
import { useVideoAnalysis, VideoInputPanel, VideoResultsPanel } from '../features/video';

export function VideoPage() {
  const { file, loading, result, error, selectFile, clearFile, analyze } = useVideoAnalysis();

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
            <Video className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Video Emotion Analysis</h1>
            <p className="text-neutral-400">Full multimodal emotion detection from video</p>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
          <VideoInputPanel
            file={file}
            loading={loading}
            error={error}
            onSelectFile={selectFile}
            onClearFile={clearFile}
            onSubmit={analyze}
          />

          <Card className="p-6 mt-6">
            <h3 className="text-lg font-semibold text-white mb-4">Multimodal Analysis Process</h3>
            <div className="space-y-3">
              {[
                { step: 1, text: 'Extract frames from video' },
                { step: 2, text: 'Detect and analyze facial expressions' },
                { step: 3, text: 'Extract audio track and transcribe with Whisper' },
                { step: 4, text: 'Analyze text and audio/tone emotions' },
                { step: 5, text: 'Fuse all modalities for the final prediction' },
              ].map((item) => (
                <div key={item.step} className="flex items-center gap-3 text-sm">
                  <div className="w-6 h-6 rounded-full bg-primary-500/10 flex items-center justify-center text-primary-400 font-medium">
                    {item.step}
                  </div>
                  <span className="text-neutral-400">{item.text}</span>
                </div>
              ))}
            </div>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
          {result ? (
            <VideoResultsPanel result={result} />
          ) : (
            <Card className="p-6 h-full flex flex-col items-center justify-center text-center min-h-[400px]">
              <div className="w-16 h-16 rounded-2xl bg-neutral-800 flex items-center justify-center mb-4">
                <Video className="w-8 h-8 text-neutral-600" />
              </div>
              <p className="text-neutral-500">
                Upload a video file to see multimodal emotion analysis results
              </p>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  );
}
