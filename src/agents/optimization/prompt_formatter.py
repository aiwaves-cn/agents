import re

from agents import SOP, DEFAULT_NODE_PROMPT_TEMPLATES
from agents.evaluation.state import State
from agents.evaluation.case import Case
from agents.task.node import Node


def check_variables(s):
    """
    Check for variables needed in a prompt template.

    This function identifies all variables wrapped in `{}` but not `{{}}` within a given prompt template string,
    while ignoring content wrapped in triple backticks.

    Note: Ensure that triple backticks in the prompt are not split across segments, as this would prevent proper recognition.

    Args:
        s (str): The prompt template string to check for variables.

    Returns:
        set: A set of valid variable names found in the template.
    """
    # First, remove all content wrapped in triple backticks using a regular expression
    pattern_remove_backticks = r"```.*?```"
    filtered_string = re.sub(pattern_remove_backticks, "", s, flags=re.DOTALL)

    # Next, find content within braces that are not wrapped in double braces in the filtered string
    pattern_find_braces = r"(?<!{)\{([^{}]+)\}(?!})"
    matches = re.findall(pattern_find_braces, filtered_string)
    valid_variables = {
        var for var in matches if var and re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var)
    }
    return valid_variables


def get_config_needed_variables(config, specific_key_list=None):
    """
    Get the variables needed in the prompt configuration.

    This function retrieves the variables required by the prompt templates specified in the configuration.
    It can optionally limit the check to specific prompt templates if `specific_key_list` is provided.

    Args:
        config (dict): The configuration for the prompt, formatted according to the trainer's configuration file.
        specific_key_list (list[str], optional): List of specific keys to check in the prompt configuration.
            If specified, only the prompts corresponding to these keys are checked. If not specified, the prompts
            are checked in the order defined by the "order" field in the configuration.

    Returns:
        list: A list of variables needed by the prompt templates.

    Raises:
        AssertionError: If the "order" field is not present in the configuration and `specific_key_list` is not provided.
    """
    # If a specific_key is specified, then only the prompt corresponding to the key is checked,
    # otherwise it is checked in the order of the order field
    if specific_key_list:
        prompt_names = specific_key_list
    else:
        assert (
            "order" in config.keys()
        ), f"The prompt must have an order field, config is{config}"
        prompt_names = config["order"]

    # Get the variables that are required in prompts
    all_variable = []
    for prompt_name in prompt_names:
        needed_variables = check_variables(config[prompt_name])
        all_variable += needed_variables
    return all_variable


def format_str_without_error(template, data_dict):
    """
    Format a string template with the provided data dictionary, ensuring no errors occur due to missing keys.

    This function cannot handle cases where the string contains both JSON and format placeholders simultaneously.
    Ensure that the template does not contain JSON strings when calling this function.

    Args:
        template (str): The string template to be formatted.
        data_dict (dict): The dictionary containing data to fill into the template.

    Returns:
        str: The formatted string. If any variables in the template are missing in data_dict, the original
             template is returned with an error message printed.
    """

    valid_variables = check_variables(template)

    # Check that these variables are all in data_dict
    missing_vars = valid_variables - data_dict.keys()
    if missing_vars:
        print(
            f"Error: Missing keys for variables {missing_vars}, the template is {template}, data_dict is {data_dict}"
        )
        return template
    if not valid_variables:
        # Empty lists, i.e. no format
        return template
    return template.format(**data_dict)


