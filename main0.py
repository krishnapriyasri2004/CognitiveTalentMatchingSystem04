import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
import smtplib
from email.mime.text import MIMEText

# Step 1: Read the dataset
df = pd.read_csv('candidate0.csv')

# Step 2: Convert skills and education to numerical values
label_encoder = LabelEncoder()

# Convert 'Skills' to numerical values
df['Skills'] = df['Skills'].apply(lambda x: ', '.join(sorted(str(x).split(', '))) if pd.notna(x) else x)
df['Skills'] = label_encoder.fit_transform(df['Skills'])

# Convert 'Education' to numerical values
df['Education'] = label_encoder.fit_transform(df['Education'])

# Step 3: Skill Competency Assessment (Sample code, replace with your logic)
def assess_skill_competency(skills):
    # Replace this with your logic to assess skill competency
    return skills

df['Skill_Competency'] = df['Skills'].apply(assess_skill_competency)

# Step 4: Personality Assessment (Sample code, replace with your logic)
def assess_personality(openness, conscientiousness, extroversion, agreeableness, neuroticism):
    # Replace this with your logic to assess personality
    return openness + conscientiousness + extroversion + agreeableness - neuroticism

df['Personality_Score'] = df.apply(lambda row: assess_personality(row['Openness'], row['Conscientiousness'],
                                                                row['Extroversion'], row['Agreeableness'],
                                                                row['Neuroticism']), axis=1)

# Save the updated dataframe to a new CSV file
df.to_csv('updated_candidate0.csv', index=False)

# Feature Engineering
# Feature 1: Years of Experience and Education
df['Years_Experience_Education'] = df['Education']

# Feature 2: Skill and Education Interaction
df['Skill_Education_Interaction'] = df['Skills'] * df['Education']

# Feature 3: Normalized Personality Score
scaler = StandardScaler()
df['Normalized_Personality_Score'] = scaler.fit_transform(df[['Personality_Score']])

# Add the 'Hired' column (for training) and initialize it to zero
df['Hired'] = 0

# Save the dataset with new features and the 'Hired' column
df.to_csv('updated_candidate0.csv', index=False)

# Assuming 'Hired' is the target variable
outcomes = df['Hired']

# Model Selection
skill_model = LinearRegression()
personality_model = RandomForestClassifier()

# Model Training
features = df[['Skill_Competency', 'Normalized_Personality_Score', 'Years_Experience_Education', 'Skill_Education_Interaction']]
X_train, X_test, y_train, y_test = train_test_split(features, outcomes, test_size=0.2, random_state=42)

# Train the models
skill_model.fit(X_train, y_train)
personality_model.fit(X_train, y_train)

# Model Evaluation
skill_predictions = skill_model.predict(X_test)
personality_predictions = personality_model.predict(X_test)

# Set thresholds for skill competency, personality score, and skill-education interaction
skill_threshold = 0.7  # Adjust as needed
personality_threshold = 0.6  # Adjust as needed
interaction_threshold = 100  # Adjust as needed

# Update the 'Hired' column based on competency thresholds
df['Hired'] = (
    (df['Skill_Competency'] >= skill_threshold) &
    (df['Normalized_Personality_Score'] >= personality_threshold) &
    (df['Skill_Education_Interaction'] >= interaction_threshold)
).astype(int)

# Filter the selected candidates
selected_candidates = df[df['Hired'] == 1]

# Print the names of hired candidates or say no one is hired
hired_candidates = selected_candidates['Name'].tolist()

if hired_candidates:
    print("Hired Candidates:")
    for candidate in hired_candidates:
        print(candidate)
else:
    print("No one is hired.")

# Save the updated dataset with predictions
df.to_csv('final_candidate_dataset0.csv', index=False)

# Send emails to selected candidates
if hired_candidates:
    # Email configuration (replace placeholders)
    sender_email = "71762133044@cit.edu.in"
    sender_password = "mani@2133044"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Connect to the SMTP server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)

    # Email content
    subject = "Congratulations! You've been hired."
    body = "Dear {},\n\nCongratulations! We are pleased to inform you that you have been selected for the position.\n\nBest regards,\nDSK Company"

    # Send emails to selected candidates
    for candidate_email in selected_candidates['Email']:
        msg = MIMEText(body.format(candidate_email))
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = candidate_email

        server.sendmail(sender_email, candidate_email, msg.as_string())

    # Quit the SMTP server
    server.quit()

    print("Emails sent successfully.")
else:
    print("No one is hired.")
