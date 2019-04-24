from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
import matplotlib
from matplotlib.dates import num2date, date2num
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
import pandas as pd
import numpy as np
import math
import os

matplotlib.use('TkAgg')

class label_tool:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Acti :: Label Tool")
        self.parent.option_add('*tearOff', FALSE)
        self.parent.grid_rowconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        # Variables
        self.dataframe = None  # to store read data frame
        self.mouse_event = None  # mouse event
        self.labels = None  # to store user labels for marking sleep
        self.current_xlim = None  # store current x axis limits info
        self.button_1_pressed = False  # mouse left button press indicator
        self.pan_init_xlim = None  # panning event x axis limits info
        self.folder_dir = None  # data source directory
        self.folder_items = None  # indicates the file being worked on
        self.folder_labeled_dir = None  # results directory
        self.zoom_speed = 0.3  # zoom speed
        # UI Elements
        # menu
        self.menu_bar = Menu(self.parent)
        self.parent.config(menu=self.menu_bar)
        self.file_menu = Menu(self.menu_bar)
        self.file_menu.add_command(label='Open',
            command=self.btn_load)
        self.file_menu.add_command(label='Open Folder',
            command=self.btn_load_folder)
        self.file_menu.add_command(label='Save',
            command=self.btn_save, state='disabled')
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Set Result Folder',
            command=self.btn_labeled_folder)
        self.file_menu.add_separator()
        self.file_menu.add_command(label='Exit', comman=self.btn_exit)
        self.menu_bar.add_cascade(label='File', menu=self.file_menu)
        self.help_menu = Menu(self.menu_bar)
        self.help_menu.add_command(label='About', command=self.btn_about)
        self.menu_bar.add_cascade(label='Help', menu=self.help_menu)
        # structure
        self.upper_frame = ttk.Frame(self.parent)
        self.upper_frame.grid(column=0, row=0, sticky=(N,E,S))
        self.lower_frame = ttk.Frame(self.parent)
        self.lower_frame.grid(column=0, row=1, sticky=(N,W,E,S))
        # undo button
        self.btn_undo = Button(self.upper_frame, text="Undo",
                                command = self.btn_undo)
        self.btn_undo.grid(column=1, row=0, sticky=(E))
        # file list
        self.file_list = Listbox(self.parent, selectmode=SINGLE,
            selectbackground="purple")
        self.file_list.grid(column=1, row=1,sticky=(N,W,E,S))
        self.file_list.bind("<Double-Button-1>", self.read_selected_file)
        # canvas & figure
        self.fig = Figure()
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.lower_frame)
        self.plot_canvas._tkcanvas.pack(fill=BOTH, expand=True)
        # data and label subplots
        self.fig_plot_vm = self.fig.add_subplot(111, label='vm')
        self.fig_plot_label = self.fig_plot_vm.twinx()
        self.fig_plot_label.yaxis.set_ticks_position('none')
        self.fig_plot_label.get_yaxis().set_visible(False)
        self.fig.subplots_adjust(left=0.06, bottom=0.1, right=0.95,
            top=0.90, wspace=0, hspace=0)
        self.fig_plot_vm.set_title('Please Load Data File')
        self.fig_plot_vm.set_xlabel('Timestamp')
        self.fig_plot_vm.set_ylabel('VM Counts')
        self.fig_plot_vm.axhline(y=100, color='r', linestyle='--', alpha=0.5, linewidth=1)
        self.fig_plot_vm.axhline(y=500, color='r', linestyle='--', alpha=0.5, linewidth=1)
        self.fig_plot_vm.set_ylim([0, 3000])
        self.fig_plot_vm.yaxis.set_ticks_position('both')
        self.fig_plot_vm.tick_params(labelright=True)
        self.fig_plot_vm.grid(True, linewidth=0.2)
        self.cursor = Cursor(self.fig_plot_label,
                        horizOn = True,
                        vertOn = True,
                        color = 'green',
                        linewidth=0.3)
        # callbacks of plots
        self.plot_canvas.callbacks.connect('scroll_event', self.scroll_func)
        self.plot_canvas.callbacks.connect('key_press_event',
            self.key_press_func)
        self.plot_canvas.callbacks.connect('button_press_event',
            self.button_press_func)
        self.plot_canvas.callbacks.connect('button_release_event',
            self.button_release_func)
        self.plot_canvas.callbacks.connect('motion_notify_event',
            self.motion_notify_func)
        self.plot_canvas.draw()

    def btn_load(self):
        """ load file prompt """
        full_path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv',)])
        if full_path:
            self.reset()
            self.read_file(file_path=full_path)
            self.format_data()
            self.plot()

    def btn_load_folder(self):
        """ load folder prompt """
        self.folder_dir = filedialog.askdirectory()
        if self.folder_dir:
            list_of_files = sorted(os.listdir(self.folder_dir))
            for csv_files in list_of_files:
                self.file_list.insert(END, csv_files)
            # If result folder is already loaded, check which files are done
            if self.folder_labeled_dir:
                self.which_are_done()

    def btn_labeled_folder(self):
        """ set the result folder """
        self.folder_labeled_dir = filedialog.askdirectory()
        # if a data folder is loaded, check which files are done
        if self.folder_dir:
            self.which_are_done()

    def btn_save(self):
        """ save file prompt """
        if self.dataframe is not None:
            f = filedialog.asksaveasfile(defaultextension=".csv",
                initialfile=os.path.split(self.dataframe.filename)[1])
            if f is not None:
                self.tidy()
                self.dataframe.to_csv(f, index=False, sep=',', encoding='utf-8')
                # indicate file is saved in folder list 
                if self.folder_dir:
                    self.which_are_done(f.name)
        else:
            pass

    def btn_about(self):
        """author contact information window"""
        ttk.simpleDialog.showinfo('About Acti :: Label Tool', 
            'Author: Shi Xin\nContact: stevexinshi@gmail.com\nhttps://github.com/shi-xin/acti_labeler',)
        #help_dialog = simpledialog.Dialog(self.parent, "About Acti::Label Tool")
        #ttk.Label(help_dialog, text='ok').grid(column=0, row=0)

    def btn_exit(self):
        """quit program"""
        self.parent.destroy()

    def btn_undo(self):
        """Undo labeling, all kinds of them"""
        self.current_xlim = self.fig_plot_vm.get_xlim()
        if self.labels is None:
            pass
        elif self.labels.shape[0] == 1:
            # erase dataframe marker, set self.labels to None
            self.dataframe.loc[self.dataframe.ts_num == self.labels['where'].iloc[0] , "marker"] = 0
            self.labels = None
            self.plot()
        else:
            self.dataframe.loc[self.dataframe.ts_num == self.labels['where'].iloc[-1] , "marker"] = 0
            self.labels.drop(self.labels.tail(1).index,inplace=True)
            self.plot()

    def button_press_func(self, event):
        """
        Define mouse click behavior
        """
        # left click and hold to pan plot
        if event.button == 1:
            self.button_1_pressed = True
            self.mouse_event = event
            self.pan_init_xlim = self.fig_plot_vm.get_xlim()
        # right click to enter popup menu for labeling
        if event.button == 3:
            self.mouse_event = event
            self.current_xlim = self.fig_plot_vm.get_xlim()
            self.label_popup_menu()

    def button_release_func(self, event):
        """Release mouse left click is end of drag pan"""
        if event.button == 1:
            self.button_1_pressed = False
            self.mouse_event = None
            self.pan_init_xlim = None

    def motion_notify_func(self, event):
        """When left clicked, drag motion triggers panning"""
        if self.button_1_pressed is True:
            if event.x != self.mouse_event.x:
                current_xlim = self.fig_plot_vm.get_xlim()
                start_data = self.fig_plot_vm.transData.inverted().transform_point((self.mouse_event.x, self.mouse_event.y))
                end_data = self.fig_plot_vm.transData.inverted().transform_point((event.x, event.y))
                move_delta = (end_data[0] - start_data[0])
                self.fig_plot_vm.set_xlim([self.pan_init_xlim[0] - move_delta,
                    self.pan_init_xlim[1] - move_delta])
                self.plot_canvas.draw()

    def key_press_func(self, event):
        """Use keyboard to zoom or pan"""
        if self.dataframe is not None:
            current_xlim = self.fig_plot_vm.get_xlim()
            current_xrange = (current_xlim[1] - current_xlim[0])
            scale_factor = 0.1
            if event.key == 'left':
                self.fig_plot_vm.set_xlim([current_xlim[0] - current_xrange/30,
                    current_xlim[1] - current_xrange/30])
                self.plot_canvas.draw()
            elif event.key == 'right':
                self.fig_plot_vm.set_xlim([current_xlim[0] + current_xrange/30,
                    current_xlim[1] + current_xrange/30])
                self.plot_canvas.draw()
            elif event.key == 'up':
                # zoom in
                self.fig_plot_vm.set_xlim([current_xlim[0] + scale_factor*current_xrange,
                    current_xlim[1] - scale_factor*current_xrange])
                self.fig_plot_vm.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
                self.fig.autofmt_xdate()
                self.plot_canvas.draw()
            elif event.key == 'down':
                # zoom out
                self.fig_plot_vm.set_xlim([current_xlim[0] - scale_factor*current_xrange,
                    current_xlim[1] + scale_factor*current_xrange])
                self.fig_plot_vm.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
                self.fig.autofmt_xdate()
                self.plot_canvas.draw()
            else:
                pass

    def scroll_func(self, event):
        """use mouse scroll to zoom"""
        if self.dataframe is not None:
            current_xlim = self.fig_plot_vm.get_xlim()
            current_xrange = (current_xlim[1] - current_xlim[0])
            scale_factor = self.zoom_speed
            #ydata = event.ydata # get event y location
            if event.button == 'up':
                # zoom in
                self.fig_plot_vm.set_xlim([current_xlim[0] + scale_factor*current_xrange, 
                    current_xlim[1] - scale_factor*current_xrange])
                self.fig_plot_vm.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
                self.fig.autofmt_xdate()
                self.plot_canvas.draw()
            elif event.button == 'down':
                # zoom out
                self.fig_plot_vm.set_xlim([current_xlim[0] - scale_factor*current_xrange, 
                    current_xlim[1] + scale_factor*current_xrange])
                self.fig_plot_vm.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
                self.fig.autofmt_xdate()
                self.plot_canvas.draw()
            else:
                pass

    def label_popup_menu(self):
        """ create a pop-up menu at the clicked point on the plot """
        popup = Menu(self.parent)
        popup.add_command(label="Label Start", command=self.label_start)
        popup.add_command(label="Label End", command=self.label_end)
        popup.add_separator()
        popup.add_command(label="Discard data before this point", command=self.label_discard_before)
        popup.add_command(label="Discard data after this point", command=self.label_discard_after)
        popup.add_separator()
        popup.add_command(label="Cancel")
        popup.tk_popup(int(self.parent.winfo_pointerx()), int(self.parent.winfo_pointery()))
        popup.grab_release()

    def label_start(self):
        self.which_x('s')

    def label_end(self):
        self.which_x('e')

    def label_discard_after(self):
        self.which_x('da')

    def label_discard_before(self):
        self.which_x('db')

    def which_x(self, label):
        # TODO: add a check when event.xdata is out of dataframe bounds
        target_x = self.mouse_event.xdata
        # finding neighbor x
        if self.dataframe.loc[self.dataframe.ts_num == target_x].shape[0] == 1:
            target_x = target_x
        else:
            up_x = self.dataframe.loc[self.dataframe.ts_num < target_x].iloc[-1,].ts_num
            down_x = self.dataframe.loc[self.dataframe.ts_num > target_x].iloc[0,].ts_num
            if (target_x - up_x) > (down_x - target_x):
                target_x = down_x
            else:
                target_x = up_x
        # mark in label container
        if self.labels is None:
            self.labels = pd.DataFrame({'where':[target_x], 'state':[label]})
        else:
            self.labels = self.labels.append({'where':target_x, 'state':label}, ignore_index=True)
        self.plot()

    def reset(self):
        """ reset variables before loading new file """
        self.mouse_event = None
        self.current_xlim = None
        if self.labels is not None:
            self.labels = None

    def read_file(self, file_name=None, file_path=None):
        """ Utility function for loading data """
        if file_path is None:
            file_path = self.folder_dir + "/" + file_name
        self.dataframe = pd.read_csv(file_path,
                delimiter=',', encoding="utf-8-sig")
        self.dataframe.filename = os.path.split(file_path)[1]
        self.file_menu.entryconfig('Save', state='normal')

    def format_data(self):
        """
        Prepare data; called by other methods
        """
        self.dataframe.reset_index()
        self.dataframe.columns = self.dataframe.columns.str.lower()
        col_names = self.dataframe.columns.values
        # get a timestamp column
        if 'date' in col_names:
            self.dataframe['timestamp'] = pd.to_datetime(self.dataframe['date'] + ' ' + self.dataframe['time'])
        elif 'ts' in col_names:
            self.dataframe['timestamp'] = pd.to_datetime(self.dataframe['ts'])
        elif 'timestamp' in col_names:
            self.dataframe['timestamp'] = pd.to_datetime(self.dataframe['timestamp'])
        self.dataframe['ts_num'] = date2num(self.dataframe['timestamp'])  # matplotlib data2num
        if 'vector.magnitude' in col_names:
            self.dataframe.rename(columns={'vector.magnitude': 'vm'}, inplace=True)

    def tidy(self):
        """ tidy data before saving """
        # process sleep marker
        self.dataframe['sleep'] = self.dataframe.shape[0]*[0]
        sleep_labels = self.labels[self.labels['state'].isin(['s', 'e'])]
        for i in range(0, sleep_labels.shape[0]):
            if sleep_labels['state'].iloc[i] == 's':
                self.dataframe.loc[self.dataframe.ts_num >= sleep_labels['where'].iloc[i], 'sleep'] = 1
            elif sleep_labels['state'].iloc[i] == 'e':
                self.dataframe.loc[self.dataframe.ts_num >= sleep_labels['where'].iloc[i], 'sleep'] = 0
        # process discard marker
        self.dataframe['discard'] = self.dataframe.shape[0]*[1]
        discard_labels = self.labels[self.labels['state'].isin(['db', 'da'])]
        for i in range(0, discard_labels.shape[0]):
            if discard_labels['state'].iloc[i] == 'db':
                self.dataframe.loc[self.dataframe.ts_num > discard_labels['where'].iloc[i], 'discard'] = 0
            elif discard_labels['state'].iloc[i] == 'da':
                self.dataframe.loc[self.dataframe.ts_num >= discard_labels['where'].iloc[i], 'discard'] = 1
        self.dataframe = self.dataframe[['timestamp', 'axis1', 'axis2', 'axis3', 'vm', 'sleep', 'discard']]  # put it in the end

    def read_selected_file(self, event):
        """
        Once a list of files in a folder is loaded, double click on any
        file to load it.
        """
        selected_file = self.file_list.get(ACTIVE)
        if selected_file:
            self.reset()
            self.read_file(selected_file)
            self.format_data()
            self.plot()

    def which_are_done(self, result_dir=None):
        """ determine which files are done by comparing file and result folders """
        if result_dir is not None:
            self.folder_labeled_dir = os.path.split(result_dir)[0]
        list_of_files = sorted(os.listdir(self.folder_dir))
        list_of_labeled_files = sorted(os.listdir(self.folder_labeled_dir))
        for n in range(0, len(list_of_labeled_files)):
            nn = list_of_files.index(list_of_labeled_files[n])
            self.file_list.itemconfig(nn, bg='grey', fg='white')

    def plot(self):
        """plot utility"""
        self.fig_plot_vm.clear()
        self.fig_plot_label.clear()
        self.fig_plot_vm.plot(self.dataframe['timestamp'], self.dataframe['vm'], 
                                alpha=0.5, marker='o', markersize=5)
        self.fig_plot_vm.fill_between(date2num(self.dataframe['timestamp']), 0, self.dataframe['vm'],
                                        alpha = 0.3)
        self.fig_plot_vm.set_ylim(min(self.dataframe['vm']), max([3000]))
        # plot label
        if self.labels is not None:
            loc_in_dataframe = self.dataframe['ts_num'].isin(list(self.labels['where']))
            label_x = list(self.dataframe.loc[loc_in_dataframe, "timestamp"])
            label_y = self.labels.shape[0]*[0]
            self.fig_plot_label.plot(label_x, label_y, 'ro')  # rewrite this to make it shorter
            # shade labeled sleep area and discarded area
            if self.labels.shape[0] >= 2:
                for i in range(0, self.labels.shape[0]-1):
                    if self.labels['state'].iloc[i] == 's' and self.labels['state'].iloc[i+1] == 'e':
                        start = self.labels['where'].iloc[i]
                        end = self.labels['where'].iloc[i+1]
                        xtime = date2num(self.dataframe['timestamp'])
                        xtime = xtime[xtime >= start]
                        xtime = xtime[xtime <= end]
                        self.fig_plot_label.fill_between(xtime, 0, 3000,
                                                        color='grey',
                                                        alpha = 0.4)
                for i in range(0, self.labels.shape[0]):
                    if self.labels['state'].iloc[i] == 'db':
                        start = date2num(min(self.dataframe['timestamp']))
                        end = self.labels['where'].iloc[i]
                        xtime = date2num(self.dataframe['timestamp'])
                        xtime = xtime[xtime >= start]
                        xtime = xtime[xtime <= end]
                        self.fig_plot_label.fill_between(xtime, 0, 3000,
                                                        color='black',
                                                        alpha = 0.8)
                    elif self.labels['state'].iloc[i] == 'da':
                        start = self.labels['where'].iloc[i]
                        end = date2num(max(self.dataframe['timestamp']))
                        xtime = date2num(self.dataframe['timestamp'])
                        xtime = xtime[xtime >= start]
                        xtime = xtime[xtime <= end]
                        self.fig_plot_label.fill_between(xtime, 0, 3000,
                                                        color='black',
                                                        alpha = 0.8)
            elif self.labels.shape[0] == 1:
                if self.labels['state'].iloc[0] == 'db':
                    start = date2num(min(self.dataframe['timestamp']))
                    end = self.labels['where'].iloc[0]
                    xtime = date2num(self.dataframe['timestamp'])
                    xtime = xtime[xtime >= start]
                    xtime = xtime[xtime <= end]
                    self.fig_plot_label.fill_between(xtime, 0, 3000,
                                                    color='black',
                                                    alpha = 0.8)
            self.fig_plot_label.set_ylim(min(self.dataframe['vm']), max([3000]))
            self.fig_plot_label.yaxis.set_ticks([])

        if self.current_xlim is None:
            self.fig_plot_vm.set_xlim(min(self.dataframe['timestamp']), max(self.dataframe['timestamp']))
        else:
            self.fig_plot_vm.set_xlim([self.current_xlim[0], self.current_xlim[1]])
        self.fig_plot_vm.set_title(os.path.split(self.dataframe.filename)[1])
        self.fig_plot_vm.set_xlabel('Timestamp')
        self.fig_plot_vm.set_ylabel('Counts')
        self.fig_plot_vm.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        self.fig.autofmt_xdate()
        self.fig_plot_vm.axhline(y=100, color='r', linestyle='--', alpha=0.5, linewidth=1)  #TODO: modifiable
        self.fig_plot_vm.axhline(y=500, color='r', linestyle='--', alpha=0.5, linewidth=1)  #TODO: modifiable
        self.fig_plot_vm.grid(True)
        self.cursor = Cursor(self.fig_plot_label,
                        horizOn = True,
                        vertOn = True,
                        color = 'green',
                        linewidth=0.3)
        self.plot_canvas.draw()



if __name__ == "__main__":
    root = Tk()
    tool = label_tool(root)
    root.mainloop()
