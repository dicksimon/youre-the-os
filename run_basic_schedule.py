
from lib import scheduler_extended 


class RunBasicSchedule(scheduler_extended.SchedulderExtended):

      
    
    def schedule(self):
    

        self.clean_io_queue()
        #Create list with all processes in descending starvation level
        sched_order = list() 
        for starvation_level, process_list in self.starvation.items():
            sched_order = sched_order + process_list

        ##remove processes that are waiting for io-events
        sched_order_new = sched_order.copy()    
        for process in sched_order:
            if self.is_process_waiting_for_io(process):
                sched_order_new.remove(process)

        ##trim sched_order to available cpu slots
        sched_order_new = sched_order_new[:self.cpu_count] 
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(sched_order_new))
                

        #calculate instruction set
        new_cpus_active = set()
        new_cpus_active.update(sched_order_new)
        self.update_cpu_schedule(new_cpus_active)
 


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

run_os = RunBasicSchedule()
