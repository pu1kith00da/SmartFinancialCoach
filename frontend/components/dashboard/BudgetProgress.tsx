"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { AlertCircle, CheckCircle, TrendingUp, Plus } from "lucide-react";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";

interface Budget {
  category: string;
  budgeted: number;
  spent: number;
  percentage: number;
  status: "on_track" | "warning" | "exceeded";
}

interface BudgetProgressProps {
  budgets: Budget[];
}

const statusConfig = {
  on_track: {
    icon: CheckCircle,
    color: "text-green-600",
    bgColor: "bg-green-600",
    label: "On Track",
  },
  warning: {
    icon: AlertCircle,
    color: "text-yellow-600",
    bgColor: "bg-yellow-600",
    label: "Warning",
  },
  exceeded: {
    icon: TrendingUp,
    color: "text-red-600",
    bgColor: "bg-red-600",
    label: "Over Budget",
  },
};

export function BudgetProgress({ budgets }: BudgetProgressProps) {
  const router = useRouter();

  if (!budgets || budgets.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Budget Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertCircle className="mx-auto h-12 w-12 text-gray-400 mb-3" />
            <p className="text-gray-500 mb-2">No budgets set</p>
            <p className="text-sm text-gray-400 mb-4">Create budgets to track your spending</p>
            <Button onClick={() => router.push("/budgets")} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Set Up Budgets
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Budget Progress</CardTitle>
            <p className="text-sm text-gray-500">This month</p>
          </div>
          <Button onClick={() => router.push("/budgets")} size="sm" variant="outline">
            Manage Budgets
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {budgets.map((budget) => {
            const config = statusConfig[budget.status];
            const Icon = config.icon;
            const progressValue = Math.min(budget.percentage, 100);
            const remaining = budget.budgeted - budget.spent;

            return (
              <div key={budget.category} className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className={cn("h-4 w-4", config.color)} />
                    <span className="font-medium text-gray-900">{budget.category}</span>
                  </div>
                  <span className={cn("text-xs font-medium px-2 py-1 rounded-full", config.color, "bg-opacity-10")}>
                    {config.label}
                  </span>
                </div>

                <div className="relative">
                  <Progress 
                    value={progressValue} 
                    className="h-2"
                  />
                  <div
                    className="absolute top-0 left-0 h-2 rounded-full transition-all"
                    style={{
                      width: `${progressValue}%`,
                      backgroundColor: budget.status === "exceeded" ? "#EF4444" : budget.status === "warning" ? "#F59E0B" : "#10B981",
                    }}
                  />
                </div>

                <div className="flex items-center justify-between text-sm">
                  <div className="space-x-2">
                    <span className="font-semibold text-gray-900">
                      ${budget.spent.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </span>
                    <span className="text-gray-500">of</span>
                    <span className="text-gray-700">
                      ${budget.budgeted.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                  <span className={cn(
                    "font-medium",
                    remaining >= 0 ? "text-gray-600" : "text-red-600"
                  )}>
                    {remaining >= 0 ? `$${remaining.toLocaleString("en-US", { minimumFractionDigits: 2 })} left` : `$${Math.abs(remaining).toLocaleString("en-US", { minimumFractionDigits: 2 })} over`}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
