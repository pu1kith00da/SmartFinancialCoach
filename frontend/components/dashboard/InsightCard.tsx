"use client";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api";
import {
  Lightbulb,
  TrendingDown,
  Target,
  PartyPopper,
  AlertTriangle,
  X,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Insight {
  id: string;
  type: "savings_opportunity" | "spending_alert" | "goal_progress" | "celebration" | "anomaly";
  title: string;
  message: string;
  priority: "low" | "normal" | "high";
  action_type?: string;
  data?: Record<string, any>;
}

const insightConfig = {
  savings_opportunity: {
    icon: Lightbulb,
    color: "text-yellow-600",
    bg: "bg-yellow-50",
    border: "border-yellow-200",
  },
  spending_alert: {
    icon: TrendingDown,
    color: "text-red-600",
    bg: "bg-red-50",
    border: "border-red-200",
  },
  goal_progress: {
    icon: Target,
    color: "text-blue-600",
    bg: "bg-blue-50",
    border: "border-blue-200",
  },
  celebration: {
    icon: PartyPopper,
    color: "text-green-600",
    bg: "bg-green-50",
    border: "border-green-200",
  },
  anomaly: {
    icon: AlertTriangle,
    color: "text-orange-600",
    bg: "bg-orange-50",
    border: "border-orange-200",
  },
};

export function InsightCard({ insight }: { insight: Insight }) {
  const [dismissed, setDismissed] = useState(false);
  const queryClient = useQueryClient();

  const { mutate: markRead } = useMutation({
    mutationFn: () => api.insights.markRead(insight.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["insights"] });
    },
  });

  const config = insightConfig[insight.type] || insightConfig.savings_opportunity;
  const Icon = config.icon;

  if (dismissed) return null;

  const handleDismiss = () => {
    markRead();
    setDismissed(true);
  };

  return (
    <Card className={cn("relative overflow-hidden border", config.border, config.bg)}>
      <CardContent className="p-4">
        <button
          onClick={handleDismiss}
          className="absolute top-2 right-2 p-1 rounded-full hover:bg-white/50 transition-colors"
          aria-label="Dismiss"
        >
          <X className="h-4 w-4 text-gray-500" />
        </button>

        <div className="flex items-start space-x-3 pr-8">
          <div className={cn("flex-shrink-0 p-2 rounded-lg bg-white", config.color)}>
            <Icon className="h-5 w-5" />
          </div>
          
          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900 mb-1">
              {insight.title}
            </h3>
            <p className="text-sm text-gray-700 mb-3">
              {insight.message}
            </p>
            
            {insight.action_type && (
              <Button
                size="sm"
                variant="outline"
                className="text-xs"
                onClick={() => markRead()}
              >
                Take Action
                <ChevronRight className="ml-1 h-3 w-3" />
              </Button>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
