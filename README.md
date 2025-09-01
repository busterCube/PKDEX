<center><img src="Images/banner/PKDEX_banner.png" alt="banner" width="200" height="200"></center>


# PKDEX - Enhanced Pokedex Application

A comprehensive, feature-rich Pokedex application built with Python and ttkbootstrap, featuring advanced Pokemon data visualization, evolution chains, move databases, and Gender and Breeding data.

## 🌟 Features

### Core Functionality
- **Complete Pokemon Database** - Access to all Pokemon with detailed information
- **Advanced Search & Filtering** - Search by name, number, type, and stats
- **Interactive Pokemon List** - Browse through all Pokemon with real-time filtering
- **Detailed Pokemon Profiles** - Comprehensive information for each Pokemon

### Visual Features
- **High-Quality Pokemon Images** - Official artwork and sprites
- **Interactive Radar Charts** - Visual representation of Pokemon stats
- **Type Effectiveness Display** - Real-time type weaknesses and resistances
- **Evolution Chain Visualization** - Beautiful tree-style evolution displays

### Data Categories
- **Basic Information** - Name, number, species, height, weight
- **Stats & Abilities** - Base stats, abilities with descriptions
- **Moves Database** - Level-up, TM/HM, Tutor, and Egg moves with version filtering
- **Evolution Chains** - Complete evolution trees with requirements
- **Breeding Information** - Egg groups, compatibility, breeding mechanics
- **Location Data** - Where to find Pokemon in different games
- **Characteristics** - Personality traits and nature information

### Advanced Features
- **Move Filtering** - Filter moves by game version and learn method
- **Type Analysis** - Comprehensive type effectiveness calculations
- **Gender Information** - Visual gender ratios with icons

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 512MB minimum (1GB recommended)
- **Storage**: 500MB for application and data

### Python Dependencies

The application requires the following Python packages:

```bash
pip install ttkbootstrap
pip install Pillow
pip install requests
pip install matplotlib
pip install numpy
```

#### Individual Installation Commands:

```bash
# Core UI framework
pip install ttkbootstrap

# Image processing
pip install Pillow

# HTTP requests for data fetching
pip install requests

# Charts and data visualization
pip install matplotlib

# Numerical computations
pip install numpy
```

### Database Requirements
- **SQLite3** (included with Python)
- **Pokemon.db** - Download before running the application: https://gofile.io/d/ErILTY

## 🚀 Installation

1. **Clone or Download** the repository
2. **Install Python Dependencies**:
   ```bash
   pip install ttkbootstrap Pillow requests matplotlib numpy
   ```
3. **Ensure Database File** is present:
   - `Pokemon.db` should be in the same directory as `Pokedex_X.py`
4. **Run the Application**:
   ```bash
   python Pokedex_X.py
   ```

## 🎮 How to Use

### Getting Started
1. **Launch the Application**:
   ```bash
   python Pokedex_X.py
   ```

2. **Browse Pokemon**:
   - Use the **Pokemon List** on the left to browse all Pokemon
   - Click on any Pokemon to view detailed information

### Navigation
- **Tabs**: Switch between different information categories:
  - **Basic Info**: Overview, stats, and radar chart
  - **Evolution Chain**: Evolution tree and requirements
  - **Characteristics**: Abilities, breeding, and personality
  - **Moves**: All moves with filtering options

### Search & Filtering
- **Name Search**: Type in the name field to search by Pokemon name
- **Number Search**: Search by Pokedex number
- **Type Filter**: Filter Pokemon by their types
- **Advanced Filters**: Use stat filters for more specific searches

### Moves Tab Features
- **Version Filtering**: Select specific game versions to see relevant moves
- **Move Categories**:
  - **Level Up Moves**: Moves learned by leveling up
  - **TM/HM Moves**: Technical Machines and Hidden Machines
  - **Tutor Moves**: Moves taught by Move Tutors
  - **Egg Moves**: Moves that can be inherited from breeding


