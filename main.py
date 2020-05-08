import tkinter as tk
from tk_html_widgets import HTMLLabel
# from tkinterhtml import HtmlFrame
from tkinter import ttk
from tkinter import messagebox
import random
from pprint import pprint
import threading
import time
from collections import OrderedDict
from copy import deepcopy


def read_file(path):
    with open(path, 'r') as f:
        return f.read()


class ValidatorFunctor:
    def __init__(self, upperbound=None, lowerbound=None, validation_func=int, converion_func=int, throw=True, return_self=True, action=None, action_args=None):
        self.upperbound         = upperbound
        self.lowerbound         = lowerbound
        self.validation_func    = validation_func
        self.converion_func     = converion_func
        self.throw              = throw
        self.action             = action
        self.action_args        = action_args
        self.return_self        = return_self


    def check(self, x):
        try:
#            print('x is: ', x)
            if self.validation_func:
                if not self.validation_func(x):
                    raise Exception('Validation failed')

            if self.converion_func:
                x = self.converion_func(x)

            if self.upperbound:
                if x > self.upperbound:
                    raise Exception('Upper bound exceeded')
            if self.lowerbound:
                if x < self.lowerbound:
                    raise Exception('Lower bound exceeded')

            return True if not self.return_self else x
        except:
            if self.throw:
                raise
            else:
                if self.action:
                    self.action(*self.action_args) if self.action_args else self.action()
                else:
                    return False


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


class Algorithm:
    def __init__(self, grid, algo, callback=lambda *args: True, getter=lambda a: a):
        if not grid:
            raise Exception('Empty grid given, nothing to process')
        self.maxy = len(grid[0])
        self.maxx = len(grid)
        self.grid = grid
        self.callback = callback
        self.getter = getter
        self.algo = algo


    def run(self):
        return self.algo(self)

    # wanted to make it static
    def _fill_copy_grid(self, grid): # grid must be a square matrix
        grid_copy = [[self.getter(self.grid[x][y]) for y in range(len(grid[x]))] for x in range(len(grid))]
        prev = 0
        grid_len = len(grid)

        try:
            for indx in range(grid_len - 1, grid_len - 2, -1):
                grid_copy[indx][0] += prev
                prev = self.getter(grid[indx][0])

                _prev = 0
                for i in range(len(grid[indx])):
                    grid_copy[indx][i] += _prev
                    _prev = grid_copy[indx][i]


            for indx in range(grid_len - 2, -1, -1):
                grid_copy[indx][0] += prev
                prev = grid_copy[indx][0]

            for x in range(grid_len - 2, -1, -1):
                for y in range(1, len(grid[x])):
                    grid_copy[x][y] = self.getter(grid[x][y]) + max([grid_copy[x+1][y], grid_copy[x+1][y-1], grid_copy[x][y-1]])
        except IndexError:
            grid_copy = []

        return grid_copy

    # @staticmethod
    # def _create_neighbours_dict(x, y, grid):
    #     neighbours = {}

    #     print('x:', x)
    #     print('y:', y)
    #     if (x-1 < 0 and x != 0) or (y-1 < 0 and y != 0):
    #         x = len(grid) + 1

    #     try:
    #         neighbours[grid[x+1][y]] = (x+1, y)
    #     except IndexError:
    #         print('true')
    #         pass
    #     try:
    #         neighbours[grid[x+1][y-1]] = (x+1, y-1)
    #     except IndexError:
    #         print('true')
    #         pass
    #     try:
    #         neighbours[grid[x][y-1]] = (x, y-1)
    #     except IndexError:
    #         print('true')
    #         pass

    #     print('neighbours: ', neighbours)
    #     return neighbours


    @staticmethod
    def _create_neighbours_dict(x, y, grid):
        #TODO: REFACTOR THIS technical debt
#        print('x:', x)
#        print('y:', y)
        neighbours = {}
        try:
            if x < 0 or y < 0:
                raise IndexError
            try:
                neighbours[grid[x+1][y]] = (x+1, y)
            except IndexError:
                pass
            try:
                if y-1 < 0:
                    raise IndexError
                neighbours[grid[x+1][y-1]] = (x+1, y-1)
            except IndexError:
                pass
            try:
                if y-1 < 0:
                    raise IndexError
                neighbours[grid[x][y-1]] = (x, y-1)
            except IndexError:
                pass
        except IndexError:
            pass
