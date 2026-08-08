import { motion } from 'framer-motion';
import { Video, Mic, FileText, Brain } from 'lucide-react';
import { Card, Badge } from '../../components/ui';
import { EmotionRankingList, ModalityContributionsChart } from '../../components/charts';
import { VideoAnalysisResult, EMOTION_COLORS, EMOTION_ICONS, EmotionType } from '../../types';

interface VideoResultsPanelProps {
  result: VideoAnalysisResult;
}

export function VideoResultsPanel({ result }: VideoResultsPanelProps) {
  const { fusion } = result;

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="p-6">
          <div className="flex items-center gap-4 mb-6">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl"
              style={{ backgroundColor: `${EMOTION_COLORS[fusion.final_emotion as EmotionType]}20` }}
            >
              {EMOTION_ICONS[fusion.final_emotion as EmotionType]}
            </div>
            <div>
              <p className="text-sm text-neutral-400">Fused Emotion</p>
              <h2 className="text-3xl font-bold text-white">{fusion.final_emotion}</h2>
              <p className="text-sm text-neutral-500">{(fusion.final_confidence * 100).toFixed(1)}% confidence</p>
            </div>
          </div>
          <EmotionRankingList probabilities={fusion.final_probabilities} title="Top Fused Emotion Signals" />
        </Card>
      </motion.div>

      {result.transcript && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
              <FileText className="text-primary-400" size={18} />
              Transcript
            </h3>
            <p className="text-neutral-200 bg-neutral-800/50 rounded-lg p-3">"{result.transcript}"</p>
          </Card>
        </motion.div>
      )}

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <Card className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <ModalityMiniCard
              icon={Video}
              title="Facial Expression"
              emotion={result.facial_emotion.emotion}
              confidence={result.facial_emotion.confidence}
            />
            {result.audio_emotion && (
              <ModalityMiniCard
                icon={Mic}
                title="Acoustic Tone"
                emotion={result.audio_emotion.emotion}
                confidence={result.audio_emotion.confidence}
              />
            )}
            {result.text_emotion && (
              <ModalityMiniCard
                icon={FileText}
                title="Derived Text Emotion"
                emotion={result.text_emotion.emotion}
                confidence={result.text_emotion.confidence}
              />
            )}
          </div>
        </Card>
      </motion.div>

      {result.frame_emotions && result.frame_emotions.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card className="p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Emotion Timeline</h3>
            <div className="overflow-x-auto">
              <div className="flex gap-2 min-w-max pb-2">
                {result.frame_emotions.map((frame, i) => (
                  <motion.div
                    key={frame.frame_index}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.04 }}
                    className="flex flex-col items-center gap-1"
                    title={`${frame.emotion} - ${(frame.confidence * 100).toFixed(0)}%`}
                  >
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center text-lg"
                      style={{ backgroundColor: `${EMOTION_COLORS[frame.emotion as EmotionType]}20` }}
                    >
                      {EMOTION_ICONS[frame.emotion as EmotionType]}
                    </div>
                    <span className="text-xs text-neutral-500">#{frame.frame_index}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </Card>
        </motion.div>
      )}

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Brain className="text-primary-400" size={20} />
            Fusion Breakdown
          </h3>
          <div className="flex items-center gap-2 mb-4">
            <Badge variant="primary">{fusion.fusion_method}</Badge>
            <Badge variant="neutral">{fusion.inference_time_ms.toFixed(0)} ms</Badge>
          </div>
          <ModalityContributionsChart contributions={fusion.modality_contributions} />
        </Card>
      </motion.div>
    </div>
  );
}

function ModalityMiniCard({
  icon: Icon,
  title,
  emotion,
  confidence,
}: {
  icon: React.ElementType;
  title: string;
  emotion: string;
  confidence: number;
}) {
  return (
    <div className="bg-gradient-to-br from-primary-500/10 to-primary-500/5 border border-primary-500/30 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="text-primary-400" size={18} />
        <span className="text-sm font-medium text-neutral-300">{title}</span>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-2xl">{EMOTION_ICONS[emotion as EmotionType]}</span>
        <div>
          <p className="font-medium text-white">{emotion}</p>
          <p className="text-xs text-neutral-500">{(confidence * 100).toFixed(1)}% confident</p>
        </div>
      </div>
    </div>
  );
}
