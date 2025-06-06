"""Add pdf_path field to Manifiesto

Revision ID: a280684e68f3
Revises: 
Create Date: 2025-06-02 11:19:12.422561

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a280684e68f3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('MANIFIESTOS', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pdf_path', sa.String(length=255), nullable=True))
        batch_op.alter_column('id',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.alter_column('numero',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('placa',
               existing_type=sa.VARCHAR(length=10),
               type_=sa.String(length=20),
               nullable=True)
        batch_op.alter_column('conductor',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('origen',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('destino',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('fecha',
               existing_type=sa.DATE(),
               nullable=True)
        batch_op.alter_column('mes',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('kof1',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('remesa',
               existing_type=sa.VARCHAR(length=20),
               nullable=True)
        batch_op.alter_column('empresa',
               existing_type=sa.VARCHAR(length=100),
               nullable=True)
        batch_op.alter_column('valor_flete',
               existing_type=sa.INTEGER(),
               type_=sa.Float(),
               nullable=True)

    with op.batch_alter_table('Tractocamion', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['PLACA'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Tractocamion', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('MANIFIESTOS', schema=None) as batch_op:
        batch_op.alter_column('valor_flete',
               existing_type=sa.Float(),
               type_=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('empresa',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('remesa',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('kof1',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('mes',
               existing_type=sa.VARCHAR(length=20),
               nullable=False)
        batch_op.alter_column('fecha',
               existing_type=sa.DATE(),
               nullable=False)
        batch_op.alter_column('destino',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('origen',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('conductor',
               existing_type=sa.VARCHAR(length=100),
               nullable=False)
        batch_op.alter_column('placa',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=10),
               nullable=False)
        batch_op.alter_column('numero',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('id',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
        batch_op.drop_column('pdf_path')

    # ### end Alembic commands ###
