import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  FileText,
  Mic,
  Video,
  History,
  Waves,
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Cockpit', icon: LayoutDashboard },
  { path: '/text', label: 'Text', icon: FileText },
  { path: '/audio', label: 'Audio', icon: Mic },
  { path: '/video', label: 'Video', icon: Video },
  { path: '/history', label: 'History', icon: History },
];

export function Header() {
  const location = useLocation();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-neutral-950/80 backdrop-blur-xl border-b border-neutral-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3">
            <motion.div
              whileHover={{ rotate: 360 }}
              transition={{ duration: 0.5 }}
              className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-secondary-500
                flex items-center justify-center"
            >
              <Waves className="w-6 h-6 text-white" />
            </motion.div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary-400 to-secondary-400
              bg-clip-text text-transparent">
              EmotionAI
            </span>
          </Link>

          {/* Navigation */}
          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path ||
                location.pathname.startsWith(item.path);
              const Icon = item.icon;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`
                    relative px-4 py-2 rounded-lg flex items-center gap-2
                    transition-colors duration-200
                    ${isActive ? 'text-primary-400' : 'text-neutral-400 hover:text-neutral-200'}
                  `}
                >
                  <Icon size={18} />
                  <span className="text-sm font-medium">{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="nav-indicator"
                      className="absolute inset-0 bg-primary-500/10 rounded-lg border border-primary-500/30"
                    />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Status */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-neutral-900 border border-neutral-800">
              <span className="w-2 h-2 rounded-full bg-primary-400 animate-pulse-glow" />
              <span className="text-sm text-neutral-400 hidden sm:block">
                Open access
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-neutral-950/95
        backdrop-blur-xl border-t border-neutral-800 safe-area-pb">
        <div className="flex items-center justify-around py-2">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`
                  flex flex-col items-center gap-1 p-2 rounded-lg
                  transition-colors duration-200
                  ${isActive ? 'text-primary-400' : 'text-neutral-400'}
                `}
              >
                <Icon size={20} />
                <span className="text-xs">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </header>
  );
}
