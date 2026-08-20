'use client';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Search, Zap, Shield, Clock, DollarSign, 
  TrendingUp, AlertCircle, CheckCircle, XCircle,
  ChevronRight, ExternalLink, FileText, 
  Globe, Store, Building, Brain, Video,
  Filter, Loader2
} from 'lucide-react';
import { formatCurrency, formatRelativeTime, cn } from '@/lib/utils';
import { researchApi, marketplaceApi, businessesApi, aiModelsApi, promotionsApi, reviewsApi } from '@/lib/api';
import { useQuery } from '@tanstack/react-query';

interface ResearchResultCardProps {
  runId: string;
  query: string;
  status: string;
  createdAt: string;
  completedAt?: string;
  totalCost: number;
}

export function ResearchResultCard({ runId, query, status, createdAt, completedAt, totalCost }: ResearchResultCardProps) {
  const statusColors = {
    PLANNING: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    SEARCHING: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    EXTRACTING: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    VERIFYING: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
    SYNTHESIZING: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-400',
    COMPLETED: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    FAILED: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    CANCELLED: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
  };

  const statusIcons = {
    PLANNING: Clock,
    SEARCHING: Search,
    EXTRACTING: FileText,
    VERIFYING: Shield,
    SYNTHESIZING: Brain,
    COMPLETED: CheckCircle,
    FAILED: XCircle,
    CANCELLED: AlertCircle,
  };

  const StatusIcon = statusIcons[status as keyof typeof statusIcons] || Clock;
  const statusClass = statusColors[status as keyof typeof statusColors] || statusColors.PLANNING;

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => window.location.href = `/research/${runId}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <p className="font-medium text-foreground truncate">{query}</p>
            <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {formatRelativeTime(createdAt)}
              </span>
              {completedAt && (
                <span className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Completed {formatRelativeTime(completedAt)}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={cn('gap-1', statusClass)}>
              <StatusIcon className="w-3 h-3" />
              {status}
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span className="flex items-center gap-1">
              <DollarSign className="w-3 h-3" />
              {formatCurrency(totalCost)}
            </span>
          </div>
          <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

export function MarketplaceListingCard({ listing }: { listing: any }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h3 className="font-medium text-foreground line-clamp-2">{listing.title}</h3>
            <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
              <Badge variant="secondary">{listing.source}</Badge>
              {listing.seller_type && (
                <Badge variant="outline">{listing.seller_type}</Badge>
              )}
              {listing.condition && (
                <Badge variant="outline">{listing.condition}</Badge>
              )}
            </div>
            {listing.location && (
              <p className="mt-1 text-sm text-muted-foreground flex items-center gap-1">
                <Globe className="w-3 h-3" />
                {listing.location}
              </p>
            )}
          </div>
          {listing.price && (
            <div className="text-right">
              <p className="text-xl font-bold text-foreground">{formatCurrency(listing.price)}</p>
              <p className="text-sm text-muted-foreground">{listing.currency}</p>
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between">
          {listing.deal_score !== null && listing.deal_score !== undefined && (
            <Badge className={cn(
              'gap-1',
              listing.deal_score > 0.7 ? 'bg-green-100 text-green-800' :
              listing.deal_score > 0.4 ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            )}>
              <TrendingUp className="w-3 h-3" />
              Deal Score: {(listing.deal_score * 100).toFixed(0)}%
            </Badge>
          )}
          <a href={listing.source_url} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline flex items-center gap-1">
            View Listing
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </CardContent>
    </Card>
  );
}

export function BusinessCard({ business }: { business: any }) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-foreground">{business.name}</h3>
              {business.is_verified && (
                <Badge variant="secondary" className="gap-1">
                  <CheckCircle className="w-3 h-3" />
                  Verified
                </Badge>
              )}
            </div>
            {business.specializations && business.specializations.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {business.specializations.slice(0, 3).map((spec: string) => (
                  <Badge key={spec} variant="outline" className="text-xs">{spec}</Badge>
                ))}
              </div>
            )}
            <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
              {business.suburb && (
                <span className="flex items-center gap-1">
                  <Building className="w-3 h-3" />
                  {business.suburb}, {business.state}
                </span>
              )}
              {business.distance_km !== null && business.distance_km !== undefined && (
                <span className="flex items-center gap-1">
                  <Globe className="w-3 h-3" />
                  {business.distance_km.toFixed(1)} km
                </span>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium">Confidence: {(business.confidence * 100).toFixed(0)}%</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between">
          {business.phone && (
            <a href={`tel:${business.phone}`} className="text-sm text-primary hover:underline flex items-center gap-1">
              <Building className="w-3 h-3" />
              Call
            </a>
          )}
          {business.website && (
            <a href={business.website} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline flex items-center gap-1">
              <ExternalLink className="w-3 h-3" />
              Website
            </a>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function AIModelCard({ model }: { model: any }) {
  const capabilityBadges = [];
  if (model.has_vision) capabilityBadges.push(<Badge key="vision" variant="secondary" className="gap-1"><Video className="w-3 h-3" /> Vision</Badge>);
  if (model.has_audio) capabilityBadges.push(<Badge key="audio" variant="secondary" className="gap-1">🔊 Audio</Badge>);
  if (model.has_tool_use) capabilityBadges.push(<Badge key="tools" variant="secondary" className="gap-1">🔧 Tools</Badge>);
  if (model.has_reasoning) capabilityBadges.push(<Badge key="reasoning" variant="secondary" className="gap-1">🧠 Reasoning</Badge>);
  if (model.free_availability) capabilityBadges.push(<Badge key="free" variant="secondary" className="gap-1 bg-green-100 text-green-800"><Zap className="w-3 h-3" /> Free</Badge>);

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-foreground">{model.model_name}</h3>
              <Badge variant="outline">{model.provider}</Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-1">{model.model_id}</p>
            <div className="flex flex-wrap gap-1 mt-2">
              {capabilityBadges}
            </div>
          </div>
          <div className="text-right">
            {model.context_window && (
              <p className="text-sm text-muted-foreground">
                Context: {(model.context_window / 1000).toFixed(0)}K
              </p>
            )}
            {model.coding_score !== null && model.coding_score !== undefined && (
              <p className="text-sm font-medium text-primary">Coding: {(model.coding_score * 100).toFixed(1)}%</p>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          {model.price_per_million_tokens !== null && model.price_per_million_tokens !== undefined && (
            <span>${model.price_per_million_tokens.toFixed(4)}/1M tokens</span>
          )}
          {model.free_limits && (
            <span className="text-green-600 dark:text-green-400">Free tier available</span>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function PromotionCard({ promotion }: { promotion: any }) {
  const statusColors = {
    ACTIVE: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    EXPIRING: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    EXPIRED: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
    UNVERIFIED: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    COMMUNITY_REPORTED: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400',
    DISPUTED: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
  };

  return (
    <Card className="hover:shadow-md transition-shadow border-l-4 border-primary">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-foreground">{promotion.provider}</h3>
              <Badge className={statusColors[promotion.status as keyof typeof statusColors] || statusColors.UNVERIFIED}>
                {promotion.status}
              </Badge>
            </div>
            <p className="text-sm text-muted-foreground mt-1">{promotion.offer}</p>
            {promotion.free_limit && (
              <p className="text-sm text-green-600 dark:text-green-400 mt-1">Free limit: {promotion.free_limit}</p>
            )}
            <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
              {promotion.amount !== null && promotion.amount !== undefined && (
                <span className="flex items-center gap-1">
                  <DollarSign className="w-3 h-3" />
                  {formatCurrency(promotion.amount)} {promotion.currency}
                </span>
              )}
              {promotion.expiry_date && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Expires {formatRelativeTime(promotion.expiry_date)}
                </span>
              )}
              {promotion.card_required && (
                <Badge variant="outline" className="gap-1">💳 Card required</Badge>
              )}
              {!promotion.commercial_use && (
                <Badge variant="outline" className="gap-1">🚫 Non-commercial</Badge>
              )}
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium">Confidence: {(promotion.confidence * 100).toFixed(0)}%</p>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        {promotion.official_source_url && (
          <a href={promotion.official_source_url} target="_blank" rel="noopener noreferrer" className="text-sm text-primary hover:underline flex items-center gap-1">
            <FileText className="w-3 h-3" />
            Official Source
          </a>
        )}
      </CardContent>
    </Card>
  );
}

export function ReviewCard({ review }: { review: any }) {
  const sentimentColors = {
    POSITIVE: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    NEGATIVE: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    MIXED: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    NEUTRAL: 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400',
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            {review.title && <h3 className="font-medium text-foreground">{review.title}</h3>}
            <div className="flex items-center gap-2 mt-1">
              <Badge className={sentimentColors[review.sentiment as keyof typeof sentimentColors] || sentimentColors.NEUTRAL}>
                {review.sentiment}
              </Badge>
              {review.rating && (
                <span className="text-sm font-medium">★ {review.rating.toFixed(1)}</span>
              )}
              <Badge variant="outline">{review.source}</Badge>
            </div>
            {review.text && (
              <p className="mt-2 text-sm text-muted-foreground line-clamp-3">{review.text}</p>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          {review.author && <span>{review.author}</span>}
          {review.review_date && <span>{formatRelativeTime(review.review_date)}</span>}
        </div>
      </CardContent>
    </Card>
  );
}

export function LoadingCard() {
  return (
    <Card>
      <CardHeader>
        <div className="h-4 bg-muted rounded w-3/4 animate-pulse" />
        <div className="h-4 bg-muted rounded w-1/2 animate-pulse mt-2" />
      </CardHeader>
      <CardContent>
        <div className="h-4 bg-muted rounded w-full animate-pulse" />
        <div className="h-4 bg-muted rounded w-2/3 animate-pulse mt-2" />
      </CardContent>
    </Card>
  );
}

export function EmptyState({ icon: Icon, title, description, action }: { 
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="text-center py-12">
      <Icon className="w-16 h-16 mx-auto text-muted-foreground/30 mb-4" />
      <h3 className="text-lg font-medium text-foreground mb-2">{title}</h3>
      <p className="text-muted-foreground mb-4">{description}</p>
      {action}
    </div>
  );
}