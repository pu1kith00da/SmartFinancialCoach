"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/authStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { AccountCard } from "@/components/dashboard/AccountCard";
import { StatCard } from "@/components/dashboard/StatCard";
import { TransactionItem } from "@/components/dashboard/TransactionItem";
import { InsightCard } from "@/components/dashboard/InsightCard";
import { SpendingChart } from "@/components/dashboard/SpendingChart";
import { BudgetProgress } from "@/components/dashboard/BudgetProgress";
import { GoalProgress } from "@/components/dashboard/GoalProgress";
import { Chatbot } from "@/components/chat/Chatbot";
import { Wallet, TrendingUp, CreditCard, PiggyBank, Plus, RefreshCw, Loader2, Link2, Building2, Database } from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, isAuthenticated, isLoading, logout } = useAuthStore();

  // State for AI generation (must be before any conditional returns)
  const [populatingTransactions, setPopulatingTransactions] = useState(false);

  // Fetch accounts (must be before any conditional returns)
  const { data: accountsData, isLoading: accountsLoading } = useQuery({
    queryKey: ["plaid", "accounts"],
    queryFn: async () => {
      const response = await api.plaid.getAccounts();
      return response.data;
    },
    enabled: isAuthenticated,
  });

  // Fetch recent transactions
  const { data: transactionsData, isLoading: transactionsLoading, error: transactionsError, refetch: refetchTransactions } = useQuery({
    queryKey: ["transactions", "recent"],
    queryFn: async () => {
      console.log("Fetching transactions...");
      const response = await api.transactions.list({ limit: 10 });
      console.log("Transactions response:", response.data);
      return response.data;
    },
    enabled: isAuthenticated,
    refetchOnWindowFocus: true,
  });

  // Fetch dashboard summary
  const { data: dashboardSummary, isLoading: summaryLoading } = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: async () => {
      const response = await api.analytics.dashboard();
      return response.data;
    },
    enabled: isAuthenticated,
  });

  // Fetch insights with proper cache control
  const { data: insightsData, isLoading: insightsLoading } = useQuery({
    queryKey: ["insights"],
    queryFn: async () => {
      const response = await api.insights.list({ limit: 5 });
      return response.data;
    },
    enabled: isAuthenticated,
    staleTime: 0, // Always consider data stale
    refetchOnMount: true, // Refetch when component mounts
  });

  // Mutation for generating insights with proper cache invalidation
  const generateInsightsMutation = useMutation({
    mutationFn: () => api.insights.generate(),
    onMutate: async () => {
      // Cancel any outgoing refetches to avoid overwriting optimistic update
      await queryClient.cancelQueries({ queryKey: ["insights"] });
    },
    onSuccess: () => {
      // Invalidate and refetch insights
      queryClient.invalidateQueries({ queryKey: ["insights"] });
    },
    onError: (error) => {
      console.error("Failed to generate insights:", error);
    },
  });

  // Fetch budgets
  const { data: budgetsData, isLoading: budgetsLoading, refetch: refetchBudgets } = useQuery({
    queryKey: ["budgets", "summary"],
    queryFn: async () => {
      const response = await api.budgets.summary();
      return response.data;
    },
    enabled: isAuthenticated,
  });

  // Fetch goals
  const { data: goalsData, isLoading: goalsLoading, refetch: refetchGoals } = useQuery({
    queryKey: ["goals"],
    queryFn: async () => {
      const response = await api.goals.list();
      return response.data;
    },
    enabled: isAuthenticated,
  });

  // Handle logout
  const handleLogout = () => {
    logout();
    router.push("/");
  };

  // Handle AI insight generation with mutation
  const handleGenerateInsights = () => {
    generateInsightsMutation.mutate();
  };

  // Handle sandbox data loading (transactions, budgets, goals, insights, subscriptions)
  const handlePopulateTransactions = async () => {
    setPopulatingTransactions(true);
    try {
      const response = await api.plaid.loadSampleData();
      console.log("Sample data loaded:", response.data);
      
      // Invalidate all queries after loading sample data
      await queryClient.invalidateQueries({ queryKey: ["transactions"] });
      await queryClient.invalidateQueries({ queryKey: ["insights"] });
      await queryClient.invalidateQueries({ queryKey: ["budgets"] });
      await queryClient.invalidateQueries({ queryKey: ["goals"] });
      
      const data = response.data;
      alert(
        `Successfully loaded sample data!\n\n` +
        `✅ ${data.plaid_transactions || 0} Plaid transactions\n` +
        `✅ ${data.demo_transactions || 0} demo transactions (6 months)\n` +
        `📊 Total: ${data.total_transactions} transactions\n\n` +
        `✅ ${data.budgets_created} budgets\n` +
        `✅ ${data.goals_created} goals\n` +
        `✅ ${data.insights_created} insights\n` +
        `✅ ${data.subscriptions_created} sample subscriptions\n` +
        `✅ ${data.subscriptions_detected} detected subscriptions\n` +
        `📊 Total: ${data.total_subscriptions} subscriptions\n\n` +
        `Your demo account is now ready!`
      );
    } catch (error: any) {
      console.error("Failed to load sample data:", error);
      const errorMsg = error.response?.data?.detail || "Failed to load sample data";
      alert(errorMsg);
    } finally {
      setPopulatingTransactions(false);
    }
  };

  // Redirect to login if not authenticated (after all hooks are called)
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state while auth is initializing
  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // If not authenticated after loading, return null (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  // Calculate totals from dashboard summary
  const accounts = accountsData?.accounts || [];
  const totalBalance = dashboardSummary?.current_balance || accounts.reduce((sum: number, acc: any) => sum + (acc.balance?.current || 0), 0);
  const monthlyIncome = dashboardSummary?.total_income_this_month || 0;
  const monthlyExpenses = dashboardSummary?.total_spending_this_month || 0;
  const savingsRate = dashboardSummary?.savings_rate || 0;
  const netWorth = dashboardSummary?.net_worth || totalBalance;

  // Extract data from responses
  const transactions = transactionsData?.transactions || [];
  const insights = insightsData?.insights || [];
  const budgets = budgetsData?.budgets || [];
  const goals = goalsData?.goals || [];
  const spendingByCategory = dashboardSummary?.top_spending_categories || [];
  
  // Debug logging
  console.log("Dashboard data:", {
    transactionsData,
    transactions,
    transactionsLoading,
    transactionsError,
    insights,
    budgets,
    goals,
    spendingByCategory
  });
  
  const isDataLoading = accountsLoading || transactionsLoading || summaryLoading || insightsLoading || budgetsLoading || goalsLoading;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">Smart Financial Coach</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button onClick={handleLogout} variant="outline" size="sm">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.first_name}! 👋
          </h2>
          <p className="mt-2 text-gray-600">
            Here's your financial overview for today
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <StatCard
            title="Net Worth"
            value={`$${netWorth.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
            change="+5.2% this month"
            changeType="positive"
            icon={Wallet}
            iconColor="text-blue-600"
          />
          <StatCard
            title="Monthly Income"
            value={`$${monthlyIncome.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
            change="+12% vs last month"
            changeType="positive"
            icon={TrendingUp}
            iconColor="text-green-600"
          />
          <StatCard
            title="Monthly Expenses"
            value={`$${monthlyExpenses.toLocaleString("en-US", { minimumFractionDigits: 2 })}`}
            change="-3% vs last month"
            changeType="positive"
            icon={CreditCard}
            iconColor="text-orange-600"
          />
          <StatCard
            title="Savings Rate"
            value={`${savingsRate.toFixed(1)}%`}
            change="On track"
            changeType="neutral"
            icon={PiggyBank}
            iconColor="text-purple-600"
          />
        </div>

        {/* AI Insights Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">AI Financial Insights</h3>
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handlePopulateTransactions}
                disabled={populatingTransactions}
              >
                {populatingTransactions ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Loading...
                  </>
                ) : (
                  <>
                    <Database className="h-4 w-4 mr-2" />
                    Load Sample Data
                  </>
                )}
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={handleGenerateInsights}
                disabled={generateInsightsMutation.isPending}
              >
                {generateInsightsMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Generate AI Insights
                  </>
                )}
              </Button>
              <Button variant="ghost" size="sm" onClick={() => router.push("/insights")}>
                View All
              </Button>
            </div>
          </div>
          
          {insights && insights.length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {insights.slice(0, 3).map((insight: any) => (
                <InsightCard key={insight.id} insight={insight} />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
              <p className="text-gray-500 mb-4">No insights yet. Click the button above to generate AI-powered financial insights!</p>
              <Button 
                onClick={handleGenerateInsights}
                disabled={generateInsightsMutation.isPending}
              >
                {generateInsightsMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating AI Insights...
                  </>
                ) : (
                  <>
                    Generate Your First Insights
                  </>
                )}
              </Button>
            </div>
          )}
        </div>

        {/* Charts and Progress Section */}
        <div className="grid gap-6 lg:grid-cols-2 mb-8">
          <SpendingChart data={spendingByCategory} total={monthlyExpenses} />
          <BudgetProgress budgets={budgets} />
        </div>

        {/* Goals Section */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Financial Goals</h3>
          <GoalProgress goals={goals} onAddGoal={() => router.push("/goals/new")} onManageGoals={() => router.push("/goals")} />
        </div>

        {/* AI Chatbot - Floating button */}
        <Chatbot />

        <div className="grid gap-6 lg:grid-cols-3 mb-8">
          {/* Accounts Section */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900">Accounts</h3>
              <Button size="sm" onClick={() => router.push("/accounts")}>
                <Link2 className="h-4 w-4 mr-2" />
                Manage Accounts
              </Button>
            </div>
            
            {accountsLoading ? (
              <div className="flex items-center justify-center py-12 bg-white rounded-lg border border-gray-200">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              </div>
            ) : accounts && accounts.length > 0 ? (
              <div className="grid gap-4 md:grid-cols-2">
                {accounts.map((account: any) => (
                  <AccountCard
                    key={account.id}
                    name={account.name}
                    type={account.type}
                    balance={account.balance?.current || 0}
                    currency={account.balance?.currency_code || "USD"}
                    lastUpdated={account.last_updated}
                  />
                ))}
              </div>
            ) : (
              <div className="bg-white rounded-lg border-2 border-dashed border-gray-300 p-12 text-center">
                <Building2 className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No accounts linked</h3>
                <p className="text-gray-500 mb-4">
                  Connect your bank accounts to start tracking your finances
                </p>
                <Button onClick={() => router.push("/accounts")}>
                  <Link2 className="h-4 w-4 mr-2" />
                  Connect Your First Account
                </Button>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-3">
              <Button className="w-full justify-start" variant="outline" onClick={() => router.push("/accounts")}>
                <Building2 className="h-4 w-4 mr-2" />
                Manage Bank Accounts
              </Button>
              <Button className="w-full justify-start" variant="outline" onClick={() => router.push("/transactions/add")}>
                <Plus className="h-4 w-4 mr-2" />
                Add Transaction
              </Button>
              <Button className="w-full justify-start" variant="outline" onClick={() => router.push("/goals")}>
                <PiggyBank className="h-4 w-4 mr-2" />
                Create Savings Goal
              </Button>
              <Button className="w-full justify-start" variant="outline" onClick={() => router.push("/insights")}>
                <TrendingUp className="h-4 w-4 mr-2" />
                View Insights
              </Button>
              <Button className="w-full justify-start" variant="outline" onClick={() => router.push("/subscriptions")}>
                <CreditCard className="h-4 w-4 mr-2" />
                Manage Subscriptions
              </Button>
            </div>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h3 className="text-xl font-semibold text-gray-900">Recent Transactions</h3>
            <Button variant="ghost" size="sm" onClick={() => router.push("/transactions")}>
              View All
            </Button>
          </div>
          <div className="p-6">
            {transactionsLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
              </div>
            ) : transactionsData && transactionsData.transactions && transactionsData.transactions.length > 0 ? (
              <div className="space-y-3">
                {transactionsData.transactions.slice(0, 5).map((transaction: any) => (
                  <TransactionItem
                    key={transaction.id}
                    name={transaction.name}
                    category={transaction.category}
                    amount={transaction.amount}
                    date={transaction.date}
                    type={transaction.amount < 0 ? "expense" : "income"}
                    pending={transaction.pending}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <CreditCard className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-500">No transactions yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Link an account to see your transactions
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
