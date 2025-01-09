import tkinter as tk
from tkinter import ttk

class Node:

    def __init__(self, name):
        self.name = name
        self.children = [] # Stores child nodes
        self.parent = None # Stores parent node
        
    def add_child(self, child):
        #Prevent duplicate children
        if any(existing_child.name.lower() == child.name.lower() for existing_child in self.children):
            raise ValueError((f"Child with name '{child.name}' already exists under 'self.name'."))
        child.parent = self # Set the parent of the child
        self.children.append(child) # Add child to the current node's children

    def add_parent(self, parent):
        #Prevent duplicate parents
        if self.parent and self.parent.name == parent.name:
            raise ValueError(f"Node '{self.name}' already has a parent named 'parent.name'.")
        
        #Add a new parent above the current node
        if self.parent: #If current node already has a parent
            self.parent.children.remove(self) #Remove this node from old parent's children
            parent.add_child(self.parent) # Add the old parent as a child of the new parent
        parent.add_child(self) #Add this node to the new parent
        self.parent = parent # Set the new parent as the current node's parent
    
    def __repr__(self):
        return f"Node(name='{self.name}')"
    
    def display_tree(self, level=0):
        indent = " " * level # Indentation based on tree level
        tree = f"{indent}{self.name}\n"
        for child in self.children:
            tree += child.display_tree(level +1) # Recursively display children
        return tree
    
    def get_full_lineage(self):
        #Traverse upwards to get the full lineage
        lineage = []
        current = self
        while current:
            lineage.append(current.name)
            current = current.parent
        return " > ".join(reversed(lineage)) # Reverse to get root-to-node order

