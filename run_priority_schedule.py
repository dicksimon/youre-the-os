
from lib import scheduler_extended 


class RunPrioritySchedule(scheduler_extended.SchedulderExtended):


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
    
        #Create list with all processes in descending starvation level
        self.cpu_owner = self.remove_io_blocked_processes(self.cpu_owner)

        if len (self.cpu_owner) < self.cpu_count:
            num_cpu_free = self.cpu_count - len(self.cpu_owner)
            starvation_list = list() 
            for starvation_level, process_list in self.starvation.items():
                for process in process_list:
                    starvation_list.append(process[0])

            starvation_list_copy = starvation_list.copy()
            for process in starvation_list_copy:
                if process in self.cpu_owner:
                    starvation_list.remove(process)
            ##remove processes that are waiting for io-events
            sched_cpu = self.remove_io_blocked_processes(starvation_list)
            sched_cpu = sched_cpu[:num_cpu_free]
            self.cpu_owner = self.cpu_owner + sched_cpu

        #clean io_queue
        self.clean_io_queue()

        
        #update ram schedule 
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(self.cpu_owner))
            
        #update cpu schedule
        self.update_cpu_schedule(self.cpu_owner)
        
 


#
# the main entrypoint to run the scheduler
#
# it expects a callable `run_os`
#
# it receives a list of events generated from processes/pages
# see `src/lib/event_manager` for generated events
#
# it should return a list of events to happen
#

run_os = RunPrioritySchedule()
