import customtkinter
import Constraints
import typing
import time
from defs import *

customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

class ConstraintsFrame(customtkinter.CTkFrame):
    def __init__(self, master, CM: Constraints.ConstraintManager):
        super().__init__(master)
        self.CM = CM
        self.checkboxes = {}
        self.last_checkboxes_state = {}
        self.constraint_labels = {}
        self.encoding_labels = {}
        self.height_checkbox_frame = 20
        self.width_checkbox_frame = 31
        
        i_row = 0
        for k,r in CM.raw_constraints.items():
            
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
                
        
        print(self.constraint_labels['R0'].cget('font'))
                
        # Initialize last checkboxes state
        self.updateLastStateCheckboxes()
        
        self.hideEncodings()
                
        self.button_toggle_checkboxes = customtkinter.CTkButton(self, text="Toggle checkboxes", command=self.toggleCheckboxes)
        self.button_toggle_checkboxes.grid(row=i_row, column=0, padx=10, pady=10, sticky="w")
        self.show_checkboxes = False
        i_row+=1
        
        self.hideCheckboxes()
        
        self.button_toggle_encodings = customtkinter.CTkButton(self, text="Toggle encodings", command=self.toggleEncodings, width=30)
        self.button_toggle_encodings.grid(row=i_row, column=0, padx=10, pady=10, sticky="w")
        self.show_encodings = False
        i_row+=1
        
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
        if checkbox in self.CM.raw_constraints:
            for child in self.CM.raw_constraints[checkbox].children:
                if checked:
                    # Then check all children 
                    self.checkboxes[child.symbol].select()
                else:
                    # uncheck all chidren
                    self.checkboxes[child.symbol].deselect()
                
        # If decomposed
        elif checkbox in self.CM.decomposed_constraints:
            parent = self.CM.constraints[checkbox].parent
            
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
        self.show_checkboxes = not self.show_checkboxes
    def showCheckboxes(self):
        # Delect all first
        for symbol in self.checkboxes:
            self.checkboxes[symbol].deselect()
        self.updateLastStateCheckboxes()
        
        for k,cb in self.checkboxes.items():
            cb.grid()
    def hideCheckboxes(self):
        for k,cb in self.checkboxes.items():
            cb.grid_remove()
                    
    def toggleEncodings(self):
        if self.show_encodings:
            self.hideEncodings()
        else:
            self.showEncodings()
        self.show_encodings = not self.show_encodings
    def showEncodings(self):
        for k,x in self.encoding_labels.items():
            x.grid()
    def hideEncodings(self):
        for k,x in self.encoding_labels.items():
            x.grid_remove()
        
class ButtonsFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.title = "Constraint actions"
        self.buttons = {}
        
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
        
    def add(self):
        pass
    def delete(self):
        pass
    def activate(self):
        pass
    def deactivate(self):
        pass
    def plan(self):
        pass
        
class DisplayFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.label = customtkinter.CTkLabel(self, text="CTkLabel", fg_color="transparent")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        self.entry = customtkinter.CTkEntry(self, placeholder_text="CTkEntry")
        self.entry.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

class App(customtkinter.CTk):
    def __init__(self, CM: Constraints.ConstraintManager):
        super().__init__()

        self.title("my app")
        self.geometry("1200x800")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.constraints_frame = ConstraintsFrame(self, CM)
        self.constraints_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.buttons_frame = ButtonsFrame(self)
        self.buttons_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.display_frame = DisplayFrame(self)
        self.display_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# def key_handler(event):
    # print(event.char, event.keysym, event.keycode)

if __name__=="__main__":
    CM = Constraints.ConstraintManager()
    r = CM.createRaw("never use plane1")
    d = CM.createDecomposed(r, "Person1, person2, person3, and person4 should never be in plane1.")
    d.encoding = "(always (and (not (in person1 plane1)) (not (in person2 plane1)) (not (in person3 plane1)) (not (in person4 plane1))))"
    d = CM.createDecomposed(r, "Plane1 should remain at its initial location (city1) throughout the plan.")
    d.encoding = "(always (located plane1 city1))"
    d = CM.createDecomposed(r, "The number of people onboard plane1 should always be zero.")
    d.encoding = "(always (= (onboard plane1) 0))"
    d = CM.createDecomposed(r, "The fuel level of plane1 should remain unchanged from its initial value.")
    d.encoding = "(always (= (fuel plane1) 174))"
    r = CM.createRaw("plane2 should be in city2 at the end")
    d = CM.createDecomposed(r, "plane2 must be located in city2 in the final state")
    d.encoding = "(at-end (located plane2 city2))"
    
    app = App(CM)
    app.bind("<Escape>", lambda x: exit())
    # app.bind("<Key>", key_handler)
    # app.bind("beef", lambda x: print("ooh yummy!"))
    app.mainloop()