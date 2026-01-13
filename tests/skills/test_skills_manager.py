import os
import shutil
import tempfile
from unittest.mock import patch

import pytest
from hypothesis import given, strategies as st, assume

from relay.skills.skills_manager import SkillsManager, ConfigurationError


class TestSkillManager:


    @given(
        skill_names=st.lists(
            st.text(
                alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')),
                min_size=1, 
                max_size=20
            ).filter(lambda x: x.strip() == x and len(x.strip()) > 0),
            min_size=0,
            max_size=5,
            unique=True
        )
    )
    def test_complete_skill_listing(self, skill_names):
        for name in skill_names:
            assume(not name.endswith('.'))
            assume(name not in ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 
                               'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 
                               'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'])

        with tempfile.TemporaryDirectory() as temp_dir:
            skills_dir = os.path.join(temp_dir, "skills")
            os.makedirs(skills_dir)

            for skill_name in skill_names:
                skill_dir = os.path.join(skills_dir, skill_name)
                os.makedirs(skill_dir)

                with open(os.path.join(skill_dir, "SKILLS.md"), 'w', encoding='utf-8') as f:
                    f.write(f"Skills content for {skill_name}")

                with open(os.path.join(skill_dir, "RESOURCES.md"), 'w', encoding='utf-8') as f:
                    f.write(f"Resources content for {skill_name}")

            skills_manager = SkillsManager(skills_dir)
            skills_manager.load_skills()

            listed_skills = skills_manager.list_skills()

            assert isinstance(listed_skills, list)
            assert len(listed_skills) == len(skill_names)
            assert set(listed_skills) == set(skill_names)

            assert len(listed_skills) == len(set(listed_skills))

            for skill_name in listed_skills:
                assert skills_manager.get_skill(skill_name) is not None

    def test_skill_listing_empty_registry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_dir = os.path.join(temp_dir, "empty_skills")
            os.makedirs(skills_dir)

            skills_manager = SkillsManager(skills_dir)
            skills_manager.load_skills()

            listed_skills = skills_manager.list_skills()
            assert isinstance(listed_skills, list)
            assert len(listed_skills) == 0


    @given(
        num_directories=st.integers(min_value=2, max_value=3),
        skills_per_dir=st.lists(
            st.lists(
                st.text(
                    alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')),
                    min_size=1, 
                    max_size=15
                ).filter(lambda x: x.strip() == x and len(x.strip()) > 0),
                min_size=1,
                max_size=2,
                unique=True
            ),
            min_size=2,
            max_size=3
        )
    )
    def test_skill_listing_multiple_directories(self, num_directories, skills_per_dir):
        assume(len(skills_per_dir) >= num_directories)
        skills_per_dir = skills_per_dir[:num_directories]

        all_skills = [skill for skills in skills_per_dir for skill in skills]
        for name in all_skills:
            assume(not name.endswith('.'))
            assume(name not in ['con', 'prn', 'aux', 'nul', 'com1', 'com2', 'com3', 'com4', 'com5', 
                               'com6', 'com7', 'com8', 'com9', 'lpt1', 'lpt2', 'lpt3', 'lpt4', 
                               'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9'])

        with tempfile.TemporaryDirectory() as temp_dir:
            skills_dirs = []
            expected_skills = set()

            for i in range(num_directories):
                skills_dir = os.path.join(temp_dir, f"skills_dir_{i}")
                os.makedirs(skills_dir)
                skills_dirs.append(skills_dir)

                for skill_name in skills_per_dir[i]:
                    skill_dir = os.path.join(skills_dir, skill_name)
                    os.makedirs(skill_dir)

                    with open(os.path.join(skill_dir, "SKILLS.md"), 'w', encoding='utf-8') as f:
                        f.write(f"Skills content for {skill_name} from dir {i}")

                    with open(os.path.join(skill_dir, "RESOURCES.md"), 'w', encoding='utf-8') as f:
                        f.write(f"Resources content for {skill_name} from dir {i}")

                    if skill_name not in expected_skills:
                        expected_skills.add(skill_name)

            skills_manager = SkillsManager(skills_dirs)
            skills_manager.load_skills()

            listed_skills = skills_manager.list_skills()

            assert isinstance(listed_skills, list)
            assert len(listed_skills) == len(expected_skills)
            assert set(listed_skills) == expected_skills



    @given(
        num_directories=st.integers(min_value=1, max_value=5)
    )
    def test_configuration_handling_multiple_directories(self, num_directories):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory_paths = []
            for i in range(num_directories):
                dir_path = os.path.join(temp_dir, f"skills_dir_{i}")
                os.makedirs(dir_path, exist_ok=True)
                directory_paths.append(dir_path)

            skills_manager = SkillsManager(directory_paths)

            assert len(skills_manager.skills_dirs) == num_directories
            for dir_path in directory_paths:
                assert dir_path in skills_manager.skills_dirs

            assert isinstance(skills_manager.skills_registry, dict)
            assert len(skills_manager.skills_registry) == 0


    @given(
        invalid_input=st.one_of(
            st.integers(),
            st.floats(),
            st.booleans(),
            st.dictionaries(st.text(), st.text()),
            st.none()
        ).filter(lambda x: x is not None)
    )
    def test_configuration_error_for_invalid_types(self, invalid_input):
        with pytest.raises(ConfigurationError) as exc_info:
            SkillsManager(invalid_input)

        assert "must be a string or list of strings" in str(exc_info.value)

    def test_configuration_error_for_existing_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            with pytest.raises(ConfigurationError) as exc_info:
                SkillsManager(temp_file_path)

            assert "is not a directory" in str(exc_info.value)
        finally:
            os.unlink(temp_file_path)

    @given(
        mixed_list=st.lists(
            st.one_of(
                st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),  # Only non-whitespace strings
                st.integers(),
                st.floats(),
                st.booleans()
            ),
            min_size=1,
            max_size=5
        ).filter(lambda x: not all(isinstance(item, str) for item in x))
    )
    def test_configuration_error_for_mixed_type_list(self, mixed_list):
        with pytest.raises(ConfigurationError) as exc_info:
            SkillsManager(mixed_list)

        assert "must be strings" in str(exc_info.value)

    def test_load_skills_from_nonexistent_directory(self):
        nonexistent_path = "/this/path/definitely/does/not/exist/12345"
        skills_manager = SkillsManager(nonexistent_path)

        skills_manager.load_skills()

        assert len(skills_manager.skills_registry) == 0



