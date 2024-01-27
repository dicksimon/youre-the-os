
from lib import scheduler_extended 


class RunBasicSchedule(scheduler_extended.SchedulderExtended):

    def update_cpu_schedule(self):
    
        #Überprüfe ob es mehr slots als wartende Prozesse gibt
        if len(self.processes) <= self.cpu_count:
            for process in self.processes.keys():
                if process not in self.cpu_owners:
                    self.move_process_to_cpu(process)
        else:
            #Create list with all processes in descending starvation level
            sched_order = list() 
            for starvation_level, process_list in self.starvation.items():
                sched_order = sched_order + process_list

            #Create set with n entries
            new_cpu_owners = set()
            new_cpu_owners.update(sched_order[:self.cpu_count])
        


            #Entferne Prozesse von CPU, die nicht mehr die erforderliche Priorität haben
            to_remove = self.cpu_owners.difference(new_cpu_owners)
            
            for process in to_remove:
                self.relase_process_from_cpu(process)

            #Weise neue Prozesse freien CPUs zu
            to_add = new_cpu_owners.difference(self.cpu_owners) 
            for process in to_add:
                self.move_process_to_cpu(process)

    def schedule(self):
        self.clean_io_queue()
        self.cleanup_processes()
        self.update_cpu_schedule()

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
