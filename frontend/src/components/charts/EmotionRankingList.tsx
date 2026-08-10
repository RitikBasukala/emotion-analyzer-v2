import { useMemo } from 'react';
import { motion } from 'framer-motion';
import { resolveEmotionTheme } from '../../types';

interface EmotionRankingListProps {
  probabilities: Record<string, number>;
  title?: string;
  topCount?: number;
  previewCount?: number;
}

interface RankedEmotion {
  name: string;
  value: number;
  theme: ReturnType<typeof resolveEmotionTheme>;
}

export function EmotionRankingList({
  probabilities,
  title,
}: EmotionRankingListProps) {
  const ranked = useMemo<RankedEmotion[]>(() => (
    Object.entries(probabilities)
      .map(([emotion, value]) => ({
        name: emotion,
        value: value * 100,
        theme: resolveEmotionTheme(emotion),
      }))
      .sort((a, b) => b.value - a.value)
  ), [probabilities]);

  const primary = ranked[0];
  const others = ranked.slice(1);

  return (
    <div className="w-full space-y-5">
      {title && <h3 className="text-lg font-semibold text-white">{title}</h3>}

      {primary && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="rounded-2xl border border-primary-500/30 bg-gradient-to-br from-primary-500/15 to-primary-500/5 p-4 shadow-lg shadow-black/10"
        >
          <div className="flex items-center justify-between gap-3">
            <div className="min-w-0">
              <p className="inline-flex items-center rounded-full border border-primary-400/40 bg-primary-500/10 px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-[0.18em] text-primary-200">
                Primary Emotion
              </p>
              <p className="mt-2 truncate text-base font-semibold text-white">
                {primary.theme.icon} {primary.name}
              </p>
            </div>
            <div className="rounded-full bg-white/5 px-3 py-1 text-sm font-medium text-white">
              {primary.value.toFixed(1)}%
            </div>
          </div>
          <div className="mt-4 h-2 rounded-full bg-neutral-800 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${primary.value}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
              className="h-full rounded-full"
              style={{ backgroundColor: primary.theme.color }}
            />
          </div>
        </motion.div>
      )}

      {others.length > 0 && (
        <div className="space-y-3">
          <p className="text-xs uppercase tracking-[0.24em] text-neutral-500">Other emotions</p>
          <div className="space-y-2">
            {others.map((item, index) => (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, delay: index * 0.03 }}
                className="flex items-center gap-3 rounded-xl border border-neutral-800/80 bg-neutral-900/50 px-3 py-2"
              >
                <span className="text-lg">{item.theme.icon}</span>
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
                      style={{ backgroundColor: item.theme.color }}
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}