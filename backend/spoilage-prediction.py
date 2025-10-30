{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "_cell_guid": "b1076dfc-b9ad-4769-8c92-a6c4dae69d19",
    "_uuid": "8f2839f25d086af736a60e9eeb907d3b93b6e0e5",
    "execution": {
     "iopub.execute_input": "2025-09-06T18:40:50.420200Z",
     "iopub.status.busy": "2025-09-06T18:40:50.419886Z",
     "iopub.status.idle": "2025-09-06T18:40:57.841959Z",
     "shell.execute_reply": "2025-09-06T18:40:57.840405Z",
     "shell.execute_reply.started": "2025-09-06T18:40:50.420175Z"
    },
    "trusted": True
   },
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import numpy as np\n",
    "from sklearn.model_selection import train_test_split\n",
    "from sklearn.preprocessing import LabelEncoder\n",
    "from sklearn.ensemble import RandomForestClassifier\n",
    "from sklearn.metrics import classification_report, confusion_matrix, accuracy_score\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sns\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:45:08.029030Z",
     "iopub.status.busy": "2025-09-06T18:45:08.028687Z",
     "iopub.status.idle": "2025-09-06T18:45:08.062635Z",
     "shell.execute_reply": "2025-09-06T18:45:08.061409Z",
     "shell.execute_reply.started": "2025-09-06T18:45:08.029003Z"
    },
    "trusted": True
   },
   "outputs": [],
   "source": [
    "df = pd.read_csv(\"C:/Users/Aasavari/Downloads/SmartInventory_dm-main/backend/Grocery_Inventory_and_Sales_Dataset_Cleaned.csv\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:49:25.778290Z",
     "iopub.status.busy": "2025-09-06T18:49:25.777971Z",
     "iopub.status.idle": "2025-09-06T18:49:25.806467Z",
     "shell.execute_reply": "2025-09-06T18:49:25.805525Z",
     "shell.execute_reply.started": "2025-09-06T18:49:25.778268Z"
    },
    "trusted": True
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\Aasavari\\AppData\\Local\\Temp\\ipykernel_14432\\1148311994.py:8: UserWarning: Parsing dates in %d-%m-%Y format when dayfirst=False (the default) was specified. Pass `dayfirst=True` or specify a format to silence this warning.\n",
      "  df['Expiration_Date'] = pd.to_datetime(df['Expiration_Date'], errors='coerce')\n",
      "C:\\Users\\Aasavari\\AppData\\Local\\Temp\\ipykernel_14432\\1148311994.py:9: UserWarning: Parsing dates in %d-%m-%Y format when dayfirst=False (the default) was specified. Pass `dayfirst=True` or specify a format to silence this warning.\n",
      "  df['Date_Received'] = pd.to_datetime(df['Date_Received'], errors='coerce')\n"
     ]
    }
   ],
   "source": [
    "# --- Fix Unit_Price (remove $ and spaces, convert to float) ---\n",
    "df[\"Unit_Price\"] = (\n",
    "    df[\"Unit_Price\"].astype(str)\n",
    "    .str.replace(r\"[^0-9.]\", \"\", regex=True)\n",
    "    .astype(float)\n",
    ")\n",
    "\n",
    "df['Expiration_Date'] = pd.to_datetime(df['Expiration_Date'], errors='coerce')\n",
    "df['Date_Received'] = pd.to_datetime(df['Date_Received'], errors='coerce')\n",
    "\n",
    "# Days remaining until expiry (from today)\n",
    "df['DaysRemaining'] = (df['Expiration_Date'] - pd.Timestamp.today()).dt.days\n",
    "\n",
    "# Average daily sales proxy (avoid divide by zero)\n",
    "df['AvgDailySales'] = df['Sales_Volume'] / (df['DaysRemaining'].replace(0, np.nan))\n",
    "df['AvgDailySales'] = df['AvgDailySales'].fillna(0)\n",
    "\n",
    "# Target: 1 if stock will expire before being sold, else 0\n",
    "df['WillExpire'] = np.where((df['Stock_Quantity'] > df['Sales_Volume']) & (df['DaysRemaining'] <= 0), 1, 0)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:49:31.222821Z",
     "iopub.status.busy": "2025-09-06T18:49:31.222463Z",
     "iopub.status.idle": "2025-09-06T18:49:31.230954Z",
     "shell.execute_reply": "2025-09-06T18:49:31.229533Z",
     "shell.execute_reply.started": "2025-09-06T18:49:31.222796Z"
    },
    "trusted": True
   },
   "outputs": [],
   "source": [
    "features = ['Stock_Quantity', 'Reorder_Level', 'Reorder_Quantity', 'Unit_Price',\n",
    "            'Sales_Volume', 'DaysRemaining', 'AvgDailySales']\n",
    "X = df[features]\n",
    "y = df['WillExpire']\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:49:33.973737Z",
     "iopub.status.busy": "2025-09-06T18:49:33.973415Z",
     "iopub.status.idle": "2025-09-06T18:49:33.988771Z",
     "shell.execute_reply": "2025-09-06T18:49:33.987529Z",
     "shell.execute_reply.started": "2025-09-06T18:49:33.973714Z"
    },
    "trusted": True
   },
   "outputs": [],
   "source": [
    "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:49:37.708680Z",
     "iopub.status.busy": "2025-09-06T18:49:37.708290Z",
     "iopub.status.idle": "2025-09-06T18:49:37.950965Z",
     "shell.execute_reply": "2025-09-06T18:49:37.949721Z",
     "shell.execute_reply.started": "2025-09-06T18:49:37.708652Z"
    },
    "trusted": True
   },
   "outputs": [],
   "source": [
    "model = RandomForestClassifier(random_state=42)\n",
    "model.fit(X_train, y_train)\n",
    "\n",
    "# --- Step 5: Predictions ---\n",
    "y_pred = model.predict(X_test)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:50:32.840189Z",
     "iopub.status.busy": "2025-09-06T18:50:32.839211Z",
     "iopub.status.idle": "2025-09-06T18:50:32.858361Z",
     "shell.execute_reply": "2025-09-06T18:50:32.857146Z",
     "shell.execute_reply.started": "2025-09-06T18:50:32.840155Z"
    },
    "trusted": True
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Accuracy: 0.9595959595959596\n",
      "\n",
      "Classification Report:\n",
      "               precision    recall  f1-score   support\n",
      "\n",
      "           0       0.95      0.97      0.96       108\n",
      "           1       0.97      0.94      0.96        90\n",
      "\n",
      "    accuracy                           0.96       198\n",
      "   macro avg       0.96      0.96      0.96       198\n",
      "weighted avg       0.96      0.96      0.96       198\n",
      "\n"
     ]
    }
   ],
   "source": [
    "print(\"Accuracy:\", accuracy_score(y_test, y_pred))\n",
    "print(\"\\nClassification Report:\\n\", classification_report(y_test, y_pred))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:50:54.699930Z",
     "iopub.status.busy": "2025-09-06T18:50:54.699559Z",
     "iopub.status.idle": "2025-09-06T18:50:54.715208Z",
     "shell.execute_reply": "2025-09-06T18:50:54.714073Z",
     "shell.execute_reply.started": "2025-09-06T18:50:54.699906Z"
    },
    "trusted": True
   },
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "     Actual  Predicted\n",
      "893       0          0\n",
      "110       1          1\n",
      "82        1          1\n",
      "727       1          1\n",
      "186       1          0\n",
      "355       1          1\n",
      "217       0          0\n",
      "451       1          1\n",
      "226       1          0\n",
      "945       0          0\n",
      "370       0          0\n",
      "973       0          0\n",
      "861       1          1\n",
      "616       1          1\n",
      "820       1          1\n",
      "908       0          0\n",
      "928       1          1\n",
      "182       0          0\n",
      "613       0          0\n",
      "446       0          0\n"
     ]
    }
   ],
   "source": [
    "comparison = pd.DataFrame({\"Actual\": y_test, \"Predicted\": y_pred})\n",
    "print(comparison.head(20))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:51:19.194462Z",
     "iopub.status.busy": "2025-09-06T18:51:19.194111Z",
     "iopub.status.idle": "2025-09-06T18:51:19.601082Z",
     "shell.execute_reply": "2025-09-06T18:51:19.599831Z",
     "shell.execute_reply.started": "2025-09-06T18:51:19.194438Z"
    },
    "trusted": True
   },
   "outputs": [
    {
     "data": {
      "image/png": "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X50DsH//fpVuHJMDBw5E+QzOF/x2+FtEbdDKlStVAEdGtFOnTmodZHKx38jsmzUzyMg4wmdwrBHUUeKPDjIYWA+/Af4uXnzxRbl06ZL6bpy7nm5OI4uhjZ8857fffrP5+/urqWLFira+ffvafv31V9uDBw+irIufA9Pu3bvt886ePWtLnjy57Y033rDPa9SokS1ZsmS2U6dO2eddvHjRljp1alvVqlXt89avX6++D/+bWrVqZQsKCnLa7t27d53eI23FihWz1ahRwz5vz5496ru6d+/utG7r1q3V/EGDBtnntW3b1pY9e3bb1atXndZt1qyZLW3atFG25wrpe/XVV21XrlxR0/79+9VnsZ0uXbqodU6fPq3ep0mTxhYaGur0+Zo1a9qKFy9uu3//vn1eZGSkrVKlSrYCBQrY52Ff8B07duywz8N3IY2Yj22YqlWrpibTd999p9YZPXp0lPRjW4C0ux4bE+Y5/vnt27dPvX///fed1uvdu7eav27dOqfjg3kbN250SndAQICtV69esR5bnEf47I0bN2xxUapUKVuWLFls165ds8/D7+Hn52d79913o+xPmzZtomwvY8aMTvNwHIsWLeo0L7pz1fF3njFjhnqPdOP9l19+GWu6XX+vsWPHqs/NmTPH6TzH32SqVKls4eHhTttDmq9fv25f98cff1TzV65cGet2zf1YtGiRbdWqVTbDMGznzp1Ty/r06WN7/vnnYzwG0f1d1K5d2/4ZEz7nuG8mHCNsu0qVKrZHjx5Fu8zxnL5z544tf/786vvwt1K3bl3194RrDvk2VvV7GHrvo8SPXDxy/Cg51K5dW5VGo6t6rlixoiq1mdApECWHX3/9VZUyMf32228ql45SmAnVne+8846q/kWpOj4cS7hodwwLC1M1CiixmX755Rf1P0oJjlBCcIT8C0rV9evXV6/RxmlO2G98t+P3xgT7iFILJlTJonSGUipKjq6lP7NKHa5fv66qMVHyRInN3Pa1a9fU9k+cOKGaIQAdr1AzgepyE74LNR9Pgn1Ek4fr/kNCOk+ZncB69uzpNN/s4IjqeUeoBsZv5JhuNA+hRBob89xAU82ToAS4b98+VSpGTYoJtRY4r107roFrSRFpxLGP7zkZ27mK9ns0CcSnjRxpRXNR8+bN7fNQckfNGmofUHvl6O2331YdTB33A550fB29+uqr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",
      "text/plain": [
       "<Figure size 600x400 with 2 Axes>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    }
   ],
   "source": [
    "plt.figure(figsize=(6,4))\n",
    "sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap=\"Blues\",\n",
    "            xticklabels=[\"Not Expired\", \"Will Expire\"],\n",
    "            yticklabels=[\"Not Expired\", \"Will Expire\"])\n",
    "plt.xlabel(\"Predicted\")\n",
    "plt.ylabel(\"Actual\")\n",
    "plt.title(\"Spoilage Prediction Confusion Matrix\")\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2025-09-06T18:59:31.228350Z",
     "iopub.status.busy": "2025-09-06T18:59:31.227972Z",
     "iopub.status.idle": "2025-09-06T18:59:31.301117Z",
     "shell.execute_reply": "2025-09-06T18:59:31.300010Z",
     "shell.execute_reply.started": "2025-09-06T18:59:31.228297Z"
    },
    "trusted": True
   },
   "outputs": [],
   "source": [
    "import joblib\n",
    "\n",
    "# Save the model\n",
    "joblib.dump(model, \"spoilage_model.pkl\")\n",
    "\n",
    "# Later, load the model\n",
    "loaded_model = joblib.load(\"spoilage_model.pkl\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {
    "trusted": True
   },
   "outputs": [
    {
     "ename": "AttributeError",
     "evalue": "'RandomForestClassifier' object has no attribute 'save_model'",
     "output_type": "error",
     "traceback": [
      "\u001b[31m---------------------------------------------------------------------------\u001b[39m",
      "\u001b[31mAttributeError\u001b[39m                            Traceback (most recent call last)",
      "\u001b[36mCell\u001b[39m\u001b[36m \u001b[39m\u001b[32mIn[14]\u001b[39m\u001b[32m, line 1\u001b[39m\n\u001b[32m----> \u001b[39m\u001b[32m1\u001b[39m \u001b[43mmodel\u001b[49m\u001b[43m.\u001b[49m\u001b[43msave_model\u001b[49m(\u001b[33m'\u001b[39m\u001b[33mspoilage_model.txt\u001b[39m\u001b[33m'\u001b[39m)\n",
      "\u001b[31mAttributeError\u001b[39m: 'RandomForestClassifier' object has no attribute 'save_model'"
     ]
    }
   ],
   "source": [
    "model.save_model('spoilage_model.pkl')\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": None,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kaggle": {
   "accelerator": "none",
   "dataSources": [
    {
     "datasetId": 6746145,
     "sourceId": 10859958,
     "sourceType": "datasetVersion"
    }
   ],
   "dockerImageVersionId": 31089,
   "isGpuEnabled": False,
   "isInternetEnabled": True,
   "language": "python",
   "sourceType": "notebook"
  },
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.11.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
import pickle

# Save trained model
with open("spoilage_predictor.pkl", "wb") as file:
    pickle.dump(lgb_model, file)
