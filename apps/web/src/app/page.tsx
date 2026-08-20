'use client';

import { useState } from 'react';
import { Search, Settings, Bell, Menu, X, ChevronDown, Globe, DollarSign, Layers, Eye, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

const FREE_MODES = [
  { value: 'FREE_ONLY', label: 'FREE ONLY', description: '$0 spend, blocks all paid providers' },
  { value: 'FREE_FIRST', label: 'FREE FIRST', description: 'Search free first, show paid but dont execute' },
  { value: 'CHEAP', label: 'CHEAP', description: 'Include cheap paid, never auto-purchase' },
  { value: 'FULL', label: 'FULL', description: 'Paid providers manually enabled with budgets' },
];

const RESEARCH_DEPTHS = [
  { value: 'QUICK', label: 'Quick', description: 'Fast surface-level research' },
  { value: 'NORMAL', label: 'Normal', description: 'Balanced depth and speed' },
  { value: 'DEEP', label: 'Deep', description: 'Comprehensive multi-source research' },
  { value: 'MAXIMUM', label: 'Maximum', description: 'Exhaustive research with all sources' },
];

const MONITOR_INTERVALS = [
  { value: '0', label: 'OFF' },
  { value: '1', label: '1 hour' },
  { value: '6', label: '6 hours' },
  { value: '12', label: '12 hours' },
  { value: '24', label: '24 hours' },
  { value: '72', label: '3 days' },
  { value: '168', label: '7 days' },
];

const SOURCE_CLASSES = [
  'Web', 'Forums', 'Reddit', 'YouTube', 'GitHub', 'Marketplaces', 
  'Businesses', 'Government', 'Academic', 'News', 'Social', 'Official'
];

export default function HomePage() {
  const [query, setQuery] = useState('');
  const [freeMode, setFreeMode] = useState('FREE_ONLY');
  const [location, setLocation] = useState('Australia/Queensland/Brisbane');
  const [budget, setBudget] = useState('0');
  const [researchDepth, setResearchDepth] = useState('NORMAL');
  const [monitorInterval, setMonitorInterval] = useState('0');
  const [sourceClasses, setSourceClasses] = useState<string[]>(['Automatic']);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setIsSearching(true);
    try {
      const response = await fetch('/api/v1/research/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          free_only: freeMode === 'FREE_ONLY',
          budget_aud: parseFloat(budget) || 0,
          currency: 'AUD',
          country: 'AU',
          location,
          research_depth: researchDepth,
          monitoring_interval_hours: parseInt(monitorInterval) || null,
          source_classes: sourceClasses.includes('Automatic') ? null : sourceClasses,
        }),
      });
      
      const data = await response.json();
      if (data.run_id) {
        window.location.href = `/research/${data.run_id}`;
      } else {
        alert('Error: ' + (data.message || 'Failed to start research'));
      }
    } catch (error) {
      alert('Error starting research: ' + error);
    } finally {
      setIsSearching(true);
    }
  };

  const toggleSourceClass = (source: string) => {
    setSourceClasses(prev => {
      if (source === 'Automatic') {
        return prev.includes('Automatic') ? SOURCE_CLASSES : ['Automatic'];
      }
      const next = prev.filter(s => s !== source);
      if (next.length === 0) return ['Automatic'];
      return next.includes('Automatic') ? next.filter(s => s !== 'Automatic') : next;
    });
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary text-primary-foreground rounded-lg">
              <Zap className="w-5 h-5" />
            </div>
            <span className="text-xl font-bold">ResearchOS</span>
          </div>
          
          <nav className="hidden md:flex items-center gap-6">
            <a href="/search" className="text-sm font-medium text-muted-foreground hover:text-foreground">Search</a>
            <a href="/history" className="text-sm font-medium text-muted-foreground hover:text-foreground">History</a>
            <a href="/watchlists" className="text-sm font-medium text-muted-foreground hover:text-foreground">Watchlists</a>
            <a href="/providers" className="text-sm font-medium text-muted-foreground hover:text-foreground">Providers</a>
            <a href="/settings" className="text-sm font-medium text-muted-foreground hover:text-foreground">Settings</a>
          </nav>
          
          <div className="flex items-center gap-3">
            <button className="p-2 rounded-lg hover:bg-accent" title="Notifications">
              <Bell className="w-5 h-5" />
            </button>
            <button className="p-2 rounded-lg hover:bg-accent" title="Menu">
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Search Section */}
      <main className="container mx-auto px-4 py-12 max-w-4xl">
        {/* Search Box */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label htmlFor="query" className="block text-lg font-semibold">
              WHAT ARE YOU TRYING TO FIND?
            </label>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5" />
              <textarea
                id="query"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., Find the best free AI coding setup... or Find a 1,000hp XR6 Turbo TH400 setup in Queensland..."
                className="w-full min-h-[100px] pl-12 pr-4 py-4 bg-background border border-input rounded-lg text-lg placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent resize-y"
                rows={3}
              />
            </div>
          </div>

          {/* Quick Action Bar */}
          <div className="flex flex-wrap gap-2">
            <button
              type="submit"
              disabled={isSearching || !query.trim()}
              className="flex-1 sm:flex-none px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold text-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSearching ? 'Researching...' : 'SEARCH'}
            </button>
            
            <div className="flex-1 flex items-center gap-2 text-sm text-muted-foreground">
              <span className={cn('px-2 py-1 rounded', freeMode === 'FREE_ONLY' && 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400')}>
                🛡️ {freeMode.replace('_', ' ')}
              </span>
            </div>
          </div>

          {/* Advanced Options */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground p-2 rounded-lg hover:bg-accent w-fit"
          >
            <ChevronDown className={cn('w-4 h-4 transition-transform', showAdvanced && 'rotate-180')} />
            <span>Advanced Options</span>
          </button>

          {showAdvanced && (
            <div className="space-y-6 p-6 bg-card border border-border rounded-lg animate-in fade-in slide-in-from-top-2">
              {/* Row 1: Free Mode & Location */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">OPERATING MODE</label>
                  <div className="grid grid-cols-2 gap-2">
                    {FREE_MODES.map(mode => (
                      <button
                        key={mode.value}
                        type="button"
                        onClick={() => setFreeMode(mode.value)}
                        className={cn(
                          'p-3 text-left rounded-lg border-2 transition-all text-sm',
                          freeMode === mode.value
                            ? 'border-primary bg-primary/5 text-primary'
                            : 'border-border hover:border-primary/50 hover:bg-accent'
                        )}
                      >
                        <div className="font-medium">{mode.label}</div>
                        <div className="text-xs text-muted-foreground">{mode.description}</div>
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">LOCATION</label>
                  <select
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="Australia/Queensland/Brisbane">Australia / Queensland / Brisbane</option>
                    <option value="Australia/Queensland">Australia / Queensland</option>
                    <option value="Australia/New South Wales/Sydney">Australia / NSW / Sydney</option>
                    <option value="Australia/Victoria/Melbourne">Australia / Victoria / Melbourne</option>
                    <option value="Australia/Western Australia/Perth">Australia / WA / Perth</option>
                    <option value="Australia/South Australia/Adelaide">Australia / SA / Adelaide</option>
                    <option value="Custom">Custom Location</option>
                  </select>
                </div>
              </div>

              {/* Row 2: Budget & Research Depth */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">BUDGET (AUD)</label>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">$</span>
                    <input
                      type="number"
                      value={budget}
                      onChange={(e) => setBudget(e.target.value)}
                      min="0"
                      step="10"
                      className="w-full px-3 py-2 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring"
                      disabled={freeMode === 'FREE_ONLY'}
                    />
                    {freeMode === 'FREE_ONLY' && (
                      <span className="text-xs text-muted-foreground">Locked in FREE_ONLY mode</span>
                    )}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">RESEARCH DEPTH</label>
                  <div className="flex gap-2">
                    {RESEARCH_DEPTHS.map(depth => (
                      <button
                        key={depth.value}
                        type="button"
                        onClick={() => setResearchDepth(depth.value)}
                        className={cn(
                          'flex-1 px-3 py-2 rounded-lg border-2 text-sm transition-all',
                          researchDepth === depth.value
                            ? 'border-primary bg-primary/5 text-primary'
                            : 'border-border hover:border-primary/50'
                        )}
                      >
                        <div className="font-medium">{depth.label}</div>
                        <div className="text-xs text-muted-foreground">{depth.description}</div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Row 3: Monitoring & Sources */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">MONITOR INTERVAL</label>
                  <select
                    value={monitorInterval}
                    onChange={(e) => setMonitorInterval(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-input rounded-lg focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    {MONITOR_INTERVALS.map(opt => (
                      <option key={opt.value} value={opt.value}>{opt.label}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">SOURCE CLASSES</label>
                  <div className="flex flex-wrap gap-2">
                    {SOURCE_CLASSES.map(source => (
                      <button
                        key={source}
                        type="button"
                        onClick={() => toggleSourceClass(source)}
                        className={cn(
                          'px-3 py-1.5 rounded-full text-sm border transition-all',
                          sourceClasses.includes(source)
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-border hover:border-primary/50'
                        )}
                      >
                        {source}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Recent Research placeholder */}
          <div className="pt-4 border-t border-border">
            <h3 className="text-sm font-medium text-muted-foreground mb-3">RECENT RESEARCH</h3>
            <div className="text-center py-8 text-muted-foreground">
              <Search className="w-12 h-12 mx-auto mb-2 opacity-30" />
              <p>No recent research yet. Start your first search above.</p>
            </div>
          </div>
        </form>
      </main>

      {/* Footer */}
      <footer className="border-t border-border mt-12 py-6">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>ResearchOS v1.0 - Universal AI-Powered Research Platform</p>
          <p className="mt-1">Free-only mode: ${0} actual spend • All paid execution blocked</p>
        </div>
      </footer>
    </div>
  );
}