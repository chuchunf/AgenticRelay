import os
from typing import Optional

from skill import Skill
from utils.logger import Logger


class SkillsLoader:

    @staticmethod
    def load_skill_from_directory(skill_path: str) -> Optional[Skill]:
        logger = Logger(__name__)

        if not skill_path:
            logger.error("Skill path cannot be empty")
            return None

        if not os.path.exists(skill_path):
            logger.error(f"Skill path does not exist: {skill_path}")
            return None

        if not os.path.isdir(skill_path):
            logger.error(f"Skill path is not a directory: {skill_path}")
            return None

        skill_name = os.path.basename(skill_path)
        if not skill_name or skill_name.startswith('.'):
            logger.debug(f"Skipping hidden or invalid directory: {skill_path}")
            return None

        skills_file = os.path.join(skill_path, "SKILLS.md")
        resources_file = os.path.join(skill_path, "RESOURCES.md")

        if not os.path.exists(skills_file):
            logger.error(f"Missing SKILLS.md file in skill directory: {skill_name}")
            return None
        skills_content = SkillsLoader._read_file_safely(skills_file)

        resources_content = SkillsLoader._read_file_safely(resources_file) if os.path.exists(resources_file) else ""

        if skills_content is None:
            logger.error(f"Failed to read SKILLS.md in skill directory: {skill_name}")
            return None

        if not skills_content.strip():
            logger.warning(f"SKILLS.md is empty or contains only whitespace in skill: {skill_name}")

        try:
            skill = Skill(skill_name, skills_content, resources_content)
            logger.debug(f"Successfully created skill object for: {skill_name}")
            return skill
        except Exception as e:
            logger.error(f"Error creating skill object for {skill_name}: {e}")
            return None

    @staticmethod
    def _read_file_safely(file_path: str) -> Optional[str]:
        logger = Logger(__name__)

        try:
            if not os.access(file_path, os.R_OK):
                logger.error(f"File is not readable: {file_path}")
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                logger.debug(f"Successfully read file: {file_path} ({len(content)} characters)")
                return content

        except FileNotFoundError:
            logger.error(f"File not found: {file_path}")
            return None
        except PermissionError:
            logger.error(f"Permission denied reading file: {file_path}")
            return None
        except UnicodeDecodeError as e:
            logger.error(f"Unicode decode error reading file {file_path}: {e}")
            return None
        except OSError as e:
            logger.error(f"OS error reading file {file_path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading file {file_path}: {e}")
            return None