def formulate_prompt(config, data_dict):
    """
    Formulate a prompt using the provided configuration and data dictionary.

    This function generates a prompt by extracting necessary variables from `data_dict` and filling them
    into the templates specified in `config`. It supports both regular and loop-based templates.

    Args:
        config (dict): Configuration for the prompt, must include an "order" field that specifies the sequence
            of template names, and optionally a "loop" field for templates that should be repeated for each item
            in the "loop_data".
        data_dict (dict): Dictionary containing the data required to fill the templates. It must include all
            variables specified in the `config`, and optionally a "loop_data" field which is a list of dictionaries
            for loop-based templates.

    Returns:
        str: The formulated prompt based on the provided configuration and data.

    Raises:
        AssertionError: If the "order" field is not present in the `config`.
    """
    assert "order" in config.keys(), "prompt必须有order字段"
    order_list = config["order"]
    loop_list = config.get("loop", [])

    # Check for missing variables in data_dict and validate variable names
    all_variable = get_config_needed_variables(config)
    for var in all_variable:
        if (
            var not in data_dict.keys()
            and var not in data_dict.get("loop_data", {})[0].keys()
        ):
            print(f"\033[31m prompt中需要的变量{var} 没有在data_dict中找到\033[0m")
            data_dict[var] = ""

    # Construct the prompt
    res_prompt = ""
    for prompt_name in order_list:
        template = config[prompt_name]
        # loop_data is a list where each item is a dictionary used for filling loop parts
        if prompt_name in loop_list:
            for single_loop_data in data_dict["loop_data"]:
                res_prompt += format_str_without_error(template, single_loop_data)
        else:
            res_prompt += format_str_without_error(template, data_dict)
    return res_prompt


def formulate_prompt_for_prompt_optim(
    prompt_config, case_list: list[Case], state_idx, needed_optim_component
):
    """
    Formulate a prompt for prompt optimization.

    This function constructs a prompt for prompt optimization, where the outer loop is based on states and
    the optimizer loops through cases at the case level.

    Args:
        prompt_config (dict): Configuration for the prompt.
        case_list (list[Case]): List of Case instances to extract data from.
        state_idx (int): Index of the state to use for extracting data.
        needed_optim_component (list): List of components that need optimization.

    Returns:
        str: The formulated prompt based on the provided configuration and data.
    """
    # Get prompt names and the required variable names
    all_prompt_names = prompt_config["order"]
    loop_prompt_names = prompt_config.get("loop", [])
    not_loop_prompt_names = [
        item for item in all_prompt_names if item not in loop_prompt_names
    ]

    loop_needed_variable = get_config_needed_variables(
        prompt_config, specific_key_list=loop_prompt_names
    )
    not_loop_needed_variable = get_config_needed_variables(
        prompt_config, specific_key_list=not_loop_prompt_names
    )

    # Inner loop at the case level, gathering data for each case corresponding to loop variables
    loop_data_list = []
    first_case = case_list[0]
    first_case_action_agent_role = first_case.trajectory.states[
        state_idx
    ].action.agent_role
    for case_index, current_case in enumerate(case_list):
        # Ensure that the number of states and roles match across cases
        current_state = (
            current_case.trajectory.states[state_idx]
            if state_idx < len(current_case.trajectory.states)
            else current_case.trajectory.states[-1]
        )

        # If roles differ, find a matching role in adjacent states
        if current_state.action.agent_role != first_case_action_agent_role:
            print(
                f"Warning: case {case_index} and case 0 have different role at state {state_idx}"
            )
            offset = max(-2, -1 * state_idx)
            while offset <= 2 and state_idx + offset < len(
                current_case.trajectory.states
            ):
                current_state = current_case.trajectory.states[state_idx + offset]
                offset += 1
                if current_state.action.agent_role == first_case_action_agent_role:
                    break

        # Skip if no matching role state is found
        if current_state.action.agent_role != first_case_action_agent_role:
            print(
                f"Error: case {case_index} and case 0 have different role at state {state_idx}, cannot find same role state."
            )
            continue

        current_state_loop_data = current_state.get_dict_for_trainer(
            loop_needed_variable
        )
        current_state_loop_data["index"] = case_index + 1
        loop_data_list.append(current_state_loop_data)

    # Construct the prompt, using non-loop variables from the first case
    first_state = case_list[0].trajectory.states[state_idx]
    all_data = first_state.get_dict_for_trainer(not_loop_needed_variable)
    all_data["loop_data"] = loop_data_list
    all_data["needed_optim_component"] = (
        needed_optim_component[:] if needed_optim_component else []
    )
    all_data["needed_optim_component"].extend(
        first_state.action.used_prompt_templates.keys()
    )
    return formulate_prompt(prompt_config, all_data)


