#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2023 The Johns Hopkins University Applied Physics
# Laboratory LLC.
#
# This file is part of the Asynchronous Network Management System (ANMS).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This work was performed for the Jet Propulsion Laboratory, California
# Institute of Technology, sponsored by the United States Government under
# the prime contract 80NM0018D0004 between the Caltech and NASA under
# subcontract 1658085.
#
"""
Config Utils
Universal shared config that is used throughout the lifecycle of application.
"""

import inspect
import json
import logging
import os
import sys
import typing
from argparse import ArgumentParser
from enum import Enum
from importlib.util import find_spec
from pathlib import Path
from pprint import pformat

import six

# https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING
# Replace Class with the one you wish to get Typing Hints for when invoking ConfigBuilder...
if typing.TYPE_CHECKING:  # prevents cyclic issues
    from .config import BaseConfig as TypingConfig  # noqa: F401

# Expose Logging API
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
default_logger_name = __name__
default_log_handler = logging.StreamHandler(
    sys.stdout
)  # use logging.NullHandler if deployed as a library
default_log_handler.setFormatter(logging.Formatter("%(message)s"))
default_log_handler.setLevel(logging.INFO)


class AbstractConfig(object):
    """
    AbstractConfig.
    """

    # # # # Abstract Config - ONLY INHERIT - # # # #

    # Root of Project
    ROOT_DIR = os.path.normpath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
    )
    # Root of Python Module (may be the same as root of project)
    BASE_DIR = os.path.normpath(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
    )
    # File to look for at BASE_DIR location to load from
    BASE_CFG_FILE = "config.yaml"
    # Directory for all base data, including seed .secret files
    BASE_DATA_DIR = os.path.join(Path(BASE_DIR).parent, "data")
    # Environment Variables Prefix (used to match dynamic env vars)
    BASE_ENV_PREFIX = "ANMS_CORE_"

    # # # Commonly Used... you can override when you inherit these ones... # # #
    DEBUG = True
    TESTING = True

    # # # # Abstract Config - ONLY INHERIT - # # # #

    def __init__(self, root_dir=None, yaml_parser=None, top_level_only=False):
        """
        Init.
        """
        # Default are already loaded at this Point
        if root_dir is not None:
            self._process_paths(alt_path=root_dir)

        # Read in environment vars
        self._process_file_cfg(
            load_func=yaml_parser, top_level_only=top_level_only
        )  # Load Config File First
        self._process_env_vars(
            top_level_only=top_level_only
        )  # Process Env Vars Last
        self.on_finalized()

        # Print Vars
        if (
            getattr(self, "DEBUG", False) is True
            and getattr(self, "TESTING", False) is True
        ):
            self.get_logger().info(
                "Environment<%s>:\n%s",
                self.__class__.__name__,
                pformat(self.as_dict(), indent=2),
            )
        elif getattr(self, "TESTING", False) is True:
            self.get_logger().info(
                "Environment<%s>: %s", self.__class__.__name__, self.as_dict()
            )
        else:
            pass

    def on_finalized(self):
        pass

    @classmethod
    def get_logger(cls):
        """
        Get Internal Logger for this file.
        :rtype: logging.Logger
        """
        _logger = logging.getLogger(default_logger_name)
        if not _logger.level:
            _logger.setLevel(logging.DEBUG)
        if default_log_handler not in _logger.handlers:
            _logger.addHandler(default_log_handler)
        return _logger

    @classmethod
    def _process_paths(cls, alt_path=None):
        """
        Used to change the root directory before parsing anything else.
        :type alt_path: os.PathLike
        """
        # replace old ROOT_DIR, BASE_DIR (this assumes ROOT_DIR/BASE_DIR are the same for now)
        norm_alt_path = os.path.normpath(os.path.abspath(alt_path))
        old_root_path = getattr(cls, "ROOT_DIR")
        if not os.path.exists(alt_path):
            return
        white_list = frozenset({"ROOT_DIR", "BASE_DIR"})
        for key, value in six.iteritems(cls.as_dict()):
            if not isinstance(value, str):
                continue
            if key in white_list:
                continue
            # replace any key which had the OLD root path as a value
            if value.startswith(old_root_path) and hasattr(cls, key):
                fixed_path = value.replace(old_root_path, norm_alt_path)
                setattr(cls, key, fixed_path)
                continue
        setattr(cls, "ROOT_DIR", norm_alt_path)
        setattr(cls, "BASE_DIR", norm_alt_path)

    @classmethod
    def _process_file_cfg(cls, load_func=None, top_level_only=False):
        """
        Process File Config.
        """
        if callable(load_func):
            # custom yaml loading func...
            yaml_load = load_func
        elif cls._find_library("ruamel.yaml"):  # ruamel.yaml
            from ruamel.yaml import YAML  # pylint: disable=C0415

            yaml = YAML(typ="safe", pure=True)
            yaml_load = yaml.load
        elif cls._find_library("yaml"):  # pyyaml
            from yaml import safe_load  # pylint: disable=C0415

            yaml_load = safe_load
        else:
            cls.get_logger().warning(
                "YAML Parsing not Available, please install ruamel.yaml or pyyaml to enable"
            )
            return
        base_dir_path = getattr(cls, "BASE_DIR")
        base_cfg_name = getattr(cls, "BASE_CFG_FILE")
        yaml_path = os.path.join(base_dir_path, base_cfg_name)
        yaml_pathlib = Path(yaml_path)
        if not (yaml_pathlib.exists() or yaml_pathlib.is_file()):
            cls.get_logger().warning("YAML Config File not Available")
            return
        with yaml_pathlib.open("r") as yaml_stream:
            config_dict = yaml_load(yaml_stream)  # type: dict
        config_dict = config_dict if isinstance(config_dict, dict) else dict()
        cls.get_logger().info("YAML Config %s was Loaded", yaml_path)
        cls._merge_config(config_dict, top_level_only=top_level_only)

    @classmethod
    def _process_env_vars(cls, top_level_only=False):
        """
        Process Env Vars.
        """
        config_dict_cls = cls.as_dict()
        white_list = frozenset(
            {"ROOT_DIR", "BASE_DIR", "BASE_CFG_FILE", "BASE_ENV_PREFIX"}
        )  # don't allow BASE_ENV_PREFIX modifications
        # Prefix with BASE_ENV_PREFIX value to avoid potential conflicts
        # Default is the value in the config if not found
        env_prefix = getattr(cls, "BASE_ENV_PREFIX", "")
        # Isolate these environment variables and normalize the casing
        matching_environ = {
            str.upper(env_key.replace(env_prefix, "")): env_val
            for env_key, env_val in six.iteritems(os.environ)
            if env_key.startswith(env_prefix)
        }
        if len(matching_environ) <= 0:
            return  # don't process if there's no env variable to process...
        if not top_level_only and cls._find_library("pydash"):
            import pydash  # pylint: disable=C0415

            config_dict_expanded = cls._get_config_var_paths(
                config_dict_cls, top_level_only
            )
            for config_path, config_val in six.iteritems(config_dict_expanded):
                # config_path format: x = 1 or x.y.z = 1 or x.y.z[0] = 1 or x.y.z[0].w = 1 (in tuples)
                stringified_config_path = cls._transform_path_to_pure_string(
                    config_path
                )
                underscored_config_path = "_".join(stringified_config_path)
                underscored_config_path_upper = str.upper(
                    underscored_config_path
                )
                # skip dangerous keys
                if underscored_config_path_upper in white_list:
                    continue
                # skip non-matching keys
                if underscored_config_path_upper not in matching_environ:
                    continue
                # found a match
                env_val = matching_environ[underscored_config_path_upper]
                # parse the value to the right type (if applicable)
                parsed_val, should_replace = cls._parse_environ_value(
                    env_val, config_val
                )
                if not should_replace:
                    continue
                # retrieval from environment was successful and requires modification
                if len(config_path) == 1:
                    setattr(cls, underscored_config_path, parsed_val)
                    continue  # go to the next value since we're finished
                # config path is nested
                cls_key = config_path[
                    0
                ]  # first item in tuple is the top-level key
                cls_obj_reference = getattr(
                    cls, cls_key
                )  # pydash.set_ doesn't do 'getattr' by default
                entry_path = config_path[
                    1:
                ]  # will be y.z or y.z[0] or y.z[0].w (from example above)
                # https://pydash.readthedocs.io/en/latest/api.html#pydash.objects.set_
                pydash.set_(cls_obj_reference, list(entry_path), parsed_val)
        else:
            cls.get_logger().warning(
                "Only top level substitution is enabled, install pydash for nested support"
            )
            for cls_key, cls_val in six.iteritems(config_dict_cls):
                # skip dangerous keys
                if cls_key in white_list:
                    continue
                # skip non-matching keys
                if str.upper(cls_key) not in matching_environ:
                    continue
                # found the value
                env_val = matching_environ[str.upper(cls_key)]
                # parse the value to the right type (if applicable)
                parsed_val, should_replace = cls._parse_environ_value(
                    env_val, cls_val
                )
                if should_replace:
                    # retrieval from environment was successful and requires modification
                    setattr(cls, cls_key, parsed_val)
                    # go to the next value since we're finished

    @classmethod
    def _merge_config(cls, config_to_merge, top_level_only=False):
        """
        Merge Config.
        :type config_to_merge: dict
        :type top_level_only: bool
        """
        config_dict_cls = cls.as_dict()
        white_list = frozenset(
            {"ROOT_DIR", "BASE_DIR", "BASE_CFG_FILE"}
        )  # allow BASE_ENV_PREFIX modifications
        if not top_level_only and cls._find_library("pydash"):
            import pydash  # pylint: disable=C0415

            config_dict_expanded = cls._get_config_var_paths(
                config_dict_cls, top_level_only
            )
            config_paths_to_merge = cls._get_config_var_paths(
                config_to_merge, top_level_only
            )
            config_dict_expanded_upper_mapping = (
                cls._create_path_map_for_upper_strings(config_dict_expanded)
            )
            config_paths_to_merge_upper_mapping = (
                cls._create_path_map_for_upper_strings(config_paths_to_merge)
            )
            for config_upper_path, config_original_path in six.iteritems(
                config_dict_expanded_upper_mapping
            ):
                # config_path format: x = 1 or x.y.z = 1 or x.y.z[0] = 1 or x.y.z[0].w = 1 (in tuples)
                # skip dangerous keys
                if config_upper_path[0] in white_list:
                    continue
                # skip non-matching keys
                if config_upper_path not in config_paths_to_merge_upper_mapping:
                    continue
                # found a match
                cls_key = config_original_path[0]
                # new_conf[upper_new_conf[upper_ext_conf] -> new_conf_key] = new_value
                cls_new_val = config_paths_to_merge[
                    config_paths_to_merge_upper_mapping[config_upper_path]
                ]
                cls_orig_val = config_dict_expanded[config_original_path]
                # Enum Support (Yaml Doesn't transform them well)
                if isinstance(cls_orig_val, Enum):
                    try:
                        cls_new_val = cls_orig_val.__class__(cls_new_val)
                    except ValueError:
                        cls.get_logger().error(
                            "Invalid enum value %s provided or non-supported enum constructor.",
                            cls_new_val,
                        )
                        continue
                # Do Replacements!
                if len(config_original_path) == 1:
                    setattr(cls, cls_key, cls_new_val)
                    continue  # go to the next value since we're finished
                # config path is nested
                cls_obj_reference = getattr(
                    cls, cls_key
                )  # pydash.set_ doesn't do 'getattr' by default
                entry_path = config_original_path[
                    1:
                ]  # will be y.z or y.z[0] or y.z[0].w (from example above)
                # https://pydash.readthedocs.io/en/latest/api.html#pydash.objects.set_
                pydash.set_(cls_obj_reference, list(entry_path), cls_new_val)
        else:  # top-level only
            cls.get_logger().warning(
                "Only top level substitution is enabled, install pydash for nested support"
            )
            for config_key, config_val in six.iteritems(config_to_merge):
                upper_key = str.upper(config_key)
                if upper_key in white_list:  # skip dangerous keys
                    continue
                # standard size iteration (# config items), allows for case-insensitive search
                for cls_key in six.iterkeys(config_dict_cls):
                    if str.upper(cls_key) == upper_key:
                        setattr(cls, cls_key, config_val)
                        break  # break out of inner for-loop

    @classmethod
    def _get_config_var_paths(
        cls,
        root_dict=None,
        top_level_only=False,
        list_support=True,
        verbose=False,
    ):
        """
        Makes list of paths recursively.
        Takes a dictionary and creates a path expression to access that value in the future.
        Dictionary can optionally be nested with other dictionaries and optionally lists.
        Resulting expressions are of the following format:
        * x = 1 or x.y.z = 1 or x.y.z[0] = 1 or x.y.z[0].w = 1, x.y.z.0.w = 1 (in tuples)
        * {('x'):1, ('x','y','z'):1, ('x','y','z',0):1, ('x','y','z',0,'w'):1, ('x','y','z','0','w'):1, ...}
        :type root_dict: dict
        :type top_level_only: bool
        :type list_support: bool
        :type verbose: bool
        :rtype: dict[tuple]
        """

        return_dict = dict()
        root_obj = root_dict if root_dict is not None else cls.as_dict()

        def traverse_dict(dict_obj, _path=None):
            """
            Traverse Dict.
            :type dict_obj: dict
            :type _path: list
            :rtype: dict
            """
            if _path is None:
                _path = []
            for _key, _val in six.iteritems(dict_obj):
                next_path = _path + [_key]
                if isinstance(_val, dict) and not top_level_only:
                    for _dict in traverse_dict(_val, next_path):
                        yield _dict
                elif (
                    isinstance(_val, list)
                    and list_support
                    and not top_level_only
                ):
                    # cast to dict with indexes being the keys :)
                    tmp_dict = {
                        f"{_idx}": _item for (_idx, _item) in enumerate(_val)
                    }  # dict comprehension
                    for _dict in traverse_dict(tmp_dict, next_path):
                        yield _dict
                else:
                    yield next_path, _val

        for path, val in traverse_dict(root_obj):
            if verbose:
                merged_path = ""
                for _part in path:  # type: str
                    if str(_part).isdigit() and list_support:
                        merged_path += "[%s]" % _part
                    else:
                        merged_path += "." + str(_part)
                merged_path = merged_path.lstrip(".")  # remove the leading "."
                cls.get_logger().debug("Mapping: %s = %s", merged_path, val)
            return_dict[tuple(path)] = val
        return return_dict

    @classmethod
    def _transform_path_to_pure_string(cls, path_expression, to_upper=False):
        """
        Takes a tuple, converts each entry to string and returns the tuple back, optionally uppercased.
        :type path_expression: tuple
        :type to_upper: bool
        :rtype: tuple
        """
        final_expression = []
        for entry in path_expression:
            if isinstance(entry, str):
                t_entry = entry if not to_upper else str.upper(entry)
            elif isinstance(entry, int):
                t_entry = str(entry) if not to_upper else str.upper(str(entry))
            elif isinstance(entry, Enum):
                t_entry = entry.name if not to_upper else str.upper(entry.name)
            else:
                t_entry = str(entry) if not to_upper else str.upper(str(entry))
                cls.get_logger().warning(
                    "Bad entry %s since it's non-supported format, attempted to coerce via str()",
                    entry,
                )
            # Add Entry to Tuple
            final_expression.append(t_entry)
        return tuple(final_expression)

    @classmethod
    def _create_path_map_for_upper_strings(cls, path_dict):
        """
        Used to map original (exact) tuple mappings to normalized mappings.
        Helps with comparison between a original mapping and a new mapping to ignore case.
        tuple("MY_VAR", "NESTED_DICT_KEY") mapped <--> tuple("MY_VAR", "nested_dict_key") original
        :type path_dict: dict[tuple]
        :rtype: dict[tuple, tuple]
        """
        return {
            cls._transform_path_to_pure_string(tuple_path, True): tuple_path
            for tuple_path in six.iterkeys(path_dict)
        }

    @classmethod
    def as_dict(cls):
        """
        Returns a classic dictionary of the mappings.
        :rtype: dict
        """
        # Doing this because of inheritance chain
        member_list = inspect.getmembers(
            cls, lambda x: not (inspect.isroutine(x))
        )
        attribute_list = [
            mem
            for mem in member_list
            if not (mem[0].startswith("__") and mem[0].endswith("__"))
        ]
        return dict(attribute_list)

    @classmethod
    def as_attr_dict(cls):
        """
        Returns attribute-access enabled dictionary.
        You can access entries by doing x.y.z instead of x[y][z]
        :rtype: munch.Munch | dict
        """
        try:
            import munch  # pylint: disable=C0415

            return munch.munchify(cls.as_dict())
        except ImportError:
            cls.get_logger().warning(
                "Attribute Dict functionality not available, please install munch to enable"
            )
            return cls.as_dict()

    @classmethod
    def _parse_environ_value(cls, value_to_parse, value_to_compare):
        """
        Takes a value and a reference value and tries to cast the value into the reference value type.
        This is useful for coercing environment variables into their configuration types.
        :type value_to_parse: str
        :type value_to_compare: Any
        :rtype: Any, bool
        """
        # check if they're equal, exit quickly

        if value_to_parse == value_to_compare:
            return value_to_parse, False

        # try to infer type...
        is_bool = isinstance(value_to_compare, bool)
        is_int = isinstance(value_to_compare, six.integer_types)
        is_flt = isinstance(value_to_compare, float)
        is_arr = isinstance(value_to_compare, list)
        is_dict = isinstance(value_to_compare, dict)
        is_str = isinstance(value_to_compare, str)
        is_enum = isinstance(value_to_compare, Enum)

        # # # order of type-checking below is on purpose # # #
        # special case (identify null in an env var)...
        if value_to_parse == "null":  # pylint: disable=R1705
            return None, True
        # first on purpose
        elif is_bool:  # pylint: disable=R1705
            return cls._str2bool(value_to_parse, value_to_compare), True
        elif is_int:
            return cls._try_cast(value_to_parse, int, value_to_compare), True
        elif is_flt:
            return cls._try_cast(value_to_parse, float, value_to_compare), True
        elif is_arr or is_dict:
            try:
                _temp = json.loads(value_to_parse)
            except json.decoder.JSONDecodeError:
                return value_to_compare, False
            if is_arr and isinstance(_temp, list):  # pylint: disable=R1705
                return _temp, True
            elif is_dict and isinstance(_temp, dict):
                return _temp, True
            else:
                return value_to_compare, False
        elif is_enum:
            try:
                return value_to_compare.__class__(value_to_parse), True
            except ValueError:
                return value_to_compare, False
        # last on purpose
        elif is_str:
            return value_to_parse, True  # environment vars are always strings
        else:
            cls.get_logger().warning(
                "Unable to perform environment substitution for value %s",
                value_to_compare,
            )
            # don't support replacing other types?
            return (
                value_to_compare,
                False,
            )  # this line should never happen (environments are always strings)

    @staticmethod
    def _try_cast(value, _type, _default=None):
        """
        Try to Cast.
        """
        try:
            return _type(value) if callable(_type) else _default
        except (ValueError, TypeError):
            return _default

    @staticmethod
    def _find_library(name):
        """
        Try find a package...
        :rtype: bool
        """
        try:
            return find_spec(name) and True
        except (ModuleNotFoundError, ImportError, AttributeError, ValueError):
            return False

    @staticmethod
    def _str2bool(_str, _default=None):
        """
        Convert String to Bool.
        """
        if isinstance(_str, bool):  # pylint: disable=R1705
            return _str
        elif isinstance(_str, str):
            return _str.lower() in ("true", "1")
        else:
            return _default


