'use client';

import { useState, useCallback, useEffect } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { Button } from './ui/button';
import { Loader2, Plus } from 'lucide-react';

interface PlaidLinkButtonProps {
  onSuccess?: () => void;
  onExit?: () => void;
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
  children?: React.ReactNode;
}

// Global flag to track if Plaid Link is currently active
let plaidLinkActive = false;

export default function PlaidLinkButton({
  onSuccess,
  onExit,
  variant = 'default',
  children
}: PlaidLinkButtonProps) {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [canOpen, setCanOpen] = useState(true);
  const queryClient = useQueryClient();

  // Check if we can open Plaid Link (prevent multiple instances)
  useEffect(() => {
    const checkCanOpen = () => {
      setCanOpen(!plaidLinkActive);
    };
    
    const interval = setInterval(checkCanOpen, 1000);
    checkCanOpen();
    
    return () => clearInterval(interval);
  }, []);

  // Mutation to create link token
  const createLinkToken = useMutation({
    mutationFn: async () => {
      const response = await api.plaid.createLinkToken();
      return response.data.link_token;
    },
    onSuccess: (token) => {
      setLinkToken(token);
      setLoading(false);
      // If the script is already ready, open immediately
      if (plaidLinkActive && ready && open) {
        open();
      }
    },
    onError: (error) => {
      console.error('Failed to create link token:', error);
      plaidLinkActive = false;
      setCanOpen(true);
      setLoading(false);
    }
  });

  // Mutation to exchange public token
  const exchangePublicToken = useMutation({
    mutationFn: async (publicToken: string) => {
      const response = await api.plaid.exchangePublicToken(publicToken);
      return response.data;
    },
    onSuccess: () => {
      // Invalidate and refetch institutions and accounts
      queryClient.invalidateQueries({ queryKey: ['plaid', 'institutions'] });
      queryClient.invalidateQueries({ queryKey: ['plaid', 'accounts'] });
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      onSuccess?.();
    },
    onError: (error) => {
      console.error('Failed to exchange public token:', error);
      plaidLinkActive = false;
      setCanOpen(true);
    }
  });

  // Plaid Link callbacks
  const onPlaidSuccess = useCallback((publicToken: string) => {
    plaidLinkActive = false; // Reset flag on success
    setCanOpen(true);
    exchangePublicToken.mutate(publicToken);
  }, [exchangePublicToken]);

  const onPlaidExit = useCallback((error: any, metadata: any) => {
    plaidLinkActive = false; // Reset flag on exit
    setCanOpen(true);
    if (error) {
      console.error('Plaid Link exited with error:', error);
    }
    onExit?.();
  }, [onExit]);

  // Configure Plaid Link - always provide a config object
  const config = {
    token: linkToken,
    onSuccess: onPlaidSuccess,
    onExit: onPlaidExit,
    onEvent: (eventName: string, metadata: any) => {
      console.log('Plaid Link event:', eventName, metadata);
    },
  };

  const { open, ready } = usePlaidLink(config);

  // Auto-open once the link token is ready and Plaid script has loaded
  useEffect(() => {
    if (plaidLinkActive && linkToken && ready && open) {
      open();
    }
  }, [linkToken, ready, open]);

  // Handle button click
  const handleClick = () => {
    if (!canOpen) {
      console.warn('Cannot open Plaid Link - another instance is active');
      return;
    }
    
    plaidLinkActive = true;
    setCanOpen(false);

    if (!linkToken && !loading) {
      setLoading(true);
      createLinkToken.mutate();
    } else if (ready && linkToken && open) {
      plaidLinkActive = true; // Set flag when opening
      open();
    }
  };

  const isDisabled = loading || createLinkToken.isPending || exchangePublicToken.isPending || (linkToken && !ready) || !canOpen;

  return (
    <Button
      onClick={handleClick}
      disabled={isDisabled}
      variant={variant}
      className="flex items-center gap-2"
    >
      {(loading || createLinkToken.isPending || exchangePublicToken.isPending) ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <Plus className="h-4 w-4" />
      )}
      {children || 'Connect Bank Account'}
    </Button>
  );
}