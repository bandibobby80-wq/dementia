from django.shortcuts import render
from django.contrib import messages
from .forms import UserRegistrationForm
from .models import UserRegistrationModel
from django.conf import settings
import os
# import pickle
# Create your views here.
def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            print('Data is Valid')
            form.save()
            messages.success(request, 'You have been successfully registered')
            form = UserRegistrationForm()
            return render(request, 'UserRegistrations.html', {'form': form})
        else:
            messages.success(request, 'Email or Mobile Already Existed')
            print("Invalid form")
    else:
        form = UserRegistrationForm()
    return render(request, 'UserRegistrations.html', {'form': form})

def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHomePage.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})

def UserHome(request):
    return render(request, 'users/UserHomePage.html', {})

def DatasetView(request):
    path = os.path.join(settings.MEDIA_ROOT, 'dementia_dataset.csv')  # Removed redundant 'media'
    df = pd.read_csv(path)
    df_html = df.to_html(classes='table table-striped', index=False)
    return render(request, 'users/viewdataset.html', {'data': df_html})

# import os
# import pandas as pd
# import joblib
# from django.shortcuts import render
# from django.core.files.storage import FileSystemStorage
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder, OneHotEncoder
# from sklearn.model_selection import train_test_split
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Training view
# import os
# import pandas as pd
# import joblib
# from django.shortcuts import render
# from django.core.files.storage import FileSystemStorage
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.preprocessing import LabelEncoder, OneHotEncoder
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score, confusion_matrix
# import seaborn as sns
# import matplotlib.pyplot as plt

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# def Training(request):
#     message = ''
#     accuracy = None
#     confusion_img_path = None

#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         fs = FileSystemStorage()
#         file_path = fs.save(file.name, file)
#         data = pd.read_csv(fs.path(file_path))

#         # Drop irrelevant columns
#         data = data.drop(['Subject ID', 'MRI ID', 'Hand'], axis=1)

#         # Split features and label
#         X = data.drop('class', axis=1)
#         y = data['class']

#         # One-hot encode 'M/F'
#         ohe = OneHotEncoder()
#         gender_encoded = ohe.fit_transform(X[['M/F']]).toarray()
#         gender_df = pd.DataFrame(gender_encoded, columns=ohe.get_feature_names_out(['M/F']))
#         X = X.drop('M/F', axis=1).reset_index(drop=True)
#         X = pd.concat([X, gender_df], axis=1)

#         # Label encode target
#         le = LabelEncoder()
#         y = le.fit_transform(y)

#         # Train model
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
#         model = RandomForestClassifier()
#         model.fit(X_train, y_train)

#         # Predict and calculate accuracy
#         y_pred = model.predict(X_test)
#         accuracy = accuracy_score(y_test, y_pred)

#         # Generate and save confusion matrix plot
#         cm = confusion_matrix(y_test, y_pred)
#         plt.figure(figsize=(6, 4))
#         sns.heatmap(cm, annot=True, fmt='d', cmap='Purples', xticklabels=le.classes_, yticklabels=le.classes_)
#         plt.title("Confusion Matrix")
#         plt.xlabel("Predicted")
#         plt.ylabel("Actual")
#         plot_path = os.path.join(BASE_DIR, 'static', 'images', 'confusion_matrix.png')
#         os.makedirs(os.path.dirname(plot_path), exist_ok=True)
#         plt.savefig(plot_path)
#         plt.close()

#         confusion_img_path = 'confusion_matrix.png'

#         # Save model and encoders
#         joblib.dump(model, os.path.join(BASE_DIR, 'model.pkl'))
#         joblib.dump(le, os.path.join(BASE_DIR, 'label_encoder.pkl'))
#         joblib.dump(ohe, os.path.join(BASE_DIR, 'ohe_encoder.pkl'))

#         message = "Model trained and saved successfully!"

#     return render(request, 'users/train.html', {
#         'message': message,
#         'accuracy': accuracy,
#         'confusion_img_path': confusion_img_path
#     })


# # Prediction view
# def Prediction(request):
#     prediction = None
#     if request.method == 'POST' and request.FILES.get('file'):
#         file = request.FILES['file']
#         fs = FileSystemStorage()
#         file_path = fs.save(file.name, file)
#         df = pd.read_csv(fs.path(file_path))

#         # Drop irrelevant columns
#         df = df.drop(['Subject ID', 'MRI ID', 'Hand'], axis=1)

#         # Load encoders and model
#         model = joblib.load(os.path.join(BASE_DIR, 'ml_model/model.pkl'))
#         le = joblib.load(os.path.join(BASE_DIR, 'ml_model/label_encoder.pkl'))
#         ohe = joblib.load(os.path.join(BASE_DIR, 'ml_model/ohe_encoder.pkl'))

#         # One-hot encode gender
#         gender_encoded = ohe.transform(df[['M/F']]).toarray()
#         gender_df = pd.DataFrame(gender_encoded, columns=ohe.get_feature_names_out(['M/F']))
#         df = df.drop('M/F', axis=1).reset_index(drop=True)
#         df = pd.concat([df, gender_df], axis=1)

#         # Predict
#         preds = model.predict(df)
#         prediction = le.inverse_transform(preds)

#         df['Predicted Class'] = prediction
#         prediction = df.to_html(classes="table table-bordered")

#     return render(request, 'users/predict.html', {'prediction': prediction})

import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from .forms import PredictionForm
from django.conf import settings

BASE_DIR = settings.BASE_DIR
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
import os
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from django.conf import settings

