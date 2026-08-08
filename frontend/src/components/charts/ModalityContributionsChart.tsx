import { motion } from 'framer-motion';
import { CheckCircle2, XCircle, HelpCircle } from 'lucide-react';
import { ModalityContribution } from '../../types';
import { modalityColors } from '../../theme/palette';

interface ModalityContributionsChartProps {
  contributions: Record<string, ModalityContribution>;
}

const modalityLabels: Record<string, string> = {
  text: 'Text',
  audio: 'Audio',
  facial: 'Facial',
};

export function ModalityContributionsChart({ contributions }: ModalityContributionsChartProps) {
  const entries = Object.entries(contributions);
  const maxContribution = Math.max(0.0001, ...entries.map(([, c]) => c.contribution_to_final));

  return (
    <div className="space-y-4">
      {entries.map(([modality, data], i) => {
        const color = modalityColors[modality as keyof typeof modalityColors] ?? '#a1a1aa';
        const barWidth = (data.contribution_to_final / maxContribution) * 100;

        return (
          <motion.div
            key={modality}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="flex items-center gap-3"
          >
            <div className="w-16 text-sm font-medium text-neutral-400">
              {modalityLabels[modality] ?? modality}
            </div>

            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm text-white">
                  {data.emotion ?? <span className="text-neutral-500">no signal</span>}
                </span>
                <span className="text-xs text-neutral-500">
                  weight {(data.weight * 100).toFixed(0)}%
                </span>
              </div>
              <div className="h-2.5 bg-neutral-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${barWidth}%` }}
                  transition={{ duration: 0.6, ease: 'easeOut' }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: color }}
                />
              </div>
            </div>

            <div className="w-14 text-right text-sm text-neutral-300">
              {(data.contribution_to_final * 100).toFixed(1)}%
            </div>

            <div className="w-6 flex justify-center">
              {data.emotion === null ? (
                <HelpCircle size={16} className="text-neutral-600" />
              ) : data.agreement ? (
                <CheckCircle2 size={16} className="text-primary-400" />
              ) : (
                <XCircle size={16} className="text-secondary-400" />
              )}
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}