#        print('neighbours: ', neighbours)
        return neighbours


    def dynamic_programming_method(self):
        grid_copy = self._fill_copy_grid(self.grid)
        # return grid_copy

        x = 0
        y = self.maxy - 1

        neighbours = self._create_neighbours_dict(x, y, grid_copy)#{grid_copy[x+1][y] : (x+1, y), grid_copy[x+1][y-1] : (x+1, y-1), grid_copy[x][y-1] : (x, y-1)}

        try:
            current = grid_copy[x][y]
            res_sum = current
            self.res_path = [(x, y,)]

            while x != self.maxx - 1 or y != 0:
                current = max(neighbours.keys())
                x, y = neighbours[current]
                self.res_path.append((x, y,))

                neighbours = self._create_neighbours_dict(x, y, grid_copy)

            self.res_path.reverse()
            self.res_path = tuple(self.res_path)

            self.greatest = res_sum
        except Exception as ex:
#            print(ex)
            import traceback
            traceback.print_exc()
            # self.greatest = 0
            # self.res_path = ()

        return {'PATH_SUM' : self.greatest, 'PATH' : self.res_path}


    def find_greatest(self):
        # self.current = None
        self.greatest = None

        self.res_path = ()
        # self.curr_path = []

        self._find_greatest(self.maxx - 1, 0, None, None)

        return {'PATH_SUM' : self.greatest, 'PATH' : self.res_path}


    def _find_greatest(self, currx, curry, current, curr_path=None):
        if curr_path == None:
            curr_path = ()

        if currx >= self.maxx or currx < 0:
            return
        if curry >= self.maxy or curry < 0:
            return

        if not current:
            current = self.getter(self.grid[currx][curry])
        else:
            current += self.getter(self.grid[currx][curry])

        curr_path = curr_path + ((currx, curry,),)
        self.callback(curr_path)

        if curry == self.maxy - 1 and currx == 0:
            if not self.greatest:
                self.greatest = current
                self.res_path = curr_path
            else:
                if current > self.greatest:
                    self.greatest = current
                    self.res_path = curr_path
            # return self.grid[currx][curry]
        self._find_greatest(currx, curry + 1, current, curr_path)
        self._find_greatest(currx - 1, curry, current, curr_path)
        self._find_greatest(currx - 1, curry + 1, current, curr_path)


    GREATEST = find_greatest
    DYNAMIC  = dynamic_programming_method


class ExampleApp(tk.Tk):
    PATH_DRAWER = 'path_coloring_thread'
    LABEL_PADDING = ' ' * 10
    PATH_TO_HOWTO_HTML = 'howTo.html'

    def __init__(self):
        self.threads = {}
        tk.Tk.__init__(self)
        self.init_ui()


    def start_timer(self):
        self.started_time = time.time()


    def end_timer(self, target=None, append_text='', prepend_text=''):
        time_diff = None

        if self.started_time:
            time_diff = time.time() - self.started_time

            if target:
                target.config(text=prepend_text + str(round(time_diff, 5)) + ' sec' + append_text)

        return time_diff


    def switch_statusbar(self, active=False):
        if self.statusbar:
            if active:
                self.statusbar.config(bg='salmon', fg='white', text='Executing...')
            else:
                self.statusbar.config(bg='light sky blue', fg='grey39', text='Idle')


    def recolor_if_killed(self, target, killed, color='white'):
        if killed and killed.stopped():
            target.highlight_all(color)
        return killed


    @staticmethod
    def validate_entry(entry, validateion_func=int):
        pass


    def check_task_alive(self, thread_name=PATH_DRAWER):
        return self.threads.get(thread_name) and self.threads[thread_name].isAlive()


    def decorator_task_alive(self, thread_name=PATH_DRAWER, action=None, return_on_err=True):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if self.check_task_alive(thread_name):
                    if action:
                        action()
                        if return_on_err: return None
                    else:
                        raise Exception('Thread alive')
                return func(*args, **kwargs)
            return wrapper
        return decorator


    @staticmethod
    def set_widget_text(widget, new_value=''):
        widget['text'] = new_value


    @staticmethod
    def message_task_runnig():
        messagebox.showerror('Error', 'Task is already running.\nYou need to stop it first')


    def draw_main(self, base):
        grid_width = 5
        grid_height = 5
        upperbound = 50
        lowerbound = -50

        grid_sizes = (5, 6, 7, 8, 9, 10)
        approaches = OrderedDict([('Brute force', Algorithm.GREATEST), ('Dynamic programming', Algorithm.DYNAMIC)])
        highlighting_options = OrderedDict([('Off', None), ('Lightning', 0), ('Very fast', 0.05), ('Fast', 0.15),('Medium', 0.25), ('Slow', 0.5), ('Very slow', 1)])

        path_highlighting_speed = highlighting_options['Very fast']
        approach = approaches['Brute force']

        t = SimpleTable(base, grid_height, grid_width, lowerbound, upperbound)

        @self.decorator_task_alive(thread_name=ExampleApp.PATH_DRAWER, action=self.message_task_runnig)
        def change_grid_height(event):
            nonlocal t
            nonlocal grid_height
            t.destroy()
            grid_height = int(dropdown.get())
            t = SimpleTable(base, grid_height, grid_width, lowerbound, upperbound)
            t.grid(row=1, column=1, padx=(10, 10))
