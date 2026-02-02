"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/authStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Calendar, DollarSign, Edit3, Trash2 } from "lucide-react";
import { format } from "date-fns";

export default function TransactionDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const { isAuthenticated } = useAuthStore();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const transactionId = params.id as string;
  
  const [formData, setFormData] = useState({
    user_category: "",
    user_notes: "",
  });

  // Fetch transaction details
  const { data: transaction, isLoading: isLoadingTransaction, error } = useQuery({
    queryKey: ["transaction", transactionId],
    queryFn: async () => {
      const response = await api.transactions.get(transactionId);
      return response.data;
    },
    enabled: isAuthenticated && !!transactionId,
  });

  // Update form data when transaction loads
  useEffect(() => {
    if (transaction) {
      setFormData({
        user_category: transaction.user_category || transaction.category || "",
        user_notes: transaction.user_notes || "",
      });
    }
  }, [transaction]);

  const categories = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Bills & Utilities",
    "Healthcare",
    "Travel",
    "Income",
    "Transfer",
    "Other",
  ];

  const updateTransactionMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.transactions.update(transactionId, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transaction", transactionId] });
      queryClient.invalidateQueries({ queryKey: ["transactions"] });
      setIsEditing(false);
    },
    onError: (error) => {
      console.error("Failed to update transaction:", error);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await updateTransactionMutation.mutateAsync(formData);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  if (!isAuthenticated) {
    return null;
  }

  if (isLoadingTransaction) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-600">Loading transaction...</div>
      </div>
    );
  }

  if (error || !transaction) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Transaction not found</h2>
          <p className="text-gray-600 mb-4">The transaction you're looking for doesn't exist.</p>
          <Button onClick={() => router.push("/transactions")}>
            Back to Transactions
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push("/transactions")}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Transactions
              </Button>
              <h1 className="text-2xl font-bold text-gray-900">Transaction Details</h1>
            </div>
            <div className="flex items-center space-x-2">
              {!isEditing && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                >
                  <Edit3 className="h-4 w-4 mr-2" />
                  Edit
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm">
          {/* Transaction Overview */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">{transaction.name}</h2>
              <div className={`text-2xl font-bold ${transaction.amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <div className="text-gray-500">Date</div>
                <div className="font-medium">{format(new Date(transaction.date), 'MMM dd, yyyy')}</div>
              </div>
              <div>
                <div className="text-gray-500">Account</div>
                <div className="font-medium">{transaction.account?.name || 'Manual Entry'}</div>
              </div>
              <div>
                <div className="text-gray-500">Category</div>
                <div className="font-medium">{transaction.user_category || transaction.category}</div>
              </div>
              <div>
                <div className="text-gray-500">Type</div>
                <div className="font-medium capitalize">{transaction.amount < 0 ? 'Expense' : 'Income'}</div>
              </div>
            </div>
          </div>

          {/* Editable Section */}
          {isEditing ? (
            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                {/* Category */}
                <div>
                  <label htmlFor="user_category" className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    id="user_category"
                    name="user_category"
                    value={formData.user_category}
                    onChange={handleChange}
                    className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select a category</option>
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Notes */}
              <div>
                <label htmlFor="user_notes" className="block text-sm font-medium text-gray-700 mb-2">
                  Notes
                </label>
                <textarea
                  id="user_notes"
                  name="user_notes"
                  rows={3}
                  value={formData.user_notes}
                  onChange={handleChange}
                  placeholder="Add any additional details..."
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Submit Buttons */}
              <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsEditing(false)}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? "Saving..." : "Save Changes"}
                </Button>
              </div>
            </form>
          ) : (
            <div className="p-6">
              {/* Additional Details */}
              <div className="space-y-4">
                {transaction.user_notes && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Notes</div>
                    <div className="text-gray-900 bg-gray-50 rounded-md p-3">
                      {transaction.user_notes}
                    </div>
                  </div>
                )}

                {transaction.plaid_transaction_id && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Source</div>
                    <div className="text-gray-600">Imported from bank via Plaid</div>
                  </div>
                )}

                {transaction.merchant_name && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Merchant</div>
                    <div className="text-gray-900">{transaction.merchant_name}</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}