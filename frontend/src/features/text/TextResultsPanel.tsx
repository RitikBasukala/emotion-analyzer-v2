import { motion } from 'framer-motion';
import { Card } from '../../components/ui';
import { EmotionRankingList } from '../../components/charts';
import { EMOTION_COLORS, EMOTION_ICONS, EmotionType, TextAnalysisResult } from '../../types';

interface TextResultsPanelProps {
  result: TextAnalysisResult;
}

export function TextResultsPanel({ result }: TextResultsPanelProps) {
  const { emotion, confidence, probabilities } = result.prediction;

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="p-6">
          <div className="flex items-center gap-4 mb-6">
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl"
              style={{ backgroundColor: `${EMOTION_COLORS[emotion as EmotionType]}20` }}
            >
              {EMOTION_ICONS[emotion as EmotionType]}
            </div>
            <div>
              <p className="text-sm text-neutral-400">Detected Emotion</p>
              <h2 className="text-3xl font-bold text-white">{emotion}</h2>
              <p className="text-sm text-neutral-500">{(confidence * 100).toFixed(1)}% confidence</p>
            </div>
          </div>

          <div className="mb-6">
            <div className="h-3 bg-neutral-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${confidence * 100}%` }}
                transition={{ duration: 0.8, ease: 'easeOut' }}
                className="h-full rounded-full"
                style={{ backgroundColor: EMOTION_COLORS[emotion as EmotionType] }}
              />
            </div>
          </div>

          <EmotionRankingList probabilities={probabilities} title="Emotion Signals" />
        </Card>
      </motion.div>

    </div>
  );
}
