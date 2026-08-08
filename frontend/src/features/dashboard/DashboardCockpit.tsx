import { motion } from 'framer-motion';
import { FileText, Mic, Video, Radar } from 'lucide-react';
import { useFusionDashboard } from './useFusionDashboard';
import { ModalitySummaryCard } from './ModalitySummaryCard';
import { FusionPanel } from './FusionPanel';
import { useLastResults } from '../../hooks/useLastResults';

export function DashboardCockpit() {
  const dashboard = useFusionDashboard();
  const { bestTextEmotion, bestAudioEmotion, bestFacialEmotion } = useLastResults();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
            <Radar className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Multimodal Fusion Cockpit</h1>
            <p className="text-neutral-400">
              Live sensor-fusion view combining the latest Text, Audio, and Video signals
            </p>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <ModalitySummaryCard
          title="Text"
          icon={FileText}
          accentClassName="bg-gradient-to-br from-primary-500 to-primary-600"
          href="/text"
          prediction={bestTextEmotion}
          included={dashboard.includeText}
          onToggleIncluded={dashboard.setIncludeText}
        />
        <ModalitySummaryCard
          title="Audio"
          icon={Mic}
          accentClassName="bg-gradient-to-br from-secondary-500 to-secondary-600"
          href="/audio"
          prediction={bestAudioEmotion}
          included={dashboard.includeAudio}
          onToggleIncluded={dashboard.setIncludeAudio}
        />
        <ModalitySummaryCard
          title="Video"
          icon={Video}
          accentClassName="bg-gradient-to-br from-primary-500 to-secondary-500"
          href="/video"
          prediction={bestFacialEmotion}
          included={dashboard.includeFacial}
          onToggleIncluded={dashboard.setIncludeFacial}
        />
      </div>

      <FusionPanel
        fusion={dashboard.fusion}
        loading={dashboard.loading}
        error={dashboard.error}
        hasAnySignal={dashboard.hasAnySignal}
      />
    </div>
  );
}
