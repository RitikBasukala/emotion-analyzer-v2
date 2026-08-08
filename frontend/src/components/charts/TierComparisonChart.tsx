import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EMOTIONS } from '../../types';
import { tierColors } from '../../theme/palette';

interface TierComparisonChartProps {
  midFusionProbabilities: Record<string, number>;
  lateFusionProbabilities: Record<string, number>;
  finalProbabilities: Record<string, number>;
}

export function TierComparisonChart({
  midFusionProbabilities,
  lateFusionProbabilities,
  finalProbabilities,
}: TierComparisonChartProps) {
  const data = EMOTIONS.map((emotion) => ({
    emotion,
    Mid: (midFusionProbabilities[emotion] ?? 0) * 100,
    Late: (lateFusionProbabilities[emotion] ?? 0) * 100,
    Final: (finalProbabilities[emotion] ?? 0) * 100,
  }));

  return (
    <div className="h-72">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#3f3f46" />
          <XAxis dataKey="emotion" tick={{ fill: '#a1a1aa', fontSize: 12 }} />
          <YAxis domain={[0, 100]} tick={{ fill: '#a1a1aa' }} />
          <Tooltip
            contentStyle={{
              background: '#18181b',
              border: '1px solid #3f3f46',
              borderRadius: '8px',
            }}
            formatter={(value: number) => `${value.toFixed(1)}%`}
          />
          <Legend wrapperStyle={{ color: '#d4d4d8' }} />
          <Bar dataKey="Mid" fill={tierColors.mid} radius={[4, 4, 0, 0]} />
          <Bar dataKey="Late" fill={tierColors.late} radius={[4, 4, 0, 0]} />
          <Bar dataKey="Final" fill={tierColors.final} radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
