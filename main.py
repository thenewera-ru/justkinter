from tkinter import Tk, Label, Button, StringVar
from time import sleep
from typing import Callable
from abc import abstractmethod
import threading


class TaskThread(threading.Thread):
    def __init__(self, task):
        """
        :param task: Reference to the wrapper around actual task holding threading.Thread() object
        :type task: AsyncTask
        """
        threading.Thread.__init__(self)
        self.task = task

    def run(self):
        try:
            self.task.get_task_pointer()(self.task.is_running)
        except Exception as e:
            print(repr(e))
        self.task.stop()


class Task:

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def is_running(self):
        pass


class AsyncTask(Task):

    def __init__(self, task_pointer):
        """
        :param task_pointer: Reference to the function, responsible for code execution (potentially time consuming)
        :type task_pointer: Callable
        """
        self.task_pointer = task_pointer
        self.thread = None
        self.running = False

    def get_task_pointer(self):
        return self.task_pointer

    def is_running(self):
        return self.running and self.thread.is_alive()

    def start(self):
        if not self.running:
            self.running = True
            self.thread = TaskThread(self)
            self.thread.start()

    def stop(self):
        self.running = False


class SyncTask(Task):

    def __init__(self, root_object, task_pointer, freq_mls):
        """
        :param root_object:  Root TK() object
        :param task_pointer: Reference to function to update timer label
        :type task_pointer: Callable
        :param freq_mls: Interval duration to check the task
        """
        self.root = root_object
        self.task_pointer = task_pointer
        self.freq_mls = freq_mls
        self.running = False

    def is_running(self):
        return self.running

    def start(self):
        self.running = True
        self.timeit()

    def stop(self):
        self.running = False

    def timeit(self):
        if self.is_running():
            # Launch the task
            self.task_pointer()
            # And until it is NOT done ---> call timeit() every @freq_mls milliseconds and check
            self.root.after(self.freq_mls, self.timeit)


class UnitTestGUI:

    def __init__(self, master):
        self.master = master
        master.title("¯\\_(ツ)_/¯")

        self.testButton = Button(
            self.master, text="Blocking", command=self.time_consuming_execution)
        self.testButton.pack()

        self.threaded_button = Button(
            self.master, text="Threaded", command=self.on_threaded_button)
        self.threaded_button.pack()

        self.cancelButton = Button(
            self.master, text="Stop", command=self.on_stop_button)
        self.cancelButton.pack()

        self.statusLabelVar = StringVar()
        self.statusLabel = Label(master, textvariable=self.statusLabelVar)
        self.statusLabel.pack()

        self.clickMeButton = Button(
            self.master, text="Click Me", command=self.on_click_button)
        self.clickMeButton.pack()

        self.clickCountLabelVar = StringVar()
        self.clickCountLabel = Label(master, textvariable=self.clickCountLabelVar)
        self.clickCountLabel.pack()

        self.threadedButton = Button(
            self.master, text="Timer", command=self.on_timer_button)
        self.threadedButton.pack()

        self.timerCountLabelVar = StringVar()
        self.timerCountLabel = Label(master, textvariable=self.timerCountLabelVar)
        self.timerCountLabel.pack()

        self.time_counter = 0

        self.click_counter = 0

        self.task = AsyncTask(self.time_consuming_execution)

        self.timer = SyncTask(self.master, self.update_timer_label, 1)

    def close(self):
        print("close")
        try:
            self.task.stop()
        except:
            pass
        try:
            self.timer.stop()
        except:
            pass
        self.master.quit()

    def on_threaded_button(self):
        print("Asynchronous execution without blocking the main UI i/o loop")
        try:
            self.task.start()
        except:
            pass

    def on_timer_button(self):
        print("Timing is fired up")
        self.timer.start()

    def on_stop_button(self):
        print("Stop() is clicked")
        try:
            self.task.stop()
        except:
            pass
        try:
            self.timer.stop()
        except:
            pass

    def on_click_button(self):
        self.click_counter += 1
        print(f"Click {str(self.click_counter)}")
        self.clickCountLabelVar.set(str(self.click_counter))

    def update_timer_label(self):
        print("Time it")
        self.time_counter += 1
        self.timerCountLabelVar.set(str(self.time_counter))

    def time_consuming_execution(self, is_running=None):
        print("Считаем полет до луны и обратно ... ... ...")
        for i in range(1, 10):
            try:
                if not is_running():
                    self.update_status("Stopped!")
                    return
            except:
                pass
            self.update_status(i)
            sleep(1.5)  # Simulate long running work...
        self.update_status("Done!")

    def update_status(self, status):
        print("Process Update: %s" % (status,))
        self.statusLabelVar.set(str(status))


if __name__ == '__main__':
    root = Tk()
    gui = UnitTestGUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.close)
    root.mainloop()
