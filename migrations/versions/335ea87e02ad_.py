"""empty message

Revision ID: 335ea87e02ad
Revises: 00088b24b798
Create Date: 2023-04-07 22:46:04.840815

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '335ea87e02ad'
down_revision = '00088b24b798'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('collaboration')
    op.drop_table('study_methodology')
    op.drop_table('institutions')
    op.drop_table('study_techniques')
    op.drop_table('study_session')
    op.drop_table('gender')
    op.drop_table('majors')
    op.drop_table('identification')
    op.drop_table('verification_methods')
    op.drop_table('study_materials')
    op.drop_table('degree')
    op.drop_table('learning_styles')
    op.drop_table('education')
    op.drop_table('users_information')
    op.drop_table('study_time')
    op.drop_table('study_location')
    op.drop_table('study_environment')
    with op.batch_alter_table('availability_schedule', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['id'])

    with op.batch_alter_table('permission', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['id'])

    with op.batch_alter_table('study_preferences', schema=None) as batch_op:
        batch_op.add_column(sa.Column('study_env_prefereces', sa.Enum('Quiet study areas', 'Group study areas', 'Library', 'Coffee shop', 'Home', 'Outdoors', 'Study room', 'Computer Lab', 'Classroom', 'Open space', 'Private space', 'No preference', name='list_study_env'), nullable=False))
        batch_op.add_column(sa.Column('study_time_preferences', sa.Enum('Early morning-(5am-8am)', 'Morning-(8am-12pm)', 'Afternoon-(12pm-4pm)', 'Evening-(4pm-8pm)', 'Late night-(8pm-12am)', 'All night-(12am-5am)', 'Weekday mornings-(Mon-Fri, 8am-12pm)', 'Weekday afternoons-(Mon-Fri, 12pm-5pm)', 'Weekday evening-(Mon-Fri, 5pm-10pm)', 'Weekend mornings-(Sat-Sun, 8am-12pm)', 'Weekend afternoons-(Sat-Sun, 12pm-5pm)', 'Weekend evenings-(Sat-Sun, 5pm-10pm)', name='list_study_time'), nullable=False))
        batch_op.add_column(sa.Column('time_management_preferences', sa.Enum('Pomodoro technique-A time management method that involves breaking down work into intervals (typically 25 minutes) separated by short breaks', 'Eisenhower Matrix-A method of prioritizing tasks based on their importance and urgency', 'Time blocking-A method of scheduling where you block off specific periods of time for different tasks.', name='list_time_management_methods'), nullable=False))
        batch_op.add_column(sa.Column('study_techniques_preferences', sa.Enum('The Feynman Technique-A method of learning and retaining information by explaining it in simple terms.', 'The Cornell Method-A note-taking method that involves dividing a page into sections for notes, cues, and a summary.', 'SQ3R Method-A method of studying that involves Surveying, Questioning, Reading, Reciting and Reviewing.', 'Mind Mapping-A visual method of organizing information by connecting ideas with branches and sub-branches.', 'Flashcards-A method of studying that involves creating cards with information on them and reviewing them.', 'Active Recall-A method of studying that involves actively trying to remember information.', 'Spaced Repetition-A method of studying that involves reviewing information at increasing intervals to improve retention.', 'The Leitner System-A method of spaced repetition that involves sorting flashcards into different boxes based on how well you know the information.', 'Mnemonics-Memory aids that help you remember information by associating it with something else.', 'Visualization-A technique of creating mental images to help remember information', 'Elaborative Interrogation-A technique of generating explanations for why facts are true to help remember them.', 'Interleaving-A method of studying that involves switching between different topics or types of problems to improve retention', 'Deliberate Practice-A method of practicing that involves setting specific goals and focusing on improving weaknesses.', 'Retrieval Practice-A method of studying that involves actively trying to recall information from memory.', name='list_study_techniques'), nullable=False))
        batch_op.add_column(sa.Column('courses_preferences', sa.ARRAY(sa.String(length=10), dimensions=5), nullable=False))
        batch_op.add_column(sa.Column('communication_prefereces', sa.Enum('Facebook', 'Twitter', 'Instagram', 'LinkedIn', 'Snapchat', 'TikTok', 'WhatsApp', 'WeChat', 'Skype', 'Slack', 'Discord', 'Reddit', 'Pinterest', 'Tumblr', 'YouTube', 'Vimeo', 'Twitch', 'Clubhouse', 'Zoom', 'Microsoft Teams', name='list_social_media'), nullable=False))
        batch_op.create_unique_constraint(None, ['id'])
        batch_op.drop_constraint('study_preferences_study_methodology_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_learning_styles_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_study_material_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_study_env_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_study_session_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_study_loc_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_user_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_collaboration_styles_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_study_techniques_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('study_preferences_study_time_frame_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user_information', ['user_id'], ['id'])
        batch_op.drop_column('study_loc_id')
        batch_op.drop_column('collaboration_styles_id')
        batch_op.drop_column('study_time_frame_id')
        batch_op.drop_column('collaboration_number')
        batch_op.drop_column('learning_styles_id')
        batch_op.drop_column('study_material_id')
        batch_op.drop_column('study_motivation')
        batch_op.drop_column('study_session_id')
        batch_op.drop_column('study_methodology_id')
        batch_op.drop_column('study_env_id')
        batch_op.drop_column('collaboration_chosen')
        batch_op.drop_column('study_techniques_id')

    with op.batch_alter_table('user_information', schema=None) as batch_op:
        batch_op.create_unique_constraint(None, ['id'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verification', sa.String(length=500), nullable=False))
        batch_op.alter_column('verification_method',
               existing_type=sa.VARCHAR(length=500),
               type_=sa.Enum('--select--', 'Email', 'Phone number', 'Device Push Notification', name='verification_options'),
               existing_nullable=False)
        batch_op.drop_constraint('users_aws_token_key', type_='unique')
        batch_op.drop_constraint('users_verification_method_key', type_='unique')
        batch_op.create_unique_constraint(None, ['user_id'])
        batch_op.drop_constraint('users_verification_id_fkey', type_='foreignkey')
        batch_op.drop_column('aws_token')
        batch_op.drop_column('verification_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('verification_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('aws_token', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
        batch_op.create_foreign_key('users_verification_id_fkey', 'verification_methods', ['verification_id'], ['id'])
        batch_op.drop_constraint(None, type_='unique')
        batch_op.create_unique_constraint('users_verification_method_key', ['verification_method'])
        batch_op.create_unique_constraint('users_aws_token_key', ['aws_token'])
        batch_op.alter_column('verification_method',
               existing_type=sa.Enum('--select--', 'Email', 'Phone number', 'Device Push Notification', name='verification_options'),
               type_=sa.VARCHAR(length=500),
               existing_nullable=False)
        batch_op.drop_column('verification')

    with op.batch_alter_table('user_information', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('study_preferences', schema=None) as batch_op:
        batch_op.add_column(sa.Column('study_techniques_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('collaboration_chosen', sa.BOOLEAN(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('study_env_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('study_methodology_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('study_session_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('study_motivation', sa.TEXT(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('study_material_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('learning_styles_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('collaboration_number', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('study_time_frame_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('collaboration_styles_id', sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('study_loc_id', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('study_preferences_study_time_frame_id_fkey', 'study_time', ['study_time_frame_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_study_techniques_id_fkey', 'study_techniques', ['study_techniques_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_collaboration_styles_id_fkey', 'collaboration', ['collaboration_styles_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_user_id_fkey', 'users_information', ['user_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_study_loc_id_fkey', 'study_location', ['study_loc_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_study_session_id_fkey', 'study_session', ['study_session_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_study_env_id_fkey', 'study_environment', ['study_env_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_study_material_id_fkey', 'study_materials', ['study_material_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_learning_styles_id_fkey', 'learning_styles', ['learning_styles_id'], ['id'])
        batch_op.create_foreign_key('study_preferences_study_methodology_id_fkey', 'study_methodology', ['study_methodology_id'], ['id'])
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('communication_prefereces')
        batch_op.drop_column('courses_preferences')
        batch_op.drop_column('study_techniques_preferences')
        batch_op.drop_column('time_management_preferences')
        batch_op.drop_column('study_time_preferences')
        batch_op.drop_column('study_env_prefereces')

    with op.batch_alter_table('permission', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    with op.batch_alter_table('availability_schedule', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')

    op.create_table('study_environment',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('study_env_atm', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='study_environment_pkey')
    )
    op.create_table('study_location',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('study_env_loc', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='study_location_pkey')
    )
    op.create_table('study_time',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('study_time_frame', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='study_time_pkey')
    )
    op.create_table('users_information',
    sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('middle_name', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('last_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('age', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_of_birth', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('address_line_1', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('address_line_2', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('city', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('province', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('country', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('postal_code', sa.VARCHAR(length=10), autoincrement=False, nullable=False),
    sa.Column('timezone', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('religion', sa.VARCHAR(length=100), autoincrement=False, nullable=True),
    sa.Column('profile_picture', sa.VARCHAR(length=500), autoincrement=False, nullable=True),
    sa.Column('user_bio', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('interests', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('activity_status', sa.VARCHAR(length=20), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('user_id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('gender_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['gender_id'], ['gender.id'], name='users_information_gender_id_fkey'),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name='users_information_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='users_information_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('education',
    sa.Column('id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('profile_id', postgresql.UUID(), autoincrement=False, nullable=True),
    sa.Column('institution_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('start_date', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('graduation_date', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('identification_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('identification_material', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['identification_id'], ['identification.id'], name='education_identification_id_fkey'),
    sa.ForeignKeyConstraint(['institution_id'], ['institutions.id'], name='education_institution_id_fkey'),
    sa.ForeignKeyConstraint(['profile_id'], ['users_information.id'], name='education_profile_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='education_pkey'),
    sa.UniqueConstraint('profile_id', name='education_profile_id_key')
    )
    op.create_table('learning_styles',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('learning_styles', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='learning_styles_pkey')
    )
    op.create_table('degree',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('degree_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('degree_description', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='degree_pkey'),
    sa.UniqueConstraint('degree_description', name='degree_degree_description_key'),
    sa.UniqueConstraint('degree_name', name='degree_degree_name_key')
    )
    op.create_table('study_materials',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('study_materials_preference', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='study_materials_pkey')
    )
    op.create_table('verification_methods',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('verification_options', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='verification_methods_pkey'),
    sa.UniqueConstraint('verification_options', name='verification_methods_verification_options_key')
    )
    op.create_table('identification',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('identification_options', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='identification_pkey'),
    sa.UniqueConstraint('identification_options', name='identification_identification_options_key')
    )
    op.create_table('majors',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('majors_name', sa.VARCHAR(length=100), autoincrement=False, nullable=False),
    sa.Column('major_description', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='majors_pkey'),
    sa.UniqueConstraint('major_description', name='majors_major_description_key'),
    sa.UniqueConstraint('majors_name', name='majors_majors_name_key')
    )
    op.create_table('gender',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('gender_options', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='gender_pkey'),
    sa.UniqueConstraint('gender_options', name='gender_gender_options_key')
    )
    op.create_table('study_session',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('study_duration', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='study_session_pkey')
    )
    op.create_table('study_techniques',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('study_techniques', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='study_techniques_pkey')
    )
    op.create_table('institutions',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('university_options', sa.VARCHAR(length=200), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='institutions_pkey'),
    sa.UniqueConstraint('university_options', name='institutions_university_options_key')
    )
    op.create_table('study_methodology',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('study_methodology', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='study_methodology_pkey')
    )
    op.create_table('collaboration',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('collaboration_styles', sa.VARCHAR(length=500), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='collaboration_pkey')
    )
    # ### end Alembic commands ###
