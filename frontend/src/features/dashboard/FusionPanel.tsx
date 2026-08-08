import { motion } from 'framer-motion';
import { Layers, Zap } from 'lucide-react';
import { Card, Badge, LoadingSpinner } from '../../components/ui';
import { EarlyFusionHeatmap, ModalityContributionsChart, TierComparisonChart } from '../../components/charts';
import { EMOTION_COLORS, EMOTION_ICONS, EmotionType, FusionResult } from '../../types';

interface FusionPanelProps {
  fusion: FusionResult | null;
  loading: boolean;
  error: string | null;
  hasAnySignal: boolean;
}

export function FusionPanel({ fusion, loading, error, hasAnySignal }: FusionPanelProps) {
  if (!hasAnySignal) {
    return (
      <Card className="p-8 flex flex-col items-center justify-center text-center min-h-[300px]">
        <Layers className="w-10 h-10 text-neutral-600 mb-3" />
        <p className="text-neutral-400 font-medium">Fusion cockpit is idle</p>
        <p className="text-sm text-neutral-500 mt-1 max-w-sm">
          Run a Text, Audio, or Video analysis and its result will automatically
          feed this live sensor-fusion view.
        </p>
      </Card>
    );
  }

  if (loading && !fusion) {
    return (
      <Card className="p-8 flex items-center justify-center min-h-[300px]">
        <LoadingSpinner />
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-8">
        <p className="text-secondary-400">{error}</p>
      </Card>
    );
  }

  if (!fusion) return null;

  return (
    <div className="space-y-6">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        <Card className="p-6 glow-primary">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <Zap className="text-primary-400" size={20} />
              <h2 className="text-lg font-semibold text-white">Live Fusion Result</h2>
              {loading && <span className="text-xs text-neutral-500">refreshing...</span>}
            </div>
            <Badge variant="primary">{fusion.fusion_method}</Badge>
          </div>

          <div className="flex items-center gap-4">
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center text-4xl"
              style={{ backgroundColor: `${EMOTION_COLORS[fusion.final_emotion as EmotionType]}20` }}
            >
              {EMOTION_ICONS[fusion.final_emotion as EmotionType]}
            </div>
            <div>
              <p className="text-sm text-neutral-400">Final Decision</p>
              <h2 className="text-4xl font-bold text-white">{fusion.final_emotion}</h2>
              <p className="text-sm text-neutral-500">
                {(fusion.final_confidence * 100).toFixed(1)}% confidence · {fusion.inference_time_ms.toFixed(0)}ms
              </p>
            </div>
          </div>
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-1">Fusion Tiers</h3>
          <p className="text-sm text-neutral-500 mb-4">
            Mid (gated projection) and Late (soft-voting) tiers compared against the final blended decision.
          </p>
          <TierComparisonChart
            midFusionProbabilities={fusion.tiers.mid_fusion_probabilities}
            lateFusionProbabilities={fusion.tiers.late_fusion_probabilities}
            finalProbabilities={fusion.final_probabilities}
          />
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-1">Early Fusion Vector</h3>
          <p className="text-sm text-neutral-500 mb-4">
            Raw concatenated feature readout before any probability projection.
          </p>
          <EarlyFusionHeatmap vector={fusion.tiers.early_fusion_vector} />
        </Card>
      </motion.div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Modality Contributions & Agreement</h3>
          <ModalityContributionsChart contributions={fusion.modality_contributions} />
        </Card>
      </motion.div>
    </div>
  );
}
