from dataclasses import dataclass, field

@dataclass
class AppState:
    choosen_ips: list = field(default_factory=list)
    founded_ips: list = field(default_factory=list)
    created_card_ips: list = field(default_factory=list)
    check_ips: list = field(default_factory=list)
    ongoing_processes_list: list = field(default_factory=list)
    ongoing_processes_adb_list: list = field(default_factory=list)
    checkbutton_ips: list = field(default_factory=list)

    did_adb_work: bool = False
    did_nmap_work: bool = False
    is_expanded: bool = False
    stopla2: bool = False
    is_process_running: bool = False
    last_commands: dict = field(default_factory=dict)
    ip_card_map: dict = field(default_factory=dict)

    shared_adb_processes: list = field(default_factory=list)
    shared_nmap_processes: list = field(default_factory=list)
    active_processes: list = field(default_factory=list)
    button_references: list = field(default_factory=list)
    active_adb_list: list = field(default_factory=list)
    active_nmap_list: list = field(default_factory=list)
    adb_connect_choosen_ips: list = field(default_factory=list)
    current_lang: str = "en"
    current_theme: str = ""

    #add for adb connect process:
    """self.check_ips = []  # OK
    self.ongoing_processes_list = []  # Ok
    self.ongoing_processes_adb_list = []  OK
    self.checkbutton_ips = []  # Ok
    self.stopla2 = False  # Ok
    self.is_process_running = False  # OK"""

global_state = AppState()