## 🎨 Pokemon Types

The application supports all Pokemon types with beautiful icons:

| Type | Icon | Description |
|------|------|-------------|
| <img src="Images/Types/normal.png" alt="type" width="64" height="64"> **Normal** | Physical attacks, few weaknesses |
| <img src="Images/Types/fire.png" alt="type" width="64" height="64"> **Fire** | Strong against Grass, weak to Water |
| <img src="Images/Types/water.png" alt="type" width="64" height="64"> **Water** | Strong against Fire, weak to Electric |
| <img src="Images/Types/electric.png" alt="type" width="64" height="64"> **Electric** | Strong against Water, weak to Ground |
| <img src="Images/Types/grass.png" alt="type" width="64" height="64"> **Grass** | Strong against Water, weak to Fire |
| <img src="Images/Types/ice.png" alt="type" width="64" height="64"> **Ice** | Strong against Dragon, weak to Fire |
| <img src="Images/Types/fighting.png" alt="type" width="64" height="64"> **Fighting** | Strong against Normal, weak to Flying |
| <img src="Images/Types/poison.png" alt="type" width="64" height="64"> **Poison** | Strong against Grass, weak to Ground |
| <img src="Images/Types/ground.png" alt="type" width="64" height="64"> **Ground** | Strong against Electric, weak to Water |
| <img src="Images/Types/flying.png" alt="type" width="64" height="64"> **Flying** | Strong against Fighting, weak to Electric |
| <img src="Images/Types/psychic.png" alt="type" width="64" height="64"> **Psychic** | Strong against Fighting, weak to Bug |
| <img src="Images/Types/bug.png" alt="type" width="64" height="64"> **Bug** | Strong against Grass, weak to Fire |
| <img src="Images/Types/rock.png" alt="type" width="64" height="64"> **Rock** | Strong against Flying, weak to Water |
| <img src="Images/Types/ghost.png" alt="type" width="64" height="64"> **Ghost** | Strong against Psychic, weak to Ghost |
| <img src="Images/Types/dragon.png" alt="type" width="64" height="64"> **Dragon** | Strong against Dragon, weak to Ice |
| <img src="Images/Types/dark.png" alt="type" width="64" height="64"> **Dark** | Strong against Psychic, weak to Fighting |
| <img src="Images/Types/steel.png" alt="type" width="64" height="64"> **Steel** | Strong against Ice, weak to Fire |
| <img src="Images/Types/fairy.png" alt="type" width="64" height="64"> **Fairy** | Strong against Dragon, weak to Poison |

## ⚔️ Move Categories

Moves are categorized by their type and damage class:

| Category | Icon | Description |
|----------|------|-------------|
| <img src="Images/Types/physical.png" alt="type" width="64" height="64"> **Physical** | Physical attacks using Attack stat |
| <img src="Images/Types/special.png" alt="type" width="64" height="64"> **Special** | Special attacks using Special Attack stat |
| <img src="Images/Types/status.png" alt="type" width="64" height="64"> **Status** | Non-damaging moves that affect stats/conditions |

## 👥 Gender Information

Pokemon gender ratios are displayed with intuitive icons:

| Gender | Icon | Description |
|--------|------|-------------|
| <img src="Images/Types/male.png" alt="type" width="64" height="64"> **Male** | Male-only or male-biased Pokemon |
| <img src="Images/Types/female.png" alt="type" width="64" height="64"> **Female** | Female-only or female-biased Pokemon |
| <img src="Images/Types/genderless.png" alt="type" width="64" height="64"> **Genderless** | Pokemon without gender |

## 🛠️ Troubleshooting

### Common Issues

**Application won't start:**
- Ensure all Python dependencies are installed
- Check that `Pokemon.db` file exists in the same directory
- Verify Python version is 3.8 or higher

**Images not loading:**
- Check internet connection for online images
- Verify image files exist in `Images/` directory
- Some images may be missing from the database

