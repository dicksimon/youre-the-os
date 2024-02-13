
from enum import Enum

log_page = Enum('log_pages',['CREATED_SWAP','CREATED_RAM','MOVED_SWAP', 'MOVED_RAM', 'FREED'])


class Logger:
    
    processes: dict[int,list] = {}
    pages: dict[tuple[int,int],list] = {}


    def create_page(self, key, ram):
       if ram:
           self.pages.update({key:[log_page.CREATED_RAM]})
       else:
            self.pages.update({key:[log_page.CREATED_SWAP]})

    def move_page(self, key, ram):
        if ram:
            self.pages[key].append(log_page.MOVED_RAM)
        else:
            self.pages[key].append(log_page.MOVED_SWAP)
        pass

    def free_page(self,key):
        self.pages[key].append(log_page.FREED)