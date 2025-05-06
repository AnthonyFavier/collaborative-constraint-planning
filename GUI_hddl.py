import customtkinter
from defs import *
import CAI_hddl
import generate_htn_image
from PIL import Image, ImageTk
from updatePDSimPlan import main as updatePDSimPlan
import time
import threading
from my_scrollable_frame import MyScrollableFrame
import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

customtkinter.set_window_scaling(2)   # scales the window content (default is 1.0)
customtkinter.set_widget_scaling(2.5)   # scales widgets/fonts (default is 1.0)

# Custom thread creation with return value. Used for timers
class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class ConstraintsFrame(MyScrollableFrame):
    def __init__(self, master):
        super().__init__(master, orientation="both")
        
        self.checkboxes = {}
        self.constraint_labels = {}
        self.encoding_labels = {}
        self.frames = {}
        self.height_checkbox_frame = 20
        self.width_checkbox_frame = 31
        self.last_checkboxes_state = {}
        
        
        self.updateFrame()
        
    def clear(self):
        # Delete current grid and widgets
        l = self.grid_slaves()
        for x in self.grid_slaves():
            x.destroy()
        
        keys = set(self.checkboxes.keys())
        for k in keys:
            del self.checkboxes[k]
        keys = set(self.constraint_labels.keys())
        for k in keys:
            del self.constraint_labels[k]
        keys = set(self.encoding_labels.keys())
        for k in keys:
            del self.encoding_labels[k]
        keys = set(self.last_checkboxes_state.keys())
        for k in keys:
            del self.last_checkboxes_state[k]
        
    def updateFrame(self):
        # Delete current grid and widgets
        self.clear()
        
        i_row = 0
        
        if CAI_hddl.CM.constraints == {}:
            label = customtkinter.CTkLabel(self, text="No constraints", font = App.font)
            label.grid(row=i_row, column=0, padx=0, pady=0, sticky="w")
            i_row += 1
        else:
            for k,r in CAI_hddl.CM.raw_constraints.items():
                
                frame = customtkinter.CTkFrame(self, fg_color="transparent")
                frame.grid(row=i_row, column=0, padx=0, pady=0, sticky="w")
                
                framecb = customtkinter.CTkFrame(frame, fg_color="transparent", height=self.height_checkbox_frame, width=self.width_checkbox_frame)
                framecb.grid(row=0, column=0, padx=0, pady=0)
                
                self.checkboxes[r.symbol] = customtkinter.CTkCheckBox(framecb, text='', width=0, command=self.checkboxHandler)
                self.checkboxes[r.symbol].grid(row=0, column=0, padx=0, pady=0, sticky="w")
                
                self.constraint_labels[r.symbol] = customtkinter.CTkLabel(frame, text=f"{r.symbol} - {r.nl_constraint}", font = App.font)
                self.constraint_labels[r.symbol].grid(row=0, column=1, padx=0, pady=0, sticky="w")
                
                i_row+=1
                
                xpadding = 30
                for c in r.children:
                    frame = customtkinter.CTkFrame(self, fg_color="transparent")
                    frame.grid(row=i_row, column=0, padx=xpadding, pady=0, sticky="w")
                
                    framecb = customtkinter.CTkFrame(frame, fg_color="transparent", height=self.height_checkbox_frame, width=self.width_checkbox_frame)
                    framecb.grid(row=0, column=0, padx=0, pady=0)
                    
                    self.checkboxes[c.symbol] = customtkinter.CTkCheckBox(framecb, text="", width=0, command=self.checkboxHandler)
                    self.checkboxes[c.symbol].grid(row=0, column=0, padx=0, pady=0, sticky="w")
                
                    self.constraint_labels[c.symbol] = customtkinter.CTkLabel(frame, text=f"{c.symbol}- {c.nl_constraint}", font = App.font)
                    self.constraint_labels[c.symbol].grid(row=0, column=1, padx=0, pady=0, sticky="w")
                
                    self.encoding_labels[c.symbol] = customtkinter.CTkLabel(frame, text=f"{c.encoding}", font = App.font)
                    self.encoding_labels[c.symbol].grid(row=1, column=1, padx=20, pady=0, sticky="w")
                    
                    i_row+=1
                    
        
        # Initialize last checkboxes state
        self.updateLastStateCheckboxes()
        
        self.hideEncodings()
        self.show_encodings = False
        self.hideCheckboxes()
        self.show_checkboxes = False
        
        self.updateLabels()
            
    def updateLabels(self):
        activated_str = ''
        deactivated_str = '*** '
        for k,x in self.constraint_labels.items():
            x.configure(text=x.cget('text').replace(activated_str, '').replace(deactivated_str, ''))
            
        for symbol in self.constraint_labels:
            l = self.constraint_labels[symbol]
            if CAI_hddl.CM.constraints[symbol].isActivated():
                l.configure(text=activated_str + l.cget("text"))
            else:
                l.configure(text=deactivated_str + l.cget("text"))
    
    def updateLastStateCheckboxes(self):
        for symbol in self.checkboxes:
            self.last_checkboxes_state[symbol] = self.checkboxes[symbol].get()
        
    def checkboxHandler(self):
        # Find checkbox         
        for symbol in self.checkboxes:
            if self.checkboxes[symbol].get() != self.last_checkboxes_state[symbol]:
                checkbox = symbol
                checked = self.checkboxes[symbol].get()==1
        
        # If raw
        if checkbox in CAI_hddl.CM.raw_constraints:
            for child in CAI_hddl.CM.raw_constraints[checkbox].children:
                if checked:
                    # Then check all children 
                    self.checkboxes[child.symbol].select()
                else:
                    # uncheck all chidren
                    self.checkboxes[child.symbol].deselect()
                
        # If decomposed
        elif checkbox in CAI_hddl.CM.decomposed_constraints:
            parent = CAI_hddl.CM.constraints[checkbox].parent
            
            if checked:
                # If all decomposed of associated raw are checked then check raw
                all_checked = True
                for child in parent.children:
                    if self.checkboxes[child.symbol].get()==0:
                        all_checked=False
                        break
                if all_checked:
                    self.checkboxes[parent.symbol].select()
            
            else:
                # uncheck associated raw
                self.checkboxes[parent.symbol].deselect()
    
        self.updateLastStateCheckboxes()
                
    def toggleCheckboxes(self):
        if self.show_checkboxes:
            self.hideCheckboxes()
        else:
            self.showCheckboxes()
    def showCheckboxes(self):
        self.updateLastStateCheckboxes()
        for k,cb in self.checkboxes.items():
            cb.grid()
        self.show_checkboxes = True
    def hideCheckboxes(self):
        for k,cb in self.checkboxes.items():
            cb.grid_remove()
        self.show_checkboxes = False
    def selectActivatedCheckboxes(self):
        for symbol,cb in self.checkboxes.items():
            if CAI_hddl.CM.constraints[symbol].isActivated():
                cb.select()
            else:
                cb.deselect()
    def selectAll(self):
        for symbol,cb in self.checkboxes.items():
            cb.select()
    def unselectAll(self):
        for symbol,cb in self.checkboxes.items():
            cb.deselect()
                    
    def toggleEncodings(self):
        if self.show_encodings:
            self.hideEncodings()
        else:
            self.showEncodings()
    def showEncodings(self):
        for k,x in self.encoding_labels.items():
            x.grid()
        self.show_encodings = True
    def hideEncodings(self):
        for k,x in self.encoding_labels.items():
            x.grid_remove()
        self.show_encodings = False
    
class ButtonsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title = "Constraint actions"
        self.buttons = {}
        
        i_row = 0
        self.confirm_function = None
        self.confirm_button = customtkinter.CTkButton(self, text="Confirm", command=self.confirm)
        self.confirm_button.grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.confirm_button.grid_remove()
        
        self.buttons["Add"] = customtkinter.CTkButton(self, text="Add", command=self.add)
        self.buttons["Add"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.add_nl_constraints = []
        i_row+=1
        
        self.buttons["Delete"] = customtkinter.CTkButton(self, text="Delete", command=self.delete)
        self.buttons["Delete"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1
        
        self.buttons["Activate"] = customtkinter.CTkButton(self, text="Activate /\nDeactivate", command=self.activate)
        self.buttons["Activate"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1
        
        self.buttons["Plan"] = customtkinter.CTkButton(self, text="Plan", command=self.planT)
        self.buttons["Plan"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1
        
        self.buttons["ChangePlanningMode"] = customtkinter.CTkButton(self, text="Change\nPlanning Mode", command=self.changePlanMode)
        self.buttons["ChangePlanningMode"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1
        
        self.buttons["ChangeTimeout"] = customtkinter.CTkButton(self, text="Change\nTimeout (TO)", command=self.changeTimeout)
        self.buttons["ChangeTimeout"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1
        
        self.buttons["ShowEncodings"] = customtkinter.CTkButton(self, text="Toggle encodings", command=self.master.constraints_frame.toggleEncodings)
        self.buttons["ShowEncodings"].grid(row=i_row, column=0, padx=10, pady=10, sticky="w")
        i_row+=1

        # HDDL Button:
        i_row = 0
        self.confirm_function = None
        self.confirm_button = customtkinter.CTkButton(self, text="Confirm", command=self.confirm)
        self.confirm_button.grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.confirm_button.grid_remove()
        
        self.buttons["Add"] = customtkinter.CTkButton(self, text="Add", command=self.add_hddl)
        self.buttons["Add"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.add_nl_constraints = []
        i_row+=1

        self.buttons["Delete"] = customtkinter.CTkButton(self, text="Delete", command=self.delete_hddl)
        self.buttons["Delete"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1

        self.buttons["Activate"] = customtkinter.CTkButton(self, text="Manage All Methods", command=self.activate_hddl)
        self.buttons["Activate"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1

        self.buttons["View"] = customtkinter.CTkButton(self, text="View Graph", command=self.view_hddl)
        self.buttons["Delete"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1

        self.buttons["Plan"] = customtkinter.CTkButton(self, text="Plan", command=self.planT_hddl)
        self.buttons["Plan"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1

        self.buttons["ShowEncodings"] = customtkinter.CTkButton(self, text="Toggle encodings", command=self.master.constraints_frame.toggleEncodings)
        self.buttons["ShowEncodings"].grid(row=i_row, column=0, padx=10, pady=10, sticky="w")
        i_row+=1



    
    def confirm(self):
        self.confirm_function()
        
    def showConfirmButton(self):
        self.confirm_button.grid()
    def hideConfirmButton(self):
        self.confirm_button.grid_remove()
        
    def hideButtons(self):
        for k,x in self.buttons.items():
            x.grid_remove()
    def showButtons(self):
        for k,x in self.buttons.items():
            x.grid()
    
    def add(self):
        self.hideButtons()
        self.add_nl_constraints = []
        self.master.display_frame.prompt("\nEnter your first constraint:")
        self.master.display_frame.entry.configure(state="normal")
        self.master.display_frame.entry.configure(fg_color=self.master.display_frame.entry_light)
        self.master.display_frame.entry.focus()
        self.master.display_frame.entry_function = self.add2
    def add2(self):
        # Show input
        c = self.master.display_frame.entry_text
        
        if c!='':
            self.master.display_frame.prompt("> " + c )
            
            # Store constraint
            self.add_nl_constraints.append(c)
            # repeat
            self.master.display_frame.prompt("\nPress Enter to validate or type another constraint:")
            self.master.display_frame.entry_function = self.add2
            self.master.display_frame.entry.focus()
        
        else: # if no constraint entered
            # first time: abort
            if self.add_nl_constraints==[]:
                self.master.display_frame.prompt("Aborted\n")
                self.showButtons()
                self.master.display_frame.entry_function = None
                self.master.display_frame.entry.configure(state="disabled")
                
            else: # no additional constraint: add current ones
                try:
                    CAI_hddl.addConstraints(self.add_nl_constraints)
                except Exception as err:
                    self.master.quit()
                    raise err
                self.master.display_frame.entry_function = None
                self.master.display_frame.entry.configure(state="disabled")
                self.master.display_frame.entry.configure(fg_color=self.master.display_frame.entry_dark)
                # TODO deal with question if decomposition ok
                # ask yes or no, enter possible feedback
                self.master.constraints_frame.updateFrame()
                self.showButtons()
                
                mprint("\nConstraints added")
        
    def delete(self):
        self.master.constraints_frame.unselectAll()
        self.master.constraints_frame.showCheckboxes()
        self.hideButtons()
        self.confirm_button.configure(text="Delete")
        self.showConfirmButton()
        # TODO: Select/Deselect ALL
        self.confirm_function = self.deleteConfirm
    def deleteConfirm(self):
        # Get selection
        selection = []
        for k,x in self.master.constraints_frame.checkboxes.items():
            if x.get()==1:
                selection.append(k)
                
        if selection!=[]:
            # Delete selected constraints
            CAI_hddl.deleteConstraints(selection)
            self.master.constraints_frame.updateFrame()
        
        self.hideConfirmButton()
        self.confirm_button.configure(text="Confirm")
        self.showButtons()
        self.master.constraints_frame.hideCheckboxes()
        self.confirm_function = None
        
    def activate(self):
        self.master.constraints_frame.selectActivatedCheckboxes()
        self.master.constraints_frame.showCheckboxes()
        self.hideButtons()
        # TODO: Select/Deselect ALL
        self.showConfirmButton()
        self.confirm_function = self.activateConfirm
    def activateConfirm(self):
        for k,x in self.master.constraints_frame.checkboxes.items():
            if x.get()==1:
                CAI_hddl.CM.constraints[k].activate()
            else:
                CAI_hddl.CM.constraints[k].deactivate()
                
        self.hideConfirmButton()
        self.showButtons()
        self.master.constraints_frame.hideCheckboxes()
        self.master.constraints_frame.updateLabels()
        self.confirm_function = None
        
    def planT(self):
        threading.Thread(target=self.plan).start()
    
    def plan(self):
        txt = self.master.display_frame.startWithTimer(CAI_hddl.planWithConstraints)
        dot_graph = generate_htn_image.parse_plan(txt)
        dot_graph.render("htn_plan", format="png", cleanup=True)
        self.master.plan_frame.showText(txt)
        self.master.plan_frame.showPlanDiagram("htn_plan.png")
        mprint("\nPlan generated.")
        
        
    def changePlanMode(self):
        mprint(' ')
        mprint(f"Current planning mode: {CAI_hddl.g_planning_mode}")
        mprint(f"Select a planning mode:\n\t1 - {PlanMode.ANYTIME}\n\t2 - {PlanMode.ANYTIMEAUTO}\n\t3 - {PlanMode.DEFAULT}\n\t4 - {PlanMode.OPTIMAL}\n\t5 - {PlanMode.SATISFICING}")
        
        self.master.display_frame.entry.configure(state="normal")
        self.master.display_frame.entry.configure(fg_color=self.master.display_frame.entry_light)
        self.master.display_frame.entry.focus()
        self.master.display_frame.entry_function = self.changePlanMode2
    def changePlanMode2(self):
        c = self.master.display_frame.entry_text
        
        if c!='':
            self.master.display_frame.prompt("> " + c )
            
            # Check if correct
            if c in ['1', '2', '3', '4', '5']:
                if c=='1':
                    CAI_hddl.g_planning_mode=PlanMode.ANYTIME
                if c=='2':
                    CAI_hddl.g_planning_mode=PlanMode.ANYTIMEAUTO
                if c=='3':
                    CAI_hddl.g_planning_mode=PlanMode.DEFAULT
                if c=='4':
                    CAI_hddl.g_planning_mode=PlanMode.OPTIMAL
                if c=='5':
                    CAI_hddl.g_planning_mode=PlanMode.SATISFICING
                
                mprint(f"\nPlanning mode set to: {CAI_hddl.g_planning_mode}")
            else:
                mprint("Incorrect input")
                mprint("Aborted\n")
        else:
            mprint("Aborted\n")
            
        self.master.display_frame.entry_function = None
        self.master.display_frame.entry.configure(state="disabled")
        self.master.display_frame.entry.configure(fg_color=self.master.display_frame.entry_dark)
    
    def changeTimeout(self):
        mprint(' ')
        mprint(f"Current Timeout: {CAI_hddl.g_timeout}")
        mprint("Enter a new timeout ('Empty'=disables timeout): ")
        
        self.master.display_frame.entry.configure(state="normal")
        self.master.display_frame.entry.configure(fg_color=self.master.display_frame.entry_light)
        self.master.display_frame.entry.focus()
        self.master.display_frame.entry_function = self.changeTimeout2
    def changeTimeout2(self):
        c = self.master.display_frame.entry_text
        try:
            t = int(c)
            assert t>0
            CAI_hddl.g_timeout = t
            mprint(f'Timeout updated: {CAI_hddl.g_timeout}')
        except:
            CAI_hddl.g_timeout = None
            mprint(f'Timeout disabled')


    # HDDL function:
    def add_hddl(self):

    
class DisplayFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.textbox = customtkinter.CTkTextbox(self, wrap='word')
        self.textbox.configure(state='disabled')
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="ewsn")
        N = 20
        self.prompt("\n" * N)
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text="[Type here]")
        self.entry.configure(state='disabled')
        self.entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        self.entry_function = None
        self.entry_text = ''
        self.entry_dark = ('#F9F9FA', '#343638')
        self.entry_light = ('#F9F9FA', '#585a5c')
        # self.entry.configure(fg_color=self.entry_light)
        
        self.timer_label = customtkinter.CTkLabel(self, text="Elapsed Time: 0.0 s", font = App.font)
        self.timer_label.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.start_time = None
        self._timer_running = False
        
    def _wrapperTimer(self, function, *args, **kwargs):
        r = function(*args, **kwargs)
        self._timer_running = False
        return r
        
    def update_timer(self):
        if self._timer_running:
            elapsed = time.time() - self.start_time
            self.timer_label.configure(text=f"Elapsed Time: {elapsed:.1f} s")
            self.master.after(100, self.update_timer)
            
    def startWithTimer(self, function, *args, **kwargs):
        self.start_time = time.time()
        self._timer_running = True
        t = ThreadWithReturnValue(target=self._wrapperTimer, args=(function,)+args, kwargs=kwargs)
        t.start()
        self.update_timer()
        return t.join()
            
    def prompt(self, text):
        self.textbox.configure(state='normal')
        self.textbox.insert(customtkinter.END, '\n'+text)
        self.textbox.see('end')
        self.textbox.configure(state='disabled')
        self.textbox.focus()
        
    def validateEntry(self, event):
        if self.entry.cget("state") == 'disabled':
            return None
        self.entry_text = self.entry.get()
        self.entry.delete(0, customtkinter.END)
        self.entry_function()

class PlanFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.title = customtkinter.CTkLabel(self, text="Current Plan", fg_color="gray30", corner_radius=6,font=App.font)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        self.textbox = customtkinter.CTkTextbox(self, wrap='char')
        self.textbox.configure(state='disabled')
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Add image label for the diagram
        self.image_label = customtkinter.CTkLabel(self)
        self.image_label.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        self.buttons_frame = customtkinter.CTkFrame(self)
        self.buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.update_sim_button = customtkinter.CTkButton(self.buttons_frame, text="Update Sim", command=self.updateSimButton)
        self.update_sim_button.grid(row=0, column=0, padx=10, pady=10)
        
    def updateSimButton(self):
        plan = self.textbox.get("0.0", "end")
        updatePDSimPlan(plan)
        mprint("\nSim updated.")
        
    def showText(self, txt):
        self.textbox.configure(state='normal')
        self.textbox.delete("0.0", 'end')
        self.textbox.insert('end', txt)
        self.textbox.configure(state='disabled')
    
    def showPlanDiagram(self, image_path):
        # Load the image and display it in the image_label
        img = customtkinter.CTkImage(light_image=image_path, dark_image=image_path, size=(400, 300))
        self.image_label.configure(image=img)
        self.image_label.image = img  # Keep a reference to avoid garbage collection

class HTNViewFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.buttons_frame = customtkinter.CTkFrame(self)
        self.buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        self.all_oper_button = customtkinter.CTkButton(self.buttons_frame, text="All Operators", command=self.view_all)
        self.all_oper_button.grid(row=0, column=0, padx=10, pady=10)
        self.new_method_button = customtkinter.CTkButton(self.buttons_frame, text="New Methods", command=self.view_new_methods)
        self.new_method_button.grid(row=0, column=1, padx=10, pady=10)

    def view_all(self):
        img=CAI_hddl.get_domain_graph().resize((400,300))
        self.all_htn_graph = customtkinter.CTkImage(light_image = img, dark_image=img, size=(400,300))
        self.all_htn_graph.grid(row=1, column=0, padx=10, pady=10)


    def view_new_methods(self):
        pass




class App(customtkinter.CTk):
    font = ("Helvetica", 16, "bold")
    
    def __init__(self):
        super().__init__()

        self.title("CAI HDDL")
        self.geometry("3400x1912")
        
        # self.iconbitmap("rsc/icon.ico")
        im = Image.open('rsc/icon.png')
        photo = ImageTk.PhotoImage(im)
        self.wm_iconphoto(True, photo)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.constraints_frame = ConstraintsFrame(self)
        self.constraints_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.buttons_frame = ButtonsFrame(self)
        self.buttons_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.display_frame = DisplayFrame(self)
        self.display_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.plan_frame = PlanFrame(self)
        self.plan_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky='nsew')
        
        self.bind("<Escape>", lambda x: exit())
        self.bind("<Return>", self.display_frame.validateEntry)
        self.bind("<KP_Enter>", self.display_frame.validateEntry)
        # self.bind("<Key>", key_handler)
        # self.bind("beef", lambda x: print("ooh yummy!"))
        
def key_handler(event):
    print(event.char, event.keysym, event.keycode)