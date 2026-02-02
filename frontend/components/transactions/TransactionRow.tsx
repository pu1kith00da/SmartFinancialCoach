"use client";

import { useState } from "react";
import { MoreVertical, Edit, Trash2, Tag } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface TransactionRowProps {
  transaction: any;
  onEdit?: (transaction: any) => void;
  onDelete?: (id: string) => void;
  onCategorize?: (id: string, category: string) => void;
}

export function TransactionRow({ transaction, onEdit, onDelete, onCategorize }: TransactionRowProps) {
  const [showActions, setShowActions] = useState(false);
  const isIncome = transaction.amount > 0;

  return (
    <tr className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
      <td className="py-4 px-4">
        <input type="checkbox" className="rounded border-gray-300" />
      </td>
      <td className="py-4 px-4">
        <div className="flex flex-col">
          <span className="font-medium text-gray-900">{transaction.name}</span>
          <span className="text-sm text-gray-500">
            {formatDistanceToNow(new Date(transaction.date), { addSuffix: true })}
          </span>
        </div>
      </td>
      <td className="py-4 px-4">
        <span className="inline-flex items-center rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-800">
          {transaction.category || "Uncategorized"}
        </span>
      </td>
      <td className="py-4 px-4">
        <span className="text-sm text-gray-600">{transaction.account_name || "Unknown"}</span>
      </td>
      <td className="py-4 px-4">
        <span className={`font-semibold ${isIncome ? "text-green-600" : "text-gray-900"}`}>
          {isIncome ? "+" : "-"}${Math.abs(transaction.amount).toLocaleString("en-US", { minimumFractionDigits: 2 })}
        </span>
      </td>
      <td className="py-4 px-4">
        {transaction.pending && (
          <span className="inline-flex items-center rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-800">
            Pending
          </span>
        )}
      </td>
      <td className="py-4 px-4 relative">
        <button
          onClick={() => setShowActions(!showActions)}
          className="rounded p-1 hover:bg-gray-200 transition-colors"
        >
          <MoreVertical className="h-5 w-5 text-gray-400" />
        </button>
        
        {showActions && (
          <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
            <div className="py-1">
              <button
                onClick={() => {
                  onEdit?.(transaction);
                  setShowActions(false);
                }}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </button>
              <button
                onClick={() => {
                  onCategorize?.(transaction.id, "");
                  setShowActions(false);
                }}
                className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <Tag className="h-4 w-4 mr-2" />
                Change Category
              </button>
              <button
                onClick={() => {
                  onDelete?.(transaction.id);
                  setShowActions(false);
                }}
                className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </button>
            </div>
          </div>
        )}
      </td>
    </tr>
  );
}