#            print('THREADS: ', self.threads)

        @self.decorator_task_alive(action=self.message_task_runnig, thread_name=ExampleApp.PATH_DRAWER)
        def change_grid_width(event):
            nonlocal t
            nonlocal grid_width
            t.destroy()
            grid_width = int(dropdown2.get())
            t = SimpleTable(base, grid_height, grid_width, lowerbound, upperbound)
            t.grid(row=1, column=1, padx=(10, 10))
#            print('THREADS: ', self.threads)

        @self.decorator_task_alive(action=self.message_task_runnig, thread_name=ExampleApp.PATH_DRAWER)
        def change_upperbound(value):
            nonlocal t
            nonlocal upperbound
#            print('About to change upperbound to %d' % (value if value else '""'))
            t.destroy()
            upperbound = value
            t = SimpleTable(base, grid_height, grid_width, lowerbound, upperbound)
            t.grid(row=1, column=1, padx=(10, 10))
#            print('THREADS: ', self.threads)

        @self.decorator_task_alive(action=self.message_task_runnig, thread_name=ExampleApp.PATH_DRAWER)
        def change_lowerbound(value):
            nonlocal t
            nonlocal lowerbound
#            print('About to change lowerbound to %d' % (value if value else '""'))
            t.destroy()
            lowerbound = value
            t = SimpleTable(base, grid_height, grid_width, lowerbound, upperbound)
            t.grid(row=1, column=1, padx=(10, 10))
#            print('THREADS: ', self.threads)

        @self.decorator_task_alive(action=self.message_task_runnig, thread_name=ExampleApp.PATH_DRAWER)
        def change_speed(event):
            nonlocal path_highlighting_speed
#            print('About to change speed to %s' % (dropdown3.get() if dropdown3.get() else '""'))
            path_highlighting_speed = highlighting_options[dropdown3.get()] #!!!!!!!!!!! validate
#            print('Changed speed to %f' % path_highlighting_speed)
#            print('THREADS: ', self.threads)

        @self.decorator_task_alive(action=self.message_task_runnig, thread_name=ExampleApp.PATH_DRAWER)
        def change_approach(event):
            nonlocal approach
            approach = approaches[dropdown4.get()]
