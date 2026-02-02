"use client";

import { useState } from "react";
import { X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FilterBarProps {
  categories: string[];
  onFilterChange: (filters: any) => void;
}

export function FilterBar({ categories, onFilterChange }: FilterBarProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [dateRange, setDateRange] = useState<string>("30");
  const [minAmount, setMinAmount] = useState<string>("");
  const [maxAmount, setMaxAmount] = useState<string>("");

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    applyFilters(category, dateRange, minAmount, maxAmount);
  };

  const handleDateRangeChange = (range: string) => {
    setDateRange(range);
    applyFilters(selectedCategory, range, minAmount, maxAmount);
  };

  const handleAmountChange = (min: string, max: string) => {
    setMinAmount(min);
    setMaxAmount(max);
    applyFilters(selectedCategory, dateRange, min, max);
  };

  const applyFilters = (category: string, range: string, min: string, max: string) => {
    onFilterChange({
      category: category || undefined,
      days: range ? parseInt(range) : undefined,
      min_amount: min ? parseFloat(min) : undefined,
      max_amount: max ? parseFloat(max) : undefined,
    });
  };

  const clearFilters = () => {
    setSelectedCategory("");
    setDateRange("30");
    setMinAmount("");
    setMaxAmount("");
    onFilterChange({});
  };

  const hasActiveFilters = selectedCategory || minAmount || maxAmount || dateRange !== "30";

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Filters</h3>
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            <X className="h-4 w-4 mr-1" />
            Clear All
          </Button>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            value={selectedCategory}
            onChange={(e) => handleCategoryChange(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat}
              </option>
            ))}
          </select>
        </div>

        {/* Date Range */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Date Range
          </label>
          <select
            value={dateRange}
            onChange={(e) => handleDateRangeChange(e.target.value)}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
            <option value="365">Last year</option>
          </select>
        </div>

        {/* Min Amount */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Min Amount
          </label>
          <input
            type="number"
            value={minAmount}
            onChange={(e) => handleAmountChange(e.target.value, maxAmount)}
            placeholder="$0"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Max Amount */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Max Amount
          </label>
          <input
            type="number"
            value={maxAmount}
            onChange={(e) => handleAmountChange(minAmount, e.target.value)}
            placeholder="Any"
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  );
}
