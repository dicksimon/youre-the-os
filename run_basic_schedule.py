
from lib import scheduler_extended 


class RunBasicSchedule(scheduler_extended.SchedulderExtended):

    
    def update_cpu_schedule(self):
    
        #check if more slots than processes are available
        if len(self.processes) <= self.cpu_count:
            for process in self.processes.keys():
                if process not in self.cpu_owners:
                    self.move_process_to_cpu(process)
        else:
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
            
        
            pages_order = list()
            ##create list of needed pages in ram
          
            for entry in sched_order_new:
                process = self.processes.get(entry)
                for page in process.pages:
                    if (page.key in self.pages_used):
                        pages_order.append(page.key)

            pages_order = pages_order[:self.ram_count]
            new_pages_in_ram = set()
            new_pages_in_ram.update(pages_order)             
            ##update ram schedule
            pages_to_swap = self.pages_ram.difference(new_pages_in_ram)
            for page in pages_to_swap:
                self.move_page_to_swap(page)
            
            pages_to_ram = new_pages_in_ram.difference(self.pages_ram)
            for page in pages_to_ram:
                self.move_page_to_ram(page)

            #calculate instruction set
            new_cpu_owners = set()
            new_cpu_owners.update(sched_order_new)
        
            #find processes that need to be removed
            processes_to_release = self.cpu_owners.difference(new_cpu_owners)

            for process in processes_to_release:
                self.release_process_from_cpu(process)

            #update cpu ownership 
            processes_to_add = new_cpu_owners.difference(self.cpu_owners) 
            for process in processes_to_add:
                self.move_process_to_cpu(process)

    def schedule(self):

        #self.cleanup_processes()
        self.clean_io_queue()
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
