from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.institutions_get_by_id_request import InstitutionsGetByIdRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.sandbox_item_fire_webhook_request import SandboxItemFireWebhookRequest
from plaid.model.webhook_type import WebhookType
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid import ApiClient, Configuration
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import logging

from app.models.plaid import Institution, Account
from app.models.transaction import Transaction
from app.models.user import User
from app.core.security import encrypt_data, decrypt_data
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PlaidService:
    """Service for Plaid API integration."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = self._create_client()
    
    def _create_client(self) -> plaid_api.PlaidApi:
        """Create Plaid API client."""
        configuration = Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )
        api_client = ApiClient(configuration)
        return plaid_api.PlaidApi(api_client)
    
    def _get_plaid_host(self) -> str:
        """Get Plaid API host based on environment."""
        env_hosts = {
            'sandbox': 'https://sandbox.plaid.com',
            'development': 'https://development.plaid.com',
            'production': 'https://production.plaid.com'
        }
        return env_hosts.get(settings.PLAID_ENV, 'https://sandbox.plaid.com')
    
    async def create_link_token(
        self, 
        user_id: UUID, 
        redirect_uri: Optional[str] = None,
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a Link token for Plaid Link initialization."""
        try:
            # Get user
            user = await self.db.get(User, user_id)
            if not user:
                raise ValueError("User not found")
            
            # Create Link token request
            request_params = {
                'user': LinkTokenCreateRequestUser(client_user_id=str(user_id)),
                'client_name': settings.APP_NAME,
                'products': [Products(p) for p in settings.PLAID_PRODUCTS],
                'country_codes': [CountryCode(c) for c in settings.PLAID_COUNTRY_CODES],
                'language': 'en'
            }
            
            if redirect_uri:
                request_params['redirect_uri'] = redirect_uri
            if webhook_url:
                request_params['webhook'] = webhook_url
            
            request = LinkTokenCreateRequest(**request_params)
            
            # Create Link token
            response = self.client.link_token_create(request)
            
            logger.info(f"Created Link token for user {user_id}")
            
            return {
                'link_token': response.link_token,
                'expiration': response.expiration
            }
            
        except Exception as e:
            logger.error(f"Error creating Link token: {str(e)}")
            raise
    
    async def exchange_public_token(
        self, 
        user_id: UUID, 
        public_token: str
    ) -> Institution:
        """Exchange public token for access token and store institution."""
        try:
            # Exchange public token
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)
            
            access_token = response.access_token
            item_id = response.item_id
            
            # Get institution info
            accounts_request = AccountsGetRequest(access_token=access_token)
            accounts_response = self.client.accounts_get(accounts_request)
            
            institution_id = accounts_response.item.institution_id
            
            # Get institution details
            inst_request = InstitutionsGetByIdRequest(
                institution_id=institution_id,
                country_codes=[CountryCode(c) for c in settings.PLAID_COUNTRY_CODES]
            )
            inst_response = self.client.institutions_get_by_id(inst_request)
            inst_data = inst_response.institution
            
            # Encrypt access token
            encrypted_token = encrypt_data(access_token)
            
            # Create institution record
            institution = Institution(
                user_id=user_id,
                plaid_institution_id=institution_id,
                plaid_item_id=item_id,
                plaid_access_token=encrypted_token,
                name=inst_data.name,
                logo=getattr(inst_data, 'logo', None),
                primary_color=getattr(inst_data, 'primary_color', None),
                url=getattr(inst_data, 'url', None),
                is_active=True,
                last_synced_at=datetime.utcnow()
            )
            
            self.db.add(institution)
            await self.db.flush()
            
            # Create account records
            for acc_data in accounts_response.accounts:
                account = Account(
                    institution_id=institution.id,
                    user_id=user_id,
                    plaid_account_id=acc_data.account_id,
                    name=acc_data.name,
                    official_name=getattr(acc_data, 'official_name', None),
                    mask=getattr(acc_data, 'mask', None),
                    type=str(acc_data.type),
                    subtype=str(getattr(acc_data, 'subtype', None)) if getattr(acc_data, 'subtype', None) else None,
                    current_balance=getattr(acc_data.balances, 'current', None),
                    available_balance=getattr(acc_data.balances, 'available', None),
                    limit=getattr(acc_data.balances, 'limit', None),
                    currency=getattr(acc_data.balances, 'iso_currency_code', 'USD') or 'USD',
                    is_active=True,
                    last_synced_at=datetime.utcnow()
                )
                self.db.add(account)
            
            await self.db.commit()
            await self.db.refresh(institution)
            
            logger.info(f"Linked institution {institution.name} for user {user_id}")
            
            return institution
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error exchanging public token: {str(e)}")
            raise
    
    async def get_user_institutions(self, user_id: UUID) -> List[Institution]:
        """Get all institutions for a user."""
        result = await self.db.execute(
            select(Institution)
            .where(Institution.user_id == user_id)
            .order_by(Institution.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_institution(self, institution_id: UUID, user_id: UUID) -> Optional[Institution]:
        """Get a specific institution."""
        result = await self.db.execute(
            select(Institution)
            .where(
                Institution.id == institution_id,
                Institution.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_accounts(self, user_id: UUID) -> List[Account]:
        """Get all accounts for a user."""
        result = await self.db.execute(
            select(Account)
            .where(Account.user_id == user_id)
            .order_by(Account.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def sync_accounts(self, institution_id: UUID, user_id: UUID) -> Dict[str, Any]:
        """Sync account balances for an institution."""
        try:
            # Get institution
            institution = await self.get_institution(institution_id, user_id)
            if not institution:
                raise ValueError("Institution not found")
            
            # Decrypt access token
            access_token = decrypt_data(institution.plaid_access_token)
            
            # In sandbox, fire webhooks to generate transactions
            if settings.PLAID_ENV == 'sandbox':
                try:
                    logger.info("Firing sandbox webhook to generate default transactions")
                    webhook_request = SandboxItemFireWebhookRequest(
                        access_token=access_token,
                        webhook_code="DEFAULT_UPDATE"
                    )
                    self.client.sandbox_item_fire_webhook(webhook_request)
                    # Give Plaid a moment to process
                    import asyncio
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.warning(f"Sandbox webhook fire failed (non-critical): {e}")
            
            # Get updated account balances
            request = AccountsBalanceGetRequest(access_token=access_token)
            response = self.client.accounts_balance_get(request)
            
            accounts_updated = 0
            
            # Update account balances
            for acc_data in response['accounts']:
                result = await self.db.execute(
                    select(Account).where(
                        Account.plaid_account_id == acc_data['account_id'],
                        Account.institution_id == institution_id
                    )
                )
                account = result.scalar_one_or_none()
                
                if account:
                    account.current_balance = acc_data['balances'].get('current')
                    account.available_balance = acc_data['balances'].get('available')
                    account.limit = acc_data['balances'].get('limit')
                    account.last_synced_at = datetime.utcnow()
                    accounts_updated += 1
            
            # Update institution sync time
            institution.last_synced_at = datetime.utcnow()
            institution.error_code = None
            institution.error_message = None
            
            # Sync transactions
            transactions_added = await self._sync_transactions(institution, user_id)
            
            await self.db.commit()
            
            logger.info(f"Synced {accounts_updated} accounts and {transactions_added} transactions for institution {institution_id}")
            
            return {
                'institution_id': institution_id,
                'accounts_updated': accounts_updated,
                'transactions_added': transactions_added,
                'last_synced_at': institution.last_synced_at,
                'success': True
            }
            
        except Exception as e:
            await self.db.rollback()
            import traceback
            logger.error(f"Error syncing accounts: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            # Update institution with error
            if institution:
                institution.error_code = "SYNC_ERROR"
                institution.error_message = str(e)
                await self.db.commit()
            
            raise
    
    async def remove_institution(self, institution_id: UUID, user_id: UUID) -> bool:
        """Remove an institution and all its accounts."""
        try:
            institution = await self.get_institution(institution_id, user_id)
            if not institution:
                return False
            
            await self.db.delete(institution)
            await self.db.commit()
            
            logger.info(f"Removed institution {institution_id} for user {user_id}")
            return True
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error removing institution: {str(e)}")
            raise
    
    async def _sync_transactions(self, institution: Institution, user_id: UUID) -> int:
        """Sync transactions for an institution using cursor-based pagination."""
        try:
            from app.services.transaction_service import TransactionService
            transaction_service = TransactionService(self.db)
            
            access_token = decrypt_data(institution.plaid_access_token)
            transactions_added = 0
            has_more = True
            cursor = institution.sync_cursor
            
            while has_more:
                # For initial sync, don't pass cursor parameter
                if cursor:
                    request = TransactionsSyncRequest(
                        access_token=access_token,
                        cursor=cursor
                    )
                else:
                    request = TransactionsSyncRequest(
                        access_token=access_token
                    )
                
                response = self.client.transactions_sync(request)
                
                # Log what we received from Plaid
                added_count = len(response['added'])
                modified_count = len(response['modified'])
                removed_count = len(response['removed'])
                logger.info(f"Plaid sync response: {added_count} added, {modified_count} modified, {removed_count} removed, has_more={response['has_more']}")
                
                # Process added transactions
                for tx_data in response['added']:
                    # Check if transaction already exists
                    result = await self.db.execute(
                        select(Transaction).where(
                            Transaction.plaid_transaction_id == tx_data['transaction_id']
                        )
                    )
                    existing = result.scalar_one_or_none()
                    
                    if not existing:
                        # Get account
                        acc_result = await self.db.execute(
                            select(Account).where(
                                Account.plaid_account_id == tx_data['account_id']
                            )
                        )
                        account = acc_result.scalar_one_or_none()
                        
                        if account:
                            await transaction_service.create_transaction(
                                user_id=user_id,
                                account_id=account.id,
                                plaid_data=tx_data
                            )
                            transactions_added += 1
                
                # Process modified transactions
                for tx_data in response['modified']:
                    result = await self.db.execute(
                        select(Transaction).where(
                            Transaction.plaid_transaction_id == tx_data['transaction_id']
                        )
                    )
                    transaction = result.scalar_one_or_none()
                    
                    if transaction:
                        # Update transaction details
                        transaction.amount = abs(tx_data['amount'])
                        transaction.name = tx_data['name']
                        transaction.merchant_name = tx_data.get('merchant_name')
                        transaction.date = datetime.strptime(tx_data['date'], '%Y-%m-%d').date()
                
                # Process removed transactions  
                for tx_data in response['removed']:
                    result = await self.db.execute(
                        select(Transaction).where(
                            Transaction.plaid_transaction_id == tx_data['transaction_id']
                        )
                    )
                    transaction = result.scalar_one_or_none()
                    
                    if transaction:
                        await self.db.delete(transaction)
                
                # Update cursor
                cursor = response['next_cursor']
                has_more = response['has_more']
            
            # Save cursor for next sync
            institution.sync_cursor = cursor
            
            return transactions_added
            
        except Exception as e:
            logger.error(f"Error syncing transactions: {str(e)}")
            return 0
