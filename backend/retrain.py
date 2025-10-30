import joblib
import json

# Load the pickled model
model = joblib.load('demandforecastingmodel.pkl')

# Try to convert to text manually
output_text = ""

# Get all attributes safely
for attr in dir(model):
    if not attr.startswith("_"):
        try:
            value = getattr(model, attr)
            output_text += f"{attr}: {str(value)[:5000]}\n\n"  # Limit to first 5000 chars
        except Exception as e:
            output_text += f"{attr}: <Error reading - {e}>\n\n"

# Save as demand_model.txt
with open('demand_model.txt', 'w', encoding='utf-8') as f:
    f.write(output_text)

print("Model details successfully exported to demand_model.txt")
