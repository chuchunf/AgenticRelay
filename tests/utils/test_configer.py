import os
from unittest.mock import patch, mock_open

import hypothesis.strategies as st
import pytest
from hypothesis import given, settings

from utils.configer import Configer


class TestCommonUtilitiesConfigurationManager:

    @settings(max_examples=100, deadline=None)
    @given(
        config_key=st.text(
            alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_',
            min_size=1,
            max_size=50
        ),
        config_value=st.one_of(
            st.text(min_size=0, max_size=100).filter(lambda x: '\x00' not in x),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans()
        )
    )
    def test_property_1_configuration_management_consistency(self, config_key, config_value):

        env_value = str(config_value)

        with patch.dict(os.environ, {config_key: env_value}):
            config_manager = Configer()
            retrieved_value = config_manager.get(config_key)

            expected_value = config_manager._convert_value(env_value)
            assert retrieved_value == expected_value

        with patch.dict(os.environ, {}, clear=True):
            config_manager = Configer()
            default_value = "test_default"
            retrieved_value = config_manager.get(config_key, default=default_value)
            assert retrieved_value == default_value

        with patch.dict(os.environ, {}, clear=True):
            config_manager = Configer()
            retrieved_value = config_manager.get(config_key)
            assert retrieved_value is None

    @settings(max_examples=100, deadline=None)
    @given(
        config_keys=st.lists(
            st.text(
                alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_',
                min_size=1,
                max_size=20
            ),
            min_size=1,
            max_size=10,
            unique=True
        )
    )
    def test_configuration_list_consistency(self, config_keys):
        env_dict = {key.upper(): f"value_{key}" for key in config_keys}

        with patch.dict(os.environ, env_dict):
            config_manager = Configer()
            available_keys = config_manager.list()

            for key in config_keys:
                assert key.upper() in available_keys

            assert available_keys == sorted(available_keys)

    def test_required_key_validation(self):
        with patch.dict(os.environ, {}, clear=True):
            config_manager = Configer()

            with pytest.raises(ValueError) as exc_info:
                config_manager.get("MISSING_REQUIRED_KEY", required=True)

            assert "Required configuration key 'MISSING_REQUIRED_KEY' not found" in str(exc_info.value)

    @settings(max_examples=100, deadline=None)
    @given(
        config_key=st.text(
            alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_',
            min_size=1,
            max_size=30
        ),
        env_value=st.one_of(
            st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters=['\x00'])).filter(lambda x: x.strip()),
            st.integers().map(str),
            st.floats(allow_nan=False, allow_infinity=False).map(str),
            st.sampled_from(['true', 'false', 'True', 'False', '1', '0'])
        ),
        config_file_value=st.one_of(
            st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_characters=['\x00', '\n', '\r'])).filter(lambda x: x.strip()),
            st.integers().map(str),
            st.floats(allow_nan=False, allow_infinity=False).map(str),
            st.sampled_from(['true', 'false', 'True', 'False', '1', '0'])
        ),
        default_value=st.one_of(
            st.text(min_size=1, max_size=50),
            st.integers(),
            st.floats(allow_nan=False, allow_infinity=False),
            st.booleans()
        )
    )
    def test_property_2_configuration_validation_and_hierarchy(self, config_key, env_value, config_file_value, default_value):

        env_file_content = f"{config_key}={config_file_value}\n"

        with patch("pathlib.Path.exists", return_value=True), \
                patch("builtins.open", mock_open(read_data=env_file_content)), \
                patch("dotenv.load_dotenv"), \
                patch.dict(os.environ, {config_key: env_value}):

            config_manager = Configer()
            retrieved_value = config_manager.get(config_key)
            expected_env_value = config_manager._convert_value(env_value)

            assert retrieved_value == expected_env_value

            assert type(retrieved_value) in [str, int, float, bool]

        with patch("pathlib.Path.exists", return_value=True), \
                patch("builtins.open", mock_open(read_data=env_file_content)), \
                patch("dotenv.load_dotenv"), \
                patch.dict(os.environ, {}, clear=True):

            config_manager = Configer()
            config_manager._defaults[config_key] = default_value

            retrieved_value = config_manager.get(config_key)
            expected_config_value = config_manager._convert_value(config_file_value.strip().strip('"').strip("'"))

            assert retrieved_value == expected_config_value

            assert type(retrieved_value) in [str, int, float, bool]

        with patch("pathlib.Path.exists", return_value=False), \
                patch.dict(os.environ, {}, clear=True):

            config_manager = Configer()
            config_manager._defaults[config_key] = default_value

            retrieved_value = config_manager.get(config_key)

            assert retrieved_value == default_value

        test_values = [env_value, config_file_value.strip()]
        for test_value in test_values:
            if not test_value:
                continue

            converted = config_manager._convert_value(test_value)

            assert type(converted) in [str, int, float, bool]

            if test_value.lower() in ('true', 'yes', '1', 'on'):
                assert converted is True
            elif test_value.lower() in ('false', 'no', '0', 'off'):
                assert converted is False

            try:
                if '.' in test_value:
                    expected_float = float(test_value)
                    if isinstance(converted, (int, float)):
                        assert abs(converted - expected_float) < 1e-10
                else:
                    expected_int = int(test_value)
                    if isinstance(converted, int):
                        assert converted == expected_int
            except ValueError:
                if not isinstance(converted, bool):
                    assert isinstance(converted, str)

    def test_dotenv_file_loading(self):
        env_content = "TEST_KEY=test_value\nANOTHER_KEY=another_value\n"

        with patch("pathlib.Path.exists", return_value=True), \
                patch("builtins.open", mock_open(read_data=env_content)), \
                patch("utils.configer.load_dotenv") as mock_load_dotenv:

            config_manager = Configer()

            mock_load_dotenv.assert_called_once()
            call_args = mock_load_dotenv.call_args[0]
            assert len(call_args) == 1
            assert str(call_args[0]) == '.env'

            assert "TEST_KEY" in config_manager._config
            assert "ANOTHER_KEY" in config_manager._config
