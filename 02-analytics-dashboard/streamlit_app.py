# Streamlit Cloud entry point
# This file is required for Streamlit Cloud deployment

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from main import main

if __name__ == "__main__":
    main()