class TestSkillsManagerIntegration:

    def setup_method(self):
        self.temp_dir = tempfile.mkdtemp()
        self.skills_dir = os.path.join(self.temp_dir, "skills")
        os.makedirs(self.skills_dir)

    def teardown_method(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def _create_skill_directory(self, skill_name: str, skills_content: str = "# Skills",
                                resources_content: str = "# Resources") -> str:
        skill_path = os.path.join(self.skills_dir, skill_name)
        os.makedirs(skill_path)

        with open(os.path.join(skill_path, "SKILLS.md"), 'w') as f:
            f.write(skills_content)

        with open(os.path.join(skill_path, "RESOURCES.md"), 'w') as f:
            f.write(resources_content)

        return skill_path

    def test_end_to_end_skill_loading_and_retrieval(self):
        self._create_skill_directory("skill1", "# Skill 1 Content", "# Resources 1")
        self._create_skill_directory("skill2", "# Skill 2 Content", "# Resources 2")
        self._create_skill_directory("skill3", "# Skill 3 Content", "# Resources 3")

        manager = SkillsManager(self.skills_dir)
        manager.load_skills()

        skill1 = manager.get_skill("skill1")
        assert skill1 is not None
        assert skill1.name == "skill1"
        assert skill1.skills_content == "# Skill 1 Content"
        assert skill1.resources_content == "# Resources 1"

        skills = manager.list_skills()
        assert len(skills) == 3
        assert "skill1" in skills
        assert "skill2" in skills
        assert "skill3" in skills
        assert skills == sorted(skills)

    def test_error_scenario_missing_files(self):
        skill1_path = os.path.join(self.skills_dir, "skill1")
        os.makedirs(skill1_path)
        with open(os.path.join(skill1_path, "SKILLS.md"), 'w') as f:
            f.write("# Skills content")

        skill2_path = os.path.join(self.skills_dir, "skill2")
        os.makedirs(skill2_path)
        with open(os.path.join(skill2_path, "RESOURCES.md"), 'w') as f:
            f.write("# Resources content")

        self._create_skill_directory("skill3", "# Valid skill", "# Valid resources")

        manager = SkillsManager(self.skills_dir)
        manager.load_skills()

        skill3 = manager.get_skill("skill3")
        assert skill3 is not None
        assert skill3.name == "skill3"

    def test_error_scenario_permission_denied(self):
        self._create_skill_directory("skill1", "# Content", "# Resources")

        with patch('os.listdir', side_effect=PermissionError("Permission denied")):
            manager = SkillsManager(self.skills_dir)
            manager.load_skills()

            assert len(manager.list_skills()) == 0

    def test_error_scenario_malformed_files(self):
        skill_path = os.path.join(self.skills_dir, "skill1")
        os.makedirs(skill_path)

        skills_file = os.path.join(skill_path, "SKILLS.md")
        resources_file = os.path.join(skill_path, "RESOURCES.md")

        with open(skills_file, 'w') as f:
            f.write("# Skills content")
        with open(resources_file, 'w') as f:
            f.write("# Resources content")

        original_open = open
        def mock_open(*args, **kwargs):
            if args[0] == skills_file:
                raise UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")
            return original_open(*args, **kwargs)

        with patch('builtins.open', side_effect=mock_open):
            manager = SkillsManager(self.skills_dir)
            manager.load_skills()

            assert len(manager.list_skills()) == 0

    def test_multiple_directories_integration(self):
        skills_dir2 = os.path.join(self.temp_dir, "skills2")
        os.makedirs(skills_dir2)

        self._create_skill_directory("skill1", "# Skill 1", "# Resources 1")

        skill2_path = os.path.join(skills_dir2, "skill2")
        os.makedirs(skill2_path)
        with open(os.path.join(skill2_path, "SKILLS.md"), 'w') as f:
            f.write("# Skill 2")
        with open(os.path.join(skill2_path, "RESOURCES.md"), 'w') as f:
            f.write("# Resources 2")

        manager = SkillsManager([self.skills_dir, skills_dir2])
        manager.load_skills()

        skills = manager.list_skills()
        assert "skill1" in skills
        assert "skill2" in skills

    def test_duplicate_skill_names_across_directories(self):
        skills_dir2 = os.path.join(self.temp_dir, "skills2")
        os.makedirs(skills_dir2)

        self._create_skill_directory("duplicate_skill", "# First version", "# First resources")

        skill2_path = os.path.join(skills_dir2, "duplicate_skill")
        os.makedirs(skill2_path)
        with open(os.path.join(skill2_path, "SKILLS.md"), 'w') as f:
            f.write("# Second version")
        with open(os.path.join(skill2_path, "RESOURCES.md"), 'w') as f:
            f.write("# Second resources")

        manager = SkillsManager([self.skills_dir, skills_dir2])
        manager.load_skills()

        skill = manager.get_skill("duplicate_skill")
        assert skill is not None
        assert skill.skills_content == "# First version"
        assert skill.resources_content == "# First resources"

    def test_configuration_error_scenarios(self):
        with pytest.raises(ConfigurationError, match="cannot be empty"):
            SkillsManager("")

        with pytest.raises(ConfigurationError, match="cannot be empty"):
            SkillsManager("   ")

        with pytest.raises(ConfigurationError, match="cannot be empty"):
            SkillsManager([])

        with pytest.raises(ConfigurationError, match="must be strings"):
            SkillsManager([self.skills_dir, 123])

        file_path = os.path.join(self.temp_dir, "not_a_directory.txt")
        with open(file_path, 'w') as f:
            f.write("test")

        with pytest.raises(ConfigurationError, match="not a directory"):
            SkillsManager(file_path)

    def test_api_error_scenarios(self):
        manager = SkillsManager(self.skills_dir)

        with pytest.raises(ValueError, match="cannot be None"):
            manager.get_skill(None)

        with pytest.raises(ValueError, match="must be a string"):
            manager.get_skill(123)

        with pytest.raises(ValueError, match="cannot be empty"):
            manager.get_skill("")

        with pytest.raises(ValueError, match="cannot be empty"):
            manager.get_skill("   ")

    def test_empty_and_whitespace_files(self):
        skill_path = os.path.join(self.skills_dir, "empty_skill")
        os.makedirs(skill_path)

        with open(os.path.join(skill_path, "SKILLS.md"), 'w') as f:
            f.write("")

        with open(os.path.join(skill_path, "RESOURCES.md"), 'w') as f:
            f.write("   \n\t  \n   ")

        self._create_skill_directory("normal_skill", "# Normal", "# Normal resources")

        manager = SkillsManager(self.skills_dir)
        manager.load_skills()

        empty_skill = manager.get_skill("empty_skill")
        assert empty_skill is not None
        assert empty_skill.skills_content == ""
        assert empty_skill.resources_content == "   \n\t  \n   "

        normal_skill = manager.get_skill("normal_skill")
        assert normal_skill is not None
        assert normal_skill.skills_content == "# Normal"

    def test_hidden_directories_ignored(self):
        self._create_skill_directory("normal_skill", "# Normal", "# Resources")

        hidden_path = os.path.join(self.skills_dir, ".hidden_skill")
        os.makedirs(hidden_path)
        with open(os.path.join(hidden_path, "SKILLS.md"), 'w') as f:
            f.write("# Hidden skill")
        with open(os.path.join(hidden_path, "RESOURCES.md"), 'w') as f:
            f.write("# Hidden resources")

        manager = SkillsManager(self.skills_dir)
        manager.load_skills()

        assert len(manager.list_skills()) == 1