def formulate_prompt_for_node_backward(
    prompt_config, case: Case, node: Node, requirement_for_previous
):
    """
    Formulate a prompt for node backward optimization.

    This function creates a prompt for node backward optimization by extracting the necessary
    configuration from the provided node and case, and incorporating the requirements for the previous steps.

    Args:
        prompt_config (dict): Configuration for the prompt.
        case (Case): Case instance from which to extract data.
        node (Node): Node instance from which to extract configuration data.
        requirement_for_previous: Requirements for the previous steps.

    Returns:
        str: The formulated prompt based on the provided configuration and data.
    """
    node_name = node.node_name
    all_needed_variable_name = get_config_needed_variables(prompt_config)

    # Extract all necessary information from the case execution results
    data_dict_for_prompt = {
        "node_config": node.get_dict_for_node_optimizer(),
        "requirement_for_previous": requirement_for_previous,
    }

    case_dict = case.get_dict_for_node_optimizer(node_name, all_needed_variable_name)
    data_dict_for_prompt.update(case_dict)

    return formulate_prompt(prompt_config, data_dict_for_prompt)


def formulate_prompt_for_node_optim(prompt_config, node: Node, case_list: list[Case]):
    """
    Formulate a prompt for node optimization.

    This function creates a prompt for node optimization by gathering suggestions from the case list and
    extracting the necessary configuration from the provided node.

    Args:
        prompt_config (dict): Configuration for the prompt.
        node (Node): Node instance from which to extract configuration data.
        case_list (list[Case]): List of Case instances to extract suggestions from.

    Returns:
        str: The formulated prompt based on the provided configuration and data.
    """
    # The format method is unique, the variables are fixed in two items
    node_name = node.node_name

    # Gather all suggestions
    suggestions = ""
    suggestion_idx = 1
    for case in case_list:
        for state in case.trajectory.states:
            if (
                state.node.node_name == node_name
                and state.node_backward is not None
                and state.node_backward.suggestion
            ):
                # The suggestion is gathered for the current node.
                # In a single case, a node may be called multiple times, contributing multiple suggestions.
                suggestions += f"<suggestion_{suggestion_idx}>{state.node_backward.suggestion}</suggestion_{suggestion_idx}>\n"
                suggestion_idx += 1

    # Extract configuration information from the node
    data_dict_for_prompt = {
        "node_config": node.get_dict_for_node_optimizer(),
        "suggestions": suggestions,
    }

    return formulate_prompt(prompt_config, data_dict_for_prompt)


def formulate_prompt_for_sop_optim(
    prompt_config, sop: SOP, case_list: list[Case], consider_case_loop=True
):
    """
    Formulate a prompt for SOP optimization.

    This function creates a prompt for the SOP optimizer by extracting necessary variables from the
    provided SOP and case list, and structuring them according to the prompt configuration.

    Args:
        prompt_config (dict): Configuration for the prompt.
        sop (SOP): SOP instance from which to extract configuration data.
        case_list (list[Case]): List of Case instances to extract data from.
        consider_case_loop (bool, optional): Whether to include the case results directly in the loop_data.
            If True, each case is included in loop_data; otherwise, only the first case is used as a simple variable.
            Defaults to True.

    Returns:
        str: The formulated prompt based on the provided configuration and data.
    """
    all_needed_variable_name = get_config_needed_variables(prompt_config)

    # Retrieve information from the SOP, i.e., the configuration
    data_dict_for_prompt = {
        "sop_config": sop.get_dict_for_sop_optimizer(),
        "loop_data": [],
    }

    # Extract information from the case_list based on whether it is considered a loop variable
    if consider_case_loop:
        # Extract information from the case_list and add it to loop_data
        for idx, case in enumerate(case_list):
            case_data = case.get_dict_for_sop_optimizer(all_needed_variable_name)
            case_data["index"] = idx + 1
            data_dict_for_prompt["loop_data"].append(case_data)
    else:
        # Treat the case information as a simple variable, only extracting the first case from the case_list
        # This applies when sop is in backward mode, with only one case, hence no need to wrap in a loop
        if len(case_list) > 1:
            print(
                "Warning: case_list length is greater than 1, but not considered as a loop variable. Only the first case information will be extracted."
            )
        case = case_list[0]
        case_data_dict = case.get_dict_for_sop_optimizer(all_needed_variable_name)
        if "idx" in all_needed_variable_name or "index" in all_needed_variable_name:
            case_data_dict["index"] = 1
        data_dict_for_prompt.update(case_data_dict)

    return formulate_prompt(prompt_config, data_dict_for_prompt)
