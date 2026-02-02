"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SpendingData {
  category: string;
  amount: number;
  color: string;
  percentage: number;
}

interface SpendingChartProps {
  data: SpendingData[];
  total: number;
}

const COLORS = [
  "#3B82F6", // blue
  "#10B981", // green
  "#F59E0B", // amber
  "#EC4899", // pink
  "#8B5CF6", // purple
  "#EF4444", // red
  "#06B6D4", // cyan
  "#84CC16", // lime
];

export function SpendingChart({ data, total }: SpendingChartProps) {
  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Spending by Category</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64 text-gray-500">
            No spending data available
          </div>
        </CardContent>
      </Card>
    );
  }

  // Sort by amount descending and take top 8
  const topCategories = [...data]
    .sort((a, b) => b.amount - a.amount)
    .slice(0, 8)
    .map((item, index) => ({
      ...item,
      color: COLORS[index % COLORS.length],
      percentage: (item.amount / total) * 100,
    }));

  const maxAmount = Math.max(...topCategories.map((c) => c.amount));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Spending by Category</CardTitle>
        <p className="text-sm text-gray-500">Last 30 days</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {topCategories.map((category) => (
            <div key={category.category} className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: category.color }}
                  />
                  <span className="font-medium text-gray-700">{category.category}</span>
                </div>
                <div className="flex items-center space-x-3">
                  <span className="text-gray-500">{category.percentage.toFixed(1)}%</span>
                  <span className="font-semibold text-gray-900">
                    ${category.amount.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </span>
                </div>
              </div>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    backgroundColor: category.color,
                    width: `${(category.amount / maxAmount) * 100}%`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700">Total Spending</span>
            <span className="text-lg font-bold text-gray-900">
              ${total.toLocaleString("en-US", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
