"""update_models_for_interval_repetition

Revision ID: 001
Revises: 
Create Date: 2025-11-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Удаляем старые таблицы если они существуют (для чистой миграции)
    op.execute('DROP TABLE IF EXISTS interval_repetitions CASCADE')
    op.execute('DROP TABLE IF EXISTS cards CASCADE')
    op.execute('DROP TABLE IF EXISTS module_accesses CASCADE')
    op.execute('DROP TABLE IF EXISTS modules CASCADE')
    op.execute('DROP TABLE IF EXISTS users CASCADE')
    
    # Удаляем старые enum типы если они существуют
    op.execute('DROP TYPE IF EXISTS repetitionstate CASCADE')
    op.execute('DROP TYPE IF EXISTS accesslevel CASCADE')
    
    # Создаем таблицу users с новой структурой
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('oidc_sub', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_oidc_sub'), 'users', ['oidc_sub'], unique=True)
    
    # Создаем таблицу modules
    op.create_table('modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modules_id'), 'modules', ['id'], unique=False)
    
    # Создаем таблицу cards
    op.create_table('cards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cards_id'), 'cards', ['id'], unique=False)
    
    # Создаем таблицу interval_repetitions (enum создается автоматически)
    op.create_table('interval_repetitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('card_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('state', sa.Enum('Learning', 'Review', 'Relearning', name='repetitionstate'), nullable=False),
        sa.Column('step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('stability', sa.Float(), nullable=False, server_default='0.5'),
        sa.Column('difficulty', sa.Float(), nullable=False, server_default='0.3'),
        sa.Column('due', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_review', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['card_id'], ['cards.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interval_repetitions_id'), 'interval_repetitions', ['id'], unique=False)
    
    # Создаем таблицу module_accesses (enum создается автоматически)
    op.create_table('module_accesses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('view_access', sa.Enum('all_users', 'users_with_password', 'only_me', name='accesslevel'), nullable=False),
        sa.Column('edit_access', sa.Enum('all_users', 'users_with_password', 'only_me', name='accesslevel'), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['modules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_module_accesses_id'), 'module_accesses', ['id'], unique=False)


def downgrade() -> None:
    # Удаляем таблицы в обратном порядке
    op.drop_index(op.f('ix_module_accesses_id'), table_name='module_accesses')
    op.drop_table('module_accesses')
    
    op.drop_index(op.f('ix_interval_repetitions_id'), table_name='interval_repetitions')
    op.drop_table('interval_repetitions')
    
    op.drop_index(op.f('ix_cards_id'), table_name='cards')
    op.drop_table('cards')
    
    op.drop_index(op.f('ix_modules_id'), table_name='modules')
    op.drop_table('modules')
    
    op.drop_index(op.f('ix_users_oidc_sub'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Удаляем enums
    sa.Enum(name='accesslevel').drop(op.get_bind())
    sa.Enum(name='repetitionstate').drop(op.get_bind())

