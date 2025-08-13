from datetime import datetime
import customtkinter
from customtkinter import filedialog
from defs import *
import CAI
from PIL import Image, ImageTk
from updatePDSimPlan import main as updatePDSimPlan
import time
import threading
import pyperclip
import ctypes
import json
import jsonpickle
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except:
    pass

customtkinter.set_window_scaling(2.0)   # scales the window content (default is 1.0)
customtkinter.set_widget_scaling(1.5)   # scales widgets/fonts (default is 1.0)

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

class ConstraintsFrame(customtkinter.CTkScrollableFrame):
    font = ("Arial", 18)
    encoding_font = ("Courier New", 12)
    def __init__(self, master):
        super().__init__(master, orientation="both")
        
        self.checkboxes = {}
        self.constraint_labels = {}
        self.encoding_labels = {}
        self.decomp_frame = []
        self.height_checkbox_frame = 20
        self.width_checkbox_frame = 31
        self.last_checkboxes_state = {}
        
        
        self.bind('<Enter>', self._bound_to_mousewheel)
        self.bind('<Leave>', self._unbound_to_mousewheel)
        
        self.show_decomps = False
        self.show_encodings = False
        self.show_checkboxes = False
        
        self.updateFrame()
        
    def updateFrame(self):
        
        self.master.configure(state='disabled')
        
        # Delete current grid and widgets
        self.clear()
        
        i_self_row = 0
        
        if CAI.CM.constraints == {}:
            label = customtkinter.CTkLabel(self, text="No constraints", font = App.font)
            label.grid(row=i_self_row, column=0, padx=0, pady=0, sticky="w")
            i_self_row += 1
        else:
            # for k,r in CAI.CM.raw_constraints.items():
            for i,(id,r) in enumerate(CAI.CM.raw_constraints.items()):
                
                frame = customtkinter.CTkFrame(self, fg_color="transparent")
                frame.grid(row=i_self_row, column=0, padx=0, pady=0, sticky="w")
                
                if i!=0:
                    empty_top_frame = customtkinter.CTkFrame(frame, fg_color="transparent", height=10)
                    empty_top_frame.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="w")
                
                framecb = customtkinter.CTkFrame(frame, fg_color="transparent", height=self.height_checkbox_frame, width=self.width_checkbox_frame)
                framecb.grid(row=1, column=0, padx=0, pady=0)
                self.checkboxes[r.symbol] = customtkinter.CTkCheckBox(framecb, text='', width=0, command=self.checkboxHandler)
                self.checkboxes[r.symbol].grid(row=0, column=0, padx=0, pady=0, sticky="w")
                
                self.constraint_labels[r.symbol] = customtkinter.CTkLabel(frame, text=f"{r.symbol} - {r.nl_constraint}", font = ConstraintsFrame.font, fg_color='grey30')
                self.constraint_labels[r.symbol].grid(row=1, column=1, padx=0, pady=0, sticky="w")
                
                i_self_row+=1
                
                xpadding_between_raw_and_decomposed_constraints = 30
                for c in r.children:
                    frame = customtkinter.CTkFrame(self, fg_color="transparent")
                    self.decomp_frame.append(frame)
                    frame.grid(row=i_self_row, column=0, padx=xpadding_between_raw_and_decomposed_constraints, pady=0, sticky="w")
                
                    framecb = customtkinter.CTkFrame(frame, fg_color="transparent", height=self.height_checkbox_frame, width=self.width_checkbox_frame)
                    framecb.grid(row=0, column=0, padx=0, pady=0)
                    
                    self.checkboxes[c.symbol] = customtkinter.CTkCheckBox(framecb, text="", width=0, command=self.checkboxHandler)
                    self.checkboxes[c.symbol].grid(row=0, column=0, padx=0, pady=0, sticky="w")
                
                    self.constraint_labels[c.symbol] = customtkinter.CTkLabel(frame, text=f"{c.symbol}- {c.nl_constraint}", font = ConstraintsFrame.font)
                    self.constraint_labels[c.symbol].grid(row=0, column=1, padx=0, pady=0, sticky="w")
                
                    self.encoding_labels[c.symbol] = customtkinter.CTkLabel(frame, text=f"{c.encoding}", justify='left', font = ConstraintsFrame.encoding_font)
                    self.encoding_labels[c.symbol].grid(row=1, column=1, padx=20, pady=0, sticky="w")
                    
                    i_self_row+=1
                    
        
        # Initialize last checkboxes state
        self.updateLastStateCheckboxes()
        
        self.updateLabels()
        
        if not self.show_decomps:
            self.hideDecomps()
        if not self.show_encodings:
            self.hideEncodings()
        if not self.show_checkboxes:
            self.hideCheckboxes()
            
        self.master.configure(state='normal')
        
    def _bound_to_mousewheel(self, event):
        # print("_bound_to_mousewheel")
        self.master.bind_all("<MouseWheel>", self._on_mousewheel)
        self.master.bind_all("<Button-4>", self._on_mousewheel)
        self.master.bind_all("<Button-5>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        # print("_unbound_to_mousewheel")
        self.master.unbind_all("<MouseWheel>")
        self.master.unbind_all("<Button-4>")
        self.master.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        # print("_on_mousewheel")
        if event.num==4:
            self.master.yview_scroll(int(-1*event.num), 'units')
        elif event.num==5:
            self.master.yview_scroll(int(event.num), 'units')
        
    def clear(self):
        # Delete current grid and widgets
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
            
        self.decomp_frame = []
     
    def updateLabels(self):
        """ Update constraint label according to activation state: Activated / Partially activated / Deactivated"""
        
        activated_str = ''
        deactivated_str = '*** '
        partial_str = '* '
        for k,x in self.constraint_labels.items():
            x.configure(text=x.cget('text').replace(activated_str, '').replace(deactivated_str, '').replace(partial_str, ''))
            
        for symbol in self.constraint_labels:
            l = self.constraint_labels[symbol]
            c = CAI.CM.constraints[symbol]
            if c.isActivated():
                l.configure(text=activated_str + l.cget("text"))
            else:
                if c.isPartiallyActivated():
                    l.configure(text=partial_str + l.cget("text"))
                else:
                    l.configure(text=deactivated_str + l.cget("text"))
    
    def updateLastStateCheckboxes(self):
        for symbol in self.checkboxes:
            self.last_checkboxes_state[symbol] = self.checkboxes[symbol].get()
        
    def checkboxHandler(self):
        """ Handle dynamic selection of all decomposed when clicking on raw"""
        
        # Find clicked checkbox
        for symbol in self.checkboxes:
            if self.checkboxes[symbol].get() != self.last_checkboxes_state[symbol]:
                checkbox = symbol
                checked = self.checkboxes[symbol].get()==1
        
        # If raw
        if checkbox in CAI.CM.raw_constraints:
            for child in CAI.CM.raw_constraints[checkbox].children:
                if checked:
                    # Then check all children 
                    self.checkboxes[child.symbol].select()
                else:
                    # uncheck all chidren
                    self.checkboxes[child.symbol].deselect()
                
        # If decomposed
        elif checkbox in CAI.CM.decomposed_constraints:
            parent = CAI.CM.constraints[checkbox].parent
            
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
        self.show_checkboxes = not self.show_checkboxes
        if self.show_checkboxes:
            self.showCheckboxes()
        else:
            self.hideCheckboxes()
    def showCheckboxes(self):
        self.updateLastStateCheckboxes()
        for k,cb in self.checkboxes.items():
            cb.grid()
    def hideCheckboxes(self):
        for k,cb in self.checkboxes.items():
            cb.grid_remove()
    def selectActivatedCheckboxes(self):
        for symbol,cb in self.checkboxes.items():
            if CAI.CM.constraints[symbol].isActivated():
                cb.select()
            else:
                cb.deselect()
    def selectAll(self):
        for symbol,cb in self.checkboxes.items():
            cb.select()
        self.updateLastStateCheckboxes()
    def unselectAll(self):
        for symbol,cb in self.checkboxes.items():
            cb.deselect()
        self.updateLastStateCheckboxes()
                    
    def toggleEncodings(self):
        self.show_encodings = not self.show_encodings
        if self.show_encodings:
            self.showEncodings()
        else:
            self.hideEncodings()
    def showEncodings(self):
        for k,x in self.encoding_labels.items():
            x.grid()
    def hideEncodings(self):
        for k,x in self.encoding_labels.items():
            x.grid_remove()
        
    def toggleDecomps(self):
        self.show_decomps = not self.show_decomps
        if self.show_decomps:
            self.showDecomps()
        else:
            self.hideDecomps()
    def showDecomps(self):
        for f in self.decomp_frame:
            f.grid()
    def hideDecomps(self):
        for f in self.decomp_frame:
            f.grid_remove()
    
class ButtonsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title = "Constraint actions"
        self.buttons = {}
        
        buttons_width = 100
        buttons_column1_width = 100
        
        color_constraints='OrangeRed3'
        color_planning='#3B8ED0'
        color_planning=None
        color_display='gray40'
        
        # First column (hidden)
        self.frame_hidden_column = customtkinter.CTkFrame(self, fg_color='gray17')
        self.frame_hidden_column.grid(row=0, column=0, padx=0, pady=0)
        self.frame_hidden_column.grid_remove()
        i_row=0
        self.confirm_function = None
        self.confirm_button = customtkinter.CTkButton(self.frame_hidden_column, text="Confirm", width=buttons_column1_width, command=self.confirm)
        self.confirm_button.grid(row=i_row, column=0, padx=10, pady=3)
        self.confirm_button.grid_remove()
        i_row+=1
        
        self.select_all_button = customtkinter.CTkButton(self.frame_hidden_column, text="All", width=buttons_column1_width, command=self.master.constraints_frame.selectAll)
        self.select_all_button.grid(row=i_row, column=0, padx=10, pady=3)
        self.select_all_button.grid_remove()
        i_row+=1
        
        self.unselect_all_button = customtkinter.CTkButton(self.frame_hidden_column, text="Clear", width=buttons_column1_width, command=self.master.constraints_frame.unselectAll)
        self.unselect_all_button.grid(row=i_row, column=0, padx=10, pady=3)
        self.unselect_all_button.grid_remove()
        i_row+=1
        
        # Second column (always shown)
        self.frame_always_column = customtkinter.CTkFrame(self, fg_color='gray17')
        self.frame_always_column.grid(row=0, column=1, padx=0, pady=0)
        i_row=0
        self.buttons["Add"] = customtkinter.CTkButton(self.frame_always_column, text="Add", width=buttons_width, fg_color=color_constraints, command=self.addT)
        self.buttons["Add"].grid(row=i_row, column=1, padx=10, pady=3)
        self.add_nl_constraints = []
        i_row+=1
        
        self.buttons["Delete"] = customtkinter.CTkButton(self.frame_always_column, text="Delete", width=buttons_width, fg_color=color_constraints, command=self.delete)
        self.buttons["Delete"].grid(row=i_row, column=1, padx=10, pady=3)
        i_row+=1
        
        self.buttons["Activate"] = customtkinter.CTkButton(self.frame_always_column, text="Activate /\nDeactivate", width=buttons_width, fg_color=color_constraints, command=self.activate)
        self.buttons["Activate"].grid(row=i_row, column=1, padx=10, pady=3)
        i_row+=1
        
        self.buttons["E2NL"] = customtkinter.CTkButton(self.frame_always_column, text="Activate\nE2NL" if not CAI.WITH_E2NL else "Deactivate\nE2NL", width=buttons_width, fg_color=color_constraints, command=self.toggleE2NL)
        self.buttons["E2NL"].grid(row=i_row, column=1, padx=10, pady=3)
        i_row+=1
        
        self.buttons["Plan"] = customtkinter.CTkButton(self.frame_always_column, text="Plan", width=buttons_width, fg_color=color_planning, command=self.planT)
        self.buttons["Plan"].grid(row=i_row, column=1, padx=10, pady=3)
        i_row+=1
        
        self.buttons["ChangePlanningMode"] = customtkinter.CTkButton(self.frame_always_column, text="Change\nPlanning Mode", width=buttons_width, fg_color=color_planning, command=self.changePlanModeT)
        self.buttons["ChangePlanningMode"].grid(row=i_row, column=1, padx=10, pady=3)
        i_row+=1
        
        self.buttons["ChangeTimeout"] = customtkinter.CTkButton(self.frame_always_column, text="Change\nTimeout (TO)", width=buttons_width, fg_color=color_planning, command=self.changeTimeout)
        self.buttons["ChangeTimeout"].grid(row=i_row, column=1, padx=10, pady=3)
        i_row+=1
        
        self.buttons["ToggleDecomps"] = customtkinter.CTkButton(self.frame_always_column, text="Show\nDecomps" if not self.master.constraints_frame.show_decomps else "Hide\nDecomps", width=buttons_width, fg_color=color_display, command=self.toggleDecomps)
        self.buttons["ToggleDecomps"].grid(row=i_row, column=1, padx=10, pady=3)
        i_row+=1
        
        self.buttons["ToggleEncodings"] = customtkinter.CTkButton(self.frame_always_column, text="Show\nEncodings" if not self.master.constraints_frame.show_encodings else "Hide\nEncodings", width=buttons_width, fg_color=color_display, command=self.toggleEncodings)
        self.buttons["ToggleEncodings"].grid(row=i_row, column=1, padx=10, pady=3)
        i_row+=1
        
    def confirm(self):
        self.confirm_function()
        
    def select_all(self):
        self.master.constraints_frame.selectAll()
        
    def showSelectAllButtons(self):
        self.frame_hidden_column.grid()
        self.select_all_button.grid()
        self.unselect_all_button.grid()
    def hideSelectAllButtons(self):
        self.frame_hidden_column.grid_remove()
        self.select_all_button.grid_remove()
        self.unselect_all_button.grid_remove()
        
    def showConfirmButton(self, txt="Confirm"):
        self.frame_hidden_column.grid()
        self.confirm_button.configure(text=txt)
        self.confirm_button.grid()
    def hideConfirmButton(self):
        self.frame_hidden_column.grid_remove()
        self.confirm_button.grid_remove()
    
    def disableButtons(self):
        for k,x in self.buttons.items():
            if k not in ['ToggleEncodings', 'ToggleDecomps']:
                x.configure(state='disabled')
    def enableButtons(self):
        for k,x in self.buttons.items():
            x.configure(state='normal')
        
    def activateE2NLButton(self):
        self.buttons['E2NL'].configure(state='normal')
        self.update()
    def deactivateE2NLButton(self):
        self.buttons['E2NL'].configure(state='disabled')
        self.update()
    
    def addT(self):
        threading.Thread(target=self.add).start()
    def add(self):
        self.master.disableAllButtons()
        self.activateE2NLButton()
        
        startTimer()
        
        mprint("\n=== ADDING CONSTRAINT ===")
        time_total = time.time()
        
        t_input = time.time()
        c = minput(txt="\nEnter your constraint: ")
        
        if c in ['', 'abort']:
            self.master.enableAllButtons()
            mprint("Aborted\n")
        else:
            mprint("\n> " + c )
            t_input = time.time() - t_input
            try:
                constraint = CAI.createConstraint(c, t_input)
                CAI.decompose(constraint)
                self.deactivateE2NLButton()
                CAI.encode(constraint)
                constraint.time_total += time.time() - time_total
                CAI.CM.dump(CAI.g_problem_name)
                
            except Exception as err:
                if err.args[0]=='abort':
                    mprint('Aborted\n')
                else:
                    self.master.quit()
                    raise err
            
            self.master.enableAllButtons()
            self.master.constraints_frame.updateFrame()
            # mprint("\nConstraints added")
            
            # For ablation
            self.master.plan_frame.export()
            
            
        stopTimer()
        
            
        
    def delete(self):
        self.master.constraints_frame.unselectAll()
        self.master.constraints_frame.showCheckboxes()
        self.master.disableAllButtons()
        self.showConfirmButton(txt="Delete")
        self.showSelectAllButtons()
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
            CAI.CM.deleteConstraints(selection)
            self.master.constraints_frame.updateFrame()
        
        self.hideConfirmButton()
        self.hideSelectAllButtons()
        self.master.enableAllButtons()
        self.master.constraints_frame.hideCheckboxes()
        self.confirm_function = None
        
    def activate(self):
        self.master.constraints_frame.selectActivatedCheckboxes()
        self.master.constraints_frame.showCheckboxes()
        self.master.disableAllButtons()
        self.showSelectAllButtons()
        self.showConfirmButton()
        self.confirm_function = self.activateConfirm
    def activateConfirm(self):
        for k,x in self.master.constraints_frame.checkboxes.items():
            if x.get()==1:
                CAI.CM.constraints[k].activate()
            else:
                CAI.CM.constraints[k].deactivate()
                
        self.hideConfirmButton()
        self.hideSelectAllButtons()
        self.master.enableAllButtons()
        self.master.constraints_frame.hideCheckboxes()
        self.master.constraints_frame.updateLabels()
        self.confirm_function = None
        
    def planT(self):
        threading.Thread(target=self.plan).start()
    def plan(self):
        self.master.disableAllButtons()
        self.master.plan_frame = self.master.plan_frame
        
        # Planning
        result, plan, planlength, metric, fail_reason, time_compilation, time_planning = self.master.display_frame.startWithTimer(CAI.planWithConstraints)
        
        # Save results
        self.master.plan_frame.previous_results = self.master.plan_frame.last_results
        self.master.plan_frame.last_results = {
            'result': result,
            'plan': plan,
            'planlength': planlength,
            'metric': metric,
            'fail_reason': fail_reason,
            'time_compilation': time_compilation,
            'time_planning': time_planning,
        }
        
        # Show previous results
        if self.master.plan_frame.previous_results=={}:
            self.master.plan_frame.printPrevious("None")
        elif self.master.plan_frame.previous_results['result']=='failed':
            self.master.plan_frame.printPrevious('Failed to plan: '+self.master.plan_frame.previous_results['fail_reason'])
        else:
            txt = ''
            txt += 'Plan-Length: ' + str(self.master.plan_frame.previous_results['planlength']) + '\n'
            txt += 'Metric: ' + str(self.master.plan_frame.previous_results['metric']) + '\n'
            txt += 'Planning time: ' + '{:.2f}'.format(self.master.plan_frame.previous_results['time_planning'])
            self.master.plan_frame.printPrevious(txt)
            
        # Show last results
        if self.master.plan_frame.last_results['result']=='failed':
            self.master.plan_frame.printMain('Failed to plan: '+self.master.plan_frame.last_results['fail_reason'])
        else:
            txt = ''
            txt += 'Plan-Length: ' + str(self.master.plan_frame.last_results['planlength']) + '\n'
            txt += 'Metric: ' + str(self.master.plan_frame.last_results['metric']) + '\n'
            txt += 'Planning time: ' + '{:.2f}'.format(self.master.plan_frame.last_results['time_planning']) + '\n'
            txt += 'Found Plan:\n' + self.master.plan_frame.last_results['plan']
            self.master.plan_frame.printMain(txt)
        
        self.master.plan_frame.updateSimButton()
        
    def changePlanModeT(self):
        threading.Thread(target=self.changePlanMode).start()
    def changePlanMode(self):
        self.master.disableAllButtons()
        
        mprint(f"\nCurrent planning mode: {CAI.g_planning_mode}")
        mprint(f"Select a planning mode:\n\t1 - {PlanMode.ANYTIME}\n\t2 - {PlanMode.ANYTIMEAUTO}\n\t3 - {PlanMode.DEFAULT}\n\t4 - {PlanMode.OPTIMAL}\n\t5 - {PlanMode.SATISFICING}")
        
        c = minput()
        
        # Check if correct
        if c in ['1', '2', '3', '4', '5']:
            mprint("> " + c )
            if c=='1':
                CAI.g_planning_mode=PlanMode.ANYTIME
            if c=='2':
                CAI.g_planning_mode=PlanMode.ANYTIMEAUTO
            if c=='3':
                CAI.g_planning_mode=PlanMode.DEFAULT
            if c=='4':
                CAI.g_planning_mode=PlanMode.OPTIMAL
            if c=='5':
                CAI.g_planning_mode=PlanMode.SATISFICING
            
            mprint(f"\nPlanning mode set to: {CAI.g_planning_mode}")
            
            if CAI.g_timeout==None and CAI.g_planning_mode in [PlanMode.ANYTIME, PlanMode.ANYTIMEAUTO]:
                mprint('WARNING: Timeout disabled with Anytime planning mode!')
        else: 
            if c=='':
                mprint("Incorrect input")
            mprint("Aborted\n")
            
        self.master.enableAllButtons()
    
    def changeTimeout(self):
        self.master.disableAllButtons()
        x = customtkinter.CTkInputDialog(title='Enter Timeout', text=f"Current Timeout: {CAI.g_timeout}s\nEnter a new timeout\n(Leave empty to disable timeout): ")
        c = x.get_input()
        
        try:
            t = float(c)
            assert t>0
            CAI.g_timeout = t
            mprint(f'Timeout updated: {CAI.g_timeout}')
        except:
            CAI.g_timeout = None
            mprint(f'Timeout disabled')
            if CAI.g_planning_mode in [PlanMode.ANYTIME, PlanMode.ANYTIMEAUTO]:
                mprint('WARNING: Timeout disabled with Anytime planning mode!')

        self.master.enableAllButtons()
    
    def toggleEncodings(self):
        self.master.constraints_frame.toggleEncodings()
        self.buttons['ToggleEncodings'].configure(text="Show\nEncodings" if not self.master.constraints_frame.show_encodings else "Hide\nEncodings")
        
    def toggleE2NL(self):
        CAI.WITH_E2NL = not CAI.WITH_E2NL
        self.buttons['E2NL'].configure(text="Activate\nE2NL" if not CAI.WITH_E2NL else "Deactivate\nE2NL")
        
    def toggleDecomps(self):
        self.master.constraints_frame.toggleDecomps()
        self.buttons['ToggleDecomps'].configure(text="Show\nDecomps" if not self.master.constraints_frame.show_decomps else "Hide\nDecomps")
    
class DisplayFrame(customtkinter.CTkFrame):
    font = ('Arial', 18)
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.write_lock = threading.Lock()
        self.textbox = customtkinter.CTkTextbox(self, wrap='word', font=DisplayFrame.font)
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="ewsn")
        self.textbox.bind("<Escape>", lambda x: exit())
        self.textbox.bind('<Key>',lambda e: 'break') 
        # tab = customtkinter.CTkFont(self.textbox._font).measure('    ')
        self.textbox.configure(tabs=70)
        
        self.buttons = {}
        
        
        # Clear display
        N = 20
        self.prompt("\n" * N)
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text="", font=DisplayFrame.font)
        self.entry.configure(state='disabled')
        self.entry.grid(row=1, column=0, padx=10, pady=0, sticky="ew")
        self.entry_text = ''
        self.entry_stamp = None
        self.entry_dark = ('#F9F9FA', '#343638')
        self.entry_light = ('#F9F9FA', '#585a5c')
        
        self.frame_bottom = customtkinter.CTkFrame(self)
        self.frame_bottom.grid(row=2, column=0, columnspan=2, padx=0, pady=0, sticky="ewsn")
        self.frame_bottom.grid_columnconfigure(0, weight=1)
        # self.frame_bottom.grid_columnconfigure(1, weight=1)
        # self.frame_bottom.grid_columnconfigure(2, weight=1)
        self.frame_bottom.grid_columnconfigure(3, weight=1)
        
        self.timer_label = customtkinter.CTkLabel(self.frame_bottom, text="Elapsed Time: 0.0 s", font = App.font)
        self.timer_label.grid(row=0, column=0, padx=10, pady=0, sticky="ew")
        self.start_time = None
        self._timer_running = False
        
        self.suggestions = "< No suggestions >"
        self.buttons['suggestions_generate'] = customtkinter.CTkButton(self.frame_bottom, text='Generate\nSuggestions', font=DisplayFrame.font, command=self.generateSuggestionsT)
        self.buttons['suggestions_generate'].grid(row=0, column=1, padx=5, pady=5)
        
        self.buttons['suggestions_print'] = customtkinter.CTkButton(self.frame_bottom, text='Print\nSuggestions', font=DisplayFrame.font, command=self.printSuggestions)
        self.buttons['suggestions_print'].grid(row=0, column=2, padx=5, pady=5)
        
        self.buttons['dump_CM'] = customtkinter.CTkButton(self.frame_bottom, text="Dump\nConstraints", font=DisplayFrame.font, command= lambda: CAI.CM.dump(CAI.g_problem_name))
        self.buttons['dump_CM'].grid(row=0, column=4, padx=10, pady=10)
        
        self.buttons['load_CM'] = customtkinter.CTkButton(self.frame_bottom, text='Load\nConstraints', font=DisplayFrame.font, command=self.loadConstraints)
        self.buttons['load_CM'].grid(row=0, column=5, padx=5, pady=5)
    
    def disableButtons(self):
        for k,x in self.buttons.items():
            x.configure(state='disabled')
    def enableButtons(self):
        for k,x in self.buttons.items():
            x.configure(state='normal')
    
    def generateSuggestionsT(self):
        threading.Thread(target=self.generateSuggestions).start()
    def generateSuggestions(self):
        self.master.disableAllButtons()
        CAI.suggestions()
        self.master.enableAllButtons()
        
    def printSuggestions(self):
        mprint("\nSuggestions:")
        mprint(CAI.g_suggestions)
    
    def loadConstraints(self):
        self.master.disableAllButtons()
        filename = filedialog.askopenfilename(initialdir='dumps_CM/', title='Select a File', filetypes=(('JSON files', '*.json'), ('all files', '*.*')))
        if isinstance(filename, str) and filename!='':
            CAI.CM.load(filename)
            self.master.constraints_frame.updateFrame()
        self.master.enableAllButtons()
        
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
        r = t.join()
        self.master.enableAllButtons()
        return r
    
    def startTimer(self):
        self.start_time = time.time()
        self._timer_running = True
        self.update_timer()
        
    def stopTimer(self):
        self._timer_running = False
        
            
    def prompt(self, text, end="\n"):
        self.write_lock.acquire()
        # self.textbox.configure(state="normal")
        self.textbox.insert('end', text+end)
        # self.textbox.configure(state="disabled")
        self.textbox.see('end')
        # self.textbox.focus_set()
        self.write_lock.release()
        self.update()
        
    def replace_last_line(self, new_text, end='\n'):
        self.write_lock.acquire()
        # Get index of last line
        last_line_index = self.textbox.index('end-2c linestart')
        # Delete the entire last line
        self.textbox.delete(last_line_index, 'end-1c')
        # Insert the new text at the last line's start
        self.textbox.insert(last_line_index, new_text + end)
        self.write_lock.release()
        self.update()
        
    def activateEntry(self, txt=""):
        if txt!="":
            mprint(txt, end="")
        self.entry.configure(state="normal")
        self.entry.configure(fg_color=self.master.display_frame.entry_light)
        self.entry.focus()
        
    def getFromEntry(self, txt=""):
        self.activateEntry(txt)
        while self.entry_stamp==None:
            time.sleep(0.1)
        self.entry_stamp = None
        return self.entry_text
        
    def validateEntry(self, event):
        if self.entry.cget("state") == 'disabled':
            return None
        self.entry_text = self.entry.get()
        self.entry_stamp = time.time()
        self.entry.delete(0, customtkinter.END)
        self.entry.configure(state="disabled")
        self.entry.configure(fg_color=self.master.display_frame.entry_dark)
        
