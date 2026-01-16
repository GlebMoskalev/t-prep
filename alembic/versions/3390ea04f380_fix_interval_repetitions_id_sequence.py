"""fix interval_repetitions id sequence

Revision ID: 3390ea04f380
Revises: 813a303e18fb
Create Date: 2026-01-16 10:01:38.811763

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3390ea04f380'
down_revision = '813a303e18fb'
branch_labels = None
depends_on = None


def upgrade():
    # Исправляем таблицу
    op.execute("""
        -- Удаляем старую колонку id
        ALTER TABLE interval_repetitions DROP COLUMN id;
        
        -- Добавляем новую с автоинкрементом
        ALTER TABLE interval_repetitions ADD COLUMN id SERIAL PRIMARY KEY;
    """)
    
    # ИЛИ более безопасный вариант:
    # op.execute("""
    #     -- Убедимся, что последовательность существует
    #     CREATE SEQUENCE IF NOT EXISTS interval_repetitions_id_seq;
    #     
    #     -- Устанавливаем значение по умолчанию
    #     ALTER TABLE interval_repetitions 
    #     ALTER COLUMN id 
    #     SET DEFAULT nextval('interval_repetitions_id_seq');
    #     
    #     -- Связываем последовательность с колонкой
    #     ALTER SEQUENCE interval_repetitions_id_seq 
    #     OWNED BY interval_repetitions.id;
    # """)

def downgrade():
    # Возвращаем как было (если нужно откатить)
    op.execute("""
        ALTER TABLE interval_repetitions DROP COLUMN id;
        ALTER TABLE interval_repetitions ADD COLUMN id INTEGER PRIMARY KEY;
    """)
