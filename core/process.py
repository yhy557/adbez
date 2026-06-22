import logging
import os
import platform
import psutil
import subprocess
import threading

class ProcessRegistry:
    def __init__(self):
        self.processes = {}

    def start(self, process_command) -> psutil.Popen:
        process = psutil.Popen(
            process_command, shell=False, stdout=subprocess.PIPE, text=True
        )
        self.processes[process.pid] = {"object": process}
        employee = threading.Thread(target= lambda: self._watch_and_remove(process), daemon=True)
        employee.start()
        logging.debug(f"[start] processes is: {self.processes}")
        return process

    def remove(self, process_pid):
        if process_pid:
            system_os = platform.system()
            try:
                if system_os == "Windows":
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

                    subprocess.call(
                        [
                            'taskkill', '/F', '/T', '/PID',
                            str(process_pid)
                        ],
                        startupinfo=startupinfo
                    )
                else:
                    import signal
                    try:
                        os.kill(process_pid, signal.SIGTERM)
                        self.processes[process_pid]["object"].wait(1)
                    except subprocess.TimeoutExpired:
                        logging.debug("[stop_nmap]-The process is resisting, so it will be killed directly...")
                        os.kill(process_pid, signal.SIGKILL)
                self.processes.pop(process_pid, None)
                return True
            except Exception as e:
                logging.debug(
                    f"[stop_nmap]-Nmap scan is can't terminated: {e}")
                return False


    def get(self):
        pass

    def list_all(self):
        pass

    def get_stats(self):
        stats = {}
        logging.debug(f"[get_stats] called = {stats}")
        try:
            for pid, data in list(self.processes.items()):
                process_obj = data["object"]
                stats[pid] = {"ram": process_obj.memory_info().rss/1024**2, "cpu": process_obj.cpu_percent()}
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logging.error(f"Get stats is stopped = {e}")
        return stats

    def _watch_and_remove(self, process):
        process.wait()
        self.processes.pop(process.pid, None)

        

registry = ProcessRegistry()