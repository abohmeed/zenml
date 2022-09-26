#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
"""CLI for manipulating ZenML local and global config file."""

import os
from typing import TYPE_CHECKING, Optional

import click
import yaml
from rich.markdown import Markdown

from zenml.cli import utils as cli_utils
from zenml.cli.cli import TagGroup, cli
from zenml.config.global_config import GlobalConfiguration
from zenml.config.store_config import StoreConfiguration
from zenml.console import console
from zenml.enums import CliCategories, LoggingLevels
from zenml.repository import Repository
from zenml.utils import yaml_utils
from zenml.utils.analytics_utils import AnalyticsEvent, track_event

if TYPE_CHECKING:
    pass


# Analytics
@cli.group(cls=TagGroup, tag=CliCategories.MANAGEMENT_TOOLS)
def analytics() -> None:
    """Analytics for opt-in and opt-out."""


@analytics.command("get")
def is_analytics_opted_in() -> None:
    """Check whether user is opt-in or opt-out of analytics."""
    gc = GlobalConfiguration()
    cli_utils.declare(f"Analytics opt-in: {gc.analytics_opt_in}")


@analytics.command("opt-in", context_settings=dict(ignore_unknown_options=True))
def opt_in() -> None:
    """Opt-in to analytics."""
    gc = GlobalConfiguration()
    gc.analytics_opt_in = True
    cli_utils.declare("Opted in to analytics.")
    track_event(AnalyticsEvent.OPT_IN_ANALYTICS)


@analytics.command(
    "opt-out", context_settings=dict(ignore_unknown_options=True)
)
def opt_out() -> None:
    """Opt-out of analytics."""
    gc = GlobalConfiguration()
    gc.analytics_opt_in = False
    cli_utils.declare("Opted out of analytics.")
    track_event(AnalyticsEvent.OPT_OUT_ANALYTICS)


# Logging
@cli.group(cls=TagGroup, tag=CliCategories.MANAGEMENT_TOOLS)
def logging() -> None:
    """Configuration of logging for ZenML pipelines."""


# Setting logging
@logging.command("set-verbosity")
@click.argument(
    "verbosity",
    type=click.Choice(
        list(map(lambda x: x.name, LoggingLevels)), case_sensitive=False
    ),
)
def set_logging_verbosity(verbosity: str) -> None:
    """Set logging level.

    Args:
        verbosity: The logging level.

    Raises:
        KeyError: If the logging level is not supported.
    """
    verbosity = verbosity.upper()
    if verbosity not in LoggingLevels.__members__:
        raise KeyError(
            f"Verbosity must be one of {list(LoggingLevels.__members__.keys())}"
        )
    cli_utils.declare(f"Set verbosity to: {verbosity}")


# Global store configuration
@cli.group(cls=TagGroup, tag=CliCategories.MANAGEMENT_TOOLS)
def config() -> None:
    """Manage the global store ZenML configuration."""



@config.command("explain")
def explain_config() -> None:
    """Explains the concept of ZenML configurations."""
    with console.pager():
        console.print(
            Markdown(
                """
The ZenML configuration that is managed through `zenml config` determines the
type of backend that ZenML uses to persist objects such as Stacks, Stack
Components and Flavors.

The default configuration is to store all this information on the local
filesystem:

```
$ zenml config describe
Running without an active repository root.
No active project is configured. Run zenml project set PROJECT_NAME to set the active project.
The global configuration is (/home/stefan/.config/zenml/config.yaml):
 - url: 'sqlite:////home/stefan/.config/zenml/zenml.db'
The active stack is: 'default' (global)
The active project is not set.
```

The `zenml config set` CLI command can be used to change the global
configuration as well as the local configuration of a specific repository to
store the data on a remote ZenML server.

To change the global configuration to use a remote ZenML server, pass the URL
where the server can be reached along with the authentication credentials:

```
$ zenml config set --url=http://localhost:8080 --username=default --project=default --password=
Updated the global store configuration.

$ zenml config describe
Running without an active repository root.
The global configuration is (/home/stefan/.config/zenml/config.yaml):
 - url: 'http://localhost:8080'
 - username: 'default'
The active stack is: 'default' (global)
The active project is: 'default' (global)
```

To switch the global configuration back to the default local store, pass the
`--local-store` flag:

```
$ zenml config set --local-store
Using the default store for the global config.

$ zenml config describe
Running without an active repository root.
The global configuration is (/home/stefan/.config/zenml/config.yaml):
 - url: 'sqlite:////home/stefan/.config/zenml/zenml.db'
The active stack is: 'default' (global)
The active project is: 'default' (global)
```
"""
            )
        )
