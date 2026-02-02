"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Target, TrendingUp, Calendar, Plus } from "lucide-react";
import { cn } from "@/lib/utils";

interface Goal {
  id: string;
  name: string;
  type: string;
  target_amount: number;
  current_amount: number;
  target_date?: string;
  progress_percentage: number;
  status: "active" | "paused" | "completed" | "cancelled";
  is_on_track: boolean;
}

interface GoalProgressProps {
  goals: Goal[];
  onAddGoal?: () => void;
  onManageGoals?: () => void;
}

const statusConfig = {
  active: {
    color: "text-green-600",
    bgColor: "bg-green-600",
    label: "Active",
  },
  paused: {
    color: "text-gray-600",
    bgColor: "bg-gray-600",
    label: "Paused",
  },
  completed: {
    color: "text-blue-600",
    bgColor: "bg-blue-600",
    label: "Completed",
  },
  cancelled: {
    color: "text-red-600",
    bgColor: "bg-red-600",
    label: "Cancelled",
  },
};

export function GoalProgress({ goals, onAddGoal, onManageGoals }: GoalProgressProps) {
  if (!goals || goals.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Financial Goals</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <Target className="mx-auto h-12 w-12 text-gray-400 mb-3" />
            <p className="text-gray-500 mb-2">No goals yet</p>
            <p className="text-sm text-gray-400 mb-4">Set financial goals to track your progress</p>
            {onAddGoal && (
              <Button onClick={onAddGoal} size="sm">
                <Plus className="h-4 w-4 mr-2" />
                Create Goal
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Financial Goals</CardTitle>
          <div className="flex gap-2">
            {onManageGoals && (
              <Button onClick={onManageGoals} size="sm" variant="outline">
                Manage Goals
              </Button>
            )}
            {onAddGoal && (
              <Button onClick={onAddGoal} size="sm" variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Add Goal
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {goals.slice(0, 3).map((goal) => {
            const config = statusConfig[goal.status];
            const daysLeft = goal.target_date 
              ? Math.ceil((new Date(goal.target_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
              : null;

            // Determine progress bar color based on status and is_on_track
            const progressColor = goal.status === "completed" ? "#3B82F6" : 
                                  goal.status === "cancelled" ? "#EF4444" :
                                  goal.status === "paused" ? "#9CA3AF" :
                                  goal.is_on_track ? "#10B981" : "#F59E0B";

            return (
              <div key={goal.id} className="space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <Target className="h-4 w-4 text-blue-600" />
                      <h4 className="font-medium text-gray-900">{goal.name}</h4>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={cn("text-xs font-medium px-2 py-1 rounded-full", config.color, "bg-opacity-10")}>
                        {config.label}
                      </span>
                      {goal.status === "active" && (
                        <span className={cn(
                          "text-xs font-medium px-2 py-1 rounded-full",
                          goal.is_on_track ? "text-green-600 bg-green-50" : "text-yellow-600 bg-yellow-50"
                        )}>
                          {goal.is_on_track ? "On Track" : "At Risk"}
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900">
                      {goal.progress_percentage.toFixed(0)}%
                    </div>
                    {daysLeft !== null && daysLeft > 0 && (
                      <div className="flex items-center text-xs text-gray-500 mt-1">
                        <Calendar className="h-3 w-3 mr-1" />
                        {daysLeft} days left
                      </div>
                    )}
                  </div>
                </div>

                <div className="relative">
                  <Progress value={Math.min(goal.progress_percentage, 100)} className="h-2" />
                  <div
                    className="absolute top-0 left-0 h-2 rounded-full transition-all"
                    style={{
                      width: `${Math.min(goal.progress_percentage, 100)}%`,
                      backgroundColor: progressColor,
                    }}
                  />
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">
                    <span className="font-semibold text-gray-900">
                      ${goal.current_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </span>
                    {" "}of{" "}
                    ${goal.target_amount.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </span>
                  <span className="text-gray-500">
                    ${(goal.target_amount - goal.current_amount).toLocaleString("en-US", { minimumFractionDigits: 2 })} to go
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {goals.length > 3 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <Button variant="ghost" size="sm" className="w-full">
              View All Goals ({goals.length})
              <TrendingUp className="ml-2 h-4 w-4" />
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
