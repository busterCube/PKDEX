import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk_boot
from ttkbootstrap.constants import *
import sqlite3
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import random

class ScrollableFrame(ttk_boot.Frame):
    """A scrollable frame widget for ttkbootstrap"""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg='#8B0000', highlightthickness=0)
        self.scrollbar = ttk_boot.Scrollbar(self, orient="vertical", command=self.canvas.yview, style='Custom.Vertical.TScrollbar')
        self.scrollable_frame = ttk_boot.Frame(self.canvas, style='Custom.TFrame')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

class PokedexXApp:
    """Enhanced Pokedex application using all new PokeAPI tables"""

    def __init__(self):
        # Create main window with custom Pokemon-themed colors
        self.root = ttk_boot.Window(
            title="PKDEX - Pokedex",
            themename="darkly",
            size=(1400, 900)
        )

        # Set window icon
        try:
            self.root.iconbitmap("Images/icon/icon.ico")
        except Exception as e:
            print(f"Could not load window icon: {e}")

        # Configure custom colors
        self.setup_custom_theme()

        self.db_name = "Pokemon.db"
        self.conn = sqlite3.connect(self.db_name)  # Database connection
        self.current_pokemon = None
        self.pokemon_image = None
        self.pokemon_id_map = {}  # Map listbox indices to Pokemon IDs

        # Load type icons
        self.type_icons = self.load_type_icons()

        # Load gender icons
        self.gender_icons = self.load_gender_icons()

        # Load timeline move icons
        self.timeline_icons = self.load_timeline_icons()

        # Initialize search variables
        self.name_var = tk.StringVar()
        self.number_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.min_hp_var = tk.StringVar()
        self.min_attack_var = tk.StringVar()
        self.min_defense_var = tk.StringVar()
        self.min_sp_attack_var = tk.StringVar()
        self.min_sp_defense_var = tk.StringVar()
        self.min_speed_var = tk.StringVar()

        self.setup_ui()
        self.load_pokemon_list()

    def setup_custom_theme(self):
        """Setup custom Pokemon-themed colors"""
        style = ttk_boot.Style()
        
        # Configure custom colors - Dark red background, white text, dark blue inputs
        style.configure('Custom.TFrame', background='#8B0000', padding=0, borderwidth=0, relief='flat')  # Dark red with no padding or borders
        style.configure('Custom.TLabel', background='#8B0000', foreground='white', borderwidth=0, padding=0)
        style.configure('Custom.TEntry', fieldbackground='#000080', foreground='white')  # Dark blue
        style.configure('Custom.TCombobox', fieldbackground='#000080', foreground='white')
        style.configure('Custom.TLabelframe', background='#8B0000', foreground='white', borderwidth=3, relief='raised')
        style.configure('Custom.TLabelframe.Label', background='#8B0000', foreground='white', font=('Arial', 12, 'bold'), borderwidth=0, padding=0)
        
        # Configure Notebook and Tab styles - Dark grey unselected, blue selected
        style.configure('TNotebook', background='#8B0000', borderwidth=0)
        style.configure('TNotebook.Tab', background='#404040', foreground='white', borderwidth=0, padding=(10, 5))
        style.map('TNotebook.Tab', 
                 background=[('selected', '#4169E1'), ('active', '#4169E1')],
                 foreground=[('selected', 'white'), ('active', 'white')])
        
        # Configure Chart Stats frame with dark navy blue background
        style.configure('ChartStats.TLabelframe', background='#000080', foreground='white', borderwidth=3, relief='raised')
        style.configure('ChartStats.TLabelframe.Label', background='#000080', foreground='white', font=('Arial', 12, 'bold'), borderwidth=0, padding=0)
        
        # Configure Button styles to use red theme
        style.configure('TButton', background='#8B0000', foreground='white', borderwidth=1, relief='raised')
        style.map('TButton',
                 background=[('active', '#4169E1'), ('pressed', '#000080')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        
        # Configure Checkbutton and Radiobutton styles
        style.configure('TCheckbutton', background='#8B0000', foreground='white')
        style.configure('TRadiobutton', background='#8B0000', foreground='white')
        
        # Configure Scale and Progressbar styles
        style.configure('TScale', background='#8B0000')
        style.configure('Horizontal.TProgressbar', background='#4169E1', troughcolor='#8B0000')
        
        # Configure medium blue Frame style for Search
        style.configure('Blue.TFrame', background='#4169E1', borderwidth=0, relief='flat')
        style.configure('Blue.TLabel', background='#4169E1', foreground='white', borderwidth=0, padding=0)
        
        # Configure medium grey Frame style for Pokemon List
        style.configure('Grey.TFrame', background='#808080', borderwidth=0, relief='flat')
        style.configure('Grey.TLabel', background='#808080', foreground='white', borderwidth=0, padding=0)
        
        # Configure Treeview style
        style.configure('Custom.Treeview', background='#000080', foreground='white', fieldbackground='#000080', borderwidth=0)
        style.configure('Custom.Treeview.Heading', background='#4169E1', foreground='white', borderwidth=0)
        
        # Configure Scrollbar style
        style.configure('Custom.Vertical.TScrollbar', background='#8B0000', troughcolor='#8B0000', borderwidth=0)
        
        # Configure root window background
        self.root.configure(bg='#8B0000')
    
    def load_type_icons(self):
        """Load Pokemon type icons"""
        icons = {}
        types_path = "images/Types"
        
        # List of Pokemon types
        pokemon_types = [
            'Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 'Fighting', 'Poison',
            'Ground', 'Flying', 'Psychic', 'Bug', 'Rock', 'Ghost', 'Dragon', 'Dark',
            'Steel', 'Fairy', 'Physical', 'Special', 'Status'
        ]
        
        for type_name in pokemon_types:
            icon_path = f"{types_path}/{type_name}.png"
            try:
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    # Resize icon to 32x32 pixels for display
                    image = image.resize((32, 32), Image.Resampling.LANCZOS)
                    icons[type_name.lower()] = ImageTk.PhotoImage(image)
                else:
                    print(f"Warning: Icon not found: {icon_path}")
            except Exception as e:
                print(f"Error loading icon {icon_path}: {e}")
        
        return icons

    def load_gender_icons(self):
        """Load Pokemon gender icons"""
        icons = {}
        gender_icon_files = {
            'male': 'Male.png',
            'female': 'Female.png', 
            'genderless': 'Genderless.png'
        }
        
        for gender_key, filename in gender_icon_files.items():
            icon_path = f"images/Types/{filename}"
            try:
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    # Resize icon to 24x24 pixels for display
                    image = image.resize((24, 24), Image.Resampling.LANCZOS)
                    icons[gender_key] = ImageTk.PhotoImage(image)
                else:
                    print(f"Warning: Gender icon not found: {icon_path}")
            except Exception as e:
                print(f"Error loading gender icon {icon_path}: {e}")
        
        return icons

    def load_timeline_icons(self):
        """Load timeline move icons"""
        icons = {}
        timeline_icon_files = {
            'tmhm': 'HMTM.png',
            'learned': 'learned.png', 
            'evolution': 'Evolution.png',
            'status': 'status.png',
            'special': 'special.png',
            'physical': 'physical.png'
        }
        
        for icon_type, filename in timeline_icon_files.items():
            icon_path = f"images/Types/{filename}"
            try:
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    # Resize icon to 20x20 pixels for timeline display
                    image = image.resize((20, 20), Image.Resampling.LANCZOS)
                    # Ensure image has transparency support
                    if image.mode != 'RGBA':
                        image = image.convert('RGBA')
                    icons[icon_type] = ImageTk.PhotoImage(image)
                else:
                    print(f"Warning: Timeline icon not found: {icon_path}")
            except Exception as e:
                print(f"Error loading timeline icon {icon_path}: {e}")
        
        return icons

    def get_all_types(self):
        """Get all Pokemon types from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Get types from New_Pokemon_Data table
            cursor.execute("SELECT types FROM New_Pokemon_Data")
            type_results = cursor.fetchall()
            conn.close()

            # Combine and deduplicate types
            all_types = set()
            for result in type_results:
                try:
                    types_data = json.loads(result[0])
                    for type_info in types_data:
                        all_types.add(type_info['type']['name'].title())
                except:
                    pass

            return sorted(list(all_types))

        except Exception as e:
            print(f"Error getting types: {e}")
            return []

    def setup_ui(self):
        """Setup the user interface with custom theme"""
        # Configure main frame
        main_frame = ttk_boot.Frame(self.root, padding=10, style='Custom.TFrame')
        main_frame.pack(fill=BOTH, expand=True)
        
        # Top toolbar
        toolbar_frame = ttk_boot.Frame(main_frame, style='Custom.TFrame')
        toolbar_frame.pack(fill=X, pady=(0, 5))  # Adjusted padding for larger banner

        # Load banner image
        banner_image = None
        banner_path = "images/banner/PKDEX_trasparent.png"
        try:
            if os.path.exists(banner_path):
                image = Image.open(banner_path)
                # Get original image size and scale it proportionally to fit within 80x80
                # This ensures consistent sizing regardless of original image dimensions
                original_width, original_height = image.size
                max_size = 80  # Maximum dimension for banner (increased from 32 to 80)
                if original_width > original_height:
                    new_width = max_size
                    new_height = int((original_height * max_size) / original_width)
                else:
                    new_height = max_size
                    new_width = int((original_width * max_size) / original_height)

                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                banner_image = ImageTk.PhotoImage(image)
            else:
                print(f"Warning: Banner image not found: {banner_path}")
        except Exception as e:
            print(f"Error loading banner image: {e}")

        # Banner image label - only show if image loaded successfully
        if banner_image:
            banner_label = ttk_boot.Label(toolbar_frame, image=banner_image, style='Custom.TLabel')
            banner_label.pack(side=LEFT, padx=(0, 10), pady=5)  # Add padding to prevent layout issues
            # Keep a reference to prevent garbage collection
            self.banner_image = banner_image
        
        # Left panel for search and list
        left_panel = ttk_boot.Frame(main_frame, width=350, style='Custom.TFrame')
        left_panel.pack(side=LEFT, fill=Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Search section
        search_frame = ttk_boot.Frame(left_panel, padding=10, style='Blue.TFrame')
        search_frame.pack(fill=X, pady=(0, 10))
        
        # Search title
        ttk_boot.Label(search_frame, text="Search Pokemon", font=('Arial', 12, 'bold'), 
                      background='#4169E1', foreground='white').pack(anchor=W, pady=(0, 10))
        
        # Search by name
        ttk_boot.Label(search_frame, text="Name:", style='Custom.TLabel').pack(anchor=W)
        self.name_var = tk.StringVar()
        self.name_var.trace('w', self.filter_pokemon)
        name_entry = ttk_boot.Entry(search_frame, textvariable=self.name_var, style='Custom.TEntry')
        name_entry.pack(fill=X, pady=(0, 5))
        
        # Search by number
        ttk_boot.Label(search_frame, text="Number:", style='Custom.TLabel').pack(anchor=W)
        self.number_var = tk.StringVar()
        self.number_var.trace('w', self.filter_pokemon)
        number_entry = ttk_boot.Entry(search_frame, textvariable=self.number_var, style='Custom.TEntry')
        number_entry.pack(fill=X, pady=(0, 5))
        
        # Search by type
        ttk_boot.Label(search_frame, text="Type:", style='Custom.TLabel').pack(anchor=W)
        self.type_var = tk.StringVar()
        self.type_var.trace('w', self.filter_pokemon)
        type_combo = ttk_boot.Combobox(search_frame, textvariable=self.type_var, style='Custom.TCombobox')
        type_combo['values'] = self.get_all_types()
        type_combo.pack(fill=X, pady=(0, 10))
        
        # Advanced Filters Section
        advanced_frame = ttk_boot.LabelFrame(search_frame, text="Advanced Filters", padding=5, style='Custom.TLabelframe')
        advanced_frame.pack(fill=X, pady=(0, 10))
        
        # Stat filters
        stat_frame = ttk_boot.Frame(advanced_frame, style='Custom.TFrame')
        stat_frame.pack(fill=X, pady=(0, 5))
        
        ttk_boot.Label(stat_frame, text="Min HP:", style='Custom.TLabel').grid(row=0, column=0, sticky=W, padx=(0, 5))
        self.min_hp_var = tk.StringVar()
        self.min_hp_var.trace('w', self.filter_pokemon)
        ttk_boot.Entry(stat_frame, textvariable=self.min_hp_var, width=8, style='Custom.TEntry').grid(row=0, column=1, padx=(0, 10))
        
        ttk_boot.Label(stat_frame, text="Min Attack:", style='Custom.TLabel').grid(row=0, column=2, sticky=W, padx=(0, 5))
        self.min_attack_var = tk.StringVar()
        self.min_attack_var.trace('w', self.filter_pokemon)
        ttk_boot.Entry(stat_frame, textvariable=self.min_attack_var, width=8, style='Custom.TEntry').grid(row=0, column=3, padx=(0, 10))
        
        ttk_boot.Label(stat_frame, text="Min Defense:", style='Custom.TLabel').grid(row=1, column=0, sticky=W, padx=(0, 5))
        self.min_defense_var = tk.StringVar()
        self.min_defense_var.trace('w', self.filter_pokemon)
        ttk_boot.Entry(stat_frame, textvariable=self.min_defense_var, width=8, style='Custom.TEntry').grid(row=1, column=1, padx=(0, 10))
        
        ttk_boot.Label(stat_frame, text="Min Sp. Attack:", style='Custom.TLabel').grid(row=1, column=2, sticky=W, padx=(0, 5))
        self.min_sp_attack_var = tk.StringVar()
        self.min_sp_attack_var.trace('w', self.filter_pokemon)
        ttk_boot.Entry(stat_frame, textvariable=self.min_sp_attack_var, width=8, style='Custom.TEntry').grid(row=1, column=3, padx=(0, 10))
        
        ttk_boot.Label(stat_frame, text="Min Sp. Defense:", style='Custom.TLabel').grid(row=2, column=0, sticky=W, padx=(0, 5))
        self.min_sp_defense_var = tk.StringVar()
        self.min_sp_defense_var.trace('w', self.filter_pokemon)
        ttk_boot.Entry(stat_frame, textvariable=self.min_sp_defense_var, width=8, style='Custom.TEntry').grid(row=2, column=1, padx=(0, 10))
        
        ttk_boot.Label(stat_frame, text="Min Speed:", style='Custom.TLabel').grid(row=2, column=2, sticky=W, padx=(0, 5))
        self.min_speed_var = tk.StringVar()
        self.min_speed_var.trace('w', self.filter_pokemon)
        ttk_boot.Entry(stat_frame, textvariable=self.min_speed_var, width=8, style='Custom.TEntry').grid(row=2, column=3)
        
        # Clear filters button
        clear_button = ttk_boot.Button(advanced_frame, text="Clear Filters", 
                                     command=self.clear_filters, bootstyle="secondary")
        clear_button.pack(pady=(5, 0))
        
        # Pokemon list
        list_frame = ttk_boot.Frame(left_panel, padding=5, style='Grey.TFrame')
        list_frame.pack(fill=BOTH, expand=True)
        
        # List title
        ttk_boot.Label(list_frame, text="Pokemon List", font=('Arial', 12, 'bold'), 
                      background='#808080', foreground='white').pack(anchor=W, pady=(0, 10))
        
        # Listbox with scrollbar
        list_container = ttk_boot.Frame(list_frame, style='Custom.TFrame')
        list_container.pack(fill=BOTH, expand=True)
        
        scrollbar = ttk_boot.Scrollbar(list_container)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.pokemon_listbox = tk.Listbox(
            list_container, 
            yscrollcommand=scrollbar.set,
            font=('Arial', 10),
            bg='#000080',  # Dark blue background
            fg='white',    # White text
            selectbackground='#4169E1'  # Royal blue selection
        )
        self.pokemon_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.pokemon_listbox.yview)
        
        self.pokemon_listbox.bind('<<ListboxSelect>>', self.on_pokemon_select)
        
        # Right panel for Pokemon details
        right_panel = ttk_boot.Frame(main_frame, style='Custom.TFrame')
        right_panel.pack(side=RIGHT, fill=BOTH, expand=True)
        
        # Create notebook for tabbed interface
        self.notebook = ttk_boot.Notebook(right_panel, style='TNotebook')
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Bind tab change event to cleanup mouse wheel bindings
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Tab 1: Basic Info
        self.basic_tab = ttk_boot.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(self.basic_tab, text="Basic Info")
        self.setup_basic_tab()
        
        # Tab 4: Evolution Chain
        self.evolution_tab = ttk_boot.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(self.evolution_tab, text="Evolution Chain")
        self.setup_evolution_tab()
        
        # Tab 5: Characteristics
        self.abilities_tab = ttk_boot.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(self.abilities_tab, text="Characteristics")
        self.setup_abilities_tab()
        
        # Tab 6: Moves
        self.moves_tab = ttk_boot.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(self.moves_tab, text="Moves")
        self.setup_moves_tab()
    
    def clear_filters(self):
        """Clear all search filters"""
        self.name_var.set("")
        self.number_var.set("")
        self.type_var.set("")
        self.min_hp_var.set("")
        self.min_attack_var.set("")
        self.min_defense_var.set("")
        self.min_sp_attack_var.set("")
        self.min_sp_defense_var.set("")
        self.min_speed_var.set("")
    
    def on_tab_changed(self, event=None):
        """Handle tab changes to cleanup mouse wheel bindings"""
        current_tab = self.notebook.select()
        current_tab_text = self.notebook.tab(current_tab, "text")
        
        # If we're not on the Evolution Chain tab, clean up mouse wheel bindings
        if current_tab_text != "Evolution Chain":
            try:
                self.root.unbind_all("<MouseWheel>")
                self.root.unbind_all("<Button-4>")
                self.root.unbind_all("<Button-5>")
            except:
                pass
    
    def setup_basic_tab(self):
        """Setup basic information tab"""
        # Top section with image and basic info
        top_section = ttk_boot.Frame(self.basic_tab, style='Custom.TFrame')
        top_section.pack(fill=X, pady=5, padx=5)
        
        # Image frame
        image_frame = ttk_boot.Frame(top_section, width=200, height=200, style='Custom.TFrame')
        image_frame.pack(side=LEFT, padx=0)
        image_frame.pack_propagate(False)
        
        self.image_label = ttk_boot.Label(image_frame, text="No Image", style='Custom.TLabel')
        self.image_label.pack(expand=True)
        
        # Basic info frame
        basic_info_frame = ttk_boot.Frame(top_section, style='Custom.TFrame')
        basic_info_frame.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.name_label = ttk_boot.Label(basic_info_frame, text="Name: ", font=('Arial', 18, 'bold'), style='Custom.TLabel')
        self.name_label.pack(anchor=W)
        
        self.number_label = ttk_boot.Label(basic_info_frame, text="Number: ", font=('Arial', 12), style='Custom.TLabel')
        self.number_label.pack(anchor=W)
        
        self.type_label = ttk_boot.Label(basic_info_frame, text="Type: ", font=('Arial', 12), style='Custom.TLabel')
        self.type_label.pack(anchor=W)
        
        self.species_label = ttk_boot.Label(basic_info_frame, text="Species: ", font=('Arial', 12), style='Custom.TLabel')
        self.species_label.pack(anchor=W)
        
        self.height_label = ttk_boot.Label(basic_info_frame, text="Height: ", font=('Arial', 12), style='Custom.TLabel')
        self.height_label.pack(anchor=W)
        
        self.weight_label = ttk_boot.Label(basic_info_frame, text="Weight: ", font=('Arial', 12), style='Custom.TLabel')
        self.weight_label.pack(anchor=W)
        
        self.abilities_label = ttk_boot.Label(basic_info_frame, text="Abilities: ", font=('Arial', 12), style='Custom.TLabel')
        self.abilities_label.pack(anchor=W)
        
        # Type icons frame
        type_icons_frame = ttk_boot.Frame(top_section, style='Custom.TFrame')
        type_icons_frame.pack(side=RIGHT, padx=0, pady=0)
        
        # Type icons will be displayed here
        self.type_icons_container = ttk_boot.Frame(type_icons_frame, style='Custom.TFrame')
        self.type_icons_container.pack(pady=0, padx=0)
        
        # Stats section with chart and gauges side by side
        stats_container = ttk_boot.Frame(self.basic_tab, style='Custom.TFrame')
        stats_container.pack(fill=X, pady=10, padx=10)
        
        # Chart Stats section (left side)
        chart_stats_frame = ttk_boot.LabelFrame(stats_container, text="Chart Stats", padding=5, style='ChartStats.TLabelframe')
        chart_stats_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        chart_stats_frame.configure(width=260, height=220)
        
        # Create stats chart container with fixed size
        self.stats_chart_frame = ttk_boot.Frame(chart_stats_frame, style='ChartStats.TLabelframe', width=250, height=200)
        self.stats_chart_frame.pack(fill=BOTH, expand=False)
        self.stats_chart_frame.pack_propagate(False)
        
        # Base Stats section (right side) with gauges
        base_stats_frame = ttk_boot.LabelFrame(stats_container, text="Base Stats", padding=5, style='Custom.TLabelframe')
        base_stats_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        # Create stat flood gauges (half size)
        self.stat_gauges = {}
        self.stat_labels = {}
        stats = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
        
        base_stats_container = ttk_boot.Frame(base_stats_frame, style='Custom.TFrame')
        base_stats_container.pack(fill=BOTH, expand=True)
        
        for i, stat in enumerate(stats):
            row = i // 2  # 2 columns instead of 3
            col = i % 2
            
            stat_frame = ttk_boot.Frame(base_stats_container, style='Custom.TFrame')
            stat_frame.grid(row=row, column=col, padx=3, pady=3, sticky=W+E)
            
            ttk_boot.Label(stat_frame, text=f"{stat}:", font=('Arial', 8), style='Custom.TLabel').pack()
            
            # Get maximum values for each stat from database
            stat_maximums = self.get_stat_maximums()
            
            gauge = ttk_boot.Floodgauge(
                stat_frame,
                bootstyle="info",
                length=100,  # Standard length
                thickness=25,  # 25px tall
                mode='determinate',
                maximum=stat_maximums.get(stat.lower().replace(' ', '_').replace('.', ''), 255)  # Set maximum for this stat
            )
            gauge.pack(pady=1)
            
            # Add a label below the gauge to show the stat value
            value_label = ttk_boot.Label(stat_frame, text="0", font=('Arial', 8, 'bold'), style='Custom.TLabel')
            value_label.pack()
            
            gauge_key = stat.lower().replace('. ', '_').replace(' ', '_')
            self.stat_gauges[gauge_key] = gauge
            self.stat_labels[gauge_key] = value_label
        
        # Configure grid columns
        for i in range(2):
            base_stats_container.columnconfigure(i, weight=1)
        
        # Type effectiveness container (weaknesses and defenses side by side)
        type_effectiveness_container = ttk_boot.Frame(self.basic_tab, style='Custom.TFrame')
        type_effectiveness_container.pack(fill=X, pady=10, padx=10)
        
        # Weaknesses section
        weaknesses_frame = ttk_boot.LabelFrame(type_effectiveness_container, text="Type Weaknesses", padding=10, style='Custom.TLabelframe')
        weaknesses_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        # Weaknesses container
        self.weaknesses_container = ttk_boot.Frame(weaknesses_frame, style='Custom.TFrame')
        self.weaknesses_container.pack(fill=X)
        
        # Weak to section
        weak_frame = ttk_boot.Frame(self.weaknesses_container, style='Custom.TFrame')
        weak_frame.pack(fill=X, pady=2)
        
        ttk_boot.Label(weak_frame, text="Weak to (2x):", font=('Arial', 10, 'bold'), style='Custom.TLabel').pack(anchor=W)
        self.weak_icons_container = ttk_boot.Frame(weak_frame, style='Custom.TFrame')
        self.weak_icons_container.pack(fill=X, pady=2)
        
        # Very weak to section
        very_weak_frame = ttk_boot.Frame(self.weaknesses_container, style='Custom.TFrame')
        very_weak_frame.pack(fill=X, pady=2)
        
        ttk_boot.Label(very_weak_frame, text="Very Weak to (4x):", font=('Arial', 10, 'bold'), style='Custom.TLabel').pack(anchor=W)
        self.very_weak_icons_container = ttk_boot.Frame(very_weak_frame, style='Custom.TFrame')
        self.very_weak_icons_container.pack(fill=X, pady=2)
        
        # Defenses section
        defenses_frame = ttk_boot.LabelFrame(type_effectiveness_container, text="Type Defenses", padding=10, style='Custom.TLabelframe')
        defenses_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        # Defenses container
        self.defenses_container = ttk_boot.Frame(defenses_frame, style='Custom.TFrame')
        self.defenses_container.pack(fill=X)
        
        # Resistant to section (0.5x damage)
        resistant_frame = ttk_boot.Frame(self.defenses_container, style='Custom.TFrame')
        resistant_frame.pack(fill=X, pady=2)
        
        ttk_boot.Label(resistant_frame, text="Resistant (½x):", font=('Arial', 10, 'bold'), style='Custom.TLabel').pack(anchor=W)
        self.resistant_icons_container = ttk_boot.Frame(resistant_frame, style='Custom.TFrame')
        self.resistant_icons_container.pack(fill=X, pady=2)
        
        # Very resistant to section (0.25x damage)
        very_resistant_frame = ttk_boot.Frame(self.defenses_container, style='Custom.TFrame')
        very_resistant_frame.pack(fill=X, pady=2)
        
        ttk_boot.Label(very_resistant_frame, text="Very Resistant (¼x):", font=('Arial', 10, 'bold'), style='Custom.TLabel').pack(anchor=W)
        self.very_resistant_icons_container = ttk_boot.Frame(very_resistant_frame, style='Custom.TFrame')
        self.very_resistant_icons_container.pack(fill=X, pady=2)
        
        # Immune to section (0x damage)
        immune_frame = ttk_boot.Frame(self.defenses_container, style='Custom.TFrame')
        immune_frame.pack(fill=X, pady=2)
        
        ttk_boot.Label(immune_frame, text="Immune (0x):", font=('Arial', 10, 'bold'), style='Custom.TLabel').pack(anchor=W)
        self.immune_icons_container = ttk_boot.Frame(immune_frame, style='Custom.TFrame')
        self.immune_icons_container.pack(fill=X, pady=2)
        
        # Gender Information section
        gender_frame = ttk_boot.LabelFrame(self.basic_tab, text="Gender Information", padding=10, style='Custom.TLabelframe')
        gender_frame.pack(fill=X, pady=10, padx=10)
        
        # Gender container
        self.gender_container = ttk_boot.Frame(gender_frame, style='Custom.TFrame')
        self.gender_container.pack(fill=X)
        
        # Male gender section
        male_frame = ttk_boot.Frame(self.gender_container, style='Custom.TFrame')
        male_frame.pack(side=LEFT, padx=(0, 20))
        
        self.male_icon_label = ttk_boot.Label(male_frame, style='Custom.TLabel')
        self.male_icon_label.pack(side=LEFT, padx=(0, 5))
        
        self.percent_male_label = ttk_boot.Label(male_frame, text="Male: ", 
                                               font=('Arial', 11), style='Custom.TLabel')
        self.percent_male_label.pack(side=LEFT)
        
        # Female gender section
        female_frame = ttk_boot.Frame(self.gender_container, style='Custom.TFrame')
        female_frame.pack(side=LEFT, padx=(0, 20))
        
        self.female_icon_label = ttk_boot.Label(female_frame, style='Custom.TLabel')
        self.female_icon_label.pack(side=LEFT, padx=(0, 5))
        
        self.percent_female_label = ttk_boot.Label(female_frame, text="Female: ", 
                                                 font=('Arial', 11), style='Custom.TLabel')
        self.percent_female_label.pack(side=LEFT)
    
    def get_stat_maximums(self):
        """Get maximum values for each stat from the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Get max values for each stat
            cursor.execute("""
                SELECT 
                    MAX(CAST(JSON_EXTRACT(stats, '$.hp') AS INTEGER)) as max_hp,
                    MAX(CAST(JSON_EXTRACT(stats, '$.attack') AS INTEGER)) as max_attack,
                    MAX(CAST(JSON_EXTRACT(stats, '$.defense') AS INTEGER)) as max_defense,
                    MAX(CAST(JSON_EXTRACT(stats, '$.special-attack') AS INTEGER)) as max_sp_attack,
                    MAX(CAST(JSON_EXTRACT(stats, '$.special-defense') AS INTEGER)) as max_sp_defense,
                    MAX(CAST(JSON_EXTRACT(stats, '$.speed') AS INTEGER)) as max_speed
                FROM New_Pokemon_Data
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'hp': result[0] or 255,
                    'attack': result[1] or 255,
                    'defense': result[2] or 255,
                    'sp_attack': result[3] or 255,
                    'sp_defense': result[4] or 255,
                    'speed': result[5] or 255
                }
            else:
                return {
                    'hp': 255, 'attack': 255, 'defense': 255,
                    'sp_attack': 255, 'sp_defense': 255, 'speed': 255
                }
        except Exception as e:
            print(f"Error getting stat maximums: {e}")
            return {
                'hp': 255, 'attack': 255, 'defense': 255,
                'sp_attack': 255, 'sp_defense': 255, 'speed': 255
            }
    
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    
    def setup_evolution_tab(self):
        """Setup the evolution chain visualization tab"""
        # Main container - fill entire tab with no padding
        evolution_frame = ttk_boot.Frame(self.evolution_tab, style='Custom.TFrame')
        evolution_frame.pack(fill=BOTH, expand=True, padx=0, pady=0)
        
        # Title
        title_frame = ttk_boot.Frame(evolution_frame, style='Custom.TFrame')
        title_frame.pack(fill=X, pady=(10, 10))
        
        ttk_boot.Label(title_frame, text="Evolution Chain", 
                      font=('Arial', 18, 'bold'), style='Custom.TLabel').pack(side=LEFT, padx=20)
        
        # Instructions
        instructions = ttk_boot.Label(title_frame, 
                                    text="Select a Pokemon to view its evolution chain", 
                                    font=('Arial', 10), style='Custom.TLabel')
        instructions.pack(side=RIGHT, padx=20)
        
        # Evolution display area - center the content
        self.evolution_display_frame = ttk_boot.Frame(evolution_frame, style='Custom.TFrame')
        self.evolution_display_frame.pack(fill=BOTH, expand=True)
        
        # Initially show message to select Pokemon
        self.show_evolution_placeholder()
    
    def show_evolution_placeholder(self):
        """Show placeholder when no Pokemon is selected for evolution display"""
        # Clear existing content and cleanup mouse wheel bindings
        for widget in self.evolution_display_frame.winfo_children():
            # Clean up mouse wheel bindings if they exist
            if hasattr(widget, 'mousewheel_handler'):
                try:
                    self.root.unbind_all("<MouseWheel>")
                    self.root.unbind_all("<Button-4>")
                    self.root.unbind_all("<Button-5>")
                except:
                    pass
            widget.destroy()
        
        placeholder_label = ttk_boot.Label(
            self.evolution_display_frame, 
            text="Select a Pokemon from the list to view its evolution chain",
            font=('Arial', 14), 
            style='Custom.TLabel'
        )
        placeholder_label.pack(expand=True)
    
    def display_evolution_chain(self, evolution_data):
        """Display the evolution chain for a Pokemon"""
        # Clear existing content
        for widget in self.evolution_display_frame.winfo_children():
            widget.destroy()
        
        if not evolution_data:
            ttk_boot.Label(self.evolution_display_frame, text="No evolution data available", 
                          font=('Arial', 12, 'bold'), style='Custom.TLabel',
                          foreground='white').pack(expand=True)
            return
        
        # Parse evolution chain data
        try:
            chain_data = evolution_data[0] if evolution_data else None
            if not chain_data:
                ttk_boot.Label(self.evolution_display_frame, text="No evolution data available", 
                              font=('Arial', 12, 'bold'), style='Custom.TLabel',
                              foreground='white').pack(expand=True)
                return
            
            # Create scrollable frame for evolution chain
            scrollable_frame = ScrollableFrame(self.evolution_display_frame, style='Custom.TFrame')
            scrollable_frame.pack(fill=BOTH, expand=True)
            
            # Center the content within the scrollable frame
            content_frame = ttk_boot.Frame(scrollable_frame.scrollable_frame, style='Custom.TFrame')
            content_frame.pack(expand=True, fill=BOTH)
            
            # Add title showing the Pokemon's evolution chain
            base_species = chain_data.get('species', {}).get('name', 'Unknown')
            title_label = ttk_boot.Label(content_frame, 
                                       text=f"{base_species.title()} Evolution Chain",
                                       font=('Arial', 16, 'bold'), 
                                       style='Custom.TLabel',
                                       foreground='white')  # White text
            title_label.pack(pady=(20, 20))
            
            # Display evolution chain starting from the base Pokemon
            self.display_evolution_node(content_frame, chain_data, level=0, position=0)
            
        except Exception as e:
            print(f"Error displaying evolution chain: {e}")
            ttk_boot.Label(self.evolution_display_frame, text="Error loading evolution data", 
                          font=('Arial', 12, 'bold'), style='Custom.TLabel',
                          foreground='white').pack(expand=True)
    
    def display_evolution_node(self, parent, node_data, level=0, position=0):
        """Recursively display an evolution node and its evolutions"""
        try:
            # Extract Pokemon info
            species_name = node_data.get('species', {}).get('name', 'Unknown')
            evolves_to = node_data.get('evolves_to', [])
            evolution_details = node_data.get('evolution_details', [])
            
            # Create centered Pokemon display frame
            pokemon_container = ttk_boot.Frame(parent, style='Custom.TFrame')
            pokemon_container.pack(fill=X, pady=10)
            
            # Center the Pokemon frame within the container
            pokemon_frame = ttk_boot.Frame(pokemon_container, style='Custom.TFrame')
            pokemon_frame.pack(anchor=CENTER)
            
            # Pokemon image and info
            info_frame = ttk_boot.Frame(pokemon_frame, style='Custom.TFrame')
            info_frame.pack(side=LEFT, padx=(0, 20))
            
            # Pokemon image
            image_frame = ttk_boot.Frame(info_frame, width=120, height=120, style='Custom.TFrame')
            image_frame.pack()
            image_frame.pack_propagate(False)
            
            # Try to load Pokemon image
            image_label = ttk_boot.Label(image_frame, style='Custom.TLabel')
            image_label.pack(expand=True)
            
            # Load Pokemon image from database
            self.load_pokemon_image_for_evolution(species_name, image_label)
            
            # Pokemon name
            name_label = ttk_boot.Label(info_frame, text=species_name.title(), 
                                      font=('Arial', 14, 'bold'), style='Custom.TLabel',
                                      foreground='white')  # White text
            name_label.pack(pady=(10, 5))
            
            # Evolution requirements (if not the base Pokemon)
            if evolution_details and level > 0:
                req_frame = ttk_boot.Frame(info_frame, style='Custom.TFrame')
                req_frame.pack(fill=X, pady=(5, 0))
                
                requirements = []
                for detail in evolution_details:
                    req_text = self.format_evolution_requirement(detail)
                    if req_text:
                        requirements.append(req_text)
                
                if requirements:
                    # Create a styled label for requirements
                    req_label = ttk_boot.Label(req_frame, text=" → ".join(requirements), 
                                             font=('Arial', 9, 'bold'), 
                                             style='Custom.TLabel',
                                             foreground='white')  # White text
                    req_label.pack()
            
            # Display evolution arrow if there are evolutions
            if evolves_to:
                # Create a frame for the arrow positioned under the Pokemon
                arrow_frame = ttk_boot.Frame(pokemon_container, style='Custom.TFrame')
                arrow_frame.pack(anchor=CENTER, pady=(10, 0))

                # Downward pointing arrow
                arrow_label = ttk_boot.Label(arrow_frame, text="↓",
                                           font=('Arial', 20, 'bold'),
                                           style='Custom.TLabel',
                                           foreground='white')  # White color
                arrow_label.pack()
            
            # Recursively display evolutions
            if evolves_to:
                # Add separator before evolutions
                separator = ttk_boot.Frame(parent, height=2, style='Custom.TFrame')
                separator.pack(fill=X, pady=(10, 0))
                
                for i, evolution in enumerate(evolves_to):
                    self.display_evolution_node(parent, evolution, level=level+1, position=i)
                    
        except Exception as e:
            print(f"Error displaying evolution node: {e}")
    
    def format_evolution_requirement(self, detail):
        """Format evolution requirement details into readable text"""
        try:
            requirements = []
            
            # Level requirement
            if detail.get('min_level'):
                requirements.append(f"Lv. {detail['min_level']}")
            
            # Item requirement
            if detail.get('item'):
                item_name = detail['item'].get('name', '').replace('-', ' ').title()
                requirements.append(f"Use {item_name}")
            
            # Held item requirement
            if detail.get('held_item'):
                held_item = detail['held_item'].get('name', '').replace('-', ' ').title()
                requirements.append(f"Hold {held_item}")
            
            # Trade requirement
            if detail.get('trigger', {}).get('name') == 'trade':
                requirements.append("Trade")
            
            # Happiness requirement
            if detail.get('min_happiness'):
                requirements.append(f"Happiness {detail['min_happiness']}")
            
            # Time of day
            if detail.get('time_of_day'):
                time_name = detail['time_of_day'].title()
                requirements.append(f"At {time_name}")
            
            # Location requirement
            if detail.get('location'):
                location_name = detail['location'].get('name', '').replace('-', ' ').title()
                requirements.append(f"At {location_name}")
            
            # Known move requirement
            if detail.get('known_move'):
                move_name = detail['known_move'].get('name', '').replace('-', ' ').title()
                requirements.append(f"Know {move_name}")
            
            # Party species requirement
            if detail.get('party_species'):
                party_name = detail['party_species'].get('name', '').replace('-', ' ').title()
                requirements.append(f"{party_name} in party")
            
            # Party type requirement
            if detail.get('party_type'):
                type_name = detail['party_type'].get('name', '').title()
                requirements.append(f"{type_name} in party")
            
            # Gender requirement
            if detail.get('gender'):
                gender_map = {1: "Female", 2: "Male"}
                gender_name = gender_map.get(detail['gender'], "Unknown")
                requirements.append(f"{gender_name} only")
            
            # Beauty requirement
            if detail.get('min_beauty'):
                requirements.append(f"Beauty {detail['min_beauty']}")
            
            # Affection requirement
            if detail.get('min_affection'):
                requirements.append(f"Affection {detail['min_affection']}")
            
            # Special conditions
            if detail.get('needs_overworld_rain'):
                requirements.append("Rain required")
            
            if detail.get('turn_upside_down'):
                requirements.append("Turn upside down")
            
            return " + ".join(requirements) if requirements else ""
            
        except Exception as e:
            print(f"Error formatting evolution requirement: {e}")
            return ""
    
    def _pokemon_in_evolution_chain(self, pokemon_name, chain_data):
        """Check if a Pokemon appears in the given evolution chain"""
        try:
            # Check the base Pokemon
            base_species = chain_data.get('species', {}).get('name', '').lower()
            if base_species == pokemon_name.lower():
                return True
            
            # Recursively check all evolutions
            def check_evolutions(evolutions):
                for evolution in evolutions:
                    species_name = evolution.get('species', {}).get('name', '').lower()
                    if species_name == pokemon_name.lower():
                        return True
                    # Check further evolutions
                    if evolution.get('evolves_to'):
                        if check_evolutions(evolution['evolves_to']):
                            return True
                return False
            
            return check_evolutions(chain_data.get('evolves_to', []))
            
        except Exception as e:
            print(f"Error checking evolution chain: {e}")
            return False
    
    def load_pokemon_image_for_evolution(self, pokemon_name, image_label):
        """Load Pokemon image for evolution chain display"""
        try:
            # Get Pokemon ID from name
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM New_Pokemon_Data WHERE LOWER(name) = LOWER(?)", (pokemon_name,))
            result = cursor.fetchone()
            
            if result:
                pokemon_id = result[0]
                
                # Get image URL - use shiny front sprite for better visual appeal
                cursor.execute("""
                    SELECT image_url FROM New_Pokemon_Images 
                    WHERE pokemon_id = ? AND sprite_type = 'front_shiny' AND is_shiny = 1
                    LIMIT 1
                """, (pokemon_id,))
                
                image_result = cursor.fetchone()
                conn.close()
                
                if image_result and image_result[0]:
                    image_url = image_result[0]
                    
                    # Load image in background thread
                    def load_image():
                        try:
                            response = requests.get(image_url, timeout=5)
                            if response.status_code == 200:
                                image_data = BytesIO(response.content)
                                img = Image.open(image_data)
                                img = img.resize((100, 100), Image.Resampling.LANCZOS)
                                photo = ImageTk.PhotoImage(img)
                                
                                # Update image on main thread
                                def update_image():
                                    try:
                                        if image_label.winfo_exists():
                                            image_label.configure(image=photo)
                                            image_label.image = photo
                                    except Exception as e:
                                        print(f"Error updating image for {pokemon_name}: {e}")
                                
                                self.root.after(0, update_image)
                        except Exception as e:
                            print(f"Error loading evolution image for {pokemon_name}: {e}")
                            # Fallback to text
                            def update_fallback():
                                try:
                                    if image_label.winfo_exists():
                                        image_label.configure(text=f"{pokemon_name.title()}\nImage", image="",
                                                            font=('Arial', 10, 'bold'), foreground='white')
                                except Exception as e:
                                    print(f"Error updating fallback for {pokemon_name}: {e}")
                            self.root.after(0, update_fallback)
                    
                    threading.Thread(target=load_image, daemon=True).start()
                else:
                    try:
                        if image_label.winfo_exists():
                            image_label.configure(text=f"{pokemon_name.title()}\nImage", image="",
                                                font=('Arial', 10, 'bold'), foreground='white')
                    except Exception as e:
                        print(f"Error setting fallback image for {pokemon_name}: {e}")
            else:
                conn.close()
                try:
                    if image_label.winfo_exists():
                        image_label.configure(text=f"{pokemon_name.title()}\nImage", image="",
                                            font=('Arial', 10, 'bold'), foreground='white')
                except Exception as e:
                    print(f"Error setting fallback image for {pokemon_name}: {e}")
                
        except Exception as e:
            print(f"Error loading Pokemon image for evolution: {e}")
            try:
                if image_label.winfo_exists():
                    image_label.configure(text=f"{pokemon_name.title()}\nImage", image="",
                                        font=('Arial', 10, 'bold'), foreground='white')
            except Exception as e:
                print(f"Error setting final fallback for {pokemon_name}: {e}")
    
    def setup_abilities_tab(self):
        """Setup the abilities & breeding tab"""
        # Main container
        abilities_frame = ttk_boot.Frame(self.abilities_tab, style='Custom.TFrame')
        abilities_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk_boot.Label(abilities_frame, text="Pokemon Characteristics", 
                      font=('Arial', 16, 'bold'), style='Custom.TLabel').pack(pady=(0, 10))
        
        # Abilities section
        abilities_section = ttk_boot.LabelFrame(abilities_frame, text="Abilities", padding=10, style='Custom.TLabelframe')
        abilities_section.pack(fill=X, pady=(0, 10))
        
        self.abilities_display = ttk_boot.Label(abilities_section, text="Select a Pokemon to view abilities", 
                                              font=('Arial', 12), style='Custom.TLabel')
        self.abilities_display.pack(anchor=W)
        
        # Breeding section
        breeding_section = ttk_boot.LabelFrame(abilities_frame, text="Breeding Information", padding=10, style='Custom.TLabelframe')
        breeding_section.pack(fill=X, pady=(0, 10))
        
        self.breeding_display = ttk_boot.Label(breeding_section, text="Select a Pokemon to view breeding info", 
                                             font=('Arial', 12), style='Custom.TLabel')
        self.breeding_display.pack(anchor=W)
    
    def setup_moves_tab(self):
        """Setup the moves tab with side-by-side Moves and Move Details panels"""
        # Main container
        main_frame = ttk_boot.Frame(self.moves_tab, style='Custom.TFrame')
        main_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Create horizontal paned window for side-by-side layout
        paned_window = ttk_boot.PanedWindow(main_frame, orient=HORIZONTAL, style='Custom.TFrame')
        paned_window.pack(fill=BOTH, expand=True)

        # Left panel - Moves
        left_panel = ttk_boot.Frame(paned_window, style='Custom.TFrame')
        paned_window.add(left_panel, weight=3)

        # Left panel header
        left_header = ttk_boot.Frame(left_panel, style='Custom.TFrame')
        left_header.pack(fill=X, pady=(0, 5))
        ttk_boot.Label(left_header, text="Moves", font=('Arial', 16, 'bold'),
                      style='Custom.TLabel').pack(side=LEFT)
        ttk_boot.Label(left_header, text="(Click any move for details)",
                      font=('Arial', 10), style='Custom.TLabel').pack(side=RIGHT)

        # Moves display area
        self.moves_display_frame = ttk_boot.Frame(left_panel, style='Custom.TFrame')
        self.moves_display_frame.pack(fill=BOTH, expand=True)

        # Right panel - Move Details
        right_panel = ttk_boot.Frame(paned_window, style='Custom.TFrame')
        paned_window.add(right_panel, weight=2)

        # Right panel header
        ttk_boot.Label(right_panel, text="Move Details", font=('Arial', 16, 'bold'),
                      style='Custom.TLabel').pack(anchor=W, pady=(0, 5))

        # Move details display area
        self.move_details_frame = ttk_boot.Frame(right_panel, style='Custom.TFrame')
        self.move_details_frame.pack(fill=BOTH, expand=True)

        # Initially show placeholder in left panel
        placeholder_label = ttk_boot.Label(
            self.moves_display_frame,
            text="Select a Pokemon to view its moves",
            font=('Arial', 12),
            style='Custom.TLabel'
        )
        placeholder_label.pack(expand=True)

        # Initially show placeholder in right panel
        details_placeholder = ttk_boot.Label(
            self.move_details_frame,
            text="Select a move to view its details",
            font=('Arial', 12),
            style='Custom.TLabel'
        )
        details_placeholder.pack(expand=True)
    
    def setup_team_builder_tab(self):
        """Setup the team builder tab"""
        # Main container
        team_frame = ttk_boot.Frame(self.team_builder_tab, style='Custom.TFrame')
        team_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk_boot.Label(team_frame, text="Team Builder", 
                      font=('Arial', 16, 'bold'), style='Custom.TLabel').pack(pady=(0, 10))
        
        # Team slots
        team_slots_frame = ttk_boot.Frame(team_frame, style='Custom.TFrame')
        team_slots_frame.pack(fill=X, pady=(0, 10))
        
        # Create 6 team slots
        self.team_slots = []
        for i in range(6):
            slot_frame = ttk_boot.LabelFrame(team_slots_frame, text=f"Team Slot {i+1}", padding=5, style='Custom.TLabelframe')
            slot_frame.grid(row=i//3, column=i%3, padx=5, pady=5, sticky=W+E)
            
            # Pokemon display
            pokemon_label = ttk_boot.Label(slot_frame, text="Empty", style='Custom.TLabel')
            pokemon_label.pack()
            
            # Add/Remove buttons
            buttons_frame = ttk_boot.Frame(slot_frame, style='Custom.TFrame')
            buttons_frame.pack(fill=X, pady=(5, 0))
            
            add_btn = ttk_boot.Button(buttons_frame, text="Add Pokemon", bootstyle="success")
            add_btn.pack(side=LEFT, padx=(0, 5))
            
            remove_btn = ttk_boot.Button(buttons_frame, text="Remove", bootstyle="danger", state="disabled")
            remove_btn.pack(side=LEFT)
            
            self.team_slots.append({
                'frame': slot_frame,
                'label': pokemon_label,
                'add_btn': add_btn,
                'remove_btn': remove_btn,
                'pokemon': None
            })
        
        # Team analysis section
        analysis_frame = ttk_boot.LabelFrame(team_frame, text="Team Analysis", padding=10, style='Custom.TLabelframe')
        analysis_frame.pack(fill=BOTH, expand=True)
        
        self.team_analysis_display = ttk_boot.Label(analysis_frame, text="Add Pokemon to your team to see analysis", 
                                                  font=('Arial', 12), style='Custom.TLabel')
        self.team_analysis_display.pack(anchor=W)
    
    def setup_battle_simulator_tab(self):
        """Setup the battle simulator tab"""
        # Main container
        battle_frame = ttk_boot.Frame(self.battle_simulator_tab, style='Custom.TFrame')
        battle_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Title
        ttk_boot.Label(battle_frame, text="Battle Simulator", 
                      font=('Arial', 16, 'bold'), style='Custom.TLabel').pack(pady=(0, 10))
        
        # Battle setup section
        setup_frame = ttk_boot.Frame(battle_frame, style='Custom.TFrame')
        setup_frame.pack(fill=X, pady=(0, 10))
        
        # Attacker selection
        attacker_frame = ttk_boot.LabelFrame(setup_frame, text="Attacker", padding=5, style='Custom.TLabelframe')
        attacker_frame.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 5))
        
        self.attacker_label = ttk_boot.Label(attacker_frame, text="Select Pokemon", style='Custom.TLabel')
        self.attacker_label.pack()
        
        select_attacker_btn = ttk_boot.Button(attacker_frame, text="Select Attacker", bootstyle="primary")
        select_attacker_btn.pack(pady=(5, 0))
        
        # Defender selection
        defender_frame = ttk_boot.LabelFrame(setup_frame, text="Defender", padding=5, style='Custom.TLabelframe')
        defender_frame.pack(side=RIGHT, fill=BOTH, expand=True, padx=(5, 0))
        
        self.defender_label = ttk_boot.Label(defender_frame, text="Select Pokemon", style='Custom.TLabel')
        self.defender_label.pack()
        
        select_defender_btn = ttk_boot.Button(defender_frame, text="Select Defender", bootstyle="primary")
        select_defender_btn.pack(pady=(5, 0))
        
        # Move selection and damage calculation
        calc_frame = ttk_boot.LabelFrame(battle_frame, text="Damage Calculation", padding=10, style='Custom.TLabelframe')
        calc_frame.pack(fill=BOTH, expand=True)
        
        # Move selection
        move_frame = ttk_boot.Frame(calc_frame, style='Custom.TFrame')
        move_frame.pack(fill=X, pady=(0, 10))
        
        ttk_boot.Label(move_frame, text="Select Move:", style='Custom.TLabel').pack(side=LEFT)
        self.move_var = tk.StringVar()
        move_combo = ttk_boot.Combobox(move_frame, textvariable=self.move_var, style='Custom.TCombobox')
        move_combo.pack(side=LEFT, padx=(10, 0), fill=X, expand=True)
        
        calc_btn = ttk_boot.Button(move_frame, text="Calculate Damage", bootstyle="success")
        calc_btn.pack(side=RIGHT, padx=(10, 0))
        
        # Results display
        results_frame = ttk_boot.Frame(calc_frame, style='Custom.TFrame')
        results_frame.pack(fill=BOTH, expand=True)
        
        self.damage_result_label = ttk_boot.Label(results_frame, text="Select Pokemon and move to calculate damage", 
                                                font=('Arial', 14), style='Custom.TLabel')
        self.damage_result_label.pack(expand=True)

    def load_pokemon_list(self):
        """Load Pokemon list from New_Pokemon_Data table"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Get Pokemon from New_Pokemon_Data table
            cursor.execute("""
                SELECT id, name, types
                FROM New_Pokemon_Data
                ORDER BY id ASC
            """)

            pokemon_data = cursor.fetchall()
            conn.close()

            # Clear existing list
            self.pokemon_listbox.delete(0, tk.END)
            self.pokemon_id_map.clear()

            # Populate listbox
            for i, (pokemon_id, name, types_json) in enumerate(pokemon_data):
                # Parse types from JSON
                try:
                    types_data = json.loads(types_json)
                    type_names = [t['type']['name'] for t in types_data]
                    types_display = "/".join(type_names)
                except:
                    types_display = "Unknown"

                # Format display text
                display_text = f"#{pokemon_id:03d} {name.title()} ({types_display})"

                self.pokemon_listbox.insert(tk.END, display_text)
                self.pokemon_id_map[i] = pokemon_id

        except Exception as e:
            print(f"Error loading Pokemon list: {e}")
            self.pokemon_listbox.insert(tk.END, "Error loading Pokemon list")

    def filter_pokemon(self, *args):
        """Filter Pokemon list based on search criteria"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Build query with filters
            query = """
                SELECT id, name, types, stats
                FROM New_Pokemon_Data
                WHERE 1=1
            """
            params = []

            # Name filter
            if self.name_var.get():
                query += " AND name LIKE ?"
                params.append(f"%{self.name_var.get()}%")

            # Type filter
            if self.type_var.get():
                # We'll filter by type after fetching since it's stored as JSON
                pass

            # Get all Pokemon first, then filter
            cursor.execute(query, params)
            all_pokemon = cursor.fetchall()
            conn.close()

            # Apply filters
            filtered_data = []
            for pokemon_id, name, types_json, stats_json in all_pokemon:
                # Parse types
                try:
                    types_data = json.loads(types_json)
                    type_names = [t['type']['name'] for t in types_data]
                except:
                    type_names = []

                # Parse stats
                try:
                    stats_data = json.loads(stats_json)
                    stat_dict = {s['stat']['name']: s['base_stat'] for s in stats_data}
                except:
                    stat_dict = {}

                # Apply type filter
                if self.type_var.get():
                    if self.type_var.get().lower() not in type_names:
                        continue

                # Apply stat filters
                skip_pokemon = False
                stat_filters = [
                    ('hp', self.min_hp_var),
                    ('attack', self.min_attack_var),
                    ('defense', self.min_defense_var),
                    ('special-attack', self.min_sp_attack_var),
                    ('special-defense', self.min_sp_defense_var),
                    ('speed', self.min_speed_var)
                ]

                for stat_name, var in stat_filters:
                    if var.get():
                        try:
                            min_value = int(var.get())
                            if stat_dict.get(stat_name, 0) < min_value:
                                skip_pokemon = True
                                break
                        except ValueError:
                            pass

                if skip_pokemon:
                    continue

                filtered_data.append((pokemon_id, name, type_names, stat_dict))

            # Update listbox
            self.pokemon_listbox.delete(0, tk.END)
            self.pokemon_id_map.clear()

            for i, (pokemon_id, name, type_names, stat_dict) in enumerate(filtered_data):
                types_display = "/".join(type_names) if type_names else "Unknown"
                display_text = f"#{pokemon_id:03d} {name.title()} ({types_display})"
                self.pokemon_listbox.insert(tk.END, display_text)
                self.pokemon_id_map[i] = pokemon_id

        except Exception as e:
            print(f"Error filtering Pokemon: {e}")

    def on_pokemon_select(self, event):
        """Handle Pokemon selection from listbox"""
        selection = self.pokemon_listbox.curselection()
        if selection:
            index = selection[0]
            pokemon_id = self.pokemon_id_map.get(index)

            if pokemon_id:
                self.load_pokemon_details(pokemon_id)

    def load_pokemon_details(self, pokemon_id):
        """Load and display Pokemon details from new tables"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Get basic Pokemon data from New_Pokemon_Data
            cursor.execute("""
                SELECT * FROM New_Pokemon_Data WHERE id = ?
            """, (pokemon_id,))

            pokemon_data = cursor.fetchone()
            if not pokemon_data:
                print(f"No data found for Pokemon ID {pokemon_id}")
                return

            # Parse Pokemon data from JSON fields
            pokemon_info = {
                'id': pokemon_data[0],
                'name': pokemon_data[1],
                'number': pokemon_data[0],  # Use ID as number since that's what we have
            }

            # Parse stats from JSON
            try:
                stats_data = json.loads(pokemon_data[8])  # stats column
                stat_dict = {}
                for stat in stats_data:
                    stat_name = stat['stat']['name']
                    stat_value = stat['base_stat']
                    stat_dict[stat_name] = stat_value

                pokemon_info.update({
                    'hp': stat_dict.get('hp', 0),
                    'attack': stat_dict.get('attack', 0),
                    'defense': stat_dict.get('defense', 0),
                    'sp_attack': stat_dict.get('special-attack', 0),
                    'sp_defense': stat_dict.get('special-defense', 0),
                    'speed': stat_dict.get('speed', 0),
                })
                pokemon_info['total'] = sum(stat_dict.values())
            except:
                pokemon_info.update({
                    'hp': 0, 'attack': 0, 'defense': 0,
                    'sp_attack': 0, 'sp_defense': 0, 'speed': 0, 'total': 0
                })

            # Parse types from JSON
            try:
                types_data = json.loads(pokemon_data[9])  # types column
                type_names = [t['type']['name'] for t in types_data]
                pokemon_info['type1'] = type_names[0] if len(type_names) > 0 else None
                pokemon_info['type2'] = type_names[1] if len(type_names) > 1 else None
            except:
                pokemon_info['type1'] = None
                pokemon_info['type2'] = None

            # Parse abilities from JSON
            try:
                abilities_json = json.loads(pokemon_data[7])  # abilities column
                abilities_list = []
                for ability in abilities_json:
                    ability_name = ability['ability']['name']
                    is_hidden = ability.get('is_hidden', False)
                    abilities_list.append((ability_name, is_hidden))
                pokemon_info['abilities'] = abilities_list
            except:
                pokemon_info['abilities'] = []

            # Get additional data from other tables
            # Get images data - get default and shiny sprites
            cursor.execute("""
                SELECT image_url, sprite_type, is_shiny
                FROM New_Pokemon_Images
                WHERE pokemon_id = ? AND sprite_category = 'basic'
                ORDER BY is_shiny ASC, sprite_type ASC
            """, (pokemon_id,))
            images_rows = cursor.fetchall()

            # Organize images by type
            images_data = {}
            for image_url, sprite_type, is_shiny in images_rows:
                if is_shiny:
                    if sprite_type == 'front_shiny':
                        images_data['sprite_shiny'] = image_url
                    elif sprite_type == 'back_shiny':
                        images_data['back_shiny'] = image_url
                else:
                    if sprite_type == 'front_default':
                        images_data['sprite_default'] = image_url
                    elif sprite_type == 'back_default':
                        images_data['back_default'] = image_url

            # Convert to tuple format expected by display method
            images_data_tuple = (
                images_data.get('sprite_default'),
                images_data.get('sprite_shiny'),
                images_data.get('back_default'),
                images_data.get('back_shiny')
            )

            # Get breeding data
            cursor.execute("""
                SELECT egg_groups, hatch_counter, gender_rate, growth_rate,
                       base_happiness, capture_rate
                FROM New_Pokemon_Breeding_Data
                WHERE id = ?
            """, (pokemon_id,))
            breeding_row = cursor.fetchone()

            # Parse breeding data
            breeding_data = None
            if breeding_row:
                try:
                    egg_groups = json.loads(breeding_row[0]) if breeding_row[0] else []
                    breeding_data = (
                        egg_groups[0] if len(egg_groups) > 0 else None,
                        egg_groups[1] if len(egg_groups) > 1 else None,
                        breeding_row[1],  # hatch_counter
                        breeding_row[2],  # gender_rate
                        None  # egg_cycles (not available in this table)
                    )
                except:
                    breeding_data = (None, None, breeding_row[1], breeding_row[2], None)

            # Get evolution data - find the correct evolution chain for this Pokemon
            evolution_data = []
            try:
                # First, get the Pokemon's name to search for it in evolution chains
                cursor.execute("SELECT name FROM New_Pokemon_Data WHERE id = ?", (pokemon_id,))
                pokemon_name_row = cursor.fetchone()
                if pokemon_name_row:
                    pokemon_name = pokemon_name_row[0]
                    
                    # Search through all evolution chains to find which one contains this Pokemon
                    cursor.execute("SELECT id, chain FROM New_Pokemon_Evolutions")
                    all_evolution_chains = cursor.fetchall()
                    
                    for chain_id, chain_json in all_evolution_chains:
                        if chain_json:
                            try:
                                chain_data = json.loads(chain_json)
                                # Check if this Pokemon appears anywhere in this evolution chain
                                if self._pokemon_in_evolution_chain(pokemon_name, chain_data):
                                    evolution_data = [chain_data]
                                    break
                            except Exception as e:
                                print(f"Error parsing evolution chain {chain_id}: {e}")
                                continue
                
                # Fallback: if no evolution chain found, try the original method
                if not evolution_data:
                    cursor.execute("""
                        SELECT chain FROM New_Pokemon_Evolutions WHERE id = ?
                    """, (pokemon_id,))
                    evolution_row = cursor.fetchone()
                    if evolution_row:
                        try:
                            chain_data = json.loads(evolution_row[0])
                            evolution_data = [chain_data]
                        except:
                            evolution_data = []
            except Exception as e:
                print(f"Error loading evolution data: {e}")
                evolution_data = []

            # Get level-up moves data
            cursor.execute("""
                SELECT move_name, level_learned, learn_method, version_group
                FROM New_Pokemon_Move_Level_Data
                WHERE pokemon_id = ? AND learn_method = 'level-up'
                ORDER BY level_learned ASC
            """, (pokemon_id,))
            level_up_moves_data = cursor.fetchall()

            # Get tutor moves data
            cursor.execute("""
                SELECT move_name, level_learned, learn_method, version_group
                FROM New_Pokemon_Move_Level_Data
                WHERE pokemon_id = ? AND learn_method = 'tutor'
                ORDER BY move_name ASC
            """, (pokemon_id,))
            tutor_moves_data = cursor.fetchall()

            # Get egg moves data
            cursor.execute("""
                SELECT move_name, move_type, move_power, move_pp, version_group
                FROM New_Pokemon_Move_Learning_Data
                WHERE pokemon_id = ? AND is_egg_move = 1
                ORDER BY move_name
            """, (pokemon_id,))
            egg_moves_data = cursor.fetchall()

            # Get TM/HM moves (Note: This table contains all available TM/HM moves, not Pokemon-specific)
            cursor.execute("""
                SELECT move_name, machine_id, item_name, version_group_name
                FROM New_Pokemon_Machines
                WHERE machine_id IS NOT NULL
                ORDER BY machine_id ASC
                LIMIT 20
            """)
            tm_hm_moves_data = cursor.fetchall()

            # Get contest data
            cursor.execute("""
                SELECT contest_type, contest_effect_appeal, contest_effect_jam,
                       contest_effect_flavor_text, super_contest_effect_appeal,
                       super_contest_effect_flavor_text
                FROM New_Pokemon_Contest_Data
                WHERE move_id IN (
                    SELECT move_id FROM New_Pokemon_Move_Level_Data WHERE pokemon_id = ?
                )
            """, (pokemon_id,))
            contest_data = cursor.fetchall()

            # Get personality data
            cursor.execute("""
                SELECT english_description, gene_modulo, highest_stat_name
                FROM New_Pokemon_Move_Personality_Data
                LIMIT 6
            """)
            personality_data = cursor.fetchall()

            # Get egg moves data
            cursor.execute("""
                SELECT move_name, move_type, move_power, move_pp, version_group
                FROM New_Pokemon_Move_Learning_Data
                WHERE pokemon_id = ? AND is_egg_move = 1
                ORDER BY move_name
            """, (pokemon_id,))
            egg_moves_data = cursor.fetchall()

            conn.close()

            # Convert stat_dict to list of tuples for display method
            stats_list = [
                ('HP', stat_dict.get('hp', 0)),
                ('Attack', stat_dict.get('attack', 0)),
                ('Defense', stat_dict.get('defense', 0)),
                ('Sp. Attack', stat_dict.get('special-attack', 0)),
                ('Sp. Defense', stat_dict.get('special-defense', 0)),
                ('Speed', stat_dict.get('speed', 0))
            ]

            # Display Pokemon details
            self.display_pokemon_details(pokemon_data, images_data_tuple, type_names, stats_list,
                                      pokemon_info.get('abilities', []), breeding_data,
                                      evolution_data, level_up_moves_data, tutor_moves_data, tm_hm_moves_data,
                                      contest_data, personality_data, egg_moves_data)

        except Exception as e:
            print(f"Error loading Pokemon details: {e}")
            import traceback
            traceback.print_exc()

    def display_pokemon_details(self, pokemon_data, pokemon_info, type_data, stats_data,
                              abilities_data, breeding_data, evolution_data, level_up_moves_data,
                              tutor_moves_data, tm_hm_moves_data, contest_data, personality_data, egg_moves_data):
        """Display comprehensive Pokemon details across all tabs"""

        # Display data in appropriate tabs
        self.display_basic_info(pokemon_data, pokemon_info, type_data, stats_data, abilities_data, breeding_data)
        self.display_abilities_breeding(pokemon_data, abilities_data, breeding_data, personality_data)
        self.display_moves_info(level_up_moves_data, tutor_moves_data, tm_hm_moves_data, egg_moves_data)
        self.display_evolution_chain(evolution_data)

        # Store current Pokemon info for other operations
        self.current_pokemon = pokemon_data

    def display_basic_info(self, pokemon_data, pokemon_info, type_data, stats_data, abilities_data, breeding_data):
        """Display basic Pokemon information in the Basic Info tab"""
        # Update existing UI elements instead of recreating them

        # Update Pokemon name and number
        if pokemon_data:
            pokemon_name = pokemon_data[1] if len(pokemon_data) > 1 else "Unknown"
            pokemon_id = pokemon_data[0] if len(pokemon_data) > 0 else 0
            self.name_label.config(text=f"#{pokemon_id:03d} {pokemon_name}")
            self.number_label.config(text=f"Number: {pokemon_id:03d}")

            # Get species, height, and weight data from database
            try:
                conn = sqlite3.connect(self.db_name)
                cursor = conn.cursor()
                cursor.execute('SELECT species_name, height, weight FROM New_Pokemon_Data WHERE id = ?', (pokemon_id,))
                physical_data = cursor.fetchone()
                conn.close()

                if physical_data:
                    species_name = physical_data[0] or pokemon_name
                    height_dm = physical_data[1] or 0
                    weight_hg = physical_data[2] or 0

                    # Format height and weight
                    height_m = height_dm / 10.0
                    weight_kg = weight_hg / 10.0

                    self.species_label.config(text=f"Species: {species_name}")
                    self.height_label.config(text=f"Height: {height_m:.1f} m")
                    self.weight_label.config(text=f"Weight: {weight_kg:.1f} kg")
                else:
                    self.species_label.config(text=f"Species: {pokemon_name}")
                    self.height_label.config(text="Height: Unknown")
                    self.weight_label.config(text="Weight: Unknown")
            except Exception as e:
                print(f"Error loading physical data: {e}")
                self.species_label.config(text=f"Species: {pokemon_name}")
                self.height_label.config(text="Height: Unknown")
                self.weight_label.config(text="Weight: Unknown")

        # Update Pokemon image
        if pokemon_info and len(pokemon_info) > 0 and pokemon_info[0]:
            image_url = pokemon_info[0]
            try:
                response = requests.get(image_url, timeout=5)
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    img = Image.open(image_data)
                    img = img.resize((180, 180), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.image_label.configure(image=photo)
                    self.image_label.image = photo
                else:
                    self.image_label.configure(text="No Image Available", image="")
            except Exception as e:
                print(f"Error loading image: {e}")
                self.image_label.configure(text="No Image Available", image="")
        else:
            self.image_label.configure(text="No Image Available", image="")

        # Update types - display icons right under the number label
        if type_data:
            # Clear the type label text (remove "Type:" text)
            self.type_label.config(text="")

            # Clear existing type icons in the type_icons_container
            for widget in self.type_icons_container.winfo_children():
                widget.destroy()

            # Clear any existing type badge frames in the basic info frame
            parent_frame = self.type_label.master
            for widget in parent_frame.winfo_children():
                if hasattr(widget, 'winfo_class') and widget.winfo_class() == 'TFrame':
                    # Check if this is a type badge frame using our custom attribute
                    if hasattr(widget, 'is_type_badge_frame') and widget.is_type_badge_frame:
                        widget.destroy()
                        continue

                    # Fallback: Check if this is a type badge frame by looking for our specific structure
                    # Type badge frames contain exactly 2 children: icon label and text label
                    children = widget.winfo_children()
                    if len(children) == 2:
                        # Check if first child is a label with image (icon) and second is text label
                        if (len(children) >= 1 and hasattr(children[0], 'cget') and
                            hasattr(children[0], 'winfo_class') and children[0].winfo_class() == 'TLabel'):
                            try:
                                # If it has an image, it's likely a type badge frame
                                if children[0].cget('image'):
                                    widget.destroy()
                                    continue
                            except Exception:
                                pass
                        # Also check if the frame was created as a type badge frame by checking its position
                        # Type badge frames are packed before the type_label
                        try:
                            if hasattr(widget, 'pack_info'):
                                pack_info = widget.pack_info()
                                if 'before' in pack_info and pack_info['before'] == str(self.type_label):
                                    widget.destroy()
                                    continue
                        except Exception:
                            pass

            # Create a new frame for type badges and pack it right after number_label
            type_badge_frame = ttk_boot.Frame(parent_frame, style='Custom.TFrame')
            type_badge_frame.is_type_badge_frame = True  # Mark this as a type badge frame
            type_badge_frame.pack(anchor=W, pady=0, padx=0, after=self.number_label)  # Pack after number_label
            
            # Add type badges to the new frame
            for type_name in type_data:
                self.display_type_badge(type_badge_frame, type_name)
        else:
            self.type_label.config(text="")

        # Update stats
        if hasattr(self, 'stat_gauges') and stats_data:
            for stat_name, base_stat in stats_data:
                stat_key = stat_name.lower().replace(' ', '_').replace('.', '')
                if stat_key in self.stat_gauges:
                    gauge = self.stat_gauges[stat_key]
                    percentage = min(100, (base_stat / 255) * 100)
                    gauge.configure(value=percentage)
                    if stat_key in self.stat_labels:
                        self.stat_labels[stat_key].configure(text=str(base_stat))

            # Update the radar chart with stats data
            stats_dict = {stat_name.lower().replace(' ', '_').replace('.', ''): base_stat
                         for stat_name, base_stat in stats_data}
            pokemon_name = pokemon_data[1] if pokemon_data and len(pokemon_data) > 1 else "Unknown"
            self.update_stats_chart(stats_dict, pokemon_name)

        # Update abilities
        if abilities_data:
            abilities_text = []
            for ability_name, is_hidden in abilities_data:
                if is_hidden:
                    abilities_text.append(f"{ability_name} (Hidden)")
                else:
                    abilities_text.append(ability_name)
            self.abilities_label.config(text=f"Abilities: {', '.join(abilities_text)}")
        else:
            self.abilities_label.config(text="Abilities: None")

        # Update type weaknesses and defenses
        if type_data:
            self.update_type_effectiveness(type_data)

        # Update gender information
        if breeding_data and len(breeding_data) > 3:
            self.update_gender_info(breeding_data[3])  # gender_rate

    def update_type_effectiveness(self, type_names):
        """Update type weaknesses and defenses based on Pokemon types"""
        try:
            # Clear existing type icons
            for container in [self.weak_icons_container, self.very_weak_icons_container,
                            self.resistant_icons_container, self.very_resistant_icons_container,
                            self.immune_icons_container]:
                for widget in container.winfo_children():
                    widget.destroy()

            # Get type effectiveness data from Weakness_Strength table
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Define attacking type columns (columns 4-21)
            attacking_types = ['Normal', 'Fire', 'Water', 'Electric', 'Grass', 'Ice', 
                             'Fighting', 'Poison', 'Ground', 'Flying', 'Psychic', 'Bug',
                             'Rock', 'Ghost', 'Dragon', 'Dark', 'Steel', 'Fairy']

            # Find the appropriate row for this Pokemon's types
            if len(type_names) == 1:
                # Single type - capitalize first
                type1 = type_names[0].capitalize()
                cursor.execute("SELECT * FROM Weakness_Strength WHERE Type1 = ? AND Type2 IS NULL", (type1,))
            else:
                # Dual type - capitalize both
                type1 = type_names[0].capitalize()
                type2 = type_names[1].capitalize()
                cursor.execute("SELECT * FROM Weakness_Strength WHERE (Type1 = ? AND Type2 = ?) OR (Type1 = ? AND Type2 = ?)", 
                             (type1, type2, type2, type1))

            row = cursor.fetchone()
            conn.close()

            if not row:
                print(f"No type effectiveness data found for types: {type_names}")
                return

            # Initialize effectiveness dictionaries
            weaknesses = {}  # type -> multiplier
            resistances = {}  # type -> multiplier
            immunities = set()  # types with 0x

            # Check each attacking type's multiplier
            for i, attacking_type in enumerate(attacking_types):
                col_idx = i + 4  # Multipliers start at column 4
                if col_idx < len(row):
                    multiplier = row[col_idx]
                    
                    if multiplier == 0:
                        immunities.add(attacking_type)
                    elif multiplier > 1:
                        weaknesses[attacking_type] = multiplier
                    elif multiplier < 1:
                        resistances[attacking_type] = multiplier

            # Display weaknesses
            for weak_type, mult in sorted(weaknesses.items()):
                if mult == 4.0:
                    self.display_type_badge(self.very_weak_icons_container, weak_type)
                elif mult == 2.0:
                    self.display_type_badge(self.weak_icons_container, weak_type)

            # Display resistances
            for resist_type, mult in sorted(resistances.items()):
                if mult == 0.25:
                    self.display_type_badge(self.very_resistant_icons_container, resist_type)
                elif mult == 0.5:
                    self.display_type_badge(self.resistant_icons_container, resist_type)

            # Display immunities
            for immune_type in sorted(immunities):
                self.display_type_badge(self.immune_icons_container, immune_type)

        except Exception as e:
            print(f"Error updating type effectiveness: {e}")

    def update_gender_info(self, gender_rate):
        """Update gender information display"""
        try:
            # Clear existing gender icons
            self.male_icon_label.configure(image="")
            self.female_icon_label.configure(image="")

            if gender_rate == -1:
                # Genderless
                self.percent_male_label.config(text="Genderless")
                self.percent_female_label.config(text="")
                if 'genderless' in self.gender_icons:
                    self.male_icon_label.configure(image=self.gender_icons['genderless'])
            else:
                # Calculate percentages
                female_ratio = gender_rate / 8.0
                male_ratio = 1.0 - female_ratio

                male_percent = int(male_ratio * 100)
                female_percent = int(female_ratio * 100)

                self.percent_male_label.config(text=f"Male: {male_percent}%")
                self.percent_female_label.config(text=f"Female: {female_percent}%")

                # Set gender icons
                if 'male' in self.gender_icons:
                    self.male_icon_label.configure(image=self.gender_icons['male'])
                if 'female' in self.gender_icons:
                    self.female_icon_label.configure(image=self.gender_icons['female'])

        except Exception as e:
            print(f"Error updating gender info: {e}")

    def create_radar_chart(self, stats_data, pokemon_name="Pokemon"):
        """Create a radar chart for Pokemon stats"""
        # Stats in order for radar chart
        categories = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
        values = [stats_data.get(cat.lower().replace(' ', '_').replace('.', ''), 0) for cat in categories]

        # Close the polygon
        values += values[:1]
        categories += categories[:1]

        # Calculate angles
        angles = [n / float(len(categories[:-1])) * 2 * np.pi for n in range(len(categories))]

        # Create figure
        fig = Figure(figsize=(3.0, 2.5), dpi=100, facecolor='#000080')
        ax = fig.add_subplot(111, polar=True)

        # Set background color to match Chart Stats frame (dark navy blue)
        ax.set_facecolor('#000080')
        fig.patch.set_facecolor('#000080')

        # Plot data
        ax.plot(angles, values, 'o-', linewidth=0.8, label=pokemon_name, color='#00BFFF', markersize=2)
        ax.fill(angles, values, alpha=0.25, color='#00BFFF')

        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories[:-1], color='white', fontsize=6)
        ax.set_yticklabels([])

        # Set grid color to match theme
        ax.grid(color='#4169E1', alpha=0.5)

        # Set title
        ax.set_title(f"{pokemon_name} Stats", size=8, color='white', pad=5)

        # Set radial limits
        ax.set_rlim(0, 255)

        # Add stat values as text
        for i, (angle, value) in enumerate(zip(angles[:-1], values[:-1])):
            ax.text(angle, value + 2, str(int(value)), ha='center', va='center',
                   color='white', fontsize=5, fontweight='bold')

        return fig

    def update_stats_chart(self, stats_data=None, pokemon_name="Pokemon"):
        """Update the stats radar chart"""
        # Clear previous chart
        if hasattr(self, 'stats_canvas'):
            self.stats_canvas.get_tk_widget().destroy()

        # Create new chart
        fig = self.create_radar_chart(stats_data, pokemon_name)

        # Create canvas
        self.stats_canvas = FigureCanvasTkAgg(fig, master=self.stats_chart_frame)
        self.stats_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def display_abilities_breeding(self, pokemon_data, abilities_data, breeding_data, personality_data):
        """Display detailed abilities, breeding information, and personality traits"""
        # Clear existing content
        for widget in self.abilities_tab.winfo_children():
            widget.destroy()

        # Create scrollable frame
        scrollable_frame = ScrollableFrame(self.abilities_tab, style='Custom.TFrame')
        scrollable_frame.pack(fill=BOTH, expand=True)

        # Detailed abilities section
        if abilities_data:
            abilities_frame = ttk_boot.LabelFrame(scrollable_frame.scrollable_frame, text="Ability Details", padding=10, style='Custom.TLabelframe')
            abilities_frame.pack(fill=X, pady=(0, 10))

            for ability_name, is_hidden in abilities_data:
                ability_row = ttk_boot.Frame(abilities_frame, style='Custom.TFrame')
                ability_row.pack(fill=X, pady=5)

                # Ability name
                ability_text = f"{ability_name.title()} (Hidden)" if is_hidden else ability_name.title()
                ttk_boot.Label(ability_row, text=ability_text, font=('Arial', 11, 'bold'),
                              style='Custom.TLabel').pack(anchor=W)

                # Get ability description from database
                try:
                    conn = sqlite3.connect(self.db_name)
                    cursor = conn.cursor()
                    cursor.execute("SELECT effect_entries_json FROM New_Pokemon_Abilities WHERE LOWER(name) = LOWER(?)", (ability_name,))
                    ability_row_data = cursor.fetchone()
                    conn.close()

                    if ability_row_data and ability_row_data[0]:
                        import json
                        effect_entries = json.loads(ability_row_data[0])
                        if effect_entries:
                            # Get the first English effect entry
                            for entry in effect_entries:
                                if entry.get('language', {}).get('name') == 'en':
                                    description = entry.get('effect', 'No description available')
                                    # Clean up the description
                                    description = description.replace('\n', ' ').strip()
                                    ttk_boot.Label(ability_row, text=description, font=('Arial', 9),
                                                  style='Custom.TLabel', wraplength=600).pack(anchor=W, pady=(2, 0))
                                    break
                            else:
                                # If no English entry found, use the first one
                                if effect_entries:
                                    description = effect_entries[0].get('effect', 'No description available')
                                    description = description.replace('\n', ' ').strip()
                                    ttk_boot.Label(ability_row, text=description, font=('Arial', 9),
                                                  style='Custom.TLabel', wraplength=600).pack(anchor=W, pady=(2, 0))
                        else:
                            ttk_boot.Label(ability_row, text="No description available", font=('Arial', 9),
                                          style='Custom.TLabel').pack(anchor=W, pady=(2, 0))
                    else:
                        ttk_boot.Label(ability_row, text="No description available", font=('Arial', 9),
                                      style='Custom.TLabel').pack(anchor=W, pady=(2, 0))
                except Exception as e:
                    print(f"Error loading ability description for {ability_name}: {e}")
                    ttk_boot.Label(ability_row, text="Error loading description", font=('Arial', 9),
                                  style='Custom.TLabel').pack(anchor=W, pady=(2, 0))

        # Breeding information
        if breeding_data:
            breeding_frame = ttk_boot.LabelFrame(scrollable_frame.scrollable_frame, text="Breeding Information", padding=10, style='Custom.TLabelframe')
            breeding_frame.pack(fill=X, pady=(0, 10))

            # Basic breeding info
            basic_info_frame = ttk_boot.Frame(breeding_frame, style='Custom.TFrame')
            basic_info_frame.pack(fill=X, pady=(0, 10))

            # Egg Groups
            egg_groups = []
            if breeding_data[0]:
                egg_groups.append(breeding_data[0])
            if breeding_data[1]:
                egg_groups.append(breeding_data[1])

            ttk_boot.Label(basic_info_frame, text=f"Egg Groups: {', '.join(egg_groups)}",
                          font=('Arial', 10, 'bold'), style='Custom.TLabel').pack(anchor=W)

            # Hatch Counter
            if breeding_data[2]:
                hatch_steps = breeding_data[2] * 255  # Convert to steps
                ttk_boot.Label(basic_info_frame, text=f"Hatch Time: {hatch_steps:,} steps",
                              style='Custom.TLabel').pack(anchor=W)

            # Gender Rate
            if breeding_data[3] is not None:
                if breeding_data[3] == -1:
                    gender_text = "Gender: Genderless"
                else:
                    female_ratio = breeding_data[3] / 8.0
                    male_ratio = 1.0 - female_ratio
                    male_percent = int(male_ratio * 100)
                    female_percent = int(female_ratio * 100)
                    gender_text = f"Gender: {male_percent}% Male, {female_percent}% Female"
                ttk_boot.Label(basic_info_frame, text=gender_text, style='Custom.TLabel').pack(anchor=W)

            # Get additional breeding data from database
            if pokemon_data:
                pokemon_id = pokemon_data[0]
                try:
                    conn = sqlite3.connect(self.db_name)
                    cursor = conn.cursor()

                    # Get full breeding data
                    cursor.execute("""
                        SELECT growth_rate, base_happiness, capture_rate, habitat_name,
                               has_gender_differences, is_baby, is_legendary, is_mythical,
                               color_name, shape_name, genus
                        FROM New_Pokemon_Breeding_Data
                        WHERE id = ?
                    """, (pokemon_id,))

                    full_breeding_data = cursor.fetchone()

                    if full_breeding_data:
                        growth_rate, base_happiness, capture_rate, habitat_name, \
                        has_gender_differences, is_baby, is_legendary, is_mythical, \
                        color_name, shape_name, genus = full_breeding_data

                        # Additional breeding info
                        ttk_boot.Label(basic_info_frame, text=f"Growth Rate: {growth_rate.title() if growth_rate else 'Unknown'}",
                                      style='Custom.TLabel').pack(anchor=W)
                        ttk_boot.Label(basic_info_frame, text=f"Base Happiness: {base_happiness if base_happiness else 'Unknown'}",
                                      style='Custom.TLabel').pack(anchor=W)
                        ttk_boot.Label(basic_info_frame, text=f"Capture Rate: {capture_rate if capture_rate else 'Unknown'}",
                                      style='Custom.TLabel').pack(anchor=W)
                        ttk_boot.Label(basic_info_frame, text=f"Habitat: {habitat_name.title() if habitat_name else 'Unknown'}",
                                      style='Custom.TLabel').pack(anchor=W)
                        ttk_boot.Label(basic_info_frame, text=f"Color: {color_name.title() if color_name else 'Unknown'}",
                                      style='Custom.TLabel').pack(anchor=W)
                        ttk_boot.Label(basic_info_frame, text=f"Shape: {shape_name.title() if shape_name else 'Unknown'}",
                                      style='Custom.TLabel').pack(anchor=W)
                        ttk_boot.Label(basic_info_frame, text=f"Genus: {genus if genus else 'Unknown'}",
                                      style='Custom.TLabel').pack(anchor=W)

                        # Special flags
                        flags = []
                        if is_baby:
                            flags.append("Baby Pokemon")
                        if is_legendary:
                            flags.append("Legendary")
                        if is_mythical:
                            flags.append("Mythical")
                        if has_gender_differences:
                            flags.append("Has Gender Differences")

                        if flags:
                            ttk_boot.Label(basic_info_frame, text=f"Special: {', '.join(flags)}",
                                          style='Custom.TLabel').pack(anchor=W)

                    # Get compatible breeding Pokemon (same egg groups)
                    if egg_groups:
                        compatible_frame = ttk_boot.LabelFrame(breeding_frame, text="Compatible Breeding Partners", padding=10, style='Custom.TLabelframe')
                        compatible_frame.pack(fill=X, pady=(10, 0))

                        # Build query for compatible Pokemon
                        egg_group_conditions = []
                        params = []

                        for egg_group in egg_groups:
                            # Each egg group needs 4 LIKE conditions to match different JSON formats
                            egg_group_conditions.append("(egg_groups LIKE ? OR egg_groups LIKE ? OR egg_groups LIKE ? OR egg_groups LIKE ?)")
                            params.extend([f'["{egg_group}"]', f'["{egg_group}",%', f'%,"{egg_group}"]', f'%,"{egg_group}",%'])

                        query = f"""
                            SELECT name FROM New_Pokemon_Breeding_Data
                            WHERE id != ? AND ({' OR '.join(egg_group_conditions)})
                            ORDER BY name
                            LIMIT 20
                        """
                        params.insert(0, pokemon_id)

                        cursor.execute(query, params)
                        compatible_pokemon = cursor.fetchall()

                        if compatible_pokemon:
                            # Group into rows of 4 for better display
                            pokemon_names = [p[0] for p in compatible_pokemon]

                            # Create rows
                            for i in range(0, len(pokemon_names), 4):
                                row_frame = ttk_boot.Frame(compatible_frame, style='Custom.TFrame')
                                row_frame.pack(fill=X, pady=1)

                                for j in range(4):
                                    if i + j < len(pokemon_names):
                                        pokemon_name = pokemon_names[i + j]
                                        ttk_boot.Label(row_frame, text=pokemon_name.title(),
                                                      font=('Arial', 8), style='Custom.TLabel',
                                                      width=15, anchor=W).grid(row=0, column=j, padx=2)
                        else:
                            ttk_boot.Label(compatible_frame, text="No compatible breeding partners found",
                                          style='Custom.TLabel').pack(anchor=W)

                    conn.close()

                except Exception as e:
                    print(f"Error loading additional breeding data: {e}")
                    import traceback
                    traceback.print_exc()

        # Personality information
        if personality_data:
            personality_frame = ttk_boot.LabelFrame(scrollable_frame.scrollable_frame, text="Possible Characteristics", padding=10, style='Custom.TLabelframe')
            personality_frame.pack(fill=X, pady=(10, 0))

            ttk_boot.Label(personality_frame, text="Based on highest stat, this Pokemon may have:",
                          style='Custom.TLabel').pack(anchor=W, pady=(0, 5))

            for description, gene_modulo, stat in personality_data[:3]:
                ttk_boot.Label(personality_frame, text=f"• {description}",
                              style='Custom.TLabel').pack(anchor=W)
        else:
            personality_frame = ttk_boot.LabelFrame(scrollable_frame.scrollable_frame, text="Possible Characteristics", padding=10, style='Custom.TLabelframe')
            personality_frame.pack(fill=X, pady=(10, 0))
            ttk_boot.Label(personality_frame, text="No personality data available",
                          style='Custom.TLabel').pack(anchor=W)

    def display_moves_info(self, level_up_moves_data, tutor_moves_data, tm_hm_moves_data, egg_moves_data):
        """Display moves information in the Moves tab"""
        # Clear existing content in moves display frame
        for widget in self.moves_display_frame.winfo_children():
            widget.destroy()

        # Store data for filtering
        self.current_moves_data = level_up_moves_data
        self.current_tutor_moves_data = tutor_moves_data
        self.current_machines_data = tm_hm_moves_data
        self.current_egg_moves_data = egg_moves_data

        # Initialize version variable if not exists
        if not hasattr(self, 'version_var'):
            self.version_var = ttk_boot.StringVar(value="All Versions")

        # Create initial display with all versions
        self.create_moves_display(level_up_moves_data, tutor_moves_data, tm_hm_moves_data, egg_moves_data,
                               self.moves_display_frame, "All Versions")

    def filter_moves_by_version(self):
        """Filter moves by selected version"""
        selected_version = self.version_var.get()
        self.create_moves_display(self.current_moves_data, self.current_tutor_moves_data, self.current_machines_data, self.current_egg_moves_data, self.moves_display_frame, selected_version)

    def create_moves_display(self, level_up_moves_data, tutor_moves_data, tm_hm_moves_data, egg_moves_data, parent_frame, selected_version):
        """Create the moves display with filtering"""
        # Clear all content and recreate everything
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # Create scrollable frame within the parent
        scrollable_frame = ScrollableFrame(parent_frame, style='Custom.TFrame')
        scrollable_frame.pack(fill=BOTH, expand=True)
        content_frame = scrollable_frame.scrollable_frame

        # Recreate version selection dropdown
        version_frame = ttk_boot.Frame(content_frame, style='Custom.TFrame')
        version_frame.pack(fill=X, pady=(0, 10))

        ttk_boot.Label(version_frame, text="Filter by Version:", font=('Arial', 10, 'bold'),
                      style='Custom.TLabel').pack(side=LEFT, padx=(0, 10))

        # Get unique versions from all moves data
        all_versions = set()
        for move_name, level, method, version in level_up_moves_data:
            if version:
                all_versions.add(version)
        for move_name, level, method, version in tutor_moves_data:
            if version:
                all_versions.add(version)
        for move_name, move_type, move_power, move_pp, version in egg_moves_data:
            if version:
                all_versions.add(version)
        for move_name, machine_id, item_name, version in tm_hm_moves_data:
            if version:
                all_versions.add(version)

        version_list = sorted(list(all_versions))
        version_list.insert(0, "All Versions")  # Always include "All Versions" at the beginning

        self.version_var.set(selected_version)  # Update existing variable
        version_combo = ttk_boot.Combobox(version_frame, textvariable=self.version_var,
                                        values=version_list, state='readonly',
                                        width=20, style='Custom.TCombobox')
        version_combo.pack(side=LEFT)
        
        # Bind the event after setting up the combobox to avoid triggering on initial setup
        def on_version_selected(event):
            self.filter_moves_by_version()
        
        version_combo.bind('<<ComboboxSelected>>', on_version_selected)

        # Filter data by version
        if selected_version != "All Versions":
            filtered_moves = [(name, lvl, method, ver) for name, lvl, method, ver in level_up_moves_data
                            if ver and ver == selected_version]
            filtered_tutor_moves = [(name, lvl, method, ver) for name, lvl, method, ver in tutor_moves_data
                                  if ver and ver == selected_version]
            filtered_egg_moves = [(name, typ, pwr, pp, ver) for name, typ, pwr, pp, ver in egg_moves_data
                                if ver and ver == selected_version]
            filtered_tm_hm_moves = [(name, mid, item, ver) for name, mid, item, ver in tm_hm_moves_data
                                  if ver and ver == selected_version]
        else:
            filtered_moves = level_up_moves_data
            filtered_tutor_moves = tutor_moves_data
            filtered_egg_moves = egg_moves_data
            filtered_tm_hm_moves = tm_hm_moves_data

        # Level up moves section
        if filtered_moves:
            moves_frame = ttk_boot.LabelFrame(content_frame, text="Level Up Moves", padding=10, style='Custom.TLabelframe')
            moves_frame.pack(fill=X, pady=(10, 10))

            # Create treeview for moves
            columns = ('Level', 'Move', 'Method', 'Version')
            tree = ttk.Treeview(moves_frame, columns=columns, show='headings', height=min(12, len(filtered_moves)), style='Custom.Treeview')

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            # Add moves data
            for move_name, level, method, version in filtered_moves:
                tree.insert('', 'end', values=(level, move_name, method, version or "N/A"))

            # Bind selection event to show move details
            tree.bind('<<TreeviewSelect>>', lambda e, tree=tree: self.on_move_selected(tree, 'level_up'))
            tree.pack(fill=X)

        # Tutor moves section
        if filtered_tutor_moves:
            tutor_frame = ttk_boot.LabelFrame(content_frame, text="Tutor Moves", padding=10, style='Custom.TLabelframe')
            tutor_frame.pack(fill=X, pady=(0, 10))

            # Create treeview for tutor moves
            columns = ('Move', 'Method', 'Version')
            tree = ttk.Treeview(tutor_frame, columns=columns, show='headings', height=min(8, len(filtered_tutor_moves)), style='Custom.Treeview')

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=120)

            # Add tutor moves data
            for move_name, level, method, version in filtered_tutor_moves:
                tree.insert('', 'end', values=(move_name, method.title(), version or "N/A"))

            # Bind selection event to show move details
            tree.bind('<<TreeviewSelect>>', lambda e, tree=tree: self.on_move_selected(tree, 'tutor'))
            tree.pack(fill=X)

        # Egg moves section
        if filtered_egg_moves:
            egg_frame = ttk_boot.LabelFrame(content_frame, text="Egg Moves", padding=10, style='Custom.TLabelframe')
            egg_frame.pack(fill=X, pady=(0, 10))

            # Create treeview for egg moves
            columns = ('Move', 'Type', 'Power', 'PP', 'Version')
            tree = ttk.Treeview(egg_frame, columns=columns, show='headings', height=min(8, len(filtered_egg_moves)), style='Custom.Treeview')

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            # Add egg moves data
            for move_name, move_type, move_power, move_pp, version in filtered_egg_moves:
                power_text = str(move_power) if move_power else "—"
                pp_text = str(move_pp) if move_pp else "—"
                tree.insert('', 'end', values=(move_name, move_type.title(), power_text, pp_text, version or "N/A"))

            # Bind selection event to show move details
            tree.bind('<<TreeviewSelect>>', lambda e, tree=tree: self.on_move_selected(tree, 'egg'))
            tree.pack(fill=X)

        # TM/HM moves section
        if filtered_tm_hm_moves:
            machines_frame = ttk_boot.LabelFrame(content_frame, text="TM/HM Moves", padding=10, style='Custom.TLabelframe')
            machines_frame.pack(fill=X, pady=(0, 10))

            # Create treeview for TM/HM moves
            columns = ('TM/HM', 'Move', 'Item', 'Version')
            tree = ttk.Treeview(machines_frame, columns=columns, show='headings', height=6, style='Custom.Treeview')

            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)

            # Add TM/HM moves data
            for move_name, machine_id, item_name, version_group_name in filtered_tm_hm_moves[:15]:  # Limit to first 15
                tm_hm_text = f"{machine_id:02d}" if machine_id else "??"
                tree.insert('', 'end', values=(tm_hm_text, move_name, item_name.upper(), version_group_name or "N/A"))

            # Bind selection event to show move details
            tree.bind('<<TreeviewSelect>>', lambda e, tree=tree: self.on_move_selected(tree, 'tm_hm'))
            tree.pack(fill=X)

    def on_move_selected(self, tree, move_type):
        """Handle move selection from treeview"""
        selection = tree.selection()
        if selection:
            item = tree.item(selection[0])
            values = item['values']
            
            # Extract move name based on move type
            if move_type == 'level_up':
                move_name = values[1]  # Level, Move, Method, Version
            elif move_type == 'tutor':
                move_name = values[0]  # Move, Method, Version
            elif move_type == 'egg':
                move_name = values[0]  # Move, Type, Power, PP, Version
            elif move_type == 'tm_hm':
                move_name = values[1]  # TM/HM, Move, Item, Version
            
            if move_name:
                self.display_move_details(move_name)

    def display_move_details(self, move_name):
        """Display detailed information for the selected move"""
        # Clear existing content
        for widget in self.move_details_frame.winfo_children():
            widget.destroy()

        try:
            # Connect to database
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()

            # Get move details from New_Pokemon_Moves table
            cursor.execute("""
                SELECT name, accuracy, pp, priority, power, damage_class, effect_entries, type_name
                FROM New_Pokemon_Moves
                WHERE name = ?
            """, (move_name,))
            
            move_data = cursor.fetchone()
            
            # Get additional move data from New_Pokemon_Move_Learning_Data table
            cursor.execute("""
                SELECT move_effect
                FROM New_Pokemon_Move_Learning_Data
                WHERE move_name = ?
                LIMIT 1
            """, (move_name,))
            
            learning_data = cursor.fetchone()
            move_effect = learning_data[0] if learning_data and learning_data[0] else None
            
            # Get contest data from New_Pokemon_Contest_Data table
            cursor.execute("""
                SELECT contest_type, contest_effect_appeal, contest_effect_jam,
                       contest_effect_description, contest_effect_flavor_text,
                       super_contest_effect_appeal, super_contest_effect_flavor_text
                FROM New_Pokemon_Contest_Data
                WHERE move_name = ?
            """, (move_name,))
            
            contest_data = cursor.fetchone()
            
            if move_data:
                name, accuracy, pp, priority, power, damage_class, effect_entries, type_name = move_data
                
                # Create scrollable frame for move details
                scrollable_frame = ScrollableFrame(self.move_details_frame, style='Custom.TFrame')
                scrollable_frame.pack(fill=BOTH, expand=True)
                content_frame = scrollable_frame.scrollable_frame
                
                # Move name
                ttk_boot.Label(content_frame, text=move_name.title(), 
                              font=('Arial', 18, 'bold'), style='Custom.TLabel').pack(pady=(0, 10))
                
                # Basic stats frame
                stats_frame = ttk_boot.LabelFrame(content_frame, text="Move Stats", padding=10, style='Custom.TLabelframe')
                stats_frame.pack(fill=X, pady=(0, 10))
                
                # Create grid layout for stats
                stat_grid = ttk_boot.Frame(stats_frame, style='Custom.TFrame')
                stat_grid.pack(fill=X)
                
                # PP
                ttk_boot.Label(stat_grid, text="PP:", font=('Arial', 10, 'bold'), style='Custom.TLabel').grid(row=0, column=0, sticky=W, padx=(0, 5))
                ttk_boot.Label(stat_grid, text=str(pp) if pp else "—", style='Custom.TLabel').grid(row=0, column=1, sticky=W, padx=(0, 20))
                
                # Power
                ttk_boot.Label(stat_grid, text="Power:", font=('Arial', 10, 'bold'), style='Custom.TLabel').grid(row=0, column=2, sticky=W, padx=(0, 5))
                ttk_boot.Label(stat_grid, text=str(power) if power else "—", style='Custom.TLabel').grid(row=0, column=3, sticky=W, padx=(0, 20))
                
                # Accuracy
                ttk_boot.Label(stat_grid, text="Accuracy:", font=('Arial', 10, 'bold'), style='Custom.TLabel').grid(row=1, column=0, sticky=W, padx=(0, 5))
                ttk_boot.Label(stat_grid, text=f"{accuracy}%" if accuracy else "—", style='Custom.TLabel').grid(row=1, column=1, sticky=W, padx=(0, 20))
                
                # Priority
                ttk_boot.Label(stat_grid, text="Priority:", font=('Arial', 10, 'bold'), style='Custom.TLabel').grid(row=1, column=2, sticky=W, padx=(0, 5))
                ttk_boot.Label(stat_grid, text=str(priority) if priority else "0", style='Custom.TLabel').grid(row=1, column=3, sticky=W)
                
                # Damage class with icon
                ttk_boot.Label(stat_grid, text="Damage Class:", font=('Arial', 10, 'bold'), style='Custom.TLabel').grid(row=2, column=0, sticky=W, padx=(0, 5), pady=(10, 0))
                
                damage_class_frame = ttk_boot.Frame(stat_grid, style='Custom.TFrame')
                damage_class_frame.grid(row=2, column=1, sticky=W, pady=(10, 0))
                
                # Load damage class icon
                icon_path = f"images/Types/{damage_class.lower()}.png"
                try:
                    if os.path.exists(icon_path):
                        icon_image = Image.open(icon_path)
                        icon_image = icon_image.resize((20, 20), Image.Resampling.LANCZOS)
                        icon_photo = ImageTk.PhotoImage(icon_image)
                        icon_label = ttk_boot.Label(damage_class_frame, image=icon_photo, style='Custom.TLabel')
                        icon_label.image = icon_photo  # Keep reference
                        icon_label.pack(side=LEFT)
                except Exception as e:
                    print(f"Could not load damage class icon: {e}")
                
                ttk_boot.Label(damage_class_frame, text=damage_class.title(), style='Custom.TLabel').pack(side=LEFT, padx=(5, 0))
                
                # Add newline after Damage Class
                ttk_boot.Label(stat_grid, text="", style='Custom.TLabel').grid(row=3, column=0, pady=(5, 0))
                
                # Type with icon
                ttk_boot.Label(stat_grid, text="Type:", font=('Arial', 10, 'bold'), style='Custom.TLabel').grid(row=4, column=0, sticky=W, padx=(0, 5), pady=(10, 0))
                
                type_frame = ttk_boot.Frame(stat_grid, style='Custom.TFrame')
                type_frame.grid(row=4, column=1, sticky=W, pady=(10, 0))
                
                # Load type icon
                if type_name:
                    type_icon_path = f"images/Types/{type_name.lower()}.png"
                    try:
                        if os.path.exists(type_icon_path):
                            type_icon_image = Image.open(type_icon_path)
                            type_icon_image = type_icon_image.resize((20, 20), Image.Resampling.LANCZOS)
                            type_icon_photo = ImageTk.PhotoImage(type_icon_image)
                            type_icon_label = ttk_boot.Label(type_frame, image=type_icon_photo, style='Custom.TLabel')
                            type_icon_label.image = type_icon_photo  # Keep reference
                            type_icon_label.pack(side=LEFT)
                    except Exception as e:
                        print(f"Could not load type icon: {e}")
                
                ttk_boot.Label(type_frame, text=type_name.title() if type_name else "—", style='Custom.TLabel').pack(side=LEFT, padx=(5, 0))
                
                # Effect/Flavor text from both tables
                effects_to_display = []
                
                # Effect from New_Pokemon_Moves table
                if effect_entries:
                    try:
                        effects = json.loads(effect_entries)
                        if effects:
                            # Get the first English effect
                            for effect in effects:
                                if effect.get('language', {}).get('name') == 'en':
                                    english_effect = effect.get('effect', '')
                                    if english_effect:
                                        effects_to_display.append(("Move Effect (API)", english_effect))
                                    break
                    except:
                        pass
                
                # Effect from New_Pokemon_Move_Learning_Data table
                if move_effect:
                    effects_to_display.append(("Move Effect (Database)", move_effect))
                
                # Display all effects
                if effects_to_display:
                    for i, (effect_title, effect_text) in enumerate(effects_to_display):
                        effect_frame = ttk_boot.LabelFrame(content_frame, text=effect_title, padding=10, style='Custom.TLabelframe')
                        effect_frame.pack(fill=X, pady=(10, 10) if i == 0 else (0, 10))
                        
                        effect_label = ttk_boot.Label(effect_frame, text=effect_text, 
                                                    wraplength=400, justify=LEFT, style='Custom.TLabel')
                        effect_label.pack(anchor=W)
                
                # Contest data from New_Pokemon_Contest_Data table
                if contest_data:
                    contest_type, contest_appeal, contest_jam, effect_description, effect_flavor_text, super_appeal, super_flavor_text = contest_data
                    
                    contest_frame = ttk_boot.LabelFrame(content_frame, text="Contest Information", padding=10, style='Custom.TLabelframe')
                    contest_frame.pack(fill=X, pady=(0, 10))
                    
                    # Contest type
                    if contest_type:
                        ttk_boot.Label(contest_frame, text=f"Contest Type: {contest_type.title()}", 
                                     font=('Arial', 10, 'bold'), style='Custom.TLabel').pack(anchor=W, pady=(0, 5))
                    
                    # Contest stats
                    if contest_appeal is not None or contest_jam is not None:
                        stats_text = ""
                        if contest_appeal is not None:
                            stats_text += f"Appeal: {contest_appeal}"
                        if contest_jam is not None:
                            if stats_text:
                                stats_text += " | "
                            stats_text += f"Jam: {contest_jam}"
                        ttk_boot.Label(contest_frame, text=stats_text, style='Custom.TLabel').pack(anchor=W)
                    
                    # Effect description
                    if effect_description:
                        ttk_boot.Label(contest_frame, text=f"Effect: {effect_description}", 
                                     style='Custom.TLabel').pack(anchor=W, pady=(5, 0))
                    
                    # Effect flavor text
                    if effect_flavor_text:
                        ttk_boot.Label(contest_frame, text=f"Flavor: {effect_flavor_text}", 
                                     style='Custom.TLabel').pack(anchor=W, pady=(5, 0))
                    
                    # Super contest info
                    if super_appeal is not None or super_flavor_text:
                        ttk_boot.Label(contest_frame, text="Super Contest:", 
                                     font=('Arial', 10, 'bold'), style='Custom.TLabel').pack(anchor=W, pady=(10, 0))
                        
                        if super_appeal is not None:
                            ttk_boot.Label(contest_frame, text=f"Appeal: {super_appeal}", 
                                         style='Custom.TLabel').pack(anchor=W)
                        
                        if super_flavor_text:
                            ttk_boot.Label(contest_frame, text=f"Flavor: {super_flavor_text}", 
                                         style='Custom.TLabel').pack(anchor=W)
                
            else:
                # Move not found in detailed database
                ttk_boot.Label(scrollable_frame.scrollable_frame, text=f"Move details not available for {move_name}", 
                              font=('Arial', 12), style='Custom.TLabel').pack(expand=True)
            
            conn.close()
            
        except Exception as e:
            print(f"Error displaying move details: {e}")
            ttk_boot.Label(self.move_details_frame, text=f"Error loading move details: {str(e)}", 
                          font=('Arial', 12), style='Custom.TLabel').pack(expand=True)

    def display_evolution_info(self, evolution_data):
        """Display evolution information in the Evolution tab"""
        # Clear existing content
        for widget in self.evolution_tab.winfo_children():
            widget.destroy()

        # Create scrollable frame
        scrollable_frame = ScrollableFrame(self.evolution_tab, style='Custom.TFrame')
        scrollable_frame.pack(fill=BOTH, expand=True)

        if evolution_data:
            evolution_frame = ttk_boot.LabelFrame(scrollable_frame.scrollable_frame, text="Evolution Chain", padding=10, style='Custom.TLabelframe')
            evolution_frame.pack(fill=X, pady=(0, 10))

            ttk_boot.Label(evolution_frame, text="Evolution information will be displayed here",
                          style='Custom.TLabel').pack(anchor=W)
        else:
            ttk_boot.Label(scrollable_frame.scrollable_frame, text="No evolution data available",
                          style='Custom.TLabel').pack(anchor=W)

    def display_contest_info(self, contest_data):
        """Display contest information in the Contest tab"""
        # Clear existing content
        for widget in self.contest_tab.winfo_children():
            widget.destroy()

        # Create scrollable frame
        scrollable_frame = ScrollableFrame(self.contest_tab, style='Custom.TFrame')
        scrollable_frame.pack(fill=BOTH, expand=True)

        # Contest information
        if contest_data:
            contest_frame = ttk_boot.LabelFrame(scrollable_frame.scrollable_frame, text="Contest Information", padding=10, style='Custom.TLabelframe')
            contest_frame.pack(fill=X, pady=(0, 10))

            ttk_boot.Label(contest_frame, text="This Pokemon has contest moves available!",
                          style='Custom.TLabel').pack(anchor=W)

            # Show contest types available
            contest_types = set()
            for contest_type, appeal, jam, flavor, super_appeal, super_flavor in contest_data:
                if contest_type:
                    contest_types.add(contest_type)

            if contest_types:
                ttk_boot.Label(contest_frame, text=f"Contest Types: {', '.join(contest_types)}",
                              style='Custom.TLabel').pack(anchor=W)
        else:
            ttk_boot.Label(scrollable_frame.scrollable_frame, text="No contest data available",
                          style='Custom.TLabel').pack(anchor=W)



    def display_type_badge(self, parent, type_name):
        """Display a type badge with icon"""
        if not type_name:
            return

        badge_frame = ttk_boot.Frame(parent, style='Custom.TFrame')
        badge_frame.pack(side=LEFT, padx=0, pady=0)
        
        # Type icon
        if type_name.lower() in self.type_icons:
            icon_label = ttk_boot.Label(badge_frame, image=self.type_icons[type_name.lower()],
                                      style='Custom.TLabel')
            icon_label.pack(side=LEFT, padx=0, pady=0)

        # Type text
        ttk_boot.Label(badge_frame, text=type_name.title(), font=('Arial', 9, 'bold'),
                      style='Custom.TLabel').pack(side=LEFT, padx=0, pady=0)

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function to run the Pokedex X application"""
    app = PokedexXApp()
    app.run()

if __name__ == "__main__":
    main()
