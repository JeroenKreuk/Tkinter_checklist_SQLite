import tkinter as tk
import os
import datetime
import sql_module

root = tk.Tk()
root.title("Checklist")

# total frame format
height_frame = 700
width_frame = 600

#load photos that are used as buttons in the center_frame
photo_worker = tk.PhotoImage(file= r"pictures/worker.png")
photo_eye = tk.PhotoImage(file = r"pictures/eye.png")
photo_undo = tk.PhotoImage(file = r"pictures/undo.png")
photo_NA = tk.PhotoImage(file = r"pictures/na.png")

# creating multiple frames within the root
top_frame = tk.Frame(root, bg="Black")
main_frame = tk.Frame(root, bg="Black", highlightthickness=0)
bottom_frame = tk.Frame(root, bg="Black")

#place the different frames in root
top_frame.grid(row=0, sticky="n")
main_frame.grid(row=1, sticky='wens')
bottom_frame.grid(row=2, sticky="sw")

# make sure that the middle frame will get smaller or wider when adjusting the screen
root.grid_rowconfigure(1, weight=1)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)
main_frame.grid_propagate(False)

# Add a canvas in that frame, the canvas is used because there are more design possibilities with this.
canvas = tk.Canvas(main_frame, bg="black")
canvas.grid(row=0, column=0, sticky="news")

# Link a scrollbar to the canvas
tkinter_scroll = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
tkinter_scroll.grid(row=0, column=1, sticky='ns')
canvas.configure(yscrollcommand=tkinter_scroll.set)
main_frame.config(width=width_frame, height=height_frame)

# Create a frame to contain the buttons
center_frame = tk.Frame(canvas, borderwidth=0, highlightthickness=0, bg="black")
canvas.create_window((0, 10), window=center_frame, anchor='nw')

# Get usernames to update the sql database and to show in the checklist
username = os.getlogin()


def time_now():
    """ Time in a specific format
    :return: Time
    """
    return datetime.datetime.now().strftime("%H:%M:%S")


