import { motion } from 'framer-motion';
import { Mic, FileText, Brain } from 'lucide-react';
import { Card, Badge } from '../../components/ui';
import { EmotionRankingList, ModalityContributionsChart } from '../../components/charts';
import { AudioAnalysisResult, EMOTION_COLORS, EMOTION_ICONS, EmotionType } from '../../types';

interface AudioResultsPanelProps {
  result: AudioAnalysisResult;
}

export function AudioResultsPanel({ result }: AudioResultsPanelProps) {
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
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <ModalityMiniCard
              icon={Mic}
              title="Acoustic Tone"
              emotion={result.tone_emotion.emotion}
              confidence={result.tone_emotion.confidence}
            />
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

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
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
