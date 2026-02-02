"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { api } from "@/lib/api";
import { ArrowLeft, Calendar, CreditCard, TrendingUp, AlertCircle } from "lucide-react";
import { formatCurrency } from "@/lib/utils";

interface Subscription {
  id: string;
  name: string;
  service_provider: string;
  category: string;
  amount: number;
  billing_cycle: string;
  next_billing_date: string;
  status: string;
  monthly_cost: number;
}

interface SubscriptionStats {
  total_subscriptions: number;
  active_subscriptions: number;
  cancelled_subscriptions: number;
  total_monthly_cost: number;
  total_annual_cost: number;
}

export default function SubscriptionsPage() {
  const router = useRouter();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [stats, setStats] = useState<SubscriptionStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSubscriptions();
  }, []);

  const loadSubscriptions = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load both subscriptions and stats
      const [subsResponse, statsResponse] = await Promise.all([
        api.subscriptions.list(),
        api.subscriptions.stats(),
      ]);

      setSubscriptions(subsResponse.data);
      setStats(statsResponse.data);
    } catch (err: any) {
      console.error("Error loading subscriptions:", err);
      setError(err.response?.data?.detail || "Failed to load subscriptions");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return "bg-green-500";
      case "cancelled":
        return "bg-gray-500";
      case "paused":
        return "bg-yellow-500";
      default:
        return "bg-gray-500";
    }
  };

  const getBillingCycleText = (cycle: string) => {
    switch (cycle.toLowerCase()) {
      case "monthly":
        return "per month";
      case "yearly":
      case "annual":
        return "per year";
      case "weekly":
        return "per week";
      default:
        return cycle;
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="mb-6">
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-96" />
        </div>
        <div className="grid gap-4 md:grid-cols-3 mb-6">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 text-red-500">
              <AlertCircle className="h-5 w-5" />
              <p>{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => router.push("/dashboard")}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Dashboard
        </Button>
        <h1 className="text-3xl font-bold mb-2">Subscriptions</h1>
        <p className="text-muted-foreground">
          Manage your recurring subscriptions and track monthly costs
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-3 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Active Subscriptions
              </CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active_subscriptions}</div>
              <p className="text-xs text-muted-foreground">
                {stats.total_subscriptions} total
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Monthly Cost
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(stats.total_monthly_cost)}
              </div>
              <p className="text-xs text-muted-foreground">
                {formatCurrency(stats.total_annual_cost)} per year
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Average Cost
              </CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.active_subscriptions > 0
                  ? formatCurrency(stats.total_monthly_cost / stats.active_subscriptions)
                  : "$0.00"}
              </div>
              <p className="text-xs text-muted-foreground">per subscription</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Subscriptions List */}
      <Card>
        <CardHeader>
          <CardTitle>Your Subscriptions</CardTitle>
          <CardDescription>
            {subscriptions.length === 0
              ? "No subscriptions found"
              : `Showing ${subscriptions.length} subscription${subscriptions.length !== 1 ? "s" : ""}`}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {subscriptions.length === 0 ? (
            <div className="text-center py-12">
              <CreditCard className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground mb-4">
                No subscriptions tracked yet
              </p>
              <p className="text-sm text-muted-foreground">
                Connect your bank accounts to automatically detect subscriptions,
                or add them manually.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {subscriptions.map((subscription) => (
                <Card key={subscription.id} className="hover:shadow-md transition-shadow">
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-lg">{subscription.name}</h3>
                          <Badge
                            variant="secondary"
                            className={getStatusColor(subscription.status)}
                          >
                            {subscription.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {subscription.service_provider}
                          {subscription.category && ` • ${subscription.category}`}
                        </p>
                        <div className="flex items-center gap-4 text-sm">
                          <div className="flex items-center gap-1">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span>
                              Next billing:{" "}
                              {subscription.next_billing_date
                                ? new Date(subscription.next_billing_date).toLocaleDateString()
                                : "N/A"}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold">
                          {formatCurrency(subscription.amount)}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {getBillingCycleText(subscription.billing_cycle)}
                        </div>
                        {subscription.billing_cycle.toLowerCase() !== "monthly" && (
                          <div className="text-xs text-muted-foreground mt-1">
                            ~{formatCurrency(subscription.monthly_cost)}/month
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
