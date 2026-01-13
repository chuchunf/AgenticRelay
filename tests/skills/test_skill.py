from hypothesis import given, strategies as st

from relay.skills.skill import Skill


class TestSkill:

    @given(
        name=st.text(min_size=1, max_size=100),
        skills_content=st.text(min_size=0, max_size=1000),
        resources_content=st.text(min_size=0, max_size=1000)
    )
    def test_skill_parsing_consistency(self, name, skills_content, resources_content):
        skill = Skill(name, skills_content, resources_content)

        assert skill.name == name
        assert skill.skills_content == skills_content
        assert skill.resources_content == resources_content

        assert isinstance(skill.name, str)
        assert len(skill.name) > 0

        assert isinstance(skill.skills_content, str)
        assert isinstance(skill.resources_content, str)

    @given(
        name=st.text(min_size=1, max_size=100),
        skills_content=st.text(min_size=0, max_size=1000),
        resources_content=st.text(min_size=0, max_size=1000)
    )
    def test_skill_equality_consistency(self, name, skills_content, resources_content):
        skill1 = Skill(name, skills_content, resources_content)
        skill2 = Skill(name, skills_content, resources_content)

        assert skill1 == skill2
        assert skill1.name == skill2.name
        assert skill1.skills_content == skill2.skills_content
        assert skill1.resources_content == skill2.resources_content