**Performance issues:**
- Close other applications to free up RAM
- The application loads all Pokemon data on startup
- Consider using the search filters to reduce displayed data

**Database errors:**
- Ensure `Pokemon.db` is not corrupted
- Check file permissions
- Try running as administrator (Windows)

### Getting Help
- Check the console output for error messages
- Verify all required files are present
- Ensure Python path includes the application directory

## 📊 Data Structure

The application uses a comprehensive SQLite database (`Pokemon.db`) containing:

- **Pokemon Data**: Basic information, stats, abilities
- **Move Data**: All moves with type, power, accuracy, PP
- **Evolution Data**: Evolution chains and requirements
- **Type Data**: Type effectiveness and weaknesses
- **Location Data**: Where to find Pokemon in different games
- **Image Data**: URLs and file paths for Pokemon images
- **Breeding Data**: Egg groups, compatibility, breeding mechanics

## 🔧 Configuration

### Customizing Colors
The application uses a custom theme system. Colors can be modified in the `setup_custom_theme()` method:

```python
# Main theme colors
style.configure('Custom.TFrame', background='#8B0000')  # Dark red
style.configure('ChartStats.TLabelframe', background='#000080')  # Navy blue
```

### Database Configuration
- Database file: `Pokemon.db`
- Connection: Automatic on startup
- Schema: Pre-defined SQLite tables

## 📈 Performance Notes

- **Startup Time**: Initial load may take a few seconds due to data processing
- **Memory Usage**: ~100-200MB depending on system and data loaded
- **Image Loading**: Images are loaded asynchronously to prevent UI freezing
- **Search Performance**: Real-time filtering is optimized for large datasets

## 🎯 Advanced Features

### Type Effectiveness Calculations
- Visual display of weaknesses and resistances
- Support for dual-type Pokemon

### Evolution Requirements
- Detailed evolution conditions
- Level requirements, items needed
- Time-based and location-based evolutions

### Move Learning Methods
- Level-up moves with level requirements
- TM/HM moves with item locations
- Tutor moves with location information
- Egg moves with breeding requirements

## 📄 Terms of Use

This application is a fan-made project intended for educational and entertainment purposes only. It is not affiliated with, endorsed by, or sponsored by Nintendo, Game Freak, or The Pokémon Company.
All trademarks, characters, names, images, and related content associated with Pokémon are the intellectual property of their respective owners, including Nintendo, Game Freak, and The Pokémon Company. No copyright infringement is intended.
By using this application, you acknowledge and agree that:
- You will not use this app for commercial purposes.
- You understand that all Pokémon-related content is owned by its original creators.
- You indemnify and hold harmless the developers of this app from any claims, liabilities, or damages arising from misuse or misrepresentation of the content herein.

## 📚 Data Sources Used

This application utilizes publicly available Pokémon data sourced from the following platforms:
- PokeAPI – A free, open-source RESTful API providing structured data on Pokémon species, abilities, moves, and more.
- Pokémon Database – A fan-maintained resource offering detailed Pokédex entries, evolution chains, type charts, and game mechanics.
- Pokémon.com – The official Pokémon website, used for referencing canonical names, artwork, and franchise updates.
- Serebii.net – A comprehensive fan site with up-to-date information on games, anime, events, and Pokédex data across generations.
All Pokémon names, images, and related content remain the intellectual property of Nintendo, Game Freak, and The Pokémon Company. This app is a fan-made project and is not affiliated with or endorsed by any of the aforementioned entities


## 🙏 Acknowledgments

- **PokeAPI** - For providing comprehensive Pokemon data
- **ttkbootstrap** - For the beautiful UI framework
- **Pillow** - For image processing capabilities
- **Matplotlib** - For chart visualization
- **Python Community** - For the amazing ecosystem


**PKDEX** - Your comprehensive Pokemon companion! 🎮✨</content>
<parameter name="filePath">d:\Pokedex\README.md