class PhylogenyApp:
    def __init__(self, root, root_node):
        self.root = root
        self.root.title("Phylogeny Tree Viewer")
        self.root.geometry("600x400")
        
        self.tree_root = root_node # The root of the phylogenetic tree
        self.edit_mode = False # Keeps track of whether Edit Mode is active
        
        #Title Label
        self.title_label = tk.Label(self.root, text = "Phylogeny Tree Viewer", font = ("Arial", 16, "bold"))
        self.title_label.pack(pady = 10)
        
        #Add a scrollbar
        scrollbar = tk.Scrollbar(self.root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        #Tree Diaplay Area (Text Box)
        self.display_area = tk.Text(self.root, width = 70, height = 15, wrap=tk.WORD, yscrollcommand = scrollbar.set)
        self.display_area.pack(pady=10)
        scrollbar.config(command=self.display_area.yview)
        #Bind mouse wheel to display area
        self.display_area.bind("<MouseWheel>", self._on_mouse_wheel)
        
        #Search Entry and Button
        self.search_frame = tk.Frame(self.root)
        self.search_frame.pack(pady = 5)
        
        self.search_label = tk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side=tk.LEFT, padx = 5)
        
        self.search_entry = tk.Entry(self.search_frame, width=30)  # Define the search entry field
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = tk.Button(self.search_frame, text="Search", command=self.search_tree)  # Define the search button
        self.search_button.pack(side=tk.LEFT, padx=5)
        
        #Bind 'Enter' key to search entry
        self.search_entry.bind("<Return>", self.trigger_search)
        
        #Buttons
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack()
        
        self.display_button = tk.Button(self.button_frame, text="Display Tree", command = self.display_tree)
        self.display_button.grid(row = 0, column = 0, padx = 10)
        
        self.edit_mode_button = tk.Button(self.button_frame, text="Edit Tree: OFF", command=self.toggle_edit_mode)
        self.edit_mode_button.grid(row = 0, column = 1, padx = 10)
        
        self.exit_button = tk.Button(self.button_frame, text = "Exit", command = self.root.quit)
        self.exit_button.grid(row = 0, column = 2, padx = 10)
        
        #Edit Mode Frame (hidden by default)
        self.edit_frame = tk.Frame(self.root)
        
        self.add_button = tk.Button(self.edit_frame, text="Add Node", command=self.add_node)
        self.add_button.pack(side=tk.LEFT, padx = 5)
        
        self.edit_button = tk.Button(self.edit_frame, text = "Edit Node", command=self.edit_node)
        self.edit_button.pack(side=tk.LEFT, padx = 5)
        
        self.delete_button = tk.Button(self.edit_frame, text = "Delete Node", command = self.delete_node)
        self.delete_button.pack(side = tk.LEFT, padx = 5)
        
    def toggle_edit_mode(self):
        #Toggle between View Mode and Edit Mode
        self.edit_mode = not self.edit_mode
        if self.edit_mode:
            self.edit_frame.pack(pady = 10) # Show the Edit Frame
            self.edit_mode_button.config(text = "Edit Tree: On")
            self.display_area.insert(tk.END, "\nEdit Mode activated. You can now add, edit, or delete nodes.\n")
        else:
            self.edit_frame.pack_forget() # Hide the Edit Frame
            self.edit_mode_button.config(text = "Edit Tree: OFF")
            self.display_area.insert(tk.END, "\nEdit Mode deactivated.\n")
            
    def add_node(self):
        #Add a new node to the tree as a child and optionally a parent of one or multiple children
        if not self.edit_mode:
            self.display_area.insert(tk.END, "Edit Mode must be enabled to add a node.\n")
            return
    
        # Popup window for adding a node
        self.add_window = tk.Toplevel(self.root)
        self.add_window.title("Add Node")
        
        # Node Name
        tk.Label(self.add_window, text = "Node Name:").grid(row = 1, column = 0, padx = 5, pady = 5)
        self.node_name_entry = tk.Entry(self.add_window, width = 30)
        self.node_name_entry.grid(row = 1, column = 1, padx = 5, pady = 5)
    
        # Parent Node selection (Optional, if not creating a root)
        tk.Label(self.add_window, text = "Parent Node:").grid(row = 0, column = 0, padx = 5, pady = 5)
        self.parent_entry = tk.Entry(self.add_window, width = 30)
        self.parent_entry.grid(row = 0, column = 1, padx = 5, pady = 5)
        
        # Checkbox for new root
        self.new_root_var = tk.BooleanVar()
        self.new_root_checkbox = tk.Checkbutton(
            self.add_window, text="Make this a new root node", variable = self.new_root_var
        )
        self.new_root_checkbox.grid(row = 3, column = 0, columnspan = 2, pady = 5)
        
        # Existing children nodes to reassign
        tk.Label(self.add_window, text = "Existing Children Node (comma-separated):").grid(row = 2, column = 0, padx = 5, pady = 5)
        self.child_entry = tk.Entry(self.add_window, width = 30)
        self.child_entry.grid(row = 2, column = 1, padx = 5, pady = 5)
        
        # Add Node Button
        add_button = tk.Button(self.add_window, text = "Add", command = self.confirm_add_node)
        add_button.grid(row = 4, column = 0, columnspan = 2, pady = 10)
        
    def confirm_add_node(self):
        # Confirm and add the node to the tree
        parent_name = self.parent_entry.get().strip()
        node_name = self.node_name_entry.get().strip()
        existing_children_names = self.child_entry.get().strip()
        
        # Validate inputs for a new root node
        if self.new_root_var.get():
            if not node_name:
                self.display_area.insert(tk.END, "Node Name is required for the new root node.\n")
                self.add_window.destroy()
                return
            
            # Check if the new root name matches the current root
            if node_name.lower() == self.tree_root.name.lower():
                self.display_area.insert(tk.END, f"'{node_name}' is already the root of the tree.\n")
                self.add_window.destroy()
                return
            
            # Create the new root node
            new_root = Node(name = node_name)
            
            # Reassign all current root children to the new root node
            new_root.add_child(self.tree_root)
            
            # Update the root reference
            self.tree_root = new_root
            self.display_area.insert(tk.END, f"New root node '{node_name}' added.\n")
            self.add_window.destroy()
            return
        
        # Validate inputs for normal node addition
        if not node_name:
            self.display_area.insert(tk.END, "Node Name is required. \n")
            self.add_window.destroy()
            return
        
        if not parent_name:
            self.display_area.insert(tk.END, "Parent Node is required unless creating a new root.\n")
            self.add_window.destroy()
            return
        
        # Find the parent node
        parent_node = self.find_node(self.tree_root, parent_name)
        if not parent_node:
            self.display_area.insert(tk.END, f"Parent Node '{parent_name} not found.\n")
            self.add_window.destroy()
            return
        
        #if existing_child not in locals() or not existing_child:
        #    self.display_area.insert(tk.END, f"Child Node '{child_name}' not found.\n")
        #    return
        
        # Check for duplicate child
        if any(child.name.lower() == node_name.lower() for child in parent_node.children):
            self.display_area.insert(tk.END, f"A node with the name '{node_name}' already exists under '{parent_name}'.\n")
            self.add_window.destroy()
            return
        
        # Create the new node and add it as a child of the parent
        new_node = Node(name = node_name)
        parent_node.add_child
        
        # Reassign multiple children nodes, if provided
        reassigned_children = []
        if existing_children_names:
            # Split and clean the inpit
            child_names = list(filter(None, (name.strip() for name in existing_children_names.split(',') if name.strip())))
            for child_name in child_names:              
                # Find the child node
                existing_child = self.find_node(self.tree_root, child_name)
                if not existing_child:
                    self.display_area.insert(tk.END, f"Child Node '{child_name}' not found.\n")
                    continue
    
                # Remove the existing child from its current parent
                if existing_child.parent:
                    existing_child.parent.children.remove(existing_child)
            
                # Attach the existing child to the new node
                new_node.add_child(existing_child)
                reassigned_children.append(child_name)
        
        # Add the new node as a child of the parent node
        try:
            parent_node.add_child(new_node)
            self.display_area.insert(tk.END, f"Node '{node_name}' added under '{parent_name}'.\n")
        except ValueError as e:
            self.display_area.insert(tk.END, f"Error: {e}\n")
        
        if reassigned_children:
            self.display_area.insert(tk.END, f"Node '{node_name}' is now the parent of: {', '.join(reassigned_children)}.\n")
        
        # Close the popup
        self.add_window.destroy()
    
    def edit_node(self):
        # Ensure edit mode is enabled
        if not self.edit_mode:
            self.display_area.insert(tk.END, "Edit Mode must be enabled to edit a node.\n")
            return
        
        # Popup for editing a node
        self.edit_window = tk.Toplevel(self.root)
        self.edit_window.title("Edit Node")
        
        # Node to edit
        tk.Label(self.edit_window, text = "Node to Edit:").grid(row = 0, column = 0, padx = 5, pady = 5)
        self.node_to_edit_entry = tk.Entry(self.edit_window, width = 30)
        self.node_to_edit_entry.grid(row = 0, column = 1, padx = 5, pady = 5)
        
        # New name
        tk.Label(self.edit_window, text = "New Name:").grid(row = 1, column = 1, padx = 5, pady = 5)
        self.new_name_entry = tk.Entry(self.edit_window, width = 30)
        self.new_name_entry.grid(row = 1, column = 1, padx = 5, pady = 5)
        
        # New parent (optional for moving nodes)
        tk.Label(self.edit_window, text = "New Parent (optional):").grid(row = 2, column = 0, padx = 5, pady = 5)
        self.new_parent_entry = tk.Entry(self.edit_window, width = 30)
        self.new_parent_entry.grid(row = 2, column = 1, padx = 5, pady = 5)
        
        # Confirm Edit Button
        tk.Button(self.edit_window, text = "Edit", command = self.confirm_edit_node).grid(row = 3, column = 0, columnspan = 2, pady = 10)
        
    def confirm_edit_node(self):
        node_to_edit = self.node_to_edit_entry.get().strip()
        new_name = self.new_name_entry.get().strip()
        new_parent_name = self.new_parent_entry.get().strip()
        
        # Validate input
        if not node_to_edit:
            self.display_area.insert(tk.End, "Node to edit is required.\n")
            return
        
        # Find the node to edit
        node = self.find_node(self.tree_root, node_to_edit)
        if not node:
            self.display
        
    def delete_node(self):
        #Placeholder for deleting a node
        self.display_area.insert(tk.END, "\nDelete Node feature coming soon.\n")
        
    def display_tree(self):
        #Use the tree's display_tree method to show the structure
        self.display_area.delete(1.0, tk.END) # Clear the text area
        tree_structure = self.tree_root.display_tree() # Get the full tree as a string
        self.display_area.insert(tk.END, tree_structure)
            
    def search_tree(self):
        query = self.search_entry.get() # Get the search term from the input field
        if not query:
            self.display_area.delete(1.0, tk.END)
            self.display_area.insert(tk.END, "Please enter a search term.")
            return
        
        #Find the node
        result = self.find_node(self.tree_root, query)
        self.display_area.delete(1.0, tk.END) # Clear the text area
        
        if result:
            #Display the parents (lineage)
            lineage = result.get_full_lineage()
            self.display_area.insert(tk.END, f"Lineage:\n{lineage}\n\n")
            
            self.display_area.insert(tk.END, f"Subtree:\n")
            subtree_structure = result.display_tree() # Display subtree
            self.display_area.insert(tk.END, subtree_structure)
            #Display children
            #if result.children:
            #    self.display_area.insert(tk.END, f"Children:\n")
            #    for child in result.children:
            #        self.display_area.insert(tk.END, f"- {child.name}\n")
                
        else:
            self.display_area.insert(tk.END, f"No results found for '{query}'.")
    
    def trigger_search(self, event):
        """
        Trigger the search_tree method when the Enter key is pressed.
        """
        self.search_tree()
                  
    def find_node(self, current_node, name):
        # Recursively searches the tree for a node by name (case-insensitive).
        if current_node.name.lower() == name.lower(): #Case-insensitive comparison
            return current_node
        for child in current_node.children:
            result = self.find_node(child, name)
            if result:
                return result
        return None
    
    def _on_mouse_wheel(self, event):
        # Scroll the display_area with the mouse wheel. 
        self.display_area.yview_scroll(-1 * (event.delta // 120), "units")
    
#Example Usage
if __name__ == "__main__":
    # Create initial clade, genus and species tree structure
    amniota = Node("Amniota")
    synapsida = Node("Synapsida")
    sauropsida = Node("Sauropsida")
    dinosauria = Node("Dinosauria")
    psittacosauridae = Node("Psittacosauridae")
    velociraptorinae = Node("Velociraptorinae")
    tyrannosauridae = Node ("Tyrannosauridae")
    tyrannosaurinae = Node("Tyrannosaurinae")
    albertosaurinae = Node("Albertosaurinae")
    genus_psittacosaurus = Node("Psittacosaurus")
    genus_velociraptor = Node ("Velociraptor")
    genus_tyrannosaurus = Node("Tyrannosaurus")
    genus_Tarbosaurus = Node ("Tarbosaurus")
    genus_albertosaurus = Node("Albertosaurus")
    velociraptor_mongoliensis = Node("Velociraptor mongoliensis")
    velociraptor_osmolskae = Node("Velociraptor osmolskae")
    psittacosaurus_mongoliensis = Node("Psittacosaurus mongoliensis")
    species_rex = Node("Tyrannosaurus rex")
    tarbosaurus_bataar = Node("Tarbosaurus Bataar")
    species_mcraeensis = Node("Tyrannosaurus mcraeensis")
    species_sarcophagus = Node("Albertosaurus sarcophagus")
    hominidae = Node("Hominidae")
    homo = Node("Homo")
    homo_sapiens = Node("Homo sapiens")
    
    #Build the tree
    amniota.add_child(sauropsida)
    amniota.add_child(synapsida)
    sauropsida.add_child(dinosauria)
    dinosauria.add_child(psittacosauridae)
    dinosauria.add_child(velociraptorinae)
    dinosauria.add_child(tyrannosauridae)
    psittacosauridae.add_child(genus_psittacosaurus)
    velociraptorinae.add_child(genus_velociraptor)
    tyrannosauridae.add_child(tyrannosaurinae)
    tyrannosauridae.add_child(albertosaurinae)
    tyrannosaurinae.add_child(genus_tyrannosaurus)
    tyrannosaurinae.add_child(genus_Tarbosaurus)
    albertosaurinae.add_child(genus_albertosaurus)
    genus_psittacosaurus.add_child(psittacosaurus_mongoliensis)
    genus_velociraptor.add_child(velociraptor_mongoliensis)
    genus_velociraptor.add_child(velociraptor_osmolskae)
    genus_tyrannosaurus.add_child(species_rex)
    genus_tyrannosaurus.add_child(species_mcraeensis)
    genus_Tarbosaurus.add_child(tarbosaurus_bataar)
    genus_albertosaurus.add_child(species_sarcophagus)
    synapsida.add_child(hominidae)
    hominidae.add_child(homo)
    homo.add_child(homo_sapiens)
    
    # Create and launch the GUI
    root = tk.Tk()
    app = PhylogenyApp(root, amniota) # Pass the root node of the tree to the app
    root.mainloop()