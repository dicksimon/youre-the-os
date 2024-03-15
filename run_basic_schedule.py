
from lib import scheduler_extended 


class RunBasicSchedule(scheduler_extended.SchedulderExtended):

      
    def schedule(self):
    
        #Create list with all processes in descending starvation level
        starvation_list = list() 
        for starvation_level, process_list in self.starvation.items():
            for process in process_list:
                starvation_list.append(process[0])

        ##remove processes that are waiting for io-events
        sched_cpu = self.remove_io_blocked_processes(starvation_list)

        #clean io_queue
        self.clean_io_queue()

        ##trim sched_order to available cpu slots
        sched_cpu = self.trim_process_list(sched_cpu)

        #update ram schedule 
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(sched_cpu))
            
        #update cpu schedule
        self.update_cpu_schedule(sched_cpu)
 


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
