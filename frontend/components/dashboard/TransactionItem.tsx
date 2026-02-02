"use client";

import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface TransactionItemProps {
  name: string;
  category: string;
  amount: number;
  date: string;
  type: "income" | "expense";
  pending?: boolean;
}

export function TransactionItem({ name, category, amount, date, type, pending }: TransactionItemProps) {
  const isIncome = type === "income";
  
  return (
    <div className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
      <div className="flex items-center space-x-3 flex-1">
        <div className={`rounded-full p-2 ${isIncome ? "bg-green-100" : "bg-red-100"}`}>
          {isIncome ? (
            <ArrowDownRight className="h-4 w-4 text-green-600" />
          ) : (
            <ArrowUpRight className="h-4 w-4 text-red-600" />
          )}
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-gray-900 truncate">{name}</p>
          <div className="flex items-center space-x-2">
            <p className="text-sm text-gray-500">{category}</p>
            {pending && (
              <span className="inline-flex items-center rounded-full bg-yellow-50 px-2 py-0.5 text-xs font-medium text-yellow-700">
                Pending
              </span>
            )}
          </div>
        </div>
      </div>
      <div className="text-right">
        <p className={`font-semibold ${isIncome ? "text-green-600" : "text-gray-900"}`}>
          {isIncome ? "+" : "-"}${Math.abs(amount).toLocaleString("en-US", { minimumFractionDigits: 2 })}
        </p>
        <p className="text-xs text-gray-400">
          {formatDistanceToNow(new Date(date), { addSuffix: true })}
        </p>
      </div>
    </div>
  );
}
