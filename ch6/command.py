import abc
import os

history = []

class Command(object):
    """ The command interface."""

    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    def undo(self):
        pass

class LsCommand(Command):
    """Concrete command that emulates ls"""
    def __init__(self,receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.show_current_dir()

    def undo(self):
        pass

class LsReceiver(object):
    def show_current_dir(self):
        """The receiver knows how to execute the command."""
        cur_dir = '.\\'

        filenames = []
        for filename in os.listdir(cur_dir):
            if os.path.isfile(os.path.join(cur_dir,filename)):
                filenames.append(filename)
        print 'Content of dir: ', ' '.join(filenames)

class TouchCommand(Command):
    def __init__(self,receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.create_file()

    def undo(self):
        self.receiver.delete_file()


class TouchReceiver(object):
    def __init__(self,filename):
        self.filename = filename
    def create_file(self):
        """Actual implementation of unix touch"""
        with file(self.filename,'a'):
            os.utime(self.filename,None)

    def delete_file(self):
        try:
            os.remove(self.filename)
        except ValueError:
            print 'no file named',self.filename

class RmCommand(Command):
    def __init__(self,receiver):
        self.receiver = receiver
    def execute(self):
        self.receiver.delete_file()
    def undo(self):
        self.receiver.undo()

class RmReceiver(object):
    def __init__(self,filename):
        self.filename = filename
        self.backup_name = None

    def delete_file(self):
        """Deletes file with createing backup to restore it in undo method"""
        self.backup_name = '.' + self.filename
        os.rename(self.filename, self.backup_name)

    def undo(self):
        original_name = self.backup_name[1:] # remove .
        os.rename(self.backup_name, original_name)
        self.backup_name = None

class Invoker(object):
    def __init__(self,create_file_commands, delete_file_commands):
        self.create_file_commands = create_file_commands
        self.delete_file_commands = delete_file_commands
        self.history = []

    def create_file(self):
        print 'Creating file...'

        for command in self.create_file_commands:
            command.execute()
            self.history.append(command)
        print 'File created.\n'

    def delete_file(self):
        print "Deleting files..."
        for command in self.delete_file_commands:
            command.execute()
            self.history.append(command)
        print 'File deleted.\n'

    def undo_all(self):
        print 'Undo all...'

        for command in reversed(self.history):
            command.undo()

        print "Undo all finished."

if __name__ == '__main__':
    # client
    # List files in current directory
    ls_receiver = LsReceiver()
    ls_command = LsCommand(ls_receiver)

    # Create a file
    touch_receiver = TouchReceiver('Test file')
    touch_command = TouchCommand(touch_receiver)

    # Delete created file
    rm_receiver = RmReceiver("Test file")
    rm_command = RmCommand (rm_receiver)

    create_file_commands = [ls_command, touch_command, ls_command]
    delete_file_commands = [ls_command, rm_command, ls_command]

    invoker = Invoker(create_file_commands, delete_file_commands)

    invoker.create_file()
    invoker.delete_file()
    invoker.undo_all()