BASE_DIR = settings.BASE_DIR  # Ensure this is defined in settings.py

def Training(request):
    context = {}

    if request.method == 'POST' and request.FILES.get('file'):
        try:
            # =========================
            # 1️⃣ Load Dataset
            # =========================
            file = request.FILES['file']
            fs = FileSystemStorage()
            file_path = fs.save(file.name, file)
            df = pd.read_csv(fs.path(file_path))

            # Clean column names
            df.columns = df.columns.str.strip()

            # =========================
            # 2️⃣ Preprocessing
            # =========================

            # Encode target
            df['Group'] = df['Group'].replace({
                'Nondemented': 0,
                'Demented': 1,
                'Converted': 2
            })

            # Keep only binary classes
            df = df[df['Group'].isin([0, 1])].copy()

            # Ensure numeric integer labels
            df['Group'] = pd.to_numeric(df['Group'], errors='coerce')
            df = df.dropna(subset=['Group'])
            df['Group'] = df['Group'].astype(int)

            # Drop unnecessary columns (ignore error if not present)
            df.drop(['Subject ID', 'MRI ID', 'Hand'], axis=1, inplace=True, errors='ignore')

            # Fill missing values safely
            df.fillna({
                'MMSE': df['MMSE'].mode()[0] if 'MMSE' in df.columns else None,
                'SES': df['SES'].mode()[0] if 'SES' in df.columns else None
            }, inplace=True)

            # =========================
            # 3️⃣ Feature & Target Split
            # =========================
            y = df['Group']
            X = df.drop('Group', axis=1)

            # One-hot encode categorical features only
            X = pd.get_dummies(X, drop_first=True)

            # =========================
            # 4️⃣ Train-Test Split
            # =========================
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )

            # =========================
            # 5️⃣ Train Model
            # =========================
            model = LogisticRegression(
                solver='lbfgs',
                max_iter=1000,
                random_state=42
            )

            model.fit(X_train, y_train)

            # =========================
            # 6️⃣ Save Model
            # =========================
            model_dir = os.path.join(BASE_DIR, 'ml_model')
            os.makedirs(model_dir, exist_ok=True)

            joblib.dump(model, os.path.join(model_dir, 'logistic_model.pkl'))
            joblib.dump(X.columns.tolist(), os.path.join(model_dir, 'feature_columns.pkl'))

            # =========================
            # 7️⃣ Evaluation
            # =========================
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            cm = confusion_matrix(y_test, y_pred)

            # =========================
            # 8️⃣ Save Graphs
            # =========================
            img_dir = os.path.join(BASE_DIR, 'media', 'images')
            os.makedirs(img_dir, exist_ok=True)

            # Confusion Matrix
            plt.figure(figsize=(6, 5))
            sns.heatmap(
                cm,
                annot=True,
                fmt='d',
                cmap='Blues',
                xticklabels=['Non-Demented', 'Demented'],
                yticklabels=['Non-Demented', 'Demented']
            )
            plt.title("Confusion Matrix")
            plt.xlabel("Predicted")
            plt.ylabel("Actual")
            plt.tight_layout()
            plt.savefig(os.path.join(img_dir, 'confusion_matrix.png'))
            plt.close()

            # Correlation Heatmap
            plt.figure(figsize=(14, 12))
            corr = df.corr(numeric_only=True)
            sns.heatmap(corr, cmap='coolwarm', square=True)
            plt.title("Feature Correlation Heatmap")
            plt.tight_layout()
            plt.savefig(os.path.join(img_dir, 'heatmap.png'))
            plt.close()

            # =========================
            # 9️⃣ Send Results to Template
            # =========================
            context.update({
                'message': "Model trained successfully!",
                'accuracy': round(accuracy * 100, 2),
                'confusion_img': 'images/confusion_matrix.png',
                'heatmap_img': 'images/heatmap.png'
            })

        except Exception as e:
            context['message'] = f"Error during training: {str(e)}"

    return render(request, 'users/train.html', context)



import os
import joblib
import pandas as pd
from django.shortcuts import render
from .forms import PredictionForm
from django.conf import settings

BASE_DIR = settings.BASE_DIR

def Prediction(request):
    prediction = None
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            # Load logistic regression model and feature columns
            model = joblib.load(os.path.join(BASE_DIR, 'ml_model', 'logistic_model.pkl'))
            feature_columns = joblib.load(os.path.join(BASE_DIR, 'ml_model', 'feature_columns.pkl'))

            # One-hot encode gender
            gender = form.cleaned_data['M_F']
            gender_encoded = [1, 0] if gender == 'F' else [0, 1]  # Assuming order: F, M

            # Prepare input data
            input_data = [
                form.cleaned_data['Visit'],
                form.cleaned_data['MR_Delay'],
                form.cleaned_data['Age'],
                form.cleaned_data['EDUC'],
                form.cleaned_data['SES'],
                form.cleaned_data['MMSE'],
                form.cleaned_data['CDR'],
                form.cleaned_data['eTIV'],
                form.cleaned_data['nWBV'],
                form.cleaned_data['ASF']
            ] + gender_encoded

            # Align with training features
            input_df = pd.DataFrame([input_data], columns=feature_columns)

            # Predict
            result = model.predict(input_df)[0]

            # Map to label
            prediction_map = {0: "Nondemented", 1: "Demented", }
            prediction = prediction_map.get(result, "Unknown")
    else:
        form = PredictionForm()

    return render(request, 'users/predict.html', {'form': form, 'prediction': prediction})