class widget_class:
    """
    This is a class representation of the widgets in the center_frame
    :param row: this is the row of the checklist action, this is used in the to update the sql as well as the tkinter overview.
    :type row: int
    :param name_process: The name of the process.

            Tkinter_row = 0

            SQL_row = 0
    :type name_process: str
    :param check_type: this defines whether the action is a two eyed check or a four eyed check.

            Tkinter_row = 1 and 2, this will be split in the performer and checker, they get pictures as buttons

            SQL_row = 1
    :type check_type: str
    :param warning: this is the time when the process should have been started

            Tkinter_row = not on the tkinter screen

            SQL_row = 2
    :type warning: str
    :param deadline: this is the time when the process should have been finished

            Tkinter_row = 5

            SQL_row = 3
    :type deadline: str
    :param remark: not used, but in a more extensive checklist this could be used as a quick reminder or very short work description.

            Tkinter_row = Not used

            SQL_row = 4
    :type remark: str
    :param first_check_name: the first person who has finished, this can be also viewed as the performer

            Tkinter_row = 1, when the button is pressed it will go to the background. The label with the computer username goes to the foreground

            SQL_row = 5
    :type first_check_name: str
    :param first_time: the time when the first person has pressed the button and confirmed that the task has been finished.

            Tkinter_row = 3

            SQL_row = 6
    :type first_time: str
    :param second_check_name: the second person who has finished, this can be often viewed as the checker.

            Tkinter_row = 2, when the button is pressed it will go to the background. The label with the computer username goes to the foreground

            SQL_row = 7
    :type second_check_name: str
    :param second_time: the time when the second person has pressed the button and confirmed that the task has been finished.

            Tkinter_row = 3

            SQL_row = 8
    :type second_time: str
    """
    def __init__(self, row, name_process, check_type, warning, deadline, remark, first_check_name, first_time, second_check_name, second_time):
        """Constructor method
        """
        self.row = row
        self.name_process = name_process
        self.check_type = check_type
        self.warning = warning
        self.deadline = deadline
        self.remark = remark
        self.first_check_name = first_check_name
        self.first_time = first_time
        self.second_check_name = second_check_name
        self.second_time = second_time


    def place_widgets_on_opening(self):
        """
        This will create all the widgets during the start of the program. Thereafter there will be no widgets removed or created while the program runs only adjusted.
        :return: all tkinter widgets in the center_frame
        """
        #Tkinter ordered by column, no new widgets will be created only adjusted. This is to improve performance.
        tk.Label(center_frame, bg="Black", fg="white", font="none 10 bold", text=self.name_process).grid(row=self.row, column=0, sticky=tk.W)
        tk.Button(center_frame, image= photo_worker, bg = "orange", command=lambda: update_row_database("first_check_name", username, "first_time", time_now(), self.row)).grid(row=self.row, column=1, pady=1)
        tk.Label(center_frame, bg="Black", fg="green", font="none 12 bold", text="").grid(row=self.row, column=1) # place widget with empty text, will be filled later on
        if self.check_type == "4eye":
            tk.Label(center_frame, bg="Black", fg="green", font="none 12 bold", text="").grid(row=self.row, column=2)  # place widget with empty text, will be filled later on
            tk.Button(center_frame, image= photo_eye, bg = "orange", command=lambda: update_row_database("second_check_name", username, "second_time", time_now(), self.row)).grid(row=self.row, column=2, pady=1)
        tk.Label(center_frame, bg="Black", fg="white", font="none 8 bold", text="       ").grid(row=self.row, column=3, sticky=tk.W)# place widget with empty text, will be filled later on
        tk.Label(center_frame, bg="Black", fg="white", font="none 8 bold", text=str(self.deadline)[:-10]).grid(row=self.row, column=4, sticky=tk.W)
        tk.Button(center_frame, image=photo_NA, bg="gray", command=lambda:widget_class.not_applicable(self)).grid(row=self.row, column=5, sticky=tk.W, pady=1)
        tk.Button(center_frame, image=photo_undo, bg="gray", command=lambda: widget_class.undo(self)).grid(row=self.row, column=6, sticky=tk.W, pady=1)

    def update_widgets(self):
        """
        Based on the status in the sql database the widgets in the center_frame are updated. There are multiple if statements because processes can be undone or cancelled
        :return: UPDATED tkinter widgets in the center_frame
        """
        if self.first_check_name is not None: # place button on the background and label with name on the foreground.
            for widget in center_frame.grid_slaves(row=self.row, column=1):
                if widget.winfo_class() == "Button":
                    widget.lower()
                if widget.winfo_class() == "Label":
                    widget.configure(text = self.first_check_name)
                    widget.lift
                    if self.check_type == "2eye":
                        center_frame.grid_slaves(row=self.row, column=3)[0].configure(text=self.first_time[:-3])
        else:  # place button on the foreground and label with name on the background, this is needed when the undo button has been hit for example.
            for widget in center_frame.grid_slaves(row=self.row, column=1):
                if widget.winfo_class() == "Button":
                    widget.lift()
                if widget.winfo_class() == "Label":
                    widget.configure(text="")
                    widget.lift
                    center_frame.grid_slaves(row=self.row, column=3)[0].configure(text="      ")

        if self.check_type == "4eye":
            if self.second_check_name is not None:# place button on the background and label with name on the foreground.
                for widget in center_frame.grid_slaves(row=self.row, column=2):
                    if widget.winfo_class() == "Button":
                        widget.lower()
                    if widget.winfo_class() == "Label":
                        widget.configure(text=self.second_check_name)
                        center_frame.grid_slaves(row=self.row, column=3)[0].configure(text=self.second_time[:-3])
            else:  # place button on the foreground and label with name on the background, this is needed when the undo button has been hit for example.
                for widget in center_frame.grid_slaves(row=self.row, column=2):
                    if widget.winfo_class() == "Button":
                        widget.lift()
                    if widget.winfo_class() == "Label":
                        widget.configure(text="")
                        center_frame.grid_slaves(row=self.row, column=3)[0].configure(text="      ")


    def not_applicable(self):
        """
        If the button with the X is hit then the sql database is updated.
        :return: UPDATED sql database
        """
        if self.check_type == "2eye":
            update_row_database("first_check_name", "NA", "first_time", "00:00:00", self.row)
        if self.check_type == "4eye":
            update_row_database("first_check_name", "NA", "first_time", "00:00:00", self.row)
            update_row_database("second_check_name", "NA", "second_time", "00:00:00", self.row)


    def undo(self):
        """
        If the button undo is hit then the sql database is updated.
        :return: UPDATED sql database
        """
        if self.check_type == "2eye":
            update_row_database("first_check_name", None , "first_time", None, self.row)
        if self.check_type == "4eye":
            update_row_database("first_check_name", None , "first_time", None, self.row)
            update_row_database("second_check_name", None , "second_time", None, self.row)


    def update_warning(self):
        """
        The warning in the top_frame is update when a process is not yet signed of and is after the warning time.

        The deadline times in tkinter_row 5 will turn red when the warning time has past.
        :return: updated widgets topframe and center_frame row 5
        """
        if self.check_type == "2eye":
            if self.first_time is None:
                if time_now() > str(self.warning)[:-7]:
                    center_frame.grid_slaves(row=self.row, column=4)[0].configure(bg="red")
                    top_frame.grid_slaves(row=0, column=0)[0].configure(text="***" + self.name_process + "***", bg="red",fg="yellow", font="none 15 bold")
            else:
                center_frame.grid_slaves(row=self.row, column=4)[0].configure(bg="black")

        if self.check_type == "4eye":
            if self.second_time is None:
                if time_now() > str(self.warning)[:-7]:
                    center_frame.grid_slaves(row=self.row, column=4)[0].configure(bg="red")
                    top_frame.grid_slaves(row=0, column=0)[0].configure(text="***" + self.name_process + "***", bg="red", fg="yellow", font="none 15 bold")
            else:
                center_frame.grid_slaves(row=self.row, column=4)[0].configure(bg="black")


