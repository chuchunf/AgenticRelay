import os
from typing import Dict, List, Optional, Union

from relay.utils.logger import Logger
from relay.skills.skill import Skill
from relay.skills.skills_loader import SkillsLoader


class ConfigurationError(Exception):
    pass

class SkillsManager:

    def __init__(self, skills_dir: Union[str, List[str]] = None):
        self.logger = Logger(__name__)

        self._validate_and_set_skills_dirs(skills_dir)

        self.skills_registry: Dict[str, Skill] = {}
        self.logger.info(f"SkillsManager initialized with directories: {self.skills_dirs}")

        self.load_skills()
        self.logger.info(f"SkillsManager loaded skills {self.skills_registry.keys()}")

    def _validate_and_set_skills_dirs(self, skills_dir: Union[str, List[str]] = None) -> None:
        if skills_dir is None:
            self.skills_dirs = ["skills"]
        elif isinstance(skills_dir, str):
            if not skills_dir.strip():
                raise ConfigurationError("Skills directory path cannot be empty or whitespace")
            self.skills_dirs = [skills_dir.strip()]
        elif isinstance(skills_dir, list):
            if not skills_dir:
                raise ConfigurationError("Skills directory list cannot be empty")
            self.skills_dirs = []
            for directory in skills_dir:
                if not isinstance(directory, str):
                    raise ConfigurationError(f"All directory paths must be strings, got {type(directory)} for value: {directory}")
                if not directory.strip():
                    raise ConfigurationError("Skills directory path cannot be empty or whitespace")
                self.skills_dirs.append(directory.strip())
        else:
            raise ConfigurationError(f"skills_dir must be a string or list of strings, got {type(skills_dir)}")

        for directory in self.skills_dirs:
            self._validate_directory_path(directory)

    @staticmethod
    def _validate_directory_path(directory: str) -> None:
        if os.path.exists(directory):
            if not os.path.isdir(directory):
                raise ConfigurationError(
                    f"Skills directory path exists but is not a directory: {directory}. "
                    f"Please provide a valid directory path or remove the existing file."
                )
            if not os.access(directory, os.R_OK):
                raise ConfigurationError(
                    f"Skills directory is not readable: {directory}. "
                    f"Please check directory permissions."
                )
        else:
            parent_dir = os.path.dirname(os.path.abspath(directory))
            if parent_dir and os.path.exists(parent_dir) and not os.access(parent_dir, os.W_OK):
                raise ConfigurationError(
                    f"Cannot create skills directory {directory}: parent directory {parent_dir} is not writable. "
                    f"Please check directory permissions."
                )

    def load_skills(self) -> None:
        total_loaded = 0
        total_errors = 0

        for skills_dir in self.skills_dirs:
            try:
                loaded, errors = self._load_skills_from_directory(skills_dir)
                total_loaded += loaded
                total_errors += errors
            except Exception as e:
                self.logger.error(f"Critical error loading skills from {skills_dir}: {e}")
                total_errors += 1

        self.logger.info(f"Skills loading completed. Loaded: {total_loaded}, Errors: {total_errors}")

        if total_loaded == 0 and total_errors > 0:
            self.logger.warning("No skills were successfully loaded. Check directory configuration and file permissions.")

    def _load_skills_from_directory(self, skills_dir: str) -> tuple[int, int]:
        loaded_count = 0
        error_count = 0

        if not os.path.exists(skills_dir):
            self.logger.warning(f"Skills directory does not exist: {skills_dir}")
            return loaded_count, error_count

        try:
            self._validate_directory_path(skills_dir)
        except ConfigurationError as e:
            self.logger.error(f"Directory validation failed for {skills_dir}: {e}")
            return loaded_count, 1

        try:
            items = os.listdir(skills_dir)
            self.logger.debug(f"Found {len(items)} items in {skills_dir}")

            for item in items:
                skill_path = os.path.join(skills_dir, item)
                if os.path.isdir(skill_path):
                    try:
                        skill = SkillsLoader.load_skill_from_directory(skill_path)
                        if skill:
                            if skill.name in self.skills_registry:
                                self.logger.warning(f"Skill '{skill.name}' already exists, skipping duplicate from {skills_dir}")
                                error_count += 1
                            else:
                                self.skills_registry[skill.name] = skill
                                self.logger.info(f"Loaded skill: {skill.name} from {skills_dir}")
                                loaded_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        self.logger.error(f"Error loading skill from {skill_path}: {e}")
                        error_count += 1
                else:
                    self.logger.debug(f"Skipping non-directory item: {item}")

        except PermissionError:
            self.logger.error(f"Permission denied accessing skills directory: {skills_dir}")
            error_count += 1
        except OSError as e:
            self.logger.error(f"OS error accessing skills directory {skills_dir}: {e}")
            error_count += 1
        except Exception as e:
            self.logger.error(f"Unexpected error loading skills from {skills_dir}: {e}")
            error_count += 1

        return loaded_count, error_count

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        if skill_name is None:
            raise ValueError("Skill name cannot be None")
        if not isinstance(skill_name, str):
            raise ValueError(f"Skill name must be a string, got {type(skill_name)}")
        if not skill_name.strip():
            raise ValueError("Skill name cannot be empty or whitespace")

        skill_name = skill_name.strip()
        skill = self.skills_registry.get(skill_name)

        if skill:
            self.logger.debug(f"Retrieved skill: {skill_name}")
        else:
            raise ValueError(f"Skill {skill_name} could not be load")

        return skill

    def list_skills(self) -> List[str]:
        skill_names = sorted(self.skills_registry.keys())
        self.logger.debug(f"Listed {len(skill_names)} skills")
        return skill_names
