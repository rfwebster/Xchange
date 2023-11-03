import tkinter as tk
from tkinter import ttk
import microscope as GrandARM

# User defined variables
POLLING_TIME = 2000 # ms

class WarningPopup(tk.Toplevel):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.title("Warning")
        self.attributes('-topmost', True)
        self.geometry("500x100")
        self.configure(background="yellow")
        self.message = ttk.Label(self, text=message,
                                 font=("Arial", 12, "bold"), justify=tk.CENTER,
                                 background="yellow", foreground="black")
        self.message.pack(pady=10)
        self.ok_button = tk.Button(self, text="OK", width=20, command=self.destroy)
        self.ok_button.pack(pady=10)

class Xchange(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Xchange')
        self.geometry('300x300')
        self.resizable(False, False)
        self.configure(background='black')
        self.attributes('-topmost', True)

        self.setup_ui()

        self.update()
        self.mainloop()


    def setup_ui(self):
        self.style = ttk.Style()
        self.style.theme_use('vista')
        self.style.configure("TFrame", background="black")

        self.style.configure("TButton", foreground="black", background="green", font=('Arial', 12, 'bold'), borderwidth=1)
        self.style.map("TButton", background=[("disabled", "light grey"), ("active", "green")], foreground=[("disabled", "grey"), ("active", "black")])

        self.style.configure("TLabel", foreground="light green", background="black", font=('Arial', 12, 'bold'))
        self.style.configure("TCheckbutton", foreground="light green", background="black", font=('Arial', 12, 'bold'))

        title_font = ('Arial', 16, 'bold')
        font = ('Arial', 12)

        self.frame = ttk.Frame(self)
        self.frame.pack(padx=5, pady=5, fill=tk.X, expand=True, anchor='center')
        
        self.beam_value_label = ttk.Label(self.frame, text='Beam Valve: ')
        self.beam_value_label.pack(padx=5, pady=5,  fill=tk.BOTH, expand=True)

        self.holder_status_label = ttk.Label(self.frame, text='Holder: ')
        self.holder_status_label.pack(padx=5, pady=5,  fill=tk.BOTH, expand=True)

        self.xy_stage_label = ttk.Label(self.frame, text='Stage: X= ,  Y= , Z= ')
        self.xy_stage_label.pack(padx=5, pady=5,  fill=tk.BOTH, expand=True)

        self.z_stage_label = ttk.Label(self.frame, text='Z= ')
        self.z_stage_label.pack(padx=5, pady=5,  fill=tk.BOTH, expand=True)

        self.tilt_label = ttk.Label(self.frame, text='Tilt: Alpha= , Beta= ')
        self.tilt_label.pack(padx=5, pady=5,  fill=tk.BOTH, expand=True)

        self.xchange_button = ttk.Button(self, text='Exchange')
        self.xchange_button.pack(padx=5, pady=5,  fill=tk.BOTH, expand=True)

        self.ontop_checkbox = ttk.Checkbutton(self, text='Always on top', state=tk.NORMAL,
                                             command=self.toggle_ontop)
        self.ontop_checkbox.state(['!selected']) # has no effect
        self.ontop_checkbox.pack(padx=5, pady=5,  fill=tk.BOTH, expand=True)
        self.update_idletasks()

    def toggle_ontop(self):
        if self.attributes('-topmost'):
            self.attributes('-topmost', False)
        else:
            self.attributes('-topmost', True)
        self.update_idletasks()


    def update(self):
        # check if the beam valve is closed
        if GrandARM.feg.GetBeamValve():
            self.beam_valve = "Open" 
            self.beam_value_label.configure(foreground='red')
        else:
            self.beam_valve = "Closed"
            self.beam_value_label.configure(foreground='light green')
        self.beam_value_label.configure(text='Beam Valve: {}'.format(self.beam_valve))

        if GrandARM.stage.GetHolderStts():
            self.holder_status = "IN"
            self.holder_status_label.configure(foreground='light green')
        else: 
            self.holder_status = "OUT"
            self.holder_status_label.configure(foreground='red')
            
        self.holder_status_label.configure(text='Holder: ' + self.holder_status)

        self.pos = GrandARM.stage.GetPos()
        self.xy_stage_label.configure(text='Stage: X= {0:.3f}, Y= {1:.3f}'.format(self.pos[0]/1000, self.pos[1]/1000))
        self.z_stage_label.configure(text='Z= {0:.3f}'.format(self.pos[2]/1000))
        self.tilt_label.configure(text='Tilt: Alpha= {0:.3f}, Beta= {1:.3f}'.format(self.pos[3], self.pos[4]))

        # if the stage is out of bounds set the relative color to be red
        if any([p >= 2. for p in self.pos[:2]]):
            self.xy_stage_label.configure(foreground='red')
            self.z_stage_label.configure(foreground='red')
        else:
            self.xy_stage_label.configure(foreground='light green')
            self.z_stage_label.configure(foreground='light green')

        if any([t >= 1. for  t in self.pos[3:]]):
            self.tilt_label.configure(foreground='red')
        else:
            self.tilt_label.configure(foreground='light green')


        # if the holder is out disable the button so people can't neutralise stage
        if self.holder_status == "OUT":
            self.xchange_button.configure(state=tk.DISABLED)
        # else if the beam valve is closed and the stage values are between 0 and 1
        # then set the color to be green 
        elif self.beam_valve == "Closed" and all(0 <= x <= 1 for x in self.pos):
            self.xchange_button.configure(state=tk.NORMAL)
        # else if the beam valve is open and the stage values are greater than 1
        # then set the color to be red
        elif self.beam_valve == "Open" and any(x > 1 for x in self.pos):
            self.xchange_button.configure(state=tk.NORMAL)


        self.after(POLLING_TIME, self.update)
        self.update_idletasks()

    def set_xchange(self):
        # Create a pop-up window with a message
        popup = WarningPopup(self, "Make sure EDX detectors are in the S-CHANGE position!")
        popup.wait_window()
        print("EDX warning acknowledged")

        GrandARM.feg.SetBeamValve(0)
        
        GrandARM.stage.Stop()
        print("stage stopped")
        while any(GrandARM.stage.GetStatus()):
            # wait for stage to stop moving
            print("stage is moving")
            pass
        GrandARM.stage.SetOrg()
        print("stage neutralised")
        while any(GrandARM.stage.GetStatus()):
            # wait for stage to stop moving
            print("stage is moving")
            pass
        # wait for stage to stop moving
        for apt in GrandARM.aperture_list:
            # could implement a more sofisicated method to determine which apertures are allowed
            print("removing aperture {}".format(apt["Name"]))
            self.remove_aperture(apt["Index"])

    def remove_aperture(self, kind):
        
        try:
            if GrandARM.apt.GetExpSize(kind):
                GrandARM.apt.SetExpSize(kind,0)
        except:
            if GrandARM.apt.GetSize(kind):
                GrandARM.apt.SelectKind(kind)
                GrandARM.apt.SetSize(0)
                self.after(3000)

        self.update_idletasks()


if __name__ == '__main__':
    program = Xchange()