def widgets(place_or_update):
    """
    Retrieves the sql database and feeds the widget_class
    :param place_or_update: place is used on the start of the program, update is used when the program sees an update of the sql database, warning is used to update the warnings
    :return: updated widgets topframe and center_frame row 5
    """
    df = sql_module.retrieve_sqlite_to_pandas()
    for row in range(len(df)):
        name_process = df.loc[row, "name_process"]
        check_type = df.loc[row, "check_type"]
        warning = df.loc[row, "warning"]
        deadline = df.loc[row, "deadline"]
        remark = df.loc[row, "remark"]
        first_check_name = df.loc[row, "first_check_name"]
        first_time = df.loc[row, "first_time"]
        second_check_name = df.loc[row, "second_check_name"]
        second_time = df.loc[row, "second_time"]

        if place_or_update == "place":
            widget_class(row, name_process,check_type, warning, deadline, remark, first_check_name, first_time, second_check_name, second_time).place_widgets_on_opening()
        if place_or_update == "update":
            widget_class(row, name_process,check_type, warning, deadline, remark, first_check_name, first_time, second_check_name, second_time).update_widgets()
        if place_or_update == "warning":
            widget_class(row, name_process,check_type, warning, deadline, remark, first_check_name, first_time, second_check_name, second_time).update_warning()


def update_row_database(column_name, column_name_value, column_name2, column_name2_value, row_number):
    """
    This is a function that is triggered by a button, then the sql database will be updated and the tkinter frame is updated.
    :param column_name: the column in the database that needs to be updated, this is first_check_name or second_check_name
    :param column_name_value: this is the username
    :param column_name2: the second column in the database that needs to be updated, this is first_time or second_time
    :param column_name2_value: this is the time
    :param row_number: the row number of the colums of the database that needs to be updated
    :return: updated widgets centerframe, topframe and center_frame row 5
    """
    sql_module.update_row_database(column_name, column_name_value, column_name2, column_name2_value, str(int(row_number)+1))
    widgets("update")
    widgets("warning")


# bottom frame
def update_bottom_frame():
    """
    Updates the bottom frame when the last update was.
    :return: updated widgets bottomframe with the time of the last update
    """
    tk.Label(bottom_frame, fg="green", text="Last update:").grid(row=0, column=0, sticky=tk.W)
    var = tk.StringVar()
    var.set(time_now()[:-3])  # Update of time in the left corner
    tk.Label(bottom_frame, textvariable=var).grid(column=1, row=0)

# Make sure that the app updates after changes in the archive
last_update = "00:00:00"
def update_all_frames():
    """
    This function checks every minute (60000) if the sql database has been updated. It will also update all the warnings every minute.
    When there is a database update then all the tkinter widgets will be updated accordingly
    :return: updated widgets bottomframe, centerframe, topframe
    """
    global last_update
    check_for_update = sql_module.last_update_table()
    widgets("warning")
    if last_update != check_for_update: # Check of update of archive
        widgets("update")
        update_bottom_frame()
        last_update = check_for_update
    # store_last_update = get_mod_time_file(Archive_Filename) # Update stored value
    root.after(60000, lambda: update_all_frames())

sql_module.create_and_retrieve_database()
tk.Label(top_frame, fg="green", text="top").grid(row=0, column=0, sticky=tk.W) # set top frame text to its neutral position that there is noting out ouf deadline
widgets("place")
widgets("update")
widgets("warning")
update_all_frames()


# Set the canvas scrolling region
center_frame.update_idletasks()  # Needed to make bbox info available, so it knows how big the canvas is after all the added stuff in the center frame.
canvas.config(scrollregion=canvas.bbox("all"))
    # more info regarding scroll regions: https://stackoverflow.com/questions/43731784/tkinter-canvas-scrollbar-with-grid

# to scroll in the canvas
def _on_mousewheel(event):
    """
    makes sure that the canvas is scrollable
    :return: scrollable canvas in the centerframe
    """
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

root.geometry(str(width_frame) + 'x' + str(height_frame))
root.mainloop()