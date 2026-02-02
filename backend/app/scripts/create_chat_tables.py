"""
Create chat tables manually.
"""
import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def create_tables():
    async with AsyncSessionLocal() as db:
        # Check if conversations table exists
        result = await db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'conversations'
            );
        """))
        exists = result.scalar()
        
        if not exists:
            # Create conversations table
            await db.execute(text("""
                CREATE TABLE conversations (
                    id UUID PRIMARY KEY,
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    title VARCHAR(255),
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """))
            await db.execute(text("""
                CREATE INDEX ix_conversations_user_id ON conversations(user_id);
            """))
            await db.execute(text("""
                CREATE INDEX ix_conversations_updated_at ON conversations(updated_at);
            """))
            
            # Create messages table
            await db.execute(text("""
                CREATE TABLE messages (
                    id UUID PRIMARY KEY,
                    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    tools_used JSONB,
                    tool_results JSONB,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW()
                );
            """))
            await db.execute(text("""
                CREATE INDEX ix_messages_conversation_id ON messages(conversation_id);
            """))
            await db.execute(text("""
                CREATE INDEX ix_messages_created_at ON messages(created_at);
            """))
            
            await db.commit()
            print('✅ Chat tables created successfully')
        else:
            print('ℹ️  Chat tables already exist')


if __name__ == "__main__":
    asyncio.run(create_tables())
