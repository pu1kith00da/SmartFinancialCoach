"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/authStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { ArrowLeft, DollarSign, TrendingUp, AlertCircle, CheckCircle, Save } from "lucide-react";

const BUDGET_CATEGORIES = [
  { name: "Groceries", description: "Food and household items", icon: "🛒" },
  { name: "Shopping", description: "Clothing, electronics, and other purchases", icon: "🛍️" },
  { name: "Food & Dining", description: "Restaurants and takeout", icon: "🍽️" },
  { name: "Bills", description: "Utilities, rent, and recurring payments", icon: "📄" },
  { name: "Transportation", description: "Gas, public transit, and ride sharing", icon: "🚗" },
  { name: "Other", description: "Miscellaneous expenses", icon: "📦" },
  { name: "Savings", description: "Savings goals and investments", icon: "💰" },
];

interface Budget {
  id: string;
  category: string;
  amount: number;
  spent?: number;
  percentage?: number;
  status?: "on_track" | "warning" | "exceeded";
}

export default function BudgetsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const queryClient = useQueryClient();
  
  const [budgetAmounts, setBudgetAmounts] = useState<Record<string, string>>({});
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  // Fetch budgets
  const { data: budgetsData, isLoading } = useQuery({
    queryKey: ["budgets"],
    queryFn: async () => {
      const response = await api.budgets.list();
      return response.data;
    },
    enabled: isAuthenticated,
  });

  // Initialize budget amounts from existing budgets
  useEffect(() => {
    if (budgetsData?.budgets) {
      const amounts: Record<string, string> = {};
      budgetsData.budgets.forEach((budget: Budget) => {
        amounts[budget.category] = budget.amount.toString();
      });
      setBudgetAmounts(amounts);
    }
  }, [budgetsData]);

  // Create/update budget mutation
  const saveBudgetMutation = useMutation({
    mutationFn: async ({ category, amount }: { category: string; amount: number }) => {
      // Check if budget already exists
      const existing = budgetsData?.budgets.find((b: Budget) => b.category === category);
      
      if (existing) {
        return await api.budgets.update(existing.id, {
          amount,
          is_active: true,
        });
      } else {
        return await api.budgets.create({
          category,
          amount,
          period: "monthly",
          is_active: true,
        });
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["budgets"] });
      queryClient.invalidateQueries({ queryKey: ["budgets", "summary"] });
    },
  });

  const handleAmountChange = (category: string, value: string) => {
    setBudgetAmounts(prev => ({ ...prev, [category]: value }));
    setHasChanges(true);
  };

  const handleSaveAll = async () => {
    const promises = [];
    
    for (const category of BUDGET_CATEGORIES) {
      const amount = budgetAmounts[category.name];
      if (amount && parseFloat(amount) > 0) {
        promises.push(
          saveBudgetMutation.mutateAsync({
            category: category.name,
            amount: parseFloat(amount),
          })
        );
      }
    }

    try {
      await Promise.all(promises);
      setHasChanges(false);
      alert("Budgets saved successfully!");
    } catch (error) {
      console.error("Failed to save budgets:", error);
      alert("Failed to save budgets. Please try again.");
    }
  };

  const getBudgetData = (categoryName: string): Budget | undefined => {
    return budgetsData?.budgets.find((b: Budget) => b.category === categoryName);
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case "on_track":
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "warning":
        return <AlertCircle className="h-5 w-5 text-yellow-600" />;
      case "exceeded":
        return <TrendingUp className="h-5 w-5 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case "on_track":
        return "bg-green-600";
      case "warning":
        return "bg-yellow-600";
      case "exceeded":
        return "bg-red-600";
      default:
        return "bg-gray-400";
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  const totalBudgeted = budgetsData?.total_budgeted || 0;
  const totalSpent = budgetsData?.total_spent || 0;
  const overallPercentage = totalBudgeted > 0 ? (totalSpent / totalBudgeted) * 100 : 0;

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => router.push("/dashboard")}
            className="mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Budget Management</h1>
              <p className="text-gray-600 mt-2">
                Set monthly spending limits for each category
              </p>
            </div>
            
            {hasChanges && (
              <Button
                onClick={handleSaveAll}
                disabled={saveBudgetMutation.isPending}
                size="lg"
              >
                <Save className="h-4 w-4 mr-2" />
                {saveBudgetMutation.isPending ? "Saving..." : "Save All Changes"}
              </Button>
            )}
          </div>
        </div>

        {/* Overall Summary */}
        {totalBudgeted > 0 && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Overall Budget</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total Budgeted</span>
                  <span className="font-semibold">${totalBudgeted.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total Spent</span>
                  <span className="font-semibold">${totalSpent.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Remaining</span>
                  <span className={`font-semibold ${(totalBudgeted - totalSpent) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${(totalBudgeted - totalSpent).toFixed(2)}
                  </span>
                </div>
                <div className="relative">
                  <Progress value={Math.min(overallPercentage, 100)} className="h-3" />
                  <div
                    className="absolute top-0 left-0 h-3 rounded-full transition-all"
                    style={{
                      width: `${Math.min(overallPercentage, 100)}%`,
                      backgroundColor: overallPercentage >= 100 ? "#EF4444" : overallPercentage >= 80 ? "#F59E0B" : "#10B981",
                    }}
                  />
                </div>
                <p className="text-xs text-gray-500 text-center">
                  {overallPercentage.toFixed(1)}% of total budget used
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Budget Categories */}
        <div className="grid gap-6">
          {BUDGET_CATEGORIES.map((category) => {
            const budgetData = getBudgetData(category.name);
            const spent = budgetData?.spent || 0;
            const percentage = budgetData?.percentage || 0;

            return (
              <Card key={category.name}>
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4">
                    <div className="text-4xl">{category.icon}</div>
                    
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {category.name}
                          </h3>
                          <p className="text-sm text-gray-600">{category.description}</p>
                        </div>
                        {budgetData && getStatusIcon(budgetData.status)}
                      </div>

                      <div className="space-y-4 mt-4">
                        <div className="flex items-center gap-4">
                          <div className="flex-1">
                            <Label htmlFor={`budget-${category.name}`}>
                              Monthly Budget
                            </Label>
                            <div className="relative mt-1">
                              <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                              <Input
                                id={`budget-${category.name}`}
                                type="number"
                                min="0"
                                step="0.01"
                                placeholder="0.00"
                                value={budgetAmounts[category.name] || ""}
                                onChange={(e) => handleAmountChange(category.name, e.target.value)}
                                className="pl-9"
                              />
                            </div>
                          </div>

                          {budgetData && (
                            <div className="flex-1">
                              <Label>Spent This Month</Label>
                              <div className="mt-1 px-3 py-2 bg-gray-50 rounded-md">
                                <span className="font-semibold">
                                  ${spent.toFixed(2)}
                                </span>
                                <span className="text-sm text-gray-600 ml-2">
                                  ({percentage.toFixed(1)}%)
                                </span>
                              </div>
                            </div>
                          )}
                        </div>

                        {budgetData && budgetData.amount > 0 && (
                          <div className="space-y-2">
                            <div className="relative">
                              <Progress value={Math.min(percentage, 100)} className="h-2" />
                              <div
                                className={`absolute top-0 left-0 h-2 rounded-full transition-all ${getStatusColor(budgetData.status)}`}
                                style={{ width: `${Math.min(percentage, 100)}%` }}
                              />
                            </div>
                            <div className="flex justify-between text-xs text-gray-600">
                              <span>
                                ${(budgetData.amount - spent).toFixed(2)} remaining
                              </span>
                              {budgetData.status === "exceeded" && (
                                <span className="text-red-600 font-medium">
                                  Over budget by ${(spent - budgetData.amount).toFixed(2)}
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Tips Section */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Budgeting Tips</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Use the 50/30/20 rule: 50% needs, 30% wants, 20% savings</li>
              <li>• Review and adjust your budgets monthly based on spending patterns</li>
              <li>• Set realistic budgets based on your past spending history</li>
              <li>• Leave some buffer room for unexpected expenses</li>
              <li>• Ask the AI chatbot for personalized budget recommendations</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
