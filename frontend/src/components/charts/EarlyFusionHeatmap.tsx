import { motion } from 'framer-motion';
import { tierColors } from '../../theme/palette';

interface EarlyFusionHeatmapProps {
  vector: number[];
}

/**
 * Visualizes the raw concatenated early-fusion feature vector as a strip
 * of intensity cells - a "sensor readout" for the earliest fusion tier,
 * before any probabilities have been computed.
 */
export function EarlyFusionHeatmap({ vector }: EarlyFusionHeatmapProps) {
  if (vector.length === 0) {
    return <p className="text-sm text-neutral-500">No early-fusion vector available.</p>;
  }

  const min = Math.min(...vector);
  const max = Math.max(...vector);
  const range = max - min || 1;

  return (
    <div className="flex flex-wrap gap-1">
      {vector.map((value, i) => {
        const intensity = (value - min) / range;
        return (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.6 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.01 }}
            title={value.toFixed(4)}
            className="w-4 h-6 rounded-sm"
            style={{
              backgroundColor: tierColors.early,
              opacity: 0.15 + intensity * 0.85,
            }}
          />
        );
      })}
    </div>
  );
}