#            print('THREADS: ', self.threads)

        validate_upperbound = ValidatorFunctor(lowerbound=-999, upperbound=999
                                                                , validation_func=lambda x: int(x) >= lowerbound
                                                                , converion_func=int
                                                                , throw=False
                                                                , return_self=True
                                                                , action=messagebox.showerror
                                                                , action_args=("Error", f"Value must be integer between -999 and 999 inclusive;\nUpperbound must be greater/equal lowerbound\n"
                                                                f"Previous upperbound: {upperbound}\nPrevious lowerbound: {lowerbound}")
                                        )

        validate_lowerbound = ValidatorFunctor(lowerbound=-999, upperbound=999
                                                        , validation_func=lambda x: int(x) <= upperbound
                                                        , converion_func=int
                                                        , throw=False
                                                        , return_self=True
                                                        , action=messagebox.showerror
                                                        , action_args=("Error", f"Value must be integer between -999 and 999 inclusive;\nLowerbound must be less/equal upperbound\n"
                                                        f"Previous upperbound: {upperbound}\nPrevious lowerbound: {lowerbound}")
                                        )

        output_widget = tk.Frame(base)
        label_output_text = tk.Label(output_widget, text='Result: ')
        label_output = tk.Label(output_widget, text=ExampleApp.LABEL_PADDING, bg='white')
        output_clear_button = tk.Button(output_widget, text='Clear', command=lambda : self.set_widget_text(label_output, new_value=ExampleApp.LABEL_PADDING))
        label_output_text.grid(row=0, column=0)
        label_output.grid(row=0, column=1)
        output_clear_button.grid(row=0, column=2)

        buttons = tk.Frame(base)
        rerandom_grid_button = tk.Button(buttons, text='Rerandom grid', command=lambda : change_upperbound(upperbound))
        rerandom_grid_button.grid(row=0, column=0, columnspan=2, padx=(0, 15))

        label1 = tk.Label(buttons, text='Upperbound: ')
        label1.grid(row=1, column=0)
        input_frame1 = tk.Frame(buttons)
        entry1 = tk.Entry(input_frame1, width=20) #, borderwidth=2)
        submit_button1 = tk.Button(input_frame1, text='Ok', command=lambda : change_upperbound(validate_upperbound.check(entry1.get())))
        entry1.grid(row=0, column=0)
        submit_button1.grid(row=0, column=1)
        input_frame1.grid(row=2, column=0, columnspan=2)


        label2 = tk.Label(buttons, text='Lowerbound: ')
        label2.grid(row=3, column=0)
        input_frame2 = tk.Frame(buttons)
        entry2 = tk.Entry(input_frame2, width=20) #, borderwidth=2)
        submit_button2 = tk.Button(input_frame2, text='Ok', command=lambda : change_lowerbound(validate_lowerbound.check(entry2.get())))
        entry2.grid(row=0, column=0)
        submit_button2.grid(row=0, column=1)
        input_frame2.grid(row=4, column=0, columnspan=2)

        label3 = tk.Label(buttons, text='Grid height: ')
        dropdown = ttk.Combobox(buttons, value=grid_sizes)
        dropdown.current(0)
        dropdown.bind('<<ComboboxSelected>>', change_grid_height)
        label3.grid(row=5, column=0)
        dropdown.grid(row=6, column=0, columnspan=2)


        label4 = tk.Label(buttons, text='Grid width: ')
        dropdown2 = ttk.Combobox(buttons, value=grid_sizes)
        dropdown2.current(0)
        dropdown2.bind('<<ComboboxSelected>>', change_grid_width)
        label4.grid(row=7, column=0)
        dropdown2.grid(row=8, column=0, columnspan=2)


        label5 = tk.Label(buttons, text='Path highlighting: ')
        dropdown3 = ttk.Combobox(buttons, value=list(highlighting_options.keys()))
        dropdown3.current(2)
        dropdown3.bind('<<ComboboxSelected>>', change_speed)
        label5.grid(row=9, column=0)
        dropdown3.grid(row=10, column=0, columnspan=2)


        label6 = tk.Label(buttons, text='Approach: ')
        dropdown4 = ttk.Combobox(buttons, value=list(approaches.keys()))
        dropdown4.current(0)
        dropdown4.bind('<<ComboboxSelected>>', change_approach)
        label6.grid(row=11, column=0)
        dropdown4.grid(row=12, column=0, columnspan=2)

        start_terminate_btn_frame = tk.Frame(buttons)

        start_button = tk.Button(start_terminate_btn_frame, text='Go', command=
                                            lambda : [self.thread_walkt(t, sleep_time=path_highlighting_speed, draw=True if path_highlighting_speed != None else False
                                                , on_raise=lambda _ : messagebox.showerror('Error', 'Task is already running.\nYou need to stop it first')
                                                , send_res_action=lambda res : self.set_widget_text(label_output, str(res['PATH_SUM']).rjust(len(ExampleApp.LABEL_PADDING))) # .rjust(len(ExampleApp.LABEL_PADDING), ' ')
                                                , algo=approach
                                            ), self.switch_statusbar(active=True)
                                            , self.start_timer()] # , res_placeholders=[], update_method=
                                            , width=10)
        terminate_button = tk.Button(start_terminate_btn_frame, text='Stop', command=
                                            # lambda : messagebox.showinfo("Title", "Input invalid.")
                                            lambda : [self.recolor_if_killed(t, killed=self.threads[ExampleApp.PATH_DRAWER]).stop() if self.threads.get(ExampleApp.PATH_DRAWER) else None
                                            , self.switch_statusbar(active=False)]
                                            , width=10)

        start_button.grid(row=0, column=0)
        terminate_button.grid(row=0, column=1)

        start_terminate_btn_frame.grid(row=13, column=0, columnspan=2, pady=(10, 0))

        label_main = tk.Label(base, text='Find the greatest path', pady=10, font='Helvetica 11 bold')

        label_main.grid(row=0, column=0, columnspan=2)
        t.grid(row=1, column=1, padx=(10, 10))
        buttons.grid(row=1, column=0, padx=(10, 10))
        output_widget.grid(row=2, column=1, pady=(0, 10))

        # base.grid_rowconfigure(0, weight=1)
        # base.grid_columnconfigure(0, weight=1)
        # base.grid_columnconfigure(1, weight=1)

        # status = tk.Label(base, text="Idle", bd=1, relief=tk.SUNKEN, anchor="e")
        # status.grid(row=3, column=0, columnspan=100, sticky="sew")


    def terminate(self):
        self.destroy()


    def create_about_window(self):
        self.about_window = tk.Toplevel(self)
        name            = tk.Label(self.about_window, text='IndustriouSlime', font='Helvetica 11 bold')
        version         = tk.Label(self.about_window, text='Version: 1.0.0', anchor=tk.W)
        created_by      = tk.Label(self.about_window, text='Created by: Sergey Orlovskyi', anchor=tk.W)
        creation_date   = tk.Label(self.about_window, text='Createion date: 2020-05-07', anchor=tk.W)
        contact_info    = tk.Label(self.about_window, text='Contact info: 2blesteve@gmail.com', anchor=tk.W)
        purpose         = tk.Label(self.about_window, text='Purpose: App targeted at finding path with the greatest sum of nodes', anchor=tk.W)
        name.pack()
        version.pack(fill='both')
        created_by.pack(fill='both')
        creation_date.pack(fill='both')
        contact_info.pack(fill='both')
        purpose.pack(fill='both')


    def create_howto_window(self, source_html=''):
        self.howto_window = tk.Toplevel(self)
        self.html_howto = HTMLLabel(self.howto_window, html=source_html)
        self.html_howto.pack(fill="both", expand=True)
        self.html_howto.fit_height()
        # self.html_howto = HtmlFrame(self.howto_window, horizontal_scrollbar="auto")
        # self.html_howto.set_content(source_html)
        # self.html_howto.pack()

    def draw_header(self):
        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Exit', command=self.terminate)
        menubar.add_cascade(label='App', menu=filemenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='HowTo', command=lambda : self.create_howto_window(source_html=read_file(self.PATH_TO_HOWTO_HTML)))
        helpmenu.add_command(label='About', command=self.create_about_window)
        menubar.add_cascade(label='Help', menu=helpmenu)

        supportmenu = tk.Menu(menubar, tearoff=0)
        supportmenu.add_command(label='Donate', command=lambda : messagebox.showinfo('Donate', 'Just kidding :)'))
        menubar.add_cascade(label='Support', menu=supportmenu)

        self.menubar = menubar
        self.config(menu=self.menubar)


    def draw_footer(self):
        self.statusbar = tk.Label(self, text='Idle ', bd=1, relief=tk.SUNKEN, anchor=tk.E, bg='white')
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.switch_statusbar(active=False)


    def init_ui(self):
        self.base = tk.Frame()
        self.base.pack()

        self.draw_header()
        self.draw_footer()

        self.draw_main(self.base)

        # footer = tk.Frame()
        # footer.pack()


    def thread_walkt(self, t, sleep_time=0.05, draw=True, send_res_action=None, on_raise=None, algo=Algorithm.GREATEST):
        try:
            if self.threads.get(ExampleApp.PATH_DRAWER) and self.threads[ExampleApp.PATH_DRAWER].isAlive():
                raise Exception('Thread is still runnig')
            thread = StoppableThread(target=self.walkt, args=(t, sleep_time, draw, send_res_action, algo,))
            thread.daemon = True
            thread.start()
            self.threads[ExampleApp.PATH_DRAWER] = thread
        except Exception as ex:
            if on_raise:
                on_raise(ex)
            else:
                raise ex


    @staticmethod
    def raise_stop():
        raise 'The thread has been stopped'


    def walkt(self, t, sleep_time, draw=True, send_res_action=None, algo=Algorithm.GREATEST):