class PlanFrame(customtkinter.CTkFrame):
    label_font = ("Arial", 16, "bold")
    plan_font = ("Arial", 14)
    
    def __init__(self, master):
        super().__init__(master)
        
        self.buttons = {}
        
        self.last_results = {}
        self.previous_results = {}
        
        self.grid_columnconfigure(0, weight=1)
        i_self_row = 0
        
        self.title = customtkinter.CTkLabel(self, text="Plans", fg_color="gray30", width=400, corner_radius=6,font=App.font)
        self.title.grid(row=i_self_row, column=0, padx=10, pady=(10, 0), sticky="ew")
        i_self_row+=1
        
        self.previous_label = customtkinter.CTkLabel(self, text="Previous:", font=PlanFrame.label_font)
        self.previous_label.grid(row=i_self_row, column=0, padx=10, pady=5, sticky="ew")
        i_self_row+=1
        
        self.write_previous_lock = threading.Lock()
        self.previous_textbox = customtkinter.CTkTextbox(self, wrap='char', font=PlanFrame.plan_font)
        self.printPrevious("None")
        self.previous_textbox.configure(height=98)
        self.previous_textbox.grid(row=i_self_row, column=0, padx=10, pady=2, sticky="nsew")
        # self.grid_rowconfigure(2, weight=1)
        i_self_row+=1
        
        self.current_label = customtkinter.CTkLabel(self, text="Current:", font=PlanFrame.label_font)
        self.current_label.grid(row=i_self_row, column=0, padx=10, pady=5, sticky="ew")
        i_self_row+=1
        
        self.write_main_lock = threading.Lock()
        self.textbox = customtkinter.CTkTextbox(self, wrap='char', font=PlanFrame.plan_font)
        self.printMain("None")
        self.textbox.grid(row=i_self_row, column=0, padx=10, pady=2, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        i_self_row+=1
        
        self.buttons_frame = customtkinter.CTkFrame(self)
        self.buttons_frame.grid(row=i_self_row, column=0, padx=10, pady=10, sticky="nsew")
        i_self_row+=1
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.buttons_frame.grid_columnconfigure(1, weight=1)
        
        self.buttons['update_sim'] = customtkinter.CTkButton(self.buttons_frame, text="Update Sim", command=self.updateSimButton, width=80)
        self.buttons['update_sim'] .grid(row=0, column=0, padx=10, pady=10)
        
        self.buttons['copy'] = customtkinter.CTkButton(self.buttons_frame, text="Copy", command=self.copy, width=80)
        self.buttons['copy'].grid(row=0, column=1, padx=10, pady=10)
        
        self.buttons['export'] = customtkinter.CTkButton(self.buttons_frame, text="Export", command=self.export, width=80)
        self.buttons['export'].grid(row=0, column=2, padx=10, pady=10)
    
    def disableButtons(self):
        for k,x in self.buttons.items():
            x.configure(state='disabled')
    def enableButtons(self):
        for k,x in self.buttons.items():
            x.configure(state='normal')
    
    def updateSimButton(self):
        txt = self.textbox.get("0.0", "end")
        if txt[:len("Failed to plan:")]!="Failed to plan:":
            t = "Found Plan:\n"
            i1 = txt.find(t)+len(t)
            plan = txt[i1:]
            updatePDSimPlan(plan)
            # mprint("\nSim updated.")
        
    def copy(self):
        pyperclip.copy(self.textbox.get("0.0", "end"))
        mprint("\nCopied!")
        
    def export(self):
        
        data = {}
        
        data['problem_name'] = CAI.g_problem_name
        data['detailed_translation_times'] = {
            'total_time': 0,
            'input_time': 0,
            'decomp_time': 0,
            'decomp_validation_time': 0,
            'redecomp_time': 0,
            'initial_encoding_time': 0,
            'encoding_time': 0,
            'verifier_time': 0,
            'reencoding_time': 0,
            'e2nl_time': 0,
            'encoding_validation_time': 0,
            'e2nl_reencoding_time': 0,
        }
        for idr,r in CAI.CM.raw_constraints.items():
            if r.isActivated() or r.isPartiallyActivated():
                data['detailed_translation_times']['total_time'] += r.time_total
                data['detailed_translation_times']['input_time'] += r.time_input
                data['detailed_translation_times']['decomp_time'] += r.time_initial_decomp
                data['detailed_translation_times']['decomp_validation_time'] += r.time_decomp_validation
                data['detailed_translation_times']['redecomp_time'] += r.time_redecomp
                data['detailed_translation_times']['initial_encoding_time'] += r.time_initial_encoding
                for d in r.children:
                    if d.isActivated():
                        data['detailed_translation_times']['encoding_time'] += d.time_encoding
                        data['detailed_translation_times']['verifier_time'] += d.time_verifier
                        data['detailed_translation_times']['reencoding_time'] += d.time_reencoding
                        data['detailed_translation_times']['e2nl_time'] += d.time_e2nl
                        data['detailed_translation_times']['encoding_validation_time'] += d.time_e2nl_validation
                        data['detailed_translation_times']['e2nl_reencoding_time'] += d.time_e2nl_reencoding

        data['translation_time'] = 0
        data['translation_time'] += data['detailed_translation_times']['total_time']
        
        data['decomposition_time'] = 0
        data['decomposition_time'] += data['detailed_translation_times']['decomp_time']
        data['decomposition_time'] += data['detailed_translation_times']['redecomp_time']
        
        data['encoding_time'] = 0
        data['encoding_time'] += data['detailed_translation_times']['initial_encoding_time'] 
        data['encoding_time'] += data['detailed_translation_times']['verifier_time']
        data['encoding_time'] += data['detailed_translation_times']['e2nl_time']
        data['encoding_time'] += data['detailed_translation_times']['e2nl_reencoding_time']
        
        data['input_time'] = 0
        data['input_time'] += data['detailed_translation_times']['input_time'] 
        
        data['interaction_time'] = 0
        data['interaction_time'] += data['detailed_translation_times']['decomp_validation_time']
        data['interaction_time'] += data['detailed_translation_times']['encoding_validation_time']
        
        data['planning_results'] = self.last_results
        
        data['solving_time'] = 0
        if data['planning_results']!={} and data['planning_results']['result']=='success':
            data['solving_time'] += data['translation_time']
            data['solving_time'] += data['planning_results']['time_compilation']
            data['solving_time'] += data['planning_results']['time_planning']
        
        mprint('\n=== EXPORT ===\n')
        mprint('Translation time = ' + '{:.2f}'.format(data['translation_time']))
        mprint('\tInput time = ' + '{:.2f}'.format(data['input_time']))
        mprint('\tInteraction time = ' + '{:.2f}'.format(data['interaction_time']))
        mprint('\tDecomposition time = ' + '{:.2f}'.format(data['decomposition_time']))
        mprint('\tEncoding time = ' + '{:.2f}'.format(data['encoding_time']))
        if data['planning_results']!={} and data['planning_results']['result']=='success':
            mprint('Solving time = ' + '{:.2f}'.format(data['solving_time']))
            mprint('Plan length = ' + '{}'.format(data['planning_results']['planlength']))
            mprint('Plan metric = ' + '{:.2f}'.format(data['planning_results']['metric']))
        

        
        date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
        filename = f'export_results/{CAI.g_problem_name}_{date}.json' 
        
        result, encodingsStr, err = CAI.checkIfUpdatedProblemIsParsable()
        pyperclip.copy(encodingsStr)
        if result:
            mprint('Parsable problem')
        else:
            mprint("Can't parse new problem (Syntax error)")
            mprint(str(err))
        can_parse = 1 if result else 0
        nb_h_interventions = -1
        comments = ""
        for k, d in CAI.CM.decomposed_constraints.items(): 
            for t in d.encoding_conv.turns:
                if t['role']=='user':
                    nb_h_interventions+=1
                    # if nb_h_interventions!=0:
                    #     comments += '> ' + t['content'][0]['text'] + '\n'
        nb_h_interventions -= CAI.nb_encoding_retry
        nb_h_reviews = nb_h_interventions+1
        input_t, inter_t, decomp_t, enco_t, trans_t = data['input_time'],data['interaction_time'],data['decomposition_time'],data['encoding_time'],data['translation_time']
        
        c = minput(txt="\nIs it correct?")
        mprint("\n> " + c )
        if c in ['y', 'Y', 'yes', '']:
            correct = 1
        else:
            correct = 0
            if comments =='':
                comments = c
            else:
                comments += '\n'+c
        
        txtCSV = f'"{encodingsStr}",{can_parse},{input_t},{inter_t},{decomp_t},{enco_t},{trans_t},{correct},{nb_h_reviews},{nb_h_interventions},"{comments}"\n'
        with open('test.csv', 'a') as f:
            f.write(txtCSV)
            
        data_CM = (data, CAI.CM)
        json_string= jsonpickle.encode(data_CM, indent=4)
        with open(filename, 'w') as f:
            f.write(json_string)
            
    def printMain(self, txt):
        self.write_main_lock.acquire()
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", 'end')
        self.textbox.insert('end', txt)
        self.textbox.configure(state="disabled")
        self.write_main_lock.release()
        
    def printPrevious(self, txt):
        self.write_previous_lock.acquire()
        self.previous_textbox.configure(state="normal")
        self.previous_textbox.delete("0.0", 'end')
        self.previous_textbox.insert('end', txt)
        self.previous_textbox.configure(state="disabled")
        self.write_previous_lock.release()

class App(customtkinter.CTk):
    font = ("Arial", 20, "bold")
    
    def __init__(self):
        super().__init__()

        self.title("CAI - Alpha Version")
        self.geometry("3400x1912")
        
        # self.iconbitmap("rsc/icon.ico")
        im = Image.open('rsc/icon.png')
        photo = ImageTk.PhotoImage(im)
        self.wm_iconphoto(True, photo)
        
        self.grid_columnconfigure(0, weight=20)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        
        self.constraints_frame = ConstraintsFrame(self)
        self.constraints_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.buttons_frame = ButtonsFrame(self)
        self.buttons_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        self.display_frame = DisplayFrame(self)
        self.display_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")
        
        self.plan_frame = PlanFrame(self)
        self.plan_frame.grid(row=0, column=2, rowspan=2, padx=5, pady=5, sticky='nsew')
        
        # TODO: Escape also kills child threads
        self.bind("<Escape>", lambda x: exit())
        self.bind("<Return>", self.display_frame.validateEntry)
        self.bind("<KP_Enter>", self.display_frame.validateEntry)
        self.bind('<Control-c>',lambda e: self.handleEventCopy()) 
        
        # self.bind("beef", lambda x: print("ooh yummy!"))
        
        setPrintFunction(self.display_frame.prompt)
        setInputFunction(self.display_frame.getFromEntry)
        setReplacePrintFunction(self.display_frame.replace_last_line)
        setStartTimer(self.display_frame.startTimer)
        setStopTimer(self.display_frame.stopTimer)
        
    def handleEventCopy(self):
        try:
            pyperclip.copy(self.display_frame.textbox.selection_get())
        except: 
            try:
                pyperclip.copy(self.plan_frame.textbox.selection_get())
            except:
                try:
                    pyperclip.copy(self.plan_frame.previous_textbox.selection_get())
                except: pass
        return 'break'
    
    def disableAllButtons(self):
        self.buttons_frame.disableButtons()
        self.plan_frame.disableButtons()
        self.display_frame.disableButtons()
    def enableAllButtons(self):
        self.buttons_frame.enableButtons()
        self.plan_frame.enableButtons()
        self.display_frame.enableButtons()
