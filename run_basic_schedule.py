
from lib import scheduler_extended 


class RunBasicSchedule(scheduler_extended.SchedulderExtended):


    
    def schedule(self):
    
        self.clean_io_queue()


        #Create list with all processes in descending starvation level
        sched_order = list() 
        for starvation_level, process_list in self.starvation.items():
            sched_order = sched_order + process_list

        sched_order_new = sched_order.copy() 
        ##remove processes that are waiting for io-events   
        for process in sched_order:
            if self.is_process_waiting_for_io(process):
                sched_order_new.remove(process)
                    
        ##trim sched_order to available cpu slots
        sched_order_new = sched_order_new[:self.cpus_active_limit] 
        new_cpus_active = set()
        new_cpus_active.update(sched_order_new)


        self.update_cpu_schedule(new_cpus_active)    
        new_pages_in_ram = self.calculate_ram_from_cpu_schedule(self.cpus_active)
        self.update_ram_schedule(new_pages_in_ram);
        


run_os = RunBasicSchedule()
