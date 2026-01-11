import os
import tempfile

from hypothesis import given, strategies as st, assume

from src.skills.skill import Skill
from src.skills.skills_loader import SkillsLoader


class TestSkillLoader:

    @given(
        skill_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'),
            min_size=1, 
            max_size=50
        ).filter(lambda x: x.strip() == x and len(x.strip()) > 0),
        skills_content=st.text(min_size=0, max_size=1000),
        resources_content=st.text(min_size=0, max_size=1000)
    )
    def test_complete_skill_loading(self, skill_name, skills_content, resources_content):
        assume(skill_name.strip() != "")
        assume(not skill_name.endswith('.'))
        assume(skill_name not in ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'])

        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = os.path.join(temp_dir, skill_name)
            os.makedirs(skill_dir)

            skills_file = os.path.join(skill_dir, "SKILLS.md")
            with open(skills_file, 'w', encoding='utf-8') as f:
                f.write(skills_content)

            resources_file = os.path.join(skill_dir, "RESOURCES.md")
            with open(resources_file, 'w', encoding='utf-8') as f:
                f.write(resources_content)

            loaded_skill = SkillsLoader.load_skill_from_directory(skill_dir)

            assert loaded_skill is not None
            assert isinstance(loaded_skill, Skill)

            assert loaded_skill.name == skill_name
            expected_skills_content = skills_content.replace('\r\n', '\n').replace('\r', '\n')
            expected_resources_content = resources_content.replace('\r\n', '\n').replace('\r', '\n')
            assert loaded_skill.skills_content == expected_skills_content
            assert loaded_skill.resources_content == expected_resources_content

    @given(
        skill_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'),
            min_size=1, 
            max_size=50
        ).filter(lambda x: x.strip() == x and len(x.strip()) > 0),
        skills_content=st.text(min_size=0, max_size=1000)
    )
    def test_missing_resources_file_handling(self, skill_name, skills_content):
        assume(skill_name.strip() != "")
        assume(not skill_name.endswith('.'))
        assume(skill_name not in ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'])

        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = os.path.join(temp_dir, skill_name)
            os.makedirs(skill_dir)

            skills_file = os.path.join(skill_dir, "SKILLS.md")
            with open(skills_file, 'w', encoding='utf-8') as f:
                f.write(skills_content)

            loaded_skill = SkillsLoader.load_skill_from_directory(skill_dir)

            assert loaded_skill is None

    @given(
        skill_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'),
            min_size=1, 
            max_size=50
        ).filter(lambda x: x.strip() == x and len(x.strip()) > 0),
        resources_content=st.text(min_size=0, max_size=1000)
    )
    def test_missing_skills_file_handling(self, skill_name, resources_content):
        assume(skill_name.strip() != "")
        assume(not skill_name.endswith('.'))
        assume(skill_name not in ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'])

        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = os.path.join(temp_dir, skill_name)
            os.makedirs(skill_dir)

            resources_file = os.path.join(skill_dir, "RESOURCES.md")
            with open(resources_file, 'w', encoding='utf-8') as f:
                f.write(resources_content)

            loaded_skill = SkillsLoader.load_skill_from_directory(skill_dir)

            assert loaded_skill is None

    @given(
        invalid_path=st.text(min_size=1, max_size=100)
    )
    def test_error_handling_for_invalid_skills(self, invalid_path):
        loaded_skill = SkillsLoader.load_skill_from_directory(invalid_path)

        assert loaded_skill is None

    def test_error_handling_for_non_directory_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "not_a_directory.txt")
            with open(file_path, 'w') as f:
                f.write("This is a file, not a directory")

            loaded_skill = SkillsLoader.load_skill_from_directory(file_path)

            assert loaded_skill is None

    @given(
        skill_name=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='_-'),
            min_size=1, 
            max_size=50
        ).filter(lambda x: x.strip() == x and len(x.strip()) > 0)
    )
    def test_error_handling_for_empty_directory(self, skill_name):
        assume(skill_name.strip() != "")
        assume(not skill_name.endswith('.'))
        assume(skill_name not in ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'])

        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = os.path.join(temp_dir, skill_name)
            os.makedirs(skill_dir)

            loaded_skill = SkillsLoader.load_skill_from_directory(skill_dir)

            assert loaded_skill is None
