from dataclasses import dataclass, field

@dataclass
class AppState:
    choosen_ips: list = field(default_factory=list)
    founded_ips: list = field(default_factory=list)
    did_adb_work: bool = False
    did_nmap_work: bool = False
    last_commands: dict = field(default_factory=dict)

    shared_adb_processes: list = field(default_factory=list)
    shared_nmap_processes: list = field(default_factory=list)
    active_processes: list = field(default_factory=list)
    button_references: list = field(default_factory=list)
    active_adb_list: list = field(default_factory=list)
    current_lang: str = "en"
    current_theme: str = ""

global_state = AppState()