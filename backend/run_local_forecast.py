# backend/run_local_forecast.py
from services.forecast import run_prophet
import os
import matplotlib.pyplot as plt
from PIL import Image
import io

# Get the directory of the current script to ensure correct relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "data", "ocean_dataset_cleaned.csv")
REGRESSOR_PATH = os.path.join(SCRIPT_DIR, "data", "MergedData.csv")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "prophet_30day.csv")
FUTURE_OUTPUT_PATH = os.path.join(SCRIPT_DIR, "data", "future_forecast_90day.csv")

def run_standard_forecast():
    """Run a standard 30-day forecast"""
    print("\n--- Running Standard 30-day Forecast ---")
    out = run_prophet(DATA_PATH, regressor_file_path=REGRESSOR_PATH, future_periods=30, save_csv_path=OUTPUT_PATH)
    print("MAE:", out["mae"])
    print("RMSE:", out["rmse"])
    print("Saved forecast to:", out["forecast_csv"])
    
    # Print depth plot information if available
    if "depth_plots" in out and out["depth_plots"]:
        print("\nDepth plots generated:")
        for param, plot_path in out["depth_plots"].items():
            print(f"- {param}: {plot_path}")
    
    return out

def run_future_forecast():
    """Run an extended 90-day forecast with future trends visualization"""
    print("\n--- Running Extended 90-day Future Forecast ---")
    out = run_prophet(DATA_PATH, regressor_file_path=REGRESSOR_PATH, future_periods=90, save_csv_path=FUTURE_OUTPUT_PATH)
    print("MAE:", out["mae"])
    print("RMSE:", out["rmse"])
    print("Saved future forecast to:", out["forecast_csv"])
    
    # Display future forecast visualization if available
    if "future_forecast_plot" in out and out["future_forecast_plot"] is not None:
        try:
            # Save the future forecast plot to file
            future_plot_path = os.path.join(SCRIPT_DIR, "data", "future_forecast_plot.png")
            with open(future_plot_path, 'wb') as f:
                f.write(out["future_forecast_plot"].getvalue())
            print(f"Saved future forecast visualization to: {future_plot_path}")
            
            # Try to display the image
            try:
                img = Image.open(out["future_forecast_plot"])
                plt.figure(figsize=(12, 8))
                plt.imshow(img)
                plt.axis('off')
                plt.title("Future Forecast Visualization")
                plt.show()
            except Exception as e:
                print(f"Note: Could not display image directly: {e}")
        except Exception as e:
            print(f"Error saving future forecast plot: {e}")
    else:
        print("No future forecast visualization available")
    
    return out

if __name__ == "__main__":
    # Run both forecasts
    standard_out = run_standard_forecast()
    future_out = run_future_forecast()
    
    # Compare metrics
    print("\n--- Forecast Comparison ---")
    print(f"Standard Forecast (30-day) - MAE: {standard_out['mae']:.4f}, RMSE: {standard_out['rmse']:.4f}")
    print(f"Future Forecast (90-day) - MAE: {future_out['mae']:.4f}, RMSE: {future_out['rmse']:.4f}")
    
    print("\nAll forecast outputs are saved in the data directory.")
    print("Run the FastAPI server to access these visualizations through the API endpoints.")
