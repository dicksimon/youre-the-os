
from lib import scheduler_extended 


class RunPrioritySchedule(scheduler_extended.SchedulderExtended):

    def get_events(self):
        pass

    def schedule(self):

        #clean io_queue
        self.clean_io_queue()

        
        #update ram schedule 
        self.update_ram_schedule(self.calculate_ram_from_cpu_schedule(self.cpu_owner))
            
        #update cpu schedule
        self.update_cpu_schedule(self.cpu_owner)
        

