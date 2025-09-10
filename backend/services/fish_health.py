import pandas as pd
import matplotlib.pyplot as plt
import io

def create_health_check_chart():
    """
    Generates a chart showing the overfishing status.
    """
    # Sample data for demonstration
    data = {
        'Year': range(2000, 2021),
        'Total Stock': [55, 58, 62, 64, 65, 66, 68, 72, 76, 80, 82, 85, 90, 98, 104, 108, 114, 125, 135, 141, 145],
        'Total Catch': [56, 60, 59, 59, 64, 65, 67, 72, 70, 72, 80, 145, 78, 54, 62, 61, 71, 82, 99, 121, 138]
    }
    df = pd.DataFrame(data)

    # Determine bar colors based on overfishing status
    colors = ['red' if df['Total Catch'][i] > df['Total Stock'][i] else 'green' for i in range(len(df))]

    plt.figure(figsize=(12, 7))
    plt.bar(df['Year'] - 0.2, df['Total Stock'], 0.4, label='Total Stock', color='skyblue')
    plt.bar(df['Year'] + 0.2, df['Total Catch'], 0.4, label='Total Catch', color=colors)

    plt.xlabel("Year")
    plt.ylabel("Quantity")
    plt.title("Overfishing Status: Health Check")
    plt.legend()
    
    # Save plot to a memory buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    return buf
