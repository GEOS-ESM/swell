# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from abc import ABC, abstractmethod
import copy
import datetime
import os
import yaml

from swell.swell_path import get_swell_path


# --------------------------------------------------------------------------------------------------


class PrepConfigBase(ABC):

    def __init__(self, logger, dictionary_file, suite, platform, override, advanced):

        self.override = override

        self.show_advanced = advanced

        # Store a logger for all to use
        self.logger = logger

        # Store the name of the class inheriting base
        self.prep_using = type(self).__name__.split('PrepConfig')[1]

        # Swell install path
        swell_path = get_swell_path()
        self.install_path = swell_path

        # Get the path and filename of the suite dictionary
        self.directory = os.path.join(swell_path, 'suites')
        self.filename = os.path.splitext(os.path.basename(dictionary_file))[0]

        # Keep track of the model, atmosphere, ocean etc
        self.model_path = os.path.join(self.install_path,
                                       'configuration',
                                       'jedi/interfaces/')
        self.model = None
        self.model_flag = False
        self.default_models = ['geos_atmosphere', 'geos_ocean']
        self.selected_models = None

        # Create executable keys list
        self.exec_keys = []

        # Experiment dictionary to be created and used in swell
        self.experiment_dict = {}

        # Comment dictionary to be created and used to add comments to config file
        self.comment_dict = {}

        # Dictionary validation things
        self.valid_types = ['string', 'integer', 'float',
                            'iso-datetime', 'iso-duration',
                            'string-list', 'integer-list',
                            'string-drop-list', 'string-check-list',
                            'boolean']

        # Disallowed element types
        self.dis_elem_types = [datetime.datetime, datetime.date]

        # Track the suite and platform that the user may input through the prepare_config path
        self.suite_to_run = suite
        self.platform = platform

        # Open the platform specific defaults
        platform_dict_file = os.path.join(swell_path, 'deployment', 'platforms', platform,
                                          'suite_questions.yaml')
        with open(platform_dict_file, 'r') as platform_dict_file_open:
            platform_dict_str = platform_dict_file_open.read()

        platform_task_file = os.path.join(swell_path, 'deployment', 'platforms', platform,
                                          'task_questions.yaml')
        with open(platform_task_file, 'r') as platform_dict_file_open:
            platform_dict_str = platform_dict_str + platform_dict_file_open.read()

        # Dictionary of defaults for platform
        # Use for 'defer_to_platform' default
        self.platform_dictionary = yaml.safe_load(platform_dict_str)

        # Open Master ask questions yaml
        with open(os.path.join(swell_path, 'tasks', 'task_questions.yaml'), 'r') as ymlfile:
            self.all_task_questions = yaml.safe_load(ymlfile)

        # Open tests override dictionary
        # do this only on defaults
        test_file = os.path.join(swell_path, 'test', 'suite_tests', suite + '-tier1.yaml')

        if os.path.exists(test_file):
            with open(test_file, 'r') as test_yml:
                self.test_dictionary = yaml.safe_load(test_yml)
        else:
            self.test_dictionary = {}

        # Open user selected override dictionary
        if override is not None:

            logger.info(f'Overriding experiment dictionary settings using override dictionary')

            # If override is a dictionary then use it directly
            if isinstance(override, dict):
                self.override_dictionary = override
            elif isinstance(override, str):
                # If override is a string then assume it is a path to a yaml file
                with open(override, 'r') as select_override_yml:
                    self.override_dictionary = yaml.safe_load(select_override_yml)
            else:
                logger.abort(f'Override must be a dictionary or a path to a yaml file. ' +
                             f'Instead it is {type(override)}')

        self.override_models()

    # ----------------------------------------------------------------------------------------------

    def execute(self):
        # Open the suite_to_run selected
        # check_widgets goes in cli
        # defaults gets nothing

        if self.prep_using == 'Cli':
            self.logger.info("Please answer the following questions to generate your experiment " +
                        "configuration YAML file.\n")

        # Set current dictionary variable which is needed for answer changes
        self.current_dictionary = {}

        # Generate task lists and question dictionaries
        base_tasks, model_tasks = self.suite_setup()

        # Add task questions to base question dictionary
        base_tasks_question_dict = self.task_dictionary_comber(base_tasks)
        self.base_questions_dictionary.update(base_tasks_question_dict)

        # Base model questions (i.e. questions sent to model tasks that do not depend on model)
        model_task_base_questions_tmp = self.task_dictionary_comber(model_tasks)

        model_task_base_questions = {}
        for key in model_task_base_questions_tmp.keys():
            if 'models' not in model_task_base_questions_tmp[key].keys():
                model_task_base_questions[key] = model_task_base_questions_tmp[key]

        # Add to the base questions
        self.base_questions_dictionary.update(model_task_base_questions)

        # Iterate over base questions
        for k, v in self.base_questions_dictionary.items():
            self.key_passer(k, v)

        if self.model_flag:
            # Find out what model components are to be used in the config
            self.selected_models = self.get_models()

            # Generate default model answer dictionary
            self.get_model_defaults()

            # Add tasks questions to model question dictionary
            self.model_questions_dictionary = {}
            model_tasks_question_dict = self.model_task_comber(model_tasks)
            self.model_questions_dictionary.update(model_tasks_question_dict)

            # Prepend model suite question in front of model task questions
            self.prepend_model_dict()

            model_questions_dictionary_copy = copy.deepcopy(self.model_questions_dictionary)

            # Iterate over base questions
            for m in self.selected_models:
                self.model_questions_dictionary[m] = \
                    copy.deepcopy(model_questions_dictionary_copy[m])
                copy.deepcopy(model_questions_dictionary_copy[m])
                self.model = m
                for k, v in self.model_questions_dictionary[m].items():
                    self.key_passer(k, v)

        return

    # ----------------------------------------------------------------------------------------------

    def suite_setup(self):

        # Create dictionary for asking about exp id and root
        exp_questions = {
            'experiment_id': {
                'ask_question': True,
                'default_value': f'swell-{self.suite_to_run}',
                'prompt': 'Enter the experiment ID',
                'type': 'string',
            },
            'experiment_root': {
                'ask_question': True,
                'default_value': 'defer_to_platform',
                'prompt': 'Enter the path where experiment will be staged',
                'type': 'string',
            },
            'platform': {
                'ask_question': False,
                'default_value': self.platform,
                'prompt': 'Enter the platform on which experiment will run',
                'type': 'string'
            },
            'suite_to_run': {
                'ask_question': False,
                'default_value': self.suite_to_run,
                'prompt': 'Enter the suite you wish to run',
                'type': 'string'
            }
        }

        # Look in suite_to_run dir and check for suite yaml file, if not, grep the flow.cylc file

        # Check which suite to run, check for suite_questions yaml, and grep flow file
        self.directory = os.path.join(self.directory, self.suite_to_run)
        suite_questions_path = os.path.join(self.directory, 'suite_questions.yaml')

        self.base_questions_dictionary = {}
        self.base_questions_dictionary.update(exp_questions)

        if os.path.exists(suite_questions_path):
            with open(suite_questions_path, 'r') as suite_dict_file:
                suite_questions_dict = yaml.safe_load(suite_dict_file.read())

            # Need to create a distint model suite dictionary to prepend later
            # onto model questions from task_questions.yaml file
            self.model_suite_questions = {}

            for k, v in suite_questions_dict.items():
                if 'models' in v.keys():
                    self.model_flag = True
                    self.model_suite_questions[k] = v
                else:
                    self.base_questions_dictionary[k] = v

        # Get the tasks asked prior to model selection and model-based tasks
        base_tasks, model_tasks = self.open_flow()

        return base_tasks, model_tasks

    # ----------------------------------------------------------------------------------------------

    def open_flow(self):
        # open text file in read mode
        cylc_file = open(os.path.join(self.directory, 'flow.cylc'), "r")

        # read whole file to a string
        data = cylc_file.read()

        # close file
        cylc_file.close()

        # Find the double bracket items in the Tasks section of the flow file to ID required tasks
        task_s = data[(data.find('Tasks')):]
        task_s_lines = task_s.split('\n')

        base_task_list = []
        model_task_list = []
        for line in task_s_lines:
            if 'script = "swell task' in line:
                task_name = line.split('"swell task')[1].split(' ')[1]
                if '-m' in line:
                    if task_name in model_task_list:
                        continue
                    model_task_list.append(task_name)
                else:
                    if task_name in base_task_list:
                        continue
                    base_task_list.append(task_name)

        return base_task_list, model_task_list

    # ----------------------------------------------------------------------------------------------

    def model_task_comber(self, model_tasks):
        model_task_dict = {}
        for m in self.selected_models:
            self.model = m
            model_task_dict[m] = self.task_dictionary_comber(model_tasks)
        return model_task_dict

    # ----------------------------------------------------------------------------------------------

    def task_dictionary_comber(self, task_list):
        question_dict = {}
        for t in task_list:
            self.current_dictionary = {}
            task_dict = {}
            dependent_dict = {}
            # Pass the task list to get the question dictionaries required for
            # the task. Do not get the questions that depend on prior questions
            task_dict = self.build_question_dictionary(t, get_dependents=False)
            # Get the question dictionaries that depend on previous questions
            dependent_dict = self.build_question_dictionary(t, get_dependents=True)
            # Combine the two dictionaries above
            task_dict.update(dependent_dict)
            question_dict.update(task_dict)
            del task_dict
            del dependent_dict
        return question_dict

    # ----------------------------------------------------------------------------------------------

    def build_question_dictionary(self, task, get_dependents):
        question_dictionary = {}
        model_key_list = ['all'] + [self.model]
        big_dictionary = copy.deepcopy(self.all_task_questions)
        for k, v in big_dictionary.items():
            if self.model is not None:
                if 'models' in v.keys() and v['models'][0] in model_key_list:
                    pass
                else:
                    continue
            if task in v['tasks']:
                if get_dependents:
                    if 'depends' in v.keys():
                        question_dictionary[k] = v
                else:
                    if 'depends' not in v.keys():
                        question_dictionary[k] = v
        del big_dictionary
        return question_dictionary

    # ----------------------------------------------------------------------------------------------

    def override_models(self):
        if 'model_components' in self.test_dictionary.keys():
            self.default_models = self.test_dictionary['model_components']
        if self.override is not None:
            if 'model_components' in self.override_dictionary.keys():
                self.default_models = self.override_dictionary['model_components']

    # ----------------------------------------------------------------------------------------------

    def get_model_defaults(self):
        self.model_defaults_dict = {}
        for m in self.selected_models:
            self.model_defaults_dict[m] = {}
            for s in ['suite', 'task']:
                model_dict_path = os.path.join(self.model_path, m, f'{s}_questions.yaml')
                with open(model_dict_path, 'r') as model_dict_file:
                    model_comp_dict = yaml.safe_load(model_dict_file.read())
                self.model_defaults_dict[m].update(model_comp_dict)

    # ----------------------------------------------------------------------------------------------

    def show_deference(self, key, el_dict):

        if 'defer_to_' in str(el_dict['default_value']):
            pass
        else:
            return el_dict

        if 'defer_to_platform' == el_dict['default_value']:
            el_dict['default_value'] = self.platform_dictionary[key]['default_value']
        elif 'defer_to_model' == el_dict['default_value']:
            el_dict['default_value'] = self.model_defaults_dict[self.model][key]['default_value']
            if 'options' in self.model_defaults_dict[self.model][key].keys()\
                    and 'defer_to_model' == el_dict['options']:
                el_dict['options'] = self.model_defaults_dict[self.model][key]['options']

        return el_dict

    # ----------------------------------------------------------------------------------------------

    def override_defaults(self, key, el_dict):

        override_dict = None

        if self.model is None:
            if key in self.test_dictionary.keys():
                override_dict = self.test_dictionary
            else:
                pass
            if self.override is not None:
                if key in self.override_dictionary.keys():
                    override_dict = self.override_dictionary
                else:
                    pass
            if override_dict is None:
                return el_dict
            else:
                override_default = override_dict[key]
                if 'options' in el_dict.keys():
                    if isinstance(override_default, list):
                        override_options = override_default
                    else:
                        override_options = [override_default]
                else:
                    override_options = None
        else:
            if 'models' in self.test_dictionary.keys():
                if self.model in self.test_dictionary['models'].keys():
                    if key in self.test_dictionary['models'][self.model].keys():
                        override_dict = self.test_dictionary
                    else:
                        pass
            if self.override is not None:
                if 'models' in self.override_dictionary.keys():
                    if self.model in self.override_dictionary['models'].keys():
                        if key in self.override_dictionary['models'][self.model].keys():
                            override_dict = self.override_dictionary
                        else:
                            pass

            if override_dict is None:
                return el_dict
            else:
                override_default = override_dict['models'][self.model][key]
                if 'options' in el_dict.keys():
                    if isinstance(override_default, list):
                        override_options = override_default
                    else:
                        override_options = [override_default]
                else:
                    override_options = None

        el_dict['default_value'] = override_default
        if 'options' in el_dict.keys():
            el_dict['options'] = override_options

        return el_dict

    # ----------------------------------------------------------------------------------------------

    def key_passer(self, key, el_dict):

        # Validate the element dictionary
        self.validate_dictionary(el_dict)

        # Check that the key does not have a dependency
        depends_flag = True
        if 'depends' in el_dict.keys():
            dep_key = el_dict['depends']['key']
            dep_val = el_dict['depends']['value']
            if self.model is None:
                if self.experiment_dict[dep_key] != dep_val:
                    depends_flag = False
            else:
                if self.experiment_dict['models'][self.model][dep_key] != dep_val:
                    depends_flag = False

        # In this case the key is not expected to refer to a sub dictionary but have
        # everything needed in the elements dictionary
        if depends_flag:

            el_dict = self.show_deference(key, el_dict)

            el_dict = self.override_defaults(key, el_dict)

            if self.show_advanced:
                el_dict['ask_question'] = True

            if el_dict['ask_question']:
                el_dict['default_value'] = self.get_answer(key, el_dict)
            else:
                pass
            self.add_to_experiment_dictionary(key, el_dict)

        return

    # ----------------------------------------------------------------------------------------------

    def prepend_model_dict(self):
        complete_model_dict = {}
        for m in self.selected_models:
            model_key_list = ['all'] + [m]
            for k, v in self.model_suite_questions.items():
                if v['models'][0] in model_key_list:
                    complete_model_dict[m] = {}
                    complete_model_dict[m][k] = v
            complete_model_dict[m].update(self.model_questions_dictionary[m])
        self.model_questions_dictionary = complete_model_dict

    # ----------------------------------------------------------------------------------------------

    def validate_dictionary(self, dictionary):

        # Check for required key
        required_keys = ['default_value', 'prompt', 'type']
        for required_key in required_keys:
            if required_key not in dictionary.keys():
                self.logger.abort(f'Each section of the suites config files must contain the key ' +
                                  f'\'{required_key}\'. Offending dictionary: \n {dictionary}')

        # Check that type is supported
        type = dictionary['type']
        if type not in self.valid_types:
            self.logger.abort(f'Dictionary has type \'{type}\' that is not one of the supported ' +
                              f'types: {self.valid_types}. Offending dictionary: \n {dictionary}')

    # ----------------------------------------------------------------------------------------------

    def add_to_experiment_dictionary(self, key, element_dict):

        # Add elements to the current dictionary
        # --------------------------------------
        self.current_dictionary[key] = element_dict

        # Add executed key to exec_keys list
        # ----------------------------------
        self.exec_keys.append(key)

        # Set the element
        # ---------------
        element = element_dict['default_value']
        prompt = element_dict['prompt']

        # Validate the element
        # --------------------

        # Ensure always a list to make following logic not need to check if list or not
        if not isinstance(element, list):
            element_items = [element]
        else:
            element_items = element

        # Check for disallowed element types
        for element_item in element_items:
            for dis_elem_type in self.dis_elem_types:
                if isinstance(element_item, dis_elem_type):
                    self.logger.abort(f'Element \'{element}\' has a type that is not permitted. ' +
                                      f'Type is \'{dis_elem_type}\'. Try replacing with a string ' +
                                      f'in the configuration file.')

        # Validate the key
        # ----------------

        # Ensure there are no spaces in the key
        if ' ' in key:
            self.logger.abort(f'Key \'{key}\' contains a space. For consistency across the ' +
                              f'configurations please avoid spaces and instead use _ if needed.')

        # Check that dictionary does not already contain the key
        if key in self.experiment_dict.keys():

            self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')

        # Check if models key is present in experiment dictionary
        if self.model is not None:
            if 'models' not in self.experiment_dict.keys():
                self.experiment_dict['models'] = {}

            # If specific model dictionary not added to the list of model then add it
            if self.model not in self.experiment_dict['models'].keys():
                self.experiment_dict['models'][self.model] = {}

        # Make sure the element was not already added
        # -------------------------------------------
        if self.model is None:
            if key in self.experiment_dict.keys():
                self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')
        else:
            if key in self.experiment_dict['models'][self.model].keys():
                self.logger.abort(f'Key \'{key}\' is already in the experiment dictionary.')

        # Add element
        # -----------
        if self.model is None:
            self.experiment_dict[key] = element
        else:
            self.experiment_dict['models'][self.model][key] = element

        # Add option
        # ----------
        if self.model is None:
            option_key = key
        else:
            if 'models' not in self.comment_dict.keys():
                self.comment_dict['models'] = 'Options for individual model components'
            if 'models.' + self.model not in self.comment_dict.keys():
                self.comment_dict['models.' + self.model] = f'Options for the {self.model} ' + \
                                                            f'model component'
            option_key = 'models.' + self.model + '.' + key
        self.comment_dict[option_key] = prompt

    # ----------------------------------------------------------------------------------------------

    def update_experiment_dictionary(self, key, new_value):
        if self.model is not None:
            self.experiment_dict['models'][self.model][key] = new_value
        else:
            self.experiment_dict[key] = new_value

    # ----------------------------------------------------------------------------------------------

    @abstractmethod
    def get_answer(self, dictionary):
        pass
        # The subclass has to implement an execute method since this is how it is called into
        # action.

# --------------------------------------------------------------------------------------------------


def camel_to_snake(s):
    new_string = re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()
    return new_string
