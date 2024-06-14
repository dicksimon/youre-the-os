
from lib import scheduler_extended 

class RunPriorityBlocking(scheduler_extended.SchedulderExtended):

    cpu_owner = []

    def on_PROC_STARV(self, pid, starvation_level):
        if pid in self.cpu_owner and not self.processes[pid].has_ended:
            self.cpu_owner.remove(pid)


    def on_PROC_KILL(self, pid):
        if pid in self.cpu_owner:
            self.cpu_owner.remove(pid)


    def on_PROC_TERM(self, pid):
        if pid in self.cpu_owner:
            self.cpu_owner.remove(pid)

      
    def schedule(self):
    
        highest_starvation_level_ready = list()
        highest_starvation_level_blocked = list()
        for starvation_level, process_list in self.starvation.items():
            if starvation_level == 5:
                for process in process_list:
                    if self.is_process_waiting_for_io(process[0]):
                        highest_starvation_level_blocked.append(process[0])
                    else:
                        highest_starvation_level_ready.append(process[0])

        highest_starvation_level = highest_starvation_level_ready + highest_starvation_level_blocked
        num_starving_processes = len (highest_starvation_level)

        self.cpu_owner = highest_starvation_level
        
        if  num_starving_processes < self.cpu_count:            
            num_cpu_free = self.cpu_count - len(self.cpu_owner)
            sched_cpu = list() 
            for starvation_level, process_list in self.starvation.items():
                if starvation_level != 5:
                    for process in process_list:
                        if not self.is_process_waiting_for_io(process[0]):
                            sched_cpu.append(process[0])
            sched_cpu = sched_cpu[:num_cpu_free]
            self.cpu_owner = self.cpu_owner + sched_cpu


        elif num_starving_processes > self.cpu_count:
            self.cpu_owner = self.trim_process_list(self.cpu_owner)

        

        #clean io_queue
        self.clean_io_queue()

        #update ram schedule 
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(self.cpu_owner))
            
        #update cpu schedule
        self.update_cpu_schedule(self.cpu_owner)
        

run_os = RunPriorityBlocking()
