
import os
import shutil
import yaml

from samcli.yamlhelper import yaml_parse
from samcli.local.docker.manager import ContainerManager
from samcli.commands.local.lib.sam_function_provider import SamFunctionProvider


class BuildContext(object):

    def __init__(self, template_file,
                 base_dir,
                 build_dir,
                 manifest_path=None,
                 clean=False,
                 use_container=False,
                 docker_network=None,
                 skip_pull_image=False):

        self._template_file = template_file
        self._base_dir = base_dir
        self._build_dir = build_dir
        self._manifest_path = manifest_path
        self._clean = clean
        self._use_container = use_container
        self._docker_network = docker_network
        self._skip_pull_image = skip_pull_image

        self._function_provider = None
        self._template_dict = None
        self._app_builder = None
        self._container_manager = None

    def __enter__(self):
        self._template_dict = self._get_template_data(self._template_file)
        self._function_provider = SamFunctionProvider(self._template_dict)

        self._build_dir = self._setup_build_dir()

        if self._use_container:
            self._container_manager = ContainerManager(docker_network_id=self._docker_network,
                                                       skip_pull_image=self._skip_pull_image)

        return self

    def __exit__(self, *args):
        pass

    @property
    def container_manager(self):
        return self._container_manager

    @property
    def function_provider(self):
        return self._function_provider

    @property
    def template_dict(self):
        return self._template_dict

    @property
    def build_dir(self):
        return self._build_dir

    @property
    def base_dir(self):
        return self._base_dir

    @property
    def use_container(self):
        return self._use_container

    @property
    def output_template_path(self):
        return os.path.join(self._build_dir, "template.yaml")

    @property
    def manifest_path_override(self):
        if self._manifest_path:
            return os.path.abspath(self._manifest_path)

        return None

    def _setup_build_dir(self):

        # Get absolute path
        self._build_dir = os.path.abspath(self._build_dir)

        if not os.path.exists(self._build_dir):
            # TODO: What permissions should I apply to this directory?
            os.makedirs(self._build_dir)

        if os.listdir(self._build_dir) and self._clean:
            # Build folder contains something inside. Clear everything.
            shutil.rmtree(self._build_dir)
            # this would have cleared the parent folder as well. So recreate it.
            os.mkdir(self._build_dir)

        return self._build_dir

    @staticmethod
    def _get_template_data(template_file):
        """
        Read the template file, parse it as JSON/YAML and return the template as a dictionary.

        :param string template_file: Path to the template to read
        :return dict: Template data as a dictionary
        :raises InvokeContextException: If template file was not found or the data was not a JSON/YAML
        """
        # TODO: This method was copied from InvokeContext. Move it into a common folder

        if not os.path.exists(template_file):
            raise ValueError("Template file not found at {}".format(template_file))

        with open(template_file, 'r') as fp:
            try:
                return yaml_parse(fp.read())
            except (ValueError, yaml.YAMLError) as ex:
                raise ValueError("Failed to parse template: {}".format(str(ex)))