class ConfigBuilder(object):
    """
    ConfigBuilder.
    """

    __env_cfg_variable = "BUILDER_CFG_PROFILE"
    __current_config_instance = None
    __current_config_instance_name = None
    __current_config_instance_print = False
    __arg_parser = ArgumentParser(add_help=False)
    __arg_parser.add_argument(
        "-c",
        "--config",
        metavar='"Config Name..."',
        help="Configuration Setup",
        type=str,
        default=None,
    )

    def __new__(cls, *args, **kwargs):
        """
        Create New Config Instance.
        :type config_name: str | None
        :type enable_terminal: bool
        :type as_attr_dict: bool
        :type verbose: bool
        :rtype: TypingConfig
        """
        return cls.get_config(*args, **kwargs)

    @staticmethod
    def __get_configs():
        """
        Get Inheritable Configs.
        :rtype list[Callable[..., AbstractConfig]]
        """
        all_subclasses = []

        def get_all_subclasses(klass):
            """
            Get all Subclassing modules.
            :type klass: Callable[..., AbstractConfig]
            """
            for subclass in klass.__subclasses__():
                all_subclasses.append(subclass)
                get_all_subclasses(subclass)

        get_all_subclasses(AbstractConfig)
        return all_subclasses

    @staticmethod
    def get_config_names():
        """
        Get Available Config Names.
        :rtype: list[str]
        """
        return [klass.__name__ for klass in ConfigBuilder.__get_configs()]

    @staticmethod
    def get_default_config():
        """
        Get Default Config.
        :rtype: AbstractConfig, str
        """
        try:
            from .config import BaseConfig  # pylint: disable=C0415,R0401

            return BaseConfig, "BaseConfig"
        except ImportError:
            return AbstractConfig, "AbstractConfig"

    @classmethod
    def get_arg_parser(cls):
        """
        Get Arp Parser.
        :rtype: ArgumentParser
        """
        return cls.__arg_parser

    @classmethod
    def get_logger(cls):
        """
        Get Internal Logger for this file.
        :rtype: logging.Logger
        """
        _logger = logging.getLogger(default_logger_name)
        if not _logger.level:
            _logger.setLevel(logging.DEBUG)
        if default_log_handler not in _logger.handlers:
            _logger.addHandler(default_log_handler)
        return _logger

    @classmethod
    def init_config(
        cls,
        config_name=None,
        enable_terminal=True,
        as_attr_dict=True,
        verbose=True,
        **kwargs,
    ):
        """
        Init Config.
        :type config_name: str | None
        :type enable_terminal: bool
        :type as_attr_dict: bool
        :type verbose: bool
        """
        if cls.__current_config_instance is None:
            cls.__current_config_instance = cls.get_config(
                config_name, enable_terminal, as_attr_dict, verbose, **kwargs
            )

    @classmethod
    def get_config(
        cls,
        config_name=None,
        enable_terminal=True,
        as_attr_dict=True,
        verbose=True,
        **kwargs,
    ):
        """
        Get Config.
        :type config_name: str | None
        :type enable_terminal: bool
        :type as_attr_dict: bool
        :type verbose: bool
        :rtype: TypingConfig
        """
        if verbose:
            # Does not do much now, only here for compat with older versions...
            default_log_handler.setLevel(
                logging.INFO
            ) if not default_log_handler.level else None
        if cls.__current_config_instance is not None and not config_name:
            if not cls.__current_config_instance_print:
                cls.get_logger().info(
                    'Reusing config instance "%s"',
                    cls.__current_config_instance_name,
                )
                cls.__current_config_instance_print = True
            return ConfigBuilder.__current_config_instance
        if enable_terminal is True:
            terminal_config = getattr(
                cls.__parse_terminal_config(), "config", None
            )
            config_name = (
                terminal_config if terminal_config is not None else config_name
            )
        # Check if there's a config profile as an env variable
        config_name = os.getenv(cls.__env_cfg_variable, config_name)
        default_cfg_klazz, default_cfg_name = cls.get_default_config()
        if config_name is None:
            cls.get_logger().info('Using "%s"...', default_cfg_name)
            config_klass = default_cfg_klazz(**kwargs)
            cls.__current_config_instance = (
                config_klass.as_attr_dict() if as_attr_dict else config_klass
            )
            cls.__current_config_instance_name = config_klass.__class__.__name__
            return cls.__current_config_instance
        for klass in cls.__get_configs():
            if klass.__name__ == config_name:
                cls.get_logger().info('Using "%s" Config...', config_name)
                config_klass = klass(**kwargs)
                cls.__current_config_instance = (
                    config_klass.as_attr_dict()
                    if as_attr_dict
                    else config_klass
                )
                cls.__current_config_instance_name = (
                    config_klass.__class__.__name__
                )
                return cls.__current_config_instance
        cls.get_logger().info(
            'Config Provided Not Found, Using "%s"...', default_cfg_name
        )
        config_klass = default_cfg_klazz(**kwargs)
        cls.__current_config_instance = (
            config_klass.as_attr_dict() if as_attr_dict else config_klass
        )
        cls.__current_config_instance_name = config_klass.__class__.__name__
        return cls.__current_config_instance

    @classmethod
    def set_config(
        cls,
        config_name=None,
        enable_terminal=True,
        as_attr_dict=True,
        verbose=True,
        **kwargs,
    ):
        """
        Set Config.
        :type config_name: str | None
        :type enable_terminal: bool
        :type as_attr_dict: bool
        :type verbose: bool
        """
        if cls.__current_config_instance is None:  # pylint: disable=R1705
            cls.get_logger().warning(
                "set_config called before init_config... doing nothing!"
            )
            return
        else:
            cls.__current_config_instance = None
            cls.__current_config_instance = cls.get_config(
                config_name, enable_terminal, as_attr_dict, verbose, **kwargs
            )

    @classmethod
    def __parse_terminal_config(cls):
        """
        Parse Terminal Config.
        :rtype: argparse.Namespace
        """
        return cls.__arg_parser.parse_known_args()[0]


if __name__ == "__main__":
    pass
