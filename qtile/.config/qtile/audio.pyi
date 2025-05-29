from typing import Any, Dict, Optional, Tuple, TypedDict

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText

class VolumeSettings(TypedDict):
    device: str
    thresholds: list[int]
    colors: list[str]
    icons: list[str]
    muted_icon: str

def run_cmd(cmd: list[str]) -> str: ...
def parse_wpctl_output(output: str) -> Tuple[int, bool]: ...
def format_span(icon: str, color: str, volume: int) -> str: ...

class AudioWidget(GenPollText):
    kind: str
    config: VolumeSettings
    device: str
    volume_step: int

    def __init__(
        self,
        kind: str = ...,
        device: Optional[str] = ...,
        update_interval: float = ...,
        volume_step: int = ...,
        **config: Any,
    ) -> None: ...
    def _get_volume_info(self, force_refresh: bool = ...) -> Tuple[int, bool]: ...
    def _format_display(self, volume: int, muted: bool) -> str: ...
    def _poll(self) -> str: ...
    def _execute_volume_cmd(self, cmd: list[str]) -> None: ...
    @expose_command()
    def volume_up(self) -> None: ...
    @expose_command()
    def volume_down(self) -> None: ...
    @expose_command()
    def toggle_mute(self) -> None: ...
    @expose_command()
    def get_state(self) -> Dict[str, Any]: ...

class MicWidget(AudioWidget):
    def __init__(self, **config: Any) -> None: ...
