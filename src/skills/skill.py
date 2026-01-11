class Skill:

    def __init__(self, name: str, skills_content: str, resources_content: str):
        self._name = name
        self._skills_content = skills_content
        self._resources_content = resources_content

    @property
    def name(self) -> str:
        return self._name

    @property
    def skills_content(self) -> str:
        return self._skills_content

    @property
    def resources_content(self) -> str:
        return self._resources_content

    def __eq__(self, other) -> bool:
        if not isinstance(other, Skill):
            return False
        return (self.name == other.name and 
                self.skills_content == other.skills_content and
                self.resources_content == other.resources_content)

    def __repr__(self) -> str:
        return (f"Skill: '{self.name}\n')"
                f"# Content\n"
                f"{self._skills_content}")