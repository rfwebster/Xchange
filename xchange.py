_online = True
try:
    from PyJEM import TEM3, detector
except ImportError: 
    _online = False
    from PyJEM.offline import TEM3, detector

import tkinter as tk
from tkinter import ttk

POLLING_TIME = 2000 # ms

class Xchange():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Xchange')
        self.root.geometry('300x300')
        self.root.resizable(False, False)
        self.root.configure(background='black')
        self.root.attributes('-topmost', True)

        self.stage = TEM3.Stage3()
        self.feg = TEM3.FEG3()
        self.apt = TEM3.Apt3()

        self.setup_ui()

        self.update()
        self.root.mainloop()


    def setup_ui(self):
        title_font = ('Arial', 16, 'bold')
        font = ('Arial', 12)

        self.frame = tk.Frame(self.root, bg='black')
        self.frame.pack(padx=5, pady=5, fill=tk.X, expand=True, anchor='n')

        self.beam_value_label = tk.Label(self.frame, text='Beam Valve: ', 
                                         font=title_font, bg='black', fg='light green')
        self.beam_value_label.grid(row=0, column=0, sticky='nsew')

        self.holder_status_label = tk.Label(self.frame, text='Holder: ', 
                                            font=title_font, bg='black', fg='light green')
        self.holder_status_label.grid(row=1, column=0, sticky='nsew')

        self.stage_label = tk.Label(self.frame, text='Stage: X= ,  Y= , Z= ', 
                                    font=font, bg='black', fg='light green')
        self.stage_label.grid(row=2, column=0, sticky='nsew')

        self.tilt_label = tk.Label(self.frame, text='Tilt: Alpha= , Beta= ', 
                                   font=font, bg='black', fg='light green')
        self.tilt_label.grid(row=3, column=0, sticky='nsew')

        self.xchange_button = tk.Button(self.root, text='Exchange', font=title_font, 
                                        bg='light green', fg='black', borderwidth=10, 
                                        command=self.set_xchange)
        self.xchange_button.pack(padx=5, pady=5,  fill=tk.BOTH, expand=True)


    def update(self):

        beam_valve = "Closed"
        if self.feg.GetBeamValve():
            beam_valve = "Open" 
        self.beam_value_label.configure(text='Beam Valve: {}'.format(beam_valve))

        holder_status = "OUT"
        if self.stage.GetHolderStts():
            holder_status = "IN"
        self.holder_status_label.configure(text='Holder: ' + holder_status)

        pos = self.stage.GetPos()
        self.stage_label.configure(text='Stage: X= {0:.3f}, Y= {1:.3f}, Z= {2:.3f}'.format(pos[0], pos[1], pos[2]))
        self.tilt_label.configure(text='Tilt: Alpha= {0:.3f}, Beta= {1:.3f}'.format(pos[3], pos[4]))

        self.root.after(POLLING_TIME, self.update)

    def set_xchange(self):

        self.feg.SetBeamValve(1)
        
        self.stage.Stop()
        self.root.after(1000)
        self.stage.SetPosition(0, 0, 0, 0, 0)

        for i in range(0, 5):
            self.remove_aperture(i)

    def remove_aperture(self, kind):
        try:
            self.apt.SetExpSize(kind,0)
        except:
            self.apt.SelectKind(kind)
            self.apt.SetSize(0)







if __name__ == '__main__':
    program = Xchange()