#        print('sleep time: %f' % sleep_time if sleep_time else '""')
#        print('draw: %d' % draw  if draw else '""')
        path_tracker = t.createDynamicTracker(idle_time=sleep_time)
        # path_tracker.h()
        callback_ = (lambda path: path_tracker.highlight_path_common(path, 'red') if not threading.current_thread().stopped() else self.raise_stop()) if draw \
                    else (lambda path: path if not threading.current_thread().stopped() else self.raise_stop())

        a = Algorithm(t._widgets, algo, callback=callback_, getter=lambda a: int(a['text']))
        res = None
        try:
            res = a.run()
            t.highlight_all('white')
            t.highlight_path(res['PATH'], 'green2')
            if send_res_action: send_res_action(res)
            self.threads[self.PATH_DRAWER].stop()       # TODO: don't like this approach, bounding function to thread name; threading.current_thread doesn't work
            self.switch_statusbar(active=False)
            self.end_timer(target=self.statusbar, prepend_text='Executed in ')
        except:
            pass
#        print('printing res')
#        pprint(res)



class SimpleTable(tk.Frame):
    def __init__(self, parent, rows=10, columns=2, lowerbound=-10, upperbound=10, rand_func=random.randint, color='white'):
        # use black background so it 'peeks through' to
        # form grid lines
