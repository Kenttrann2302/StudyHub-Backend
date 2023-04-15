"""new migration

Revision ID: 64743d652f5b
Revises: faeecb90756e
Create Date: 2023-04-14 10:19:33.196447

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '64743d652f5b'
down_revision = 'faeecb90756e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_information', schema=None) as batch_op:
        batch_op.add_column(sa.Column('education_degrees', sa.Enum('--select--', "Associate's Degree", "Bachelor's Degree", "Master's Degree", 'Doctoral Degree', 'Professional Degree', name='degree_levels'), nullable=False))
        batch_op.drop_column('education_degree')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_information', schema=None) as batch_op:
        batch_op.add_column(sa.Column('education_degree', postgresql.ENUM('--select--', "Associate's Degree", "Bachelor's Degree", "Master's Degree", 'Doctoral Degree', 'Professional Degree', name='degree_levels'), autoincrement=False, nullable=False))
        batch_op.drop_column('education_degrees')

    # ### end Alembic commands ###
