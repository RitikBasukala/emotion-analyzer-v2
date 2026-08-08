import { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { EMOTION_COLORS, EMOTION_ICONS, EmotionType } from '../../types';

interface EmotionRankingListProps {
  probabilities: Record<string, number>;
  title?: string;
  topCount?: number;
  previewCount?: number;
}

interface RankedEmotion {
  name: string;
  value: number;
  color: string;
}

const TOP_LABELS = ['Primary', 'Secondary', 'Tertiary'];

export function EmotionRankingList({
  probabilities,
  title,
  topCount = 3,
  previewCount = 3,
}: EmotionRankingListProps) {
  const [expanded, setExpanded] = useState(false);

  const ranked = useMemo<RankedEmotion[]>(() => (
    Object.entries(probabilities)
      .map(([emotion, value]) => ({
        name: emotion,
        value: value * 100,
        color: EMOTION_COLORS[emotion as EmotionType] || '#a1a1aa',
      }))
      .sort((a, b) => b.value - a.value)
  ), [probabilities]);

  const highlighted = ranked.slice(0, topCount);
  const preview = ranked.slice(topCount, topCount + previewCount);
  const remaining = ranked.slice(topCount + previewCount);
  const hasRemaining = remaining.length > 0;

  return (
    <div className="w-full space-y-4">
      {title && <h3 className="text-lg font-semibold text-white">{title}</h3>}

      {highlighted.length > 0 && (
        <div className="grid gap-3 md:grid-cols-3">
          {highlighted.map((item, index) => (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, delay: index * 0.05 }}
              className="rounded-2xl border border-primary-500/30 bg-gradient-to-br from-primary-500/15 to-primary-500/5 p-4 shadow-lg shadow-black/10"
            >
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <p className="inline-flex items-center rounded-full border border-primary-400/40 bg-primary-500/10 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-200">
                    {TOP_LABELS[index] ?? `Top ${index + 1}`}
                  </p>
                  <p className="mt-2 truncate text-base font-semibold text-white">
                    {EMOTION_ICONS[item.name as EmotionType]} {item.name}
                  </p>
                </div>
                <div className="rounded-full bg-white/5 px-3 py-1 text-sm font-medium text-white">
                  {item.value.toFixed(1)}%
                </div>
              </div>
              <div className="mt-4 h-2 rounded-full bg-neutral-800 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${item.value}%` }}
                  transition={{ duration: 0.8, ease: 'easeOut' }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: item.color }}
                />
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {preview.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs uppercase tracking-[0.24em] text-neutral-500">Lower signals</p>
          <div className="space-y-2">
            {preview.map((item, index) => (
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
                  <div className="mt-1 h-1.5 rounded-full bg-neutral-800 overflow-hidden">
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

      {hasRemaining && (
        <div className="space-y-3">
          <button
            type="button"
            onClick={() => setExpanded((current) => !current)}
            className="inline-flex items-center gap-2 rounded-full border border-neutral-700 bg-neutral-900 px-4 py-2 text-sm font-medium text-neutral-200 transition hover:border-primary-500/50 hover:text-white"
          >
            {expanded ? 'Hide remaining emotions' : `Show ${remaining.length} remaining emotions`}
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          <AnimatePresence initial={false}>
            {expanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.25, ease: 'easeOut' }}
                className="overflow-hidden"
              >
                <div className="space-y-2 pt-1">
                  {remaining.map((item, index) => (
                    <div
                      key={item.name}
                      className="flex items-center gap-3 rounded-xl border border-neutral-800/70 bg-neutral-950/40 px-3 py-2"
                    >
                      <span className="text-lg">{EMOTION_ICONS[item.name as EmotionType]}</span>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-3">
                          <p className="truncate text-sm font-medium text-neutral-300">{item.name}</p>
                          <p className="shrink-0 text-xs text-neutral-500">{item.value.toFixed(1)}%</p>
                        </div>
                        <div className="mt-1 h-1.5 rounded-full bg-neutral-800 overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${item.value}%` }}
                            transition={{ duration: 0.7, ease: 'easeOut', delay: index * 0.02 }}
                            className="h-full rounded-full opacity-50"
                            style={{ backgroundColor: item.color }}
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}
    </div>
  );
}