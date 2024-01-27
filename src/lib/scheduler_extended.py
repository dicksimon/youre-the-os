from lib import scheduler_base 


class SchedulderExtended(scheduler_base.SchedulerBase):
    
    
    def cleanup_processes(self):
        for process in self.terminated_processes:
            self.relase_process_from_cpu(process)    
            self.terminated_processes.remove(process)

        
    def is_process_executable(self, pid):
        pass
    
    def sort_processes_starvation(self):
        pass    
    
    
    def clean_io_queue(self):
        x = range(self.io_queue.io_count)
        for n in  x:
            self.do_io()