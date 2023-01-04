import psutil
import os


class SystemMonitoring:
    def __init__(self):
        super(SystemMonitoring, self).__init__()

    def __del__(self):
        # print("The object is destroyed.")
        pass

    # noinspection PyMethodMayBeStatic
    def cpu_usage(self):
        cpu = f'CPU {psutil.cpu_percent():.1f}% {psutil.cpu_freq().current / 1024:.2f}GHz'

        return cpu

    # noinspection PyMethodMayBeStatic
    def memory_usage(self):
        memo = psutil.virtual_memory()
        avail = memo.available / 1024 ** 3
        mem_usage = f'Memory {memo.used / 1024 ** 3:.1f}/{memo.total / 1024 ** 3:.1f}GB ({memo.percent:.1f}%)'

        return mem_usage

    # noinspection PyMethodMayBeStatic
    def process_mem_usage(self, pid=None):
        memo: str = ''

        try:
            process = psutil.Process(os.getpid() if pid is None else pid)

            mem_per = process.memory_percent()
            mem_siz = process.memory_full_info().uss

            # 하위 process check
            children = process.children(recursive=True)
            if len(children) > 0:
                for cid in children:
                    mem_per += cid.memory_percent()
                    mem_siz += cid.memory_full_info().uss

            memo = f'Process {mem_siz / 2. ** 20:.1f}MB({mem_per:.1f}%)'
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

        return memo

    def whole_process_mem_usage(self):
        for proc in psutil.process_iter():
            try:
                proc_name = proc.name()
                proc_id = proc.pid
                print(f'name: {proc_name}, pid: {proc_id}, {self.process_mem_usage(pid=proc_id)}')
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass


def system_monitoring():
    sysmon = SystemMonitoring()
    return sysmon.cpu_usage(), sysmon.memory_usage(), sysmon.process_mem_usage()


if __name__ == "__main__":
    sm = SystemMonitoring()
    sm.whole_process_mem_usage()

    a, b, c = system_monitoring()
    print(f'{a}, {b}, {c}')

    # running = True
    # currentProcess = psutil.Process()
    # while running:
    #     print(currentProcess.cpu_percent(interval=1))

    # for process in psutil.process_iter():
    #     print(process.name() + "\t" + str(process.pid) + '\t' + str(process.cpu_percent()))
