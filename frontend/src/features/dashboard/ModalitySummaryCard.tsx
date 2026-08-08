import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowUpRight } from 'lucide-react';
import { Card } from '../../components/ui';
import { EMOTION_COLORS, EMOTION_ICONS, EmotionPrediction, EmotionType } from '../../types';

interface ModalitySummaryCardProps {
  title: string;
  icon: React.ElementType;
  accentClassName: string;
  href: string;
  prediction: EmotionPrediction | null;
  included: boolean;
  onToggleIncluded: (included: boolean) => void;
}

export function ModalitySummaryCard({
  title,
  icon: Icon,
  accentClassName,
  href,
  prediction,
  included,
  onToggleIncluded,
}: ModalitySummaryCardProps) {
  return (
    <Card className="p-5 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${accentClassName}`}>
            <Icon size={18} className="text-white" />
          </div>
          <span className="font-medium text-white">{title}</span>
        </div>
        <Link to={href} className="text-neutral-500 hover:text-primary-400 transition-colors">
          <ArrowUpRight size={16} />
        </Link>
      </div>

      {prediction ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-2xl">{EMOTION_ICONS[prediction.emotion as EmotionType]}</span>
            <div>
              <p className="font-semibold text-white">{prediction.emotion}</p>
              <p className="text-xs text-neutral-500">{(prediction.confidence * 100).toFixed(1)}% confident</p>
            </div>
          </div>
          <div className="h-1.5 bg-neutral-800 rounded-full overflow-hidden mb-4">
            <div
              className="h-full rounded-full"
              style={{
                width: `${prediction.confidence * 100}%`,
                backgroundColor: EMOTION_COLORS[prediction.emotion as EmotionType],
              }}
            />
          </div>
        </motion.div>
      ) : (
        <p className="text-sm text-neutral-500 flex-1">
          No live signal yet. Run a {title.toLowerCase()} analysis to feed the fusion cockpit.
        </p>
      )}

      <label className="flex items-center gap-2 text-xs text-neutral-400 mt-auto pt-3 border-t border-neutral-800">
        <input
          type="checkbox"
          checked={included}
          disabled={!prediction}
          onChange={(e) => onToggleIncluded(e.target.checked)}
          className="rounded border-neutral-600 bg-neutral-800 text-primary-500 focus:ring-primary-500"
        />
        Include in fusion
      </label>
    </Card>
  );
}
