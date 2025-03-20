import customtkinter
import Constraints
import typing
import time
from defs import *
import cai

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class ConstraintsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
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
        
        if cai.CM.constraints == {}:
            label = customtkinter.CTkLabel(self, text="No constraints")
            label.grid(row=i_row, column=0, padx=0, pady=0, sticky="w")
            i_row += 1
        else:
            for k,r in cai.CM.raw_constraints.items():
                
                frame = customtkinter.CTkFrame(self, fg_color="transparent")
                frame.grid(row=i_row, column=0, padx=0, pady=0, sticky="w")
                
                framecb = customtkinter.CTkFrame(frame, fg_color="transparent", height=self.height_checkbox_frame, width=self.width_checkbox_frame)
                framecb.grid(row=0, column=0, padx=0, pady=0)
                
                self.checkboxes[r.symbol] = customtkinter.CTkCheckBox(framecb, text='', width=0, command=self.checkboxHandler)
                self.checkboxes[r.symbol].grid(row=0, column=0, padx=0, pady=0, sticky="w")
                
                self.constraint_labels[r.symbol] = customtkinter.CTkLabel(frame, text=f"{r.symbol} - {r.nl_constraint}")
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
                
                    self.constraint_labels[c.symbol] = customtkinter.CTkLabel(frame, text=f"{c.symbol}- {c.nl_constraint}")
                    self.constraint_labels[c.symbol].grid(row=0, column=1, padx=0, pady=0, sticky="w")
                
                    self.encoding_labels[c.symbol] = customtkinter.CTkLabel(frame, text=f"{c.encoding}")
                    self.encoding_labels[c.symbol].grid(row=1, column=1, padx=20, pady=0, sticky="w")
                    
                    i_row+=1
                    
        
        # Initialize last checkboxes state
        self.updateLastStateCheckboxes()
        
        self.hideEncodings()
        self.show_encodings = False
        self.hideCheckboxes()
        self.show_checkboxes = False
        
        self.updateLabels()
            
            
        # To remove
        self.button_toggle_checkboxes = customtkinter.CTkButton(self, text="Toggle checkboxes", command=self.toggleCheckboxes)
        self.button_toggle_checkboxes.grid(row=i_row, column=0, padx=10, pady=10, sticky="w")
        i_row+=1
        
        self.button_toggle_encodings = customtkinter.CTkButton(self, text="Toggle encodings", command=self.toggleEncodings, width=30)
        self.button_toggle_encodings.grid(row=i_row, column=0, padx=10, pady=10, sticky="w")
        i_row+=1
        
        
    
    def updateLabels(self):
        activated_str = ''
        deactivated_str = '*** '
        for k,x in self.constraint_labels.items():
            x.configure(text=x.cget('text').replace(activated_str, '').replace(deactivated_str, ''))
            
        for symbol in self.constraint_labels:
            l = self.constraint_labels[symbol]
            if cai.CM.constraints[symbol].isActivated():
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
        if checkbox in cai.CM.raw_constraints:
            for child in cai.CM.raw_constraints[checkbox].children:
                if checked:
                    # Then check all children 
                    self.checkboxes[child.symbol].select()
                else:
                    # uncheck all chidren
                    self.checkboxes[child.symbol].deselect()
                
        # If decomposed
        elif checkbox in cai.CM.decomposed_constraints:
            parent = cai.CM.constraints[checkbox].parent
            
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
        # Delect all first
        for symbol in self.checkboxes:
            self.checkboxes[symbol].deselect()
        self.updateLastStateCheckboxes()
        for k,cb in self.checkboxes.items():
            cb.grid()
        self.show_checkboxes = True
    def hideCheckboxes(self):
        for k,cb in self.checkboxes.items():
            cb.grid_remove()
        self.show_checkboxes = False
                    
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
        
        self.confirm_function = None
        self.confirm_button = customtkinter.CTkButton(self, text="Confirm", command=self.confirm)
        self.confirm_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.confirm_button.grid_remove()
        
        self.buttons["Add"] = customtkinter.CTkButton(self, text="Add", command=self.add)
        self.buttons["Add"].grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.buttons["Delete"] = customtkinter.CTkButton(self, text="Delete", command=self.delete)
        self.buttons["Delete"].grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
        self.buttons["Activate"] = customtkinter.CTkButton(self, text="Activate", command=self.activate)
        self.buttons["Activate"].grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.buttons["Deactivate"] = customtkinter.CTkButton(self, text="Deactivate", command=self.deactivate)
        self.buttons["Deactivate"].grid(row=3, column=0, padx=10, pady=10, sticky="ew")
        
        self.buttons["Plan"] = customtkinter.CTkButton(self, text="Plan", command=self.plan)
        self.buttons["Plan"].grid(row=4, column=0, padx=10, pady=10, sticky="ew")
    
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
        cai.addConstraintsAsk()
        self.master.constraints_frame.updateFrame()
        
    def delete(self):
        # Version shell ask
        # cai.deleteConstraintsAsk()
        # self.master.constraints_frame.updateFrame()
        
        # Version selection
        self.master.constraints_frame.showCheckboxes()
        self.hideButtons()
        self.showConfirmButton()
        self.confirm_function = self.deleteConfirm
    def deleteConfirm(self):
        # Get selection
        selection = []
        for k,x in self.master.constraints_frame.checkboxes.items():
            if x.get()==1:
                selection.append(k)
                
        # Delete selected constraints
        cai.deleteConstraints(selection)
        
        self.hideConfirmButton()
        self.showButtons()
        self.master.constraints_frame.hideCheckboxes()
        self.confirm_function = None
        
        self.master.constraints_frame.updateFrame()
    
    def activate(self):
        # TODO: Do differently, could initialze Checkboxes with current activated constraints, then check/uncheck desired constrint and update accordingly
        self.master.constraints_frame.showCheckboxes()
        self.hideButtons()
        self.showConfirmButton()
        self.confirm_function = self.activateConfirm
    def activateConfirm(self):
        # Get Selection
        selection = []
        for k,x in self.master.constraints_frame.checkboxes.items():
            if x.get()==1:
                selection.append(k)
        
        # Activate selected constraints
        for symbol in selection:
            cai.CM.constraints[symbol].activate()
        
        self.hideConfirmButton()
        self.showButtons()
        self.master.constraints_frame.hideCheckboxes()
        self.master.constraints_frame.updateLabels()
        self.confirm_function = None
        
    def deactivate(self):
        self.master.constraints_frame.showCheckboxes()
        self.hideButtons()
        self.showConfirmButton()
        self.confirm_function = self.deactivateConfirm
    def deactivateConfirm(self):
        # Get Selection
        selection = []
        for k,x in self.master.constraints_frame.checkboxes.items():
            if x.get()==1:
                selection.append(k)
        
        # Deactivate selected constraints
        for symbol in selection:
            cai.CM.constraints[symbol].deactivate()
        
        self.hideConfirmButton()
        self.showButtons()
        self.master.constraints_frame.hideCheckboxes()
        self.master.constraints_frame.updateLabels()
        self.confirm_function = None
        
    def plan(self):
        txt = cai.planWithConstraints()
        # Update planframe with txt
        self.master.plan_frame.showText(txt)
        
        
class DisplayFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.textbox = customtkinter.CTkTextbox(self, wrap='word')
        self.textbox.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text="CTkEntfffry")
        self.entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        
    def prompt(self, text):
        self.textbox.configure(state='normal')
        self.textbox.insert(customtkinter.END, '\n'+text)
        self.textbox.see('end')
        self.textbox.configure(state='disabled')

class PlanFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.title = customtkinter.CTkLabel(self, text="Current Plan", fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        
        self.textbox = customtkinter.CTkTextbox(self, wrap='char')
        self.textbox.configure(state='disabled')
        self.textbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
    def showText(self, txt):
        self.textbox.configure(state='normal')
        self.textbox.delete("0.0", 'end')
        self.textbox.insert('end', txt)
        self.textbox.configure(state='disabled')
        
        
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("my app")
        self.geometry("1200x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.constraints_frame = ConstraintsFrame(self)
        self.constraints_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.buttons_frame = ButtonsFrame(self)
        self.buttons_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.display_frame = DisplayFrame(self)
        self.display_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        
        self.plan_frame = PlanFrame(self)
        self.plan_frame.grid(row=0, column=3, rowspan=2, padx=10, pady=10, sticky='nsew')

# def key_handler(event):
    # print(event.char, event.keysym, event.keycode)

if __name__=="__main__":
    r = cai.CM.createRaw("never use plane1")
    d = cai.CM.createDecomposed(r, "Person1, person2, person3, and person4 should never be in plane1.")
    d.encoding = "(always (and (not (in person1 plane1)) (not (in person2 plane1)) (not (in person3 plane1)) (not (in person4 plane1))))"
    d = cai.CM.createDecomposed(r, "Plane1 should remain at its initial location (city1) throughout the plan.")
    d.encoding = "(always (located plane1 city1))"
    d = cai.CM.createDecomposed(r, "The number of people onboard plane1 should always be zero.")
    d.encoding = "(always (= (onboard plane1) 0))"
    d = cai.CM.createDecomposed(r, "The fuel level of plane1 should remain unchanged from its initial value.")
    d.encoding = "(always (= (fuel plane1) 174))"
    r = cai.CM.createRaw("plane2 should be in city2 at the end")
    d = cai.CM.createDecomposed(r, "plane2 must be located in city2 in the final state")
    d.encoding = "(at-end (located plane2 city2))"
    
    cai.init('zeno5_bis', PlanMode.DEFAULT)
    
    app = App()
    app.bind("<Escape>", lambda x: exit())
    # app.bind("<Key>", key_handler)
    # app.bind("beef", lambda x: print("ooh yummy!"))
    app.mainloop()