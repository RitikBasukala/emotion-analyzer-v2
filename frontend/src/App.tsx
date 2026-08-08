import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { LastResultsProvider } from './hooks/useLastResults';
import { Layout } from './components/layout';
import { HomePage, TextPage, AudioPage, VideoPage, DashboardPage, HistoryPage } from './pages';

/**
 * Fully open, auth-free multimodal emotion recognition frontend.
 * Routes:
 *  /            - landing page
 *  /dashboard   - live multimodal fusion cockpit (flagship view)
 *  /text        - standalone text analysis
 *  /audio       - standalone audio analysis
 *  /video       - standalone video analysis
 *  /history     - past analyses
 */
function App() {
  return (
    <LastResultsProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />

          <Route path="/dashboard" element={<Layout><DashboardPage /></Layout>} />
          <Route path="/text" element={<Layout><TextPage /></Layout>} />
          <Route path="/audio" element={<Layout><AudioPage /></Layout>} />
          <Route path="/video" element={<Layout><VideoPage /></Layout>} />
          <Route path="/history" element={<Layout><HistoryPage /></Layout>} />
        </Routes>
      </BrowserRouter>
    </LastResultsProvider>
  );
}

export default App;
