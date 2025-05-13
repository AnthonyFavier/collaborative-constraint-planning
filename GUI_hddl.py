import customtkinter
from defs import *
import CAI_hddl
import tools_hddl
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
            label = customtkinter.CTkLabel(self, text="No Constraints", font = App.font)
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
        
        # i_row = 0
        # self.confirm_function = None
        # self.confirm_button = customtkinter.CTkButton(self, text="Confirm", command=self.confirm)
        # self.confirm_button.grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # self.confirm_button.grid_remove()
        
        # self.buttons["Add"] = customtkinter.CTkButton(self, text="Add", command=self.add)
        # self.buttons["Add"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # self.add_nl_constraints = []
        # i_row+=1
        
        # self.buttons["Delete"] = customtkinter.CTkButton(self, text="Delete", command=self.delete)
        # self.buttons["Delete"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # i_row+=1
        
        # self.buttons["Activate"] = customtkinter.CTkButton(self, text="Activate /\nDeactivate", command=self.activate)
        # self.buttons["Activate"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # i_row+=1
        
        # self.buttons["Plan"] = customtkinter.CTkButton(self, text="Plan", command=self.planT)
        # self.buttons["Plan"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # i_row+=1
        
        # self.buttons["ChangePlanningMode"] = customtkinter.CTkButton(self, text="Change\nPlanning Mode", command=self.changePlanMode)
        # self.buttons["ChangePlanningMode"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # i_row+=1
        
        # self.buttons["ChangeTimeout"] = customtkinter.CTkButton(self, text="Change\nTimeout (TO)", command=self.changeTimeout)
        # self.buttons["ChangeTimeout"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # i_row+=1
        
        # self.buttons["ShowEncodings"] = customtkinter.CTkButton(self, text="Toggle encodings", command=self.master.constraints_frame.toggleEncodings)
        # self.buttons["ShowEncodings"].grid(row=i_row, column=0, padx=10, pady=10, sticky="w")
        # i_row+=1

        # HDDL Button:
        i_row = 0
        self.confirm_function = None
        self.confirm_button = customtkinter.CTkButton(self, text="Confirm", command=self.confirm)
        self.confirm_button.grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.confirm_button.grid_remove()
        ###
        self.manage_hddl_buttons = dict()
        self.manage_hddl_buttons["View"] = customtkinter.CTkButton(self, text="View", command=self.master.htn_view_frame.view_list_operators)
        self.manage_hddl_buttons["View"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.manage_hddl_buttons["View"].grid_remove()

        self.manage_hddl_buttons['Delete'] = customtkinter.CTkButton(self, text="Delete", command=self.delete_hddl)
        self.manage_hddl_buttons['Delete'].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.manage_hddl_buttons['Delete'].grid_remove()

        self.manage_hddl_buttons['Reset'] = customtkinter.CTkButton(self, text="Reset", command=self.reset_hddl)
        self.manage_hddl_buttons['Reset'].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.manage_hddl_buttons['Reset'].grid_remove()

        self.manage_hddl_buttons['Cancel'] = customtkinter.CTkButton(self, text="Cancel", command=self.showButtons)
        self.manage_hddl_buttons['Cancel'].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        self.manage_hddl_buttons['Cancel'].grid_remove()
        ###

        self.buttons["View Domain Graph"] = customtkinter.CTkButton(self, text="View Domain Graph", command=self.master.htn_view_frame.view_all)
        self.buttons["View Domain Graph"].grid(row=i_row, column=0, padx=10, pady=10)
        i_row+=1

        self.buttons["View All Operators"] = customtkinter.CTkButton(self, text="View Operators List", command=self.master.htn_view_frame.view_list_operators)
        self.buttons["View All Operators"].grid(row=i_row, column=0, padx=10, pady=10)
        i_row+=1

        self.buttons["Add New Method"] = customtkinter.CTkButton(self, text="Add New Method",fg_color="green", hover_color="darkgreen", command=self.add_hddl)
        self.buttons["Add New Method"].grid(row=i_row, column=0, padx=10, pady=10)
        i_row+=1

        # self.buttons["Add"] = customtkinter.CTkButton(self, text="Add", command=self.add_hddl)
        # self.buttons["Add"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # self.add_nl_constraints = []
        # i_row+=1

        # self.buttons["Delete"] = customtkinter.CTkButton(self, text="Delete", command=self.delete_hddl)
        # self.buttons["Delete"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # i_row+=1

        self.buttons["Manage All Methods"] = customtkinter.CTkButton(self, text="Manage All Methods",fg_color="green", hover_color="darkgreen",  command=self.manage_hddl)
        self.buttons["Manage All Methods"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1

        # self.buttons["View"] = customtkinter.CTkButton(self, text="View Graph", command=self.view_hddl)
        # self.buttons["View"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        # i_row+=1

        self.buttons["Plan"] = customtkinter.CTkButton(self, text="Plan with HDDL Planner",fg_color="red", hover_color="darkred", command=self.plan_hddl)
        self.buttons["Plan"].grid(row=i_row, column=0, padx=10, pady=10, sticky="ew")
        i_row+=1

        # self.buttons["ShowEncodings"] = customtkinter.CTkButton(self, text="Toggle encodings", command=self.master.constraints_frame.toggleEncodings)
        # self.buttons["ShowEncodings"].grid(row=i_row, column=0, padx=10, pady=10, sticky="w")
        # i_row+=1

    def showManageButtons(self):
        r = 0
        for k,x in self.manage_hddl_buttons.items():
            x.grid(row=r, column=0, padx=10, pady=10, sticky="ew")
            r+=1
    
    def hideManageButtons(self):
        for k,x in self.manage_hddl_buttons.items():
            x.grid_remove()
    
    def plan_hddl(self):
        '''
        what to do when the user clicks the Plan button
        '''
        print("Clicked Plan button --> Perform planning with the system HDDL planner")
        result = CAI_hddl.plan_with_hddl_planner(return_format_version=False)
        if "Failed to plan" in result:
            self.master.plan_frame.showText(result)
            return
        plan_time_str = result.splitlines()[-1]
        raw_plan = "\n".join(result.splitlines()[:-1])
        formated_plan_text = tools_hddl.format_lilotane_plan(raw_plan)
        self.master.plan_frame.showText(formated_plan_text+ '\n' + plan_time_str)
        self.master.plan_frame.plan_text = formated_plan_text + '\n' + plan_time_str
        #Generate the plan diagram:
        dot_graph = generate_htn_image.parse_plan(raw_plan)
        dot_graph.render("htn_plan", format="png", cleanup=True)
        mprint("\nPlan generated.")

    def manage_hddl(self):
        '''
        what to do when the user clicks the Manage button
        '''
        # Hide all buttons
        self.hideButtons()
        # Show the view button
        self.showManageButtons()
        # self.buttons["View"].grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        # # Show the add button
        # self.buttons["Add"].grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        # # Show the delete button
        # self.buttons["Delete"].grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        # # Show the reset button
        # self.buttons["Reset"].grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.view_hddl()

    def reset_hddl(self):
        '''
        what to do when the user clicks the Reset button
        '''
        #reset domain back to the original domain

        self.master.htn_view_frame.view_list_operators()
    
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
        self.hideManageButtons()
        for k,x in self.buttons.items():
            x.grid()

    def view_hddl(self):
        self.master.htn_view_frame.view_list_operators()
        
    
    def add_hddl(self):
        self.hideButtons()
        self.add_nl_constraints = []
        self.master.display_frame.prompt("\nEnter your preferred strategy:")
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
        # self.master.plan_frame.showPlanDiagram("htn_plan.png")
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
    # def add_hddl(self):
    #     '''what to do when the user clicks the Add button'''
    #     pass
    def delete_hddl(self):
        '''what to do when the user clicks the Delete button'''
        pass
    def activate_hddl(self):
        '''what to do when the user clicks the Activate button'''
        pass
    def view_hddl(self):
        '''what to do when the user clicks the View button'''
        pass    
    

    
class InteractiveFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.label = customtkinter.CTkLabel(self, text="Interactive Input Area", fg_color="gray30", corner_radius=6,font=App.font)
        self.label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        self.textbox = customtkinter.CTkTextbox(self, wrap='word')
        self.textbox.configure(state='disabled')
        self.textbox.grid(row=1, column=0, padx=10, pady=10, sticky="ewsn")
        N = 20
        self.prompt("\n" * N)
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text="[Type here]")
        self.entry.configure(state='disabled')
        self.entry.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.entry_function = None
        self.entry_text = ''
        self.entry_dark = ('#F9F9FA', '#343638')
        self.entry_light = ('#F9F9FA', '#585a5c')
        # self.entry.configure(fg_color=self.entry_light)
        
        self.timer_label = customtkinter.CTkLabel(self, text="Elapsed Time: 0.0 s", font = App.font)
        self.timer_label.grid(row=3, column=0, padx=10, pady=10, sticky="ew")
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
        # self.grid_rowconfigure(2, weight=1)
        
        self.title = customtkinter.CTkLabel(self, text="Current Plan", fg_color="gray30", corner_radius=6,font=App.font)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.plan_text = ''

        # self.main_frame = customtkinter.CTkScrollableFrame(self)
        # self.main_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        # self.main_frame.grid_columnconfigure(0, weight=1)
        # self.main_frame.grid_rowconfigure(0, weight=1)

        # Create a canvas for scrollable content
        self.canvas = tkinter.Canvas(self, bg="gray30")
        self.canvas.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Add vertical and horizontal scrollbars
        self.v_scrollbar = tkinter.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.grid(row=1, column=1, sticky="ns")

        self.h_scrollbar = tkinter.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.grid(row=2, column=0, sticky="ew")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)

        # Create a frame inside the canvas for content
        self.main_frame = customtkinter.CTkFrame(self.canvas)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Add the frame to the canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        # Bind the canvas to update the scroll region
        self.main_frame.bind("<Configure>", self.update_scroll_region)


        self.textbox = customtkinter.CTkTextbox(self.main_frame, wrap='none')
        self.textbox.configure(state='disabled')
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        # Bind the canvas resize event to adjust the textbox size
        self.canvas.bind("<Configure>", self.resize_textbox)
        # self.textbox.grid_remove()

        # Add image label for the diagram
        self.image_label = customtkinter.CTkLabel(self.main_frame)
        self.image_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.image_label.grid_remove()
        
        self.buttons_frame = customtkinter.CTkFrame(self)
        self.buttons_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        self.update_sim_button = customtkinter.CTkButton(self.buttons_frame, text="Update Sim", command=self.updateSimButton)
        self.update_sim_button.grid(row=0, column=0, padx=10, pady=10)
        self.view_hierarchy_button = customtkinter.CTkButton(self.buttons_frame, text="View Plan Diagram", command=self.showPlanDiagram)
        self.view_hierarchy_button.grid(row=0, column=1, padx=10, pady=10)
        self.view_hierarchy_button = customtkinter.CTkButton(self.buttons_frame, text="View Plan Text", command=self.showHDDLPlanText)
        self.view_hierarchy_button.grid(row=0, column=2, padx=10, pady=10)
        
    def updateSimButton(self):
        plan = self.textbox.get("0.0", "end")
        updatePDSimPlan(plan)
        mprint("\nSim updated.")

    def resize_textbox(self, event):
        """Resize the textbox to fit the canvas."""
        canvas_width = event.width
        canvas_height = event.height
        self.textbox.configure(width=canvas_width, height=canvas_height)

    def update_scroll_region(self, event):
        """Update the scroll region of the canvas."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def showText(self, txt):
        # Clear any existing image
        self.image_label.grid_remove()
        self.textbox.grid()
        self.textbox.configure(state='normal')
        self.textbox.delete("0.0", 'end')
        self.textbox.insert('end', txt)
        self.textbox.configure(state='disabled')

    def showHDDLPlanText(self):
        # Clear any existing image
        self.image_label.grid_remove()
        self.textbox.grid()
        # show plan text in a text box:
        self.textbox.configure(state='normal')
        self.textbox.delete("0.0", 'end')
        self.textbox.insert('end', self.plan_text)
        self.textbox.configure(state='disabled')

    def showPlanDiagram(self):
        # Clear any existing text plan
        self.textbox.grid_remove()
        # Clear the image label
        self.image_label.configure(image='')
        self.image_label.image = None  # Clear the reference to the image
        # Clear the text box
        self.textbox.configure(state='normal')
        self.textbox.delete("0.0", 'end')
        self.textbox.configure(state='disabled')
        
        # Load the image and display it in the image_label
        image_path = "htn_plan.png"  # Path to the image file
        try:
            # Load the image from the file path
            print("Loading image from:", image_path)
            img = Image.open(image_path).resize((1500, 600))
            # Create a CTkImage with the resized image
            print("Creating CTkImage")
            self.plan_diagram = customtkinter.CTkImage(
                light_image=img,
                dark_image=img,
                size=(1500, 600)
            )
            # Display the image in the label or appropriate widget
            # self.image_label.configure(image=self.plan_diagram)
            # self.image_label.image = self.plan_diagram  # Keep a reference to avoid garbage collection
            # Display the image in a label or appropriate widget
            self.image_label = customtkinter.CTkLabel(self.main_frame, image=self.plan_diagram)
            self.image_label.grid(row=1, column=0, padx=10, pady=10)
            print("Image displayed successfully")
        except FileNotFoundError:
            print(f"Error: The file '{image_path}' was not found.")
        except Exception as e:
            print(f"Error loading or displaying the image: {e}")
       
import tkinter
class HTNViewFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.title = customtkinter.CTkLabel(self, text="Hierarchy Viewer", fg_color="gray30", corner_radius=6,font=App.font)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        # self.buttons_frame = customtkinter.CTkFrame(self)
        # self.buttons_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        # self.all_oper_button = customtkinter.CTkButton(self.buttons_frame, text="View Domain Graph", command=self.view_all)
        # self.all_oper_button.grid(row=0, column=0, padx=10, pady=10)
        # self.new_method_button = customtkinter.CTkButton(self.buttons_frame, text="New Methods", command=self.view_new_methods)
        # self.new_method_button.grid(row=0, column=1, padx=10, pady=10)
        # self.operators_button = customtkinter.CTkButton(self.buttons_frame, text="View All Operators", command=self.view_list_operators)
        # self.operators_button.grid(row=0, column=2, padx=10, pady=10)

    def view_all_old(self):
        """View all operators in the domain graph."""
        # Clear any existing operators frame
        if hasattr(self, 'operators_frame'):
            self.operators_frame.destroy()

        img_path=CAI_hddl.get_domain_graph_image()#.resize((400,300))
        try:
            # Load the image from the file path
            img = Image.open(img_path).resize((400, 300))
            
            # Create a CTkImage with the resized image
            self.all_htn_graph = customtkinter.CTkImage(
                light_image=img,
                dark_image=img,
                size=(400, 300)
            )
            
            # Display the image in a label or appropriate widget
            label = customtkinter.CTkLabel(self, image=self.all_htn_graph)
            label.grid(row=1, column=0, padx=10, pady=10)
        except Exception as e:
            print(f"Error loading or displaying the image: {e}")
        # self.all_htn_graph = customtkinter.CTkImage(light_image = img, dark_image=img, size=(400,300))
        # self.all_htn_graph.grid(row=1, column=0, padx=10, pady=10)

    def view_all(self):
        """View all operators in the domain graph with zoom functionality."""
        # Clear any existing operators frame
        if hasattr(self, 'operators_frame'):
            self.operators_frame.destroy()

        # Create a canvas for displaying the image
        self.operators_frame = customtkinter.CTkFrame(self)
        self.operators_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        # Configure the grid layout to allow the canvas to expand
        self.operators_frame.grid_rowconfigure(0, weight=1)
        self.operators_frame.grid_columnconfigure(0, weight=1)

        canvas = tkinter.Canvas(self.operators_frame, bg="gray30")
        canvas.grid(row=0, column=0, sticky="nsew")

        # Add scrollbars
        v_scrollbar = tkinter.Scrollbar(self.operators_frame, orient="vertical", command=canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")

        h_scrollbar = tkinter.Scrollbar(self.operators_frame, orient="horizontal", command=canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Load the image
        img_path = CAI_hddl.get_domain_graph_image()
        try:
            frame_width = self.operators_frame.winfo_width()
            frame_height = self.operators_frame.winfo_height()
            self.original_image = Image.open(img_path).resize((frame_width, frame_height))
            self.current_image = self.original_image.copy()
            self.tk_image = ImageTk.PhotoImage(self.current_image)

            # Add the image to the canvas
            self.image_id = canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
            canvas.config(scrollregion=canvas.bbox("all"))

            # Zoom functionality
            def zoom(event):
                print("Zoom event detected, event.delta:", event.delta)
                scale = 1.1 if event.delta > 0 else 0.9  # Zoom in or out
                new_width = int(self.current_image.width * scale)
                new_height = int(self.current_image.height * scale)
                self.current_image = self.original_image.resize((new_width, new_height), Image.ANTIALIAS)
                self.tk_image = ImageTk.PhotoImage(self.current_image)
                canvas.itemconfig(self.image_id, image=self.tk_image)
                canvas.config(scrollregion=canvas.bbox("all"))

            # Bind mouse wheel to zoom
            canvas.bind("<MouseWheel>", zoom)

        except Exception as e:
            print(f"Error loading or displaying the image: {e}")


    def view_list_operators(self):
        """
        Display the list of operators in the domain with checkboxes.
        Operators are represented as node names in the domain graph.
        """
        # Clear any existing operators frame
        if hasattr(self, 'operators_frame'):
            self.operators_frame.destroy()
        # Create a new scrollable frame to display images
        self.operators_frame = customtkinter.CTkScrollableFrame(self, width=500, height=400)
        self.operators_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        # Configure grid columns to scale proportionally
        self.operators_frame.grid_columnconfigure(0, weight=1)  # Task column
        self.operators_frame.grid_columnconfigure(1, weight=1)  # Method column
        self.operators_frame.grid_columnconfigure(2, weight=1)  # Action column
        self.checkbox_vars = {}

        try:
            # Add instruction label:
            instruction_label = customtkinter.CTkLabel(
                self.operators_frame,
                text="Select operators and then click confirm button to show their hierarchies:",
                text_color="white",
                wraplength=450,  # Wrap text if it exceeds the width
                justify="left"
            )
            instruction_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
            # Add a confirm button to print the checked operators
            confirm_button = customtkinter.CTkButton(self.operators_frame, text="Confirm", command=self.confirm_checked_operators)
            confirm_button.grid(row=0, column=2, columnspan=1, pady=10)
            # Add column headers
            task_label = customtkinter.CTkLabel(self.operators_frame, text="TASK", text_color="yellow")
            task_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

            method_label = customtkinter.CTkLabel(self.operators_frame, text="METHOD", text_color="green")
            method_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

            action_label = customtkinter.CTkLabel(self.operators_frame, text="ACTION", text_color="white")
            action_label.grid(row=1, column=2, padx=10, pady=5, sticky="w")

            # Get the domain graph (assumed to be a Digraph object)
            domain_graph = CAI_hddl.get_domain_graph_wrapper()
            print("Domain graph nodes:", domain_graph.nodes(data=True))  # Debugging line
            print("Domain graph edges:", domain_graph.edges(data=True))  # Debugging line

            # Create column indices for tasks, methods, and actions
            column_indices = {"task": 0, "method": 1, "action": 2}
            row_counters = {"task": 2, "method": 2, "action": 2}

            # Iterate through the nodes (operator names) and create checkboxes
            for operator, data in domain_graph.nodes(data=True):  # Nodes are operator names
                var = customtkinter.BooleanVar()  # Create a BooleanVar for this checkbox
                # Determine the text color and column based on the "type"
                operator_type = data.get("type", "action")  # Default to "action" if type is missing
                if operator_type == "task":
                    text_color = "yellow"
                elif operator_type == "method":
                    text_color = "green"
                else:
                    text_color = "white"
                
                column = column_indices.get(operator_type, 2)  # Default to the "action" column
                row = row_counters[operator_type]  # Get the current row for this type

                # Create and place the checkbox in the appropriate column and row
                checkbox = customtkinter.CTkCheckBox(
                    self.operators_frame, text=operator, variable=var, text_color=text_color
                )
                checkbox.grid(row=row, column=column, padx=10, pady=5, sticky="w")
                self.checkbox_vars[operator] = var  # Store the variable in the dictionary

                # Increment the row counter for this type
                row_counters[operator_type] += 1

            # If no operators are found, display a message
            if not domain_graph.nodes:
                label = customtkinter.CTkLabel(self.operators_frame, text="No operators found.", fg_color="red")
                label.grid(row=0, column=0, columnspan=3, pady=10)

            # # Add a confirm button to print the checked operators
            # confirm_button = customtkinter.CTkButton(self.operators_frame, text="Confirm Selected Operators", command=self.confirm_checked_operators)
            # confirm_button.grid(row=max(row_counters.values()) + 1, column=0, columnspan=3, pady=10)

        except Exception as e:
            print(f"Error displaying operators: {e}")
            label = customtkinter.CTkLabel(self.operators_frame, text="Error loading operators.", fg_color="red")
            label.grid(row=0, column=0, columnspan=3, pady=10)
    
    def confirm_checked_operators(self):
        """
        Print the list of operators that are currently checked and display their images in a scrollable frame.
        """
        checked_operators = [operator for operator, var in self.checkbox_vars.items() if var.get()]
        print("Checked operators:", checked_operators)

        # Destroy the previous operators frame if it exists
        if hasattr(self, 'operators_frame'):
            self.operators_frame.destroy()

        # Create a new scrollable frame to display images
        self.operators_frame = customtkinter.CTkScrollableFrame(self, width=500, height=400)
        self.operators_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        frame_width = self.operators_frame.winfo_width()
        frame_height = self.operators_frame.winfo_height()
        print("Frame dimensions:", frame_width, frame_height)
        
        if len(checked_operators) == 0:
            label = customtkinter.CTkLabel(self.operators_frame, text="No operators selected. Click 'View Operators List' to view and select operators.", fg_color="red")
            label.pack(padx=10, pady=10)
            return
        
        for operator in checked_operators:
            operator_graph_dir = CAI_hddl.get_operator_graph_image_saved_wrapper(operator)
            try:
                # Load the image from the file path
                img = Image.open(operator_graph_dir).resize((600,300))
                
                # Create a CTkImage with the resized image
                operator_graph = customtkinter.CTkImage(
                    light_image=img,
                    dark_image=img,
                    size=(600, 300)
                )

                # # Load the image from the file path
                # img = Image.open(operator_graph_dir)

                # # Get the width of the operators_frame
                # # self.operators_frame.update_idletasks()  # Ensure the frame dimensions are updated
                # frame_width = self.operators_frame.winfo_width()
                # print("Current Frame width:", frame_width)

                # # Calculate the new height to maintain the aspect ratio
                # aspect_ratio = img.width / img.height
                # new_width = frame_width
                # new_height = int(new_width / aspect_ratio)

                # # Resize the image
                # resized_img = img.resize((new_width, new_height))

                # # Create a CTkImage with the resized image
                # operator_graph = customtkinter.CTkImage(
                #     light_image=resized_img,
                #     dark_image=resized_img
                # )
                
                # Display the image in a label inside the scrollable frame
                print("display the image in a label inside the scrollable frame")
                label = customtkinter.CTkLabel(self.operators_frame, image=operator_graph, text="")
                label.pack(padx=10, pady=10)
            except Exception as e:
                print(f"Error loading or displaying the image for operator '{operator}': {e}")
                error_label = customtkinter.CTkLabel(self.operators_frame, text=f"Error loading image for {operator}", fg_color="red")
                error_label.pack(padx=10, pady=10)


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
        
        # self.constraints_frame = ConstraintsFrame(self)
        # self.constraints_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.display_frame = InteractiveFrame(self)
        self.display_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.htn_view_frame = HTNViewFrame(self)
        self.htn_view_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        self.buttons_frame = ButtonsFrame(self)
        self.buttons_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.plan_frame = PlanFrame(self)
        self.plan_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky='nsew')
        
        self.bind("<Escape>", lambda x: exit())
        self.bind("<Return>", self.display_frame.validateEntry)
        self.bind("<KP_Enter>", self.display_frame.validateEntry)
        # self.bind("<Key>", key_handler)
        # self.bind("beef", lambda x: print("ooh yummy!"))
        
def key_handler(event):
    print(event.char, event.keysym, event.keycode)