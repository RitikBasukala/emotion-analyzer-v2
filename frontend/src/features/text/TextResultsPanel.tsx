import { motion } from 'framer-motion';
import { Card } from '../../components/ui';
import { EMOTION_COLORS, EMOTION_ICONS, EmotionType, TextAnalysisResult } from '../../types';

interface TextResultsPanelProps {
  result: TextAnalysisResult;
}

export function TextResultsPanel({ result }: TextResultsPanelProps) {
  const { emotion, confidence, probabilities } = result.prediction;
  const nextEmotions = Object.entries(probabilities)
    .map(([name, value]) => ({
      name,
      value: value * 100,
      color: EMOTION_COLORS[name as EmotionType] || '#a1a1aa',
    }))
    .sort((left, right) => right.value - left.value)
    .slice(1, 4);

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

          {nextEmotions.length > 0 && (
            <div className="space-y-3">
              <p className="text-xs uppercase tracking-[0.24em] text-neutral-500">Later top 3 emotions</p>
              <div className="space-y-2">
                {nextEmotions.map((item, index) => (
                  <motion.div
                    key={item.name}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.25, delay: index * 0.03 }}
                    className="flex items-center gap-3 rounded-xl border border-neutral-800/80 bg-neutral-900/50 px-3 py-2"
                  >
                    <span className="text-lg">{EMOTION_ICONS[item.name as EmotionType]}</span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-3">
                        <p className="truncate text-sm font-medium text-neutral-200">{item.name}</p>
                        <p className="shrink-0 text-xs text-neutral-400">{item.value.toFixed(1)}%</p>
                      </div>
                      <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-neutral-800">
                        <motion.div
                          initial={{ width: 0 }}
                          animate={{ width: `${item.value}%` }}
                          transition={{ duration: 0.7, ease: 'easeOut' }}
                          className="h-full rounded-full opacity-70"
                          style={{ backgroundColor: item.color }}
                        />
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}
        </Card>
      </motion.div>

    </div>
  );
}
