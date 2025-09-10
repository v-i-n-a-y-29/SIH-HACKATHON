# test_combined_plot.py
import os
import matplotlib.pyplot as plt
from services.forecast import plot_combined_depth_parameters, plot_combined_depth_parameters_plotly

# Path to the data file
DATA_FOLDER = "data"
data_file = os.path.join(DATA_FOLDER, "MergedData.csv")

def test_matplotlib_combined_plot():
    """Test the static matplotlib combined plot function"""
    print("Testing static combined plot...")
    output_path = os.path.join(DATA_FOLDER, "static_combined_plot.png")
    result = plot_combined_depth_parameters(data_file, output_path)
    
    if result:
        print(f"✅ Static combined plot generated successfully at: {result}")
    else:
        print("❌ Failed to generate static combined plot")

def test_plotly_combined_plot():
    """Test the interactive Plotly combined plot function"""
    print("Testing interactive Plotly combined plot...")
    fig = plot_combined_depth_parameters_plotly(data_file)
    
    if fig:
        output_path = os.path.join(DATA_FOLDER, "interactive_combined_plot.html")
        fig.write_html(output_path)
        print(f"✅ Interactive combined plot generated successfully at: {output_path}")
    else:
        print("❌ Failed to generate interactive combined plot")

if __name__ == "__main__":
    # Check if data file exists
    if not os.path.exists(data_file):
        print(f"❌ Data file not found at: {data_file}")
        print("Please make sure the data file exists before running this test.")
    else:
        print(f"Found data file: {data_file}")
        
        # Run the tests
        test_matplotlib_combined_plot()
        test_plotly_combined_plot()
        
        print("Tests completed.")
