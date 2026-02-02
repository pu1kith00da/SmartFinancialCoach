"use client";

import { Building2, TrendingUp, TrendingDown } from "lucide-react";

interface AccountCardProps {
  name: string;
  type: string;
  balance: number;
  currency: string;
  lastUpdated?: string;
  change?: number;
}

export function AccountCard({ name, type, balance, currency, lastUpdated, change }: AccountCardProps) {
  const isPositive = change && change >= 0;
  
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="rounded-full bg-blue-100 p-2">
            <Building2 className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{name}</h3>
            <p className="text-sm text-gray-500 capitalize">{type}</p>
          </div>
        </div>
      </div>
      
      <div className="space-y-1">
        <p className="text-3xl font-bold text-gray-900">
          {currency === "USD" ? "$" : currency}
          {Math.abs(balance).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </p>
        
        {change !== undefined && (
          <div className="flex items-center space-x-1">
            {isPositive ? (
              <TrendingUp className="h-4 w-4 text-green-600" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-600" />
            )}
            <span className={`text-sm font-medium ${isPositive ? "text-green-600" : "text-red-600"}`}>
              {isPositive ? "+" : ""}{change?.toFixed(2)}%
            </span>
            <span className="text-sm text-gray-500">this month</span>
          </div>
        )}
        
        {lastUpdated && (
          <p className="text-xs text-gray-400 mt-2">Updated {lastUpdated}</p>
        )}
      </div>
    </div>
  );
}