#        print('rows: ', rows)
#        print('cols: ', columns)
#        print('-' * 20)
        tk.Frame.__init__(self, parent)
        self.rows = rows
        self.columns = columns
        self.color = color
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = tk.Label(self, text=f'{rand_func(lowerbound, upperbound)}',
                                 borderwidth=1, width=10, relief='solid', bg=self.color)
                label.grid(row=row, column=column, sticky='nsew', padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        # for column in range(columns):
        #     self.grid_columnconfigure(column, weight=1)

    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)


    def setcolor(self, row, column, color):
        widget = self._widgets[row][column]
        widget.configure(bg=color)


    def highlight_path(self, path, color):
        for x, y in path:
            self.setcolor(x, y, color)


    def highlight_all(self, color):
        for i, row in enumerate(self._widgets):
            for j, _ in enumerate(row):
                self.setcolor(i, j, color)


    def highlight_all_except(self, color, path):
        for i, row in enumerate(self._widgets):
            for j, _ in enumerate(row):
                if (i, j) not in path:
                    self.setcolor(i, j, color)


    def createDynamicTracker(self, idle_time=0.05):
        return self.DynamicPathHighlighter(self, idle_time)



    class DynamicPathHighlighter:
        def __init__(self, outer_class, idle_time):
            self.outer_table = outer_class
            self.idle_time   = idle_time


        def highlight_path_common(self, path, color):
            self.outer_table.highlight_all_except('white', path)
            self.outer_table.highlight_path(path, color)
            time.sleep(self.idle_time)


if __name__ == '__main__':
    app = ExampleApp()
    app.title('IndustriouSlime')
    app.iconbitmap('icons\\terminal.ico')
    # tk.Button(app, text='Exit', command=app.quit, width=8).grid(column=0, row=1, pady=10)
    app.mainloop()
