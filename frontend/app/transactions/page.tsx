"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useAuthStore } from "@/stores/authStore";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { FilterBar } from "@/components/transactions/FilterBar";
import { TransactionRow } from "@/components/transactions/TransactionRow";
import { Search, Download, Plus, Loader2, ArrowLeft, Filter } from "lucide-react";

export default function TransactionsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState<any>({});
  const [showFilters, setShowFilters] = useState(false);
  const [page, setPage] = useState(1);
  const limit = 50;

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  // Fetch transactions
  const { data: transactionsData, isLoading } = useQuery({
    queryKey: ["transactions", page, searchQuery, filters],
    queryFn: async () => {
      const response = await api.transactions.list({
        offset: (page - 1) * limit,
        limit,
        search: searchQuery || undefined,
        ...filters,
      });
      return response.data;
    },
    enabled: isAuthenticated,
  });

  // Fetch categories for filter
  const { data: categories } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      // This would fetch unique categories from transactions
      return [
        "Food & Dining",
        "Transportation",
        "Shopping",
        "Entertainment",
        "Bills & Utilities",
        "Healthcare",
        "Travel",
        "Income",
        "Other",
      ];
    },
    enabled: isAuthenticated,
  });

  if (!isAuthenticated) {
    return null;
  }

  const transactions = transactionsData?.transactions || [];
  const totalCount = transactionsData?.total || 0;

  const handleExport = () => {
    // Export transactions to CSV
    console.log("Exporting transactions...");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push("/dashboard")}
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
            </div>
            <div className="flex items-center space-x-3">
              <Button variant="outline" size="sm" onClick={handleExport}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <Button size="sm" onClick={() => router.push("/transactions/add")}>
                <Plus className="h-4 w-4 mr-2" />
                Add Cash Transaction
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Filter Bar */}
        <div className="mb-6 space-y-4">
          <div className="flex items-center space-x-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search transactions..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <Button
              variant={showFilters ? "default" : "outline"}
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
            >
              <Filter className="h-4 w-4 mr-2" />
              Filters
            </Button>
          </div>

          {showFilters && (
            <FilterBar
              categories={categories || []}
              onFilterChange={setFilters}
            />
          )}
        </div>

        {/* Transactions Table */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : transactions.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="py-3 px-4 text-left">
                        <input type="checkbox" className="rounded border-gray-300" />
                      </th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-gray-900">
                        Description
                      </th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-gray-900">
                        Category
                      </th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-gray-900">
                        Account
                      </th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-gray-900">
                        Amount
                      </th>
                      <th className="py-3 px-4 text-left text-sm font-semibold text-gray-900">
                        Status
                      </th>
                      <th className="py-3 px-4"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((transaction: any) => (
                      <TransactionRow
                        key={transaction.id}
                        transaction={transaction}
                      />
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination */}
              <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-medium">{(page - 1) * limit + 1}</span> to{" "}
                  <span className="font-medium">{Math.min(page * limit, totalCount)}</span> of{" "}
                  <span className="font-medium">{totalCount}</span> transactions
                </div>
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page - 1)}
                    disabled={page === 1}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(page + 1)}
                    disabled={transactions.length < limit}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <Search className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No transactions found</h3>
              <p className="text-gray-500 mb-4">
                {searchQuery || Object.keys(filters).length > 0
                  ? "Try adjusting your search or filters"
                  : "Link an account to start tracking transactions"}
              </p>
              {!searchQuery && Object.keys(filters).length === 0 && (
                <Button onClick={() => router.push("/plaid/link")}>
                  Link Account
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
