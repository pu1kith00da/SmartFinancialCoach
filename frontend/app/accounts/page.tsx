'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/authStore';
import { api } from '@/lib/api';
import PlaidLinkButton from '@/components/PlaidLinkButton';
import { formatCurrency } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { 
  Loader2, 
  Building2, 
  CreditCard, 
  Trash2,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface Institution {
  id: string;
  name: string;
  logo?: string;
  website?: string;
  primary_color?: string;
  created_at: string;
  account_count: number;
}

interface Account {
  id: string;
  institution_id: string;
  name: string;
  official_name?: string;
  type: string;
  subtype?: string;
  balance: {
    available?: number;
    current: number;
    currency_code: string;
  };
  last_updated: string;
}

export default function AccountsPage() {
  const [selectedInstitution, setSelectedInstitution] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Fetch connected institutions
  const { data: institutions, isLoading: institutionsLoading, error: institutionsError } = useQuery({
    queryKey: ['plaid', 'institutions'],
    queryFn: async () => {
      console.log('Fetching institutions...');
      const response = await api.plaid.getInstitutions();
      console.log('Institutions response:', response.data);
      return response.data as Institution[];
    },
    enabled: isAuthenticated,
    retry: (failureCount, error) => {
      console.error('Institutions query failed:', error);
      // Only retry on network errors, not authentication errors
      if (error?.response?.status === 401) {
        return false;
      }
      return failureCount < 3;
    }
  });

  // Fetch accounts
  const { data: accountsData, isLoading: accountsLoading } = useQuery({
    queryKey: ['plaid', 'accounts'],
    queryFn: async () => {
      const response = await api.plaid.getAccounts();
      return response.data;
    },
    enabled: isAuthenticated,
  });

  // Sync accounts mutation
  const syncAccountsMutation = useMutation({
    mutationFn: async () => {
      await api.plaid.syncAccounts();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plaid', 'accounts'] });
      queryClient.invalidateQueries({ queryKey: ['plaid', 'institutions'] });
    }
  });

  // Remove institution mutation
  const removeInstitutionMutation = useMutation({
    mutationFn: async (institutionId: string) => {
      await api.plaid.removeInstitution(institutionId);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['plaid', 'institutions'] });
      queryClient.invalidateQueries({ queryKey: ['plaid', 'accounts'] });
      setSelectedInstitution(null);
    }
  });

  const handleConnectionSuccess = () => {
    // This will trigger a refetch of institutions and accounts
    queryClient.invalidateQueries({ queryKey: ['plaid', 'institutions'] });
    queryClient.invalidateQueries({ queryKey: ['plaid', 'accounts'] });
  };

  const handleRemoveInstitution = (institutionId: string) => {
    if (confirm('Are you sure you want to disconnect this bank? This will remove all associated accounts and transactions.')) {
      removeInstitutionMutation.mutate(institutionId);
    }
  };

  // Don't render anything if not authenticated
  if (!isAuthenticated) {
    return null;
  }

  if (institutionsLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (institutionsError) {
    console.error('Institutions error:', institutionsError);
    const errorMessage = institutionsError?.response?.data?.detail || 
                        institutionsError?.message || 
                        'Unknown error occurred';
    
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Failed to load bank connections
          </h2>
          <p className="text-gray-600 mb-4">
            {errorMessage}
          </p>
          <div className="space-x-2">
            <Button onClick={() => window.location.reload()} variant="outline">
              Try Again
            </Button>
            <Button onClick={() => router.push('/dashboard')} variant="secondary">
              Back to Dashboard
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const accounts = accountsData?.accounts || [];

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Connected Accounts</h1>
          <p className="text-gray-600 mt-1">
            Manage your connected bank accounts and view balances
          </p>
        </div>
        <div className="flex gap-3">
          <Button
            onClick={() => syncAccountsMutation.mutate()}
            disabled={syncAccountsMutation.isPending}
            variant="outline"
            className="flex items-center gap-2"
          >
            {syncAccountsMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
            Sync Accounts
          </Button>
          <PlaidLinkButton onSuccess={handleConnectionSuccess}>
            Connect New Bank
          </PlaidLinkButton>
        </div>
      </div>

      {/* Connected Institutions */}
      {institutions && institutions.length > 0 ? (
        <div className="space-y-6">
          {institutions.map((institution) => {
            const institutionAccounts = accounts.filter(
              (account: Account) => account.institution_id === institution.id
            );

            return (
              <div 
                key={institution.id}
                className="bg-white rounded-lg border border-gray-200 shadow-sm"
              >
                {/* Institution Header */}
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 bg-gray-100 rounded-lg flex items-center justify-center">
                        {institution.logo ? (
                          <img
                            src={institution.logo}
                            alt={institution.name}
                            className="h-8 w-8 object-contain"
                          />
                        ) : (
                          <Building2 className="h-6 w-6 text-gray-600" />
                        )}
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {institution.name}
                        </h3>
                        <p className="text-sm text-gray-600">
                          {institution.account_count} account{institution.account_count !== 1 ? 's' : ''} connected
                        </p>
                      </div>
                    </div>
                    <Button
                      onClick={() => handleRemoveInstitution(institution.id)}
                      disabled={removeInstitutionMutation.isPending}
                      variant="destructive"
                      className="flex items-center gap-2"
                    >
                      {removeInstitutionMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                      Disconnect
                    </Button>
                  </div>
                </div>

                {/* Institution Accounts */}
                <div className="p-6">
                  {accountsLoading ? (
                    <div className="flex items-center justify-center py-8">
                      <Loader2 className="h-6 w-6 animate-spin" />
                    </div>
                  ) : institutionAccounts.length > 0 ? (
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {institutionAccounts.map((account: Account) => (
                        <div
                          key={account.id}
                          className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                        >
                          <div className="flex items-center gap-3 mb-3">
                            <CreditCard className="h-5 w-5 text-gray-600" />
                            <div>
                              <h4 className="font-medium text-gray-900">
                                {account.name}
                              </h4>
                              <p className="text-sm text-gray-600">
                                {account.type} • {account.subtype || 'Account'}
                              </p>
                            </div>
                          </div>
                          <div className="space-y-1">
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-600">Current Balance:</span>
                              <span className="font-medium text-gray-900">
                                {formatCurrency(account.balance.current, account.balance.currency_code)}
                              </span>
                            </div>
                            {account.balance.available !== undefined && (
                              <div className="flex justify-between text-sm">
                                <span className="text-gray-600">Available:</span>
                                <span className="font-medium text-gray-900">
                                  {formatCurrency(account.balance.available, account.balance.currency_code)}
                                </span>
                              </div>
                            )}
                            <div className="flex justify-between text-xs">
                              <span className="text-gray-500">Last Updated:</span>
                              <span className="text-gray-500">
                                {new Date(account.last_updated).toLocaleDateString()}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-gray-600">
                        No accounts found for this institution
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Empty State */
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Building2 className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            No Banks Connected
          </h2>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Connect your bank accounts to automatically track transactions, 
            view balances, and get personalized financial insights.
          </p>
          <PlaidLinkButton onSuccess={handleConnectionSuccess} />
        </div>
      )}
    </div>
  );
}