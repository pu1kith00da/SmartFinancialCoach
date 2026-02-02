"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Plus, Target, Calendar, DollarSign, Edit, Trash2, ArrowLeft } from "lucide-react";
import { useState } from "react";

interface Goal {
  id: string;
  name: string;
  description?: string;
  type: string;
  target_amount: number;
  current_amount: number;
  target_date?: string;
  progress_percentage: number;
  status: string;
  priority: string;
}

export default function GoalsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [deletingId, setDeletingId] = useState<string | null>(null);

  // Fetch goals
  const { data: goalsData, isLoading } = useQuery({
    queryKey: ["goals"],
    queryFn: async () => {
      const response = await api.goals.list();
      return response.data;
    },
    staleTime: 0, // Always fetch fresh data
    refetchOnMount: true, // Refetch when component mounts
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => api.goals.delete(id),
    onMutate: async (deletedId) => {
      // Cancel any outgoing refetches to avoid overwriting our optimistic update
      await queryClient.cancelQueries({ queryKey: ["goals"] });
      
      // Snapshot the previous value
      const previousGoals = queryClient.getQueryData(["goals"]);
      
      // Optimistically remove the goal from cache
      queryClient.setQueryData(["goals"], (old: any) => {
        if (!old) return old;
        const filteredGoals = old.goals.filter((goal: Goal) => goal.id !== deletedId);
        return {
          ...old,
          goals: filteredGoals,
          total_goals: filteredGoals.length,
          active_goals: filteredGoals.filter((g: Goal) => g.status === 'ACTIVE').length,
          completed_goals: filteredGoals.filter((g: Goal) => g.status === 'COMPLETED').length,
        };
      });
      
      // Return context with previous data for rollback
      return { previousGoals };
    },
    onSuccess: async () => {
      // Invalidate and refetch to ensure consistency with backend
      await queryClient.invalidateQueries({ queryKey: ["goals"], refetchType: 'all' });
      setDeletingId(null);
    },
    onError: (error: any, deletedId, context: any) => {
      // Rollback to previous data on error
      if (context?.previousGoals) {
        queryClient.setQueryData(["goals"], context.previousGoals);
      }
      console.error("Failed to delete goal:", error);
      setDeletingId(null);
      
      // If it's a 404, the goal is already deleted - refresh the list
      if (error.response?.status === 404) {
        queryClient.invalidateQueries({ queryKey: ["goals"], refetchType: 'all' });
        alert("This goal has already been deleted. Refreshing list...");
      } else {
        alert(`Failed to delete goal: ${error.response?.data?.detail || error.message}`);
      }
    },
  });

  const goals = goalsData?.goals || [];

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this goal?")) {
      setDeletingId(id);
      try {
        await deleteMutation.mutateAsync(id);
      } catch (error) {
        // Error already handled in onError callback
      }
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "No deadline";
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-muted-foreground">Loading goals...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Back Button */}
      <Button
        variant="ghost"
        onClick={() => router.push("/dashboard")}
        className="mb-4"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Dashboard
      </Button>

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold mb-2">Financial Goals</h1>
          <p className="text-muted-foreground">
            Track your progress toward your financial objectives
          </p>
        </div>
        <Button onClick={() => router.push("/goals/new")}>
          <Plus className="mr-2 h-4 w-4" />
          Add Goal
        </Button>
      </div>

      {/* Stats */}
      {goals.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Goals</p>
                <p className="text-2xl font-bold">{goalsData?.total_goals || 0}</p>
              </div>
              <Target className="h-8 w-8 text-blue-500" />
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-2xl font-bold">{goalsData?.active_goals || 0}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                <span className="text-green-600 font-bold">✓</span>
              </div>
            </div>
          </Card>
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Completed</p>
                <p className="text-2xl font-bold">{goalsData?.completed_goals || 0}</p>
              </div>
              <div className="h-8 w-8 rounded-full bg-purple-100 flex items-center justify-center">
                <span className="text-purple-600 font-bold">★</span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Goals List */}
      {goals.length === 0 ? (
        <Card className="p-12">
          <div className="text-center">
            <Target className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No goals yet</h3>
            <p className="text-muted-foreground mb-6">
              Start by creating your first financial goal
            </p>
            <Button onClick={() => router.push("/goals/new")}>
              <Plus className="mr-2 h-4 w-4" />
              Create Your First Goal
            </Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {goals.map((goal: Goal) => (
            <Card key={goal.id} className="p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold mb-1">{goal.name}</h3>
                  {goal.description && (
                    <p className="text-sm text-muted-foreground">{goal.description}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => router.push(`/goals/${goal.id}/edit`)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(goal.id)}
                    disabled={deletingId === goal.id}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Progress */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">
                    {formatCurrency(goal.current_amount)} of {formatCurrency(goal.target_amount)}
                  </span>
                  <span className="text-sm font-medium">{Math.round(goal.progress_percentage)}%</span>
                </div>
                <Progress value={goal.progress_percentage} className="h-2" />
              </div>

              {/* Details */}
              <div className="space-y-2">
                {goal.target_date && (
                  <div className="flex items-center text-sm text-muted-foreground">
                    <Calendar className="mr-2 h-4 w-4" />
                    Target: {formatDate(goal.target_date)}
                  </div>
                )}
                <div className="flex items-center text-sm text-muted-foreground">
                  <DollarSign className="mr-2 h-4 w-4" />
                  Remaining: {formatCurrency(goal.target_amount - goal.current_amount)}
                </div>
              </div>

              {/* Actions */}
              <div className="mt-4 pt-4 border-t">
                <Button
                  className="w-full"
                  variant="outline"
                  onClick={() => router.push(`/goals/${goal.id}`)}
                >
                  View Details
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
