'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { 
  Search, Clock, CheckCircle, XCircle, AlertCircle, 
  Brain, FileText, Shield, Zap, DollarSign, 
  TrendingUp, Filter, Download, Share2, 
  ChevronDown, ChevronUp, Eye, EyeOff,
  Loader2, RefreshCw
} from 'lucide-react';
import { researchApi, reportsApi } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';
import { formatRelativeTime, formatCurrency, cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

const statusConfig = {
  PLANNING: { icon: Clock, color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400', label: 'Planning' },
  SEARCHING: { icon: Search, color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400', label: 'Searching' },
  EXTRACTING: { icon: FileText, color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400', label: 'Extracting' },
  VERIFYING: { icon: Shield, color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400', label: 'Verifying' },
  SYNTHESIZING: { icon: Brain, color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400', label: 'Synthesizing' },
  COMPLETED: { icon: CheckCircle, color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400', label: 'Completed' },
  FAILED: { icon: XCircle, color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400', label: 'Failed' },
  CANCELLED: { icon: AlertCircle, color: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400', label: 'Cancelled' },
};

const activitySteps = [
  { key: 'planning', label: 'Planning request...', icon: Brain },
  { key: 'generating_queries', label: 'Generating search variants...', icon: Search },
  { key: 'searching', label: 'Searching providers...', icon: Search },
  { key: 'deduplicating', label: 'Deduplicating results...', icon: Filter },
  { key: 'extracting', label: 'Extracting claims...', icon: FileText },
  { key: 'verifying', label: 'Checking contradictions...', icon: Shield },
  { key: 'analyzing_reviews', label: 'Analyzing reviews...', icon: TrendingUp },
  { key: 'calculating_prices', label: 'Calculating prices...', icon: DollarSign },
  { key: 'finding_alternatives', label: 'Finding alternatives...', icon: Zap },
  { key: 'generating_report', label: 'Generating report...', icon: FileText },
];

export default function ResearchDetailPage() {
  const params = useParams();
  const router = useRouter();
  const runId = params.id as string;
  
  const [currentStep, setCurrentStep] = useState(0);
  const [showFullReport, setShowFullReport] = useState(false);

  const { data: run, isLoading, error, refetch } = useQuery({
    queryKey: ['research', runId],
    queryFn: () => researchApi.getStatus(runId),
    refetchInterval: (data) => data?.status === 'COMPLETED' || data?.status === 'FAILED' || data?.status === 'CANCELLED' ? false : 3000,
    enabled: !!runId,
  });

  const { data: report } = useQuery({
    queryKey: ['report', runId],
    queryFn: () => reportsApi.get(runId),
    enabled: !!runId && (run?.status === 'COMPLETED'),
  });

  // Simulate activity steps based on status
  useEffect(() => {
    if (!run) return;
    
    const statusOrder = ['PLANNING', 'SEARCHING', 'EXTRACTING', 'VERIFYING', 'SYNTHESIZING', 'COMPLETED'];
    const currentIndex = statusOrder.indexOf(run.status);
    setCurrentStep(Math.max(0, currentIndex * 2)); // Rough mapping
  }, [run?.status]);

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-muted rounded w-1/4" />
            <div className="h-4 bg-muted rounded w-full" />
            <div className="h-4 bg-muted rounded w-full" />
            <div className="h-4 bg-muted rounded w-3/4" />
          </div>
        </div>
      </div>
    );
  }

  if (error || !run) {
    return (
      <div className="container mx-auto px-4 py-12 text-center">
        <AlertCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
        <h2 className="text-xl font-semibold mb-2">Research not found</h2>
        <p className="text-muted-foreground mb-4">The research run could not be loaded.</p>
        <Button onClick={() => router.push('/')}>Back to Search</Button>
      </div>
    );
  }

  const config = statusConfig[run.status as keyof typeof statusConfig] || statusConfig.PLANNING;
  const StatusIcon = config.icon;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background/95 backdrop-blur sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <Search className="w-5 h-5" />
          </Button>
          <div className="flex-1 max-w-2xl mx-4 text-center">
            <h1 className="font-bold truncate">Research Details</h1>
          </div>
          <div className="w-10" />
        </div>
      </header>

      <main className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Research Header */}
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
              <div className="flex-1 min-w-0">
                <p className="text-lg font-medium text-foreground mb-2">{run.query}</p>
                <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    Started {formatRelativeTime(run.created_at)}
                  </span>
                  {run.completed_at && (
                    <span className="flex items-center gap-1">
                      <CheckCircle className="w-3 h-3" />
                      Completed {formatRelativeTime(run.completed_at)}
                    </span>
                  )}
                  <Badge className={cn('gap-1', config.color)}>
                    <StatusIcon className="w-3 h-3" />
                    {config.label}
                  </Badge>
                  {run.free_only && (
                    <Badge className="bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400 gap-1">
                      <Shield className="w-3 h-3" />
                      FREE ONLY
                    </Badge>
                  )}
                  <span className="flex items-center gap-1">
                    <DollarSign className="w-3 h-3" />
                    {formatCurrency(run.total_cost_aud)}
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" onClick={() => refetch()}>
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Refresh
                </Button>
                {run.status === 'COMPLETED' && (
                  <Button onClick={() => setShowFullReport(true)}>
                    <FileText className="w-4 h-4 mr-2" />
                    View Report
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Live Activity Feed */}
        {run.status !== 'COMPLETED' && run.status !== 'FAILED' && run.status !== 'CANCELLED' && (
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Live Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {activitySteps.map((step, index) => {
                  const isActive = index === currentStep;
                  const isCompleted = index < currentStep;
                  
                  return (
                    <div 
                      key={step.key}
                      className={cn(
                        'flex items-center gap-3 p-3 rounded-lg transition-all',
                        isActive ? 'bg-primary/5 border border-primary/20' : 
                        isCompleted ? 'bg-green-50 dark:bg-green-900/10' : 'bg-muted/30'
                      )}
                    >
                      <div className={cn(
                        'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
                        isActive ? 'bg-primary text-primary-foreground animate-pulse' :
                        isCompleted ? 'bg-green-500 text-white' : 'bg-muted text-muted-foreground'
                      )}>
                        {isCompleted ? (
                          <CheckCircle className="w-5 h-5" />
                        ) : isActive ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <step.icon className="w-5 h-5" />
                        )}
                      </div>
                      <span className={cn(
                        'text-sm',
                        isActive ? 'font-medium text-foreground' :
                        isCompleted ? 'text-green-700 dark:text-green-300' : 'text-muted-foreground'
                      )}>
                        {step.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Report Tabs - Only show when completed */}
        {run.status === 'COMPLETED' && report && (
          <Tabs defaultValue="executive" className="mt-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="executive">Executive Summary</TabsTrigger>
              <TabsTrigger value="options">Options & Recommendations</TabsTrigger>
              <TabsTrigger value="evidence">Evidence & Sources</TabsTrigger>
              <TabsTrigger value="marketplace">Marketplace & Businesses</TabsTrigger>
            </TabsList>

            <TabsContent value="executive" className="mt-4 space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Executive Answer</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-sm max-w-none">
                    {report.executive_answer || 'No executive answer generated.'}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Bottom Line</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{report.bottom_line || 'No bottom line provided.'}</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Confidence & Verification</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Confidence Score</p>
                      <p className="text-3xl font-bold text-primary">{(report.confidence * 100).toFixed(0)}%</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Last Verified</p>
                      <p className="font-medium">{report.last_verified ? formatRelativeTime(report.last_verified) : 'Unknown'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Next Check</p>
                      <p className="font-medium">{report.next_check ? formatRelativeTime(report.next_check) : 'Not scheduled'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {report.risks && report.risks.length > 0 && (
                <Card className="border-l-4 border-red-500">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-red-500" />
                      Risks & Limitations
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-1 list-disc list-inside text-sm text-muted-foreground">
                      {report.risks.map((risk: string, i: number) => (
                        <li key={i}>{risk}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {report.unknown_information && report.unknown_information.length > 0 && (
                <Card className="border-l-4 border-yellow-500">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-yellow-500" />
                      Unknown Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-1 list-disc list-inside text-sm text-muted-foreground">
                      {report.unknown_information.map((item: string, i: number) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {report.free_only_report && (
                <Card className="border-l-4 border-green-500">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="w-5 h-5 text-green-500" />
                      FREE ONLY Mode Report
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Actual Spend</p>
                        <p className="font-bold text-green-600">${report.free_only_report.actual_spend || '0.00'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Paid Providers Executed</p>
                        <p className="font-bold">{report.free_only_report.paid_providers_executed || 0}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Free Providers Used</p>
                        <p className="font-medium">{(report.free_only_report.free_providers_used || []).join(', ') || 'None'}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Local Models Used</p>
                        <p className="font-medium">{(report.free_only_report.local_models_used || []).join(', ') || 'None'}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="options" className="mt-4 space-y-4">
              {report.best_options && report.best_options.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Best Options
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {report.best_options.map((opt: any, i: number) => (
                        <div key={i} className="p-3 bg-muted/30 rounded-lg">
                          <p className="font-medium">{opt.name || opt.title || `Option ${i + 1}`}</p>
                          <p className="text-sm text-muted-foreground">{opt.reason || opt.description}</p>
                          {opt.price && <p className="text-sm font-medium text-primary">${opt.price} {opt.currency || 'AUD'}</p>}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {report.free_options && report.free_options.length > 0 && (
                <Card className="border-l-4 border-green-500">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-green-500" />
                      Free Options
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {report.free_options.map((opt: any, i: number) => (
                        <div key={i} className="p-3 bg-green-50 dark:bg-green-900/10 rounded-lg">
                          <p className="font-medium">{opt.name || opt.title || `Free Option ${i + 1}`}</p>
                          <p className="text-sm text-muted-foreground">{opt.reason || opt.description}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {report.cheap_options && report.cheap_options.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <DollarSign className="w-5 h-5" />
                      Cheap Options
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {report.cheap_options.map((opt: any, i: number) => (
                        <div key={i} className="p-3 bg-muted/30 rounded-lg">
                          <p className="font-medium">{opt.name || opt.title || `Cheap Option ${i + 1}`}</p>
                          <p className="text-sm text-muted-foreground">{opt.reason || opt.description}</p>
                          {opt.price && <p className="text-sm font-medium text-primary">${opt.price} {opt.currency || 'AUD'}</p>}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {report.similar_options && report.similar_options.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Similar Options</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {report.similar_options.map((opt: any, i: number) => (
                        <div key={i} className="text-sm text-muted-foreground">{opt.name || opt}</div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {report.alternatives && report.alternatives.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Alternatives</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {report.alternatives.map((opt: any, i: number) => (
                        <div key={i} className="text-sm text-muted-foreground">{opt.name || opt}</div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="evidence" className="mt-4 space-y-4">
              {report.evidence && report.evidence.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Supporting Evidence</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 max-h-[600px] overflow-y-auto">
                      {report.evidence.map((ev: any, i: number) => (
                        <Collapsible key={i}>
                          <CollapsibleTrigger className="w-full text-left p-3 bg-muted/30 rounded-lg hover:bg-muted/50">
                            <div className="flex items-start justify-between gap-4">
                              <div>
                                <p className="font-medium text-sm">{ev.claim || 'Evidence'}</p>
                                <p className="text-xs text-muted-foreground">{ev.source || 'Unknown source'}</p>
                              </div>
                              <span className="text-xs text-muted-foreground">Confidence: {(ev.confidence * 100).toFixed(0)}%</span>
                            </div>
                          </CollapsibleTrigger>
                          <CollapsibleContent className="pt-3 pb-3">
                            <p className="text-sm text-muted-foreground">{ev.text || ev.content}</p>
                            {ev.url && (
                              <a href={ev.url} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline mt-2 inline-block">
                                View Source →
                              </a>
                            )}
                          </CollapsibleContent>
                        </Collapsible>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {report.contradictions && report.contradictions.length > 0 && (
                <Card className="border-l-4 border-orange-500">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="w-5 h-5 text-orange-500" />
                      Contradictions Found
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {report.contradictions.map((c: any, i: number) => (
                        <div key={i} className="p-3 bg-orange-50 dark:bg-orange-900/10 rounded-lg">
                          <p className="font-medium">{c.conflict_type || 'Contradiction'}</p>
                          <p className="text-sm text-muted-foreground">{c.reason || 'No reason provided'}</p>
                          {c.resolution && <p className="text-sm text-green-600 mt-1">Resolution: {c.resolution}</p>}
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="marketplace" className="mt-4 space-y-4">
              {report.marketplace_results && report.marketplace_results.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      Marketplace Results
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {report.marketplace_results.map((item: any, i: number) => (
                        <div key={i} className="p-3 bg-muted/30 rounded-lg border">
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <p className="font-medium">{item.title}</p>
                              <p className="text-sm text-muted-foreground">{item.source} • {item.location}</p>
                              {item.price && <p className="text-sm font-medium text-primary">${item.price} {item.currency}</p>}
                            </div>
                            <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
                              View
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {report.businesses && report.businesses.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Brain className="w-5 h-5" />
                      Businesses & Workshops
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {report.businesses.map((biz: any, i: number) => (
                        <div key={i} className="p-3 bg-muted/30 rounded-lg border">
                          <div className="flex items-start justify-between gap-4">
                            <div>
                              <p className="font-medium">{biz.name}</p>
                              <p className="text-sm text-muted-foreground">{biz.suburb}, {biz.state} • {biz.distance_km?.toFixed(1)} km</p>
                              {biz.specializations && <p className="text-xs text-muted-foreground">{biz.specializations.join(', ')}</p>}
                            </div>
                            {biz.website && (
                              <a href={biz.website} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline">
                                Website
                              </a>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {report.promotions && report.promotions.length > 0 && (
                <Card className="border-l-4 border-purple-500">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Zap className="w-5 h-5 text-purple-500" />
                      Promotions & Offers
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {report.promotions.map((promo: any, i: number) => (
                        <div key={i} className="p-3 bg-purple-50 dark:bg-purple-900/10 rounded-lg">
                          <p className="font-medium">{promo.provider}: {promo.offer}</p>
                          <p className="text-sm text-muted-foreground">{promo.free_limit || `Value: ${promo.amount} ${promo.currency}`}</p>
                          <p className="text-xs text-muted-foreground">Status: {promo.status} • Confidence: {(promo.confidence * 100).toFixed(0)}%</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>
          </Tabs>
        )}

        {/* Not completed yet message */}
        {run.status !== 'COMPLETED' && run.status !== 'FAILED' && run.status !== 'CANCELLED' && (
          <div className="mt-8 text-center py-12">
            <Loader2 className="w-12 h-12 mx-auto text-primary animate-spin mb-4" />
            <h3 className="text-lg font-medium mb-2">Research in Progress</h3>
            <p className="text-muted-foreground">Results will appear here once the research is complete.</p>
            <p className="text-sm text-muted-foreground mt-2">Current status: {config.label}</p>
          </div>
        )}
      </main>
    </div>
  );
}