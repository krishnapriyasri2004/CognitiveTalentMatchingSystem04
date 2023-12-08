from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from collections import defaultdict
import os
import re
import fitz

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure secret key

# Define the file path for the Excel or CSV file for user signup
data_file = 'data.xlsx'  # Change this to the desired file path

# Load existing CSV file for junior candidates
csv_file_junior = 'candidate0.csv'
try:
    df_junior = pd.read_csv(csv_file_junior)
except FileNotFoundError:
    df_junior = pd.DataFrame(columns=['Candidate_ID', 'Name', 'Age', 'Mobile', 'Gender', 'Email','Skills', 'Education'])

# Load existing CSV file for experienced candidates
csv_file_experience = 'candidate.csv'
try:
    df_experience = pd.read_csv(csv_file_experience)
except FileNotFoundError:
    df_experience = pd.DataFrame(columns=['Candidate_ID', 'Name', 'Age', 'Mobile', 'Gender', 'Email', 'Experience','Skills', 'Education'])


# Create a route for the root URL
@app.route('/')
def home():
    return render_template('index.html')


# Create a route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['Name']
        degree = request.form['Degree']
        email = request.form['Email']
        phone_number = request.form['Phone Number']  # Change to 'Phone Number'
        experience = request.form['Experience']
        password = request.form['Password']

        # Add user details to the data structure
        user_details = {
            'Name': name,
            'Degree': degree,
            'Email': email,
            'Phone Number': phone_number,  # Change to 'Phone Number'
            'Experience': experience,
            'Password': password
        }

        # Read the existing data from the file if it exists
        if os.path.exists(data_file):
            if data_file.endswith('.xlsx'):
                df = pd.read_excel(data_file)
            elif data_file.endswith('.csv'):
                df = pd.read_csv(data_file)
            else:
                df = pd.DataFrame()

            # Create a new DataFrame with the user details
            new_user_df = pd.DataFrame([user_details])

            # Concatenate the new user DataFrame with the existing DataFrame
            df = pd.concat([df, new_user_df], ignore_index=True)

            # Save the updated data to the file
            if data_file.endswith('.xlsx'):
                df.to_excel(data_file, index=False)
            elif data_file.endswith('.csv'):
                df.to_csv(data_file, index=False)
            else:
                print('Invalid file format')

            return redirect(url_for('login'))
        else:
            print(f"File '{data_file}' does not exist.")
    else:
        return render_template('signup.html')


# Create a route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['Email']
        password = request.form['Password']

        # Read the user data from the file if it exists
        if os.path.exists(data_file):
            if data_file.endswith('.xlsx'):
                df = pd.read_excel(data_file)
            elif data_file.endswith('.csv'):
                df = pd.read_csv(data_file)
            else:
                df = pd.DataFrame()

            # Check if the user exists
            user_exists = not df[(df['Email'] == email) & (df['Password'] == password)].empty

            if user_exists:
                return render_template('profile.html', name=email)
            else:
                return redirect(url_for('signup'))
        else:
            print(f"File '{data_file}' does not exist.")
    else:
        return render_template('login.html')

def process_resume(resume_file, dataset):
    # Define the path to store the uploaded resumes
    upload_folder = 'uploads'
    os.makedirs(upload_folder, exist_ok=True)

    # Save the uploaded resume to the uploads folder
    resume_path = os.path.join(upload_folder, resume_file.filename)
    resume_file.save(resume_path)

    try:
        # Open the PDF file
        pdf_document = fitz.open(resume_path)

        resume_text = ""
        for page in pdf_document:
            resume_text += page.get_text("text")

        # Extract skills from the resume using regular expressions
        found_skills = []
        for skill in skills_to_find:
            matches = re.findall(rf'\b{re.escape(skill)}\b', resume_text, re.IGNORECASE)
            if matches:
                found_skills.extend(matches)

        # Remove duplicates
        found_skills = list(set(found_skills))

        # Extract education information from the resume using regular expressions
        found_education = []
        for keyword in education_keywords:
            matches = re.findall(rf'\b{re.escape(keyword)}\b', resume_text, re.IGNORECASE)
            if matches:
                found_education.extend(matches)

        # Remove duplicates
        found_education = list(set(found_education))

        # Update the dataset with the skills and education information
        dataset.loc[dataset.index[-1], 'Skills'] = ", ".join(found_skills)
        dataset.loc[dataset.index[-1], 'Education'] = ", ".join(found_education)

        # Redirect to a specific page after processing the resume
        return redirect(url_for('profile', selected_candidate_type=session.get('user_type')))

    except FileNotFoundError:
        print("File not found. Please provide the correct path to the PDF file.")
    finally:
        # Close the PDF document
        if 'pdf_document' in locals():
            pdf_document.close()

# List of specific skills to search for
skills_to_find = ["Java", "Python", "SQL", "C++", "JavaScript", "HTML/CSS", "C#", "PHP", "Data Structures",
                  "R", "Data Analysis", "React", "Node.js", "Machine Learning", "Angular", "UX Design",
                  "Data Science", "Database Administration"]

# List of specific education-related keywords to search for
education_keywords = ["Bachelor's", "Master's", "PhD", "Degree", "University", "College", "Graduation", "Diploma", "M.Sc"]


# Create a route for candidate type selection
@app.route('/select_candidate_type', methods=['GET', 'POST'])
def select_candidate_type():
    if request.method == 'POST':
        candidate_type = request.form.get('candidate_type')
        session['user_type'] = candidate_type
        if candidate_type == 'junior':
            return redirect('/junior')
        elif candidate_type == 'experience':
            return redirect('/experience')

    return render_template('select.html')


# Route for junior candidates
@app.route('/junior')
def index_junior():
    if 'user_type' in session and session['user_type'] == 'junior':
        return render_template('index0.html')
    else:
        return redirect(url_for('select_candidate_type'))


# Route for experienced candidates
@app.route('/experience')
def index_experience():
    if 'user_type' in session and session['user_type'] == 'experience':
        return render_template('index1.html')
    else:
        return redirect(url_for('select_candidate_type'))


# Handle form submissions for junior candidates
@app.route('/submit/junior', methods=['POST'])
def submit_junior():
    global df_junior

    name = request.form.get('name')
    age = int(request.form.get('age'))
    mobile = int(request.form.get('mobile'))
    gender = request.form.get('gender')
    email = request.form.get('email')

    candidate_id = df_junior['Candidate_ID'].max() + 1 if not df_junior.empty else 1
    candidate_id = int(candidate_id)  # Ensure the candidate_id is an integer

    # Questions related to Big Five personality traits
    questions = {
        'Openness': [int(request.form.get('openness_q1')), int(request.form.get('openness_q2'))],
        'Conscientiousness': [int(request.form.get('conscientiousness_q1')),
                              int(request.form.get('conscientiousness_q2'))],
        'Extroversion': [int(request.form.get('extroversion_q1')), int(request.form.get('extroversion_q2'))],
        'Agreeableness': [int(request.form.get('agreeableness_q1')), int(request.form.get('agreeableness_q2'))],
        'Neuroticism': [int(request.form.get('neuroticism_q1')), int(request.form.get('neuroticism_q2'))],
    }

    scores = calculate_scores(questions)

    new_data = {'Candidate_ID': [candidate_id], 'Name': [name], 'Age': [age], 'Mobile': [mobile], 'Gender': [gender],
                'Email': [email], **scores}
    new_df = pd.DataFrame(new_data)

    # Concatenate the new DataFrame with the existing DataFrame
    df_junior = pd.concat([df_junior, new_df], ignore_index=True)
    # Call the function to process the resume and update the dataset
    process_resume(request.files['resume'], df_junior)

    # Save the DataFrame to the CSV file
    df_junior.to_csv(csv_file_junior, index=False)

    return render_template('thank.html', submission_message='Submission for Junior successful!')


# Handle form submissions for experienced candidates
@app.route('/submit/experience', methods=['POST'])
def submit_experience():
    global df_experience

    name = request.form.get('name')
    age = int(request.form.get('age'))
    mobile = int(request.form.get('mobile'))
    gender = request.form.get('gender')
    email = request.form.get('email')
    experience = int(request.form.get('experience'))

    candidate_id = df_experience['Candidate_ID'].max() + 1 if not df_experience.empty else 1
    candidate_id = int(candidate_id)  # Ensure the candidate_id is an integer

    # Questions related to Big Five personality traits
    questions = {
        'Openness': [int(request.form.get('openness_q1')), int(request.form.get('openness_q2'))],
        'Conscientiousness': [int(request.form.get('conscientiousness_q1')),
                              int(request.form.get('conscientiousness_q2'))],
        'Extroversion': [int(request.form.get('extroversion_q1')), int(request.form.get('extroversion_q2'))],
        'Agreeableness': [int(request.form.get('agreeableness_q1')), int(request.form.get('agreeableness_q2'))],
        'Neuroticism': [int(request.form.get('neuroticism_q1')), int(request.form.get('neuroticism_q2'))],
    }

    scores = calculate_scores(questions)

    # Create a new DataFrame with the new data
    new_data = {'Candidate_ID': [candidate_id], 'Name': [name], 'Age': [age], 'Mobile': [mobile], 'Gender': [gender],
                'Email': [email], 'Experience': [experience], **scores}
    new_df = pd.DataFrame(new_data)

    # Concatenate the new DataFrame with the existing DataFrame
    df_experience = pd.concat([df_experience, new_df], ignore_index=True)
    # Call the function to process the resume and update the dataset
    process_resume(request.files['resume'], df_experience)

    # Save the DataFrame to the CSV file
    df_experience.to_csv(csv_file_experience, index=False)

    return render_template('thank.html', submission_message='Submission for Experience successful!')


# Route for the user profile
@app.route('/profile')
def profile():
    selected_candidate_type = request.args.get('selected_candidate_type')
    return render_template('profile.html', name=session.get('email'), selected_candidate_type=selected_candidate_type)


def calculate_scores(answers):
    scores = defaultdict(int)

    for trait, values in answers.items():
        scores[trait] = sum(values)

    return scores

def extract_skills_and_education_from_resume(pdf_file_path, skills_to_find, education_keywords):
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_file_path)

        resume_text = ""
        for page in pdf_document:
            resume_text += page.get_text("text")

        # Extract skills from the resume using regular expressions
        found_skills = []
        for skill in skills_to_find:
            matches = re.findall(rf'\b{re.escape(skill)}\b', resume_text, re.IGNORECASE)
            if matches:
                found_skills.extend(matches)

        # Remove duplicates
        found_skills = list(set(found_skills))

        # Extract education information from the resume using regular expressions
        found_education = []
        for keyword in education_keywords:
            matches = re.findall(rf'\b{re.escape(keyword)}\b', resume_text, re.IGNORECASE)
            if matches:
                found_education.extend(matches)

        # Remove duplicates
        found_education = list(set(found_education))

        # Display the found skills in the desired format
        print("Found Skills:", ", ".join(found_skills))

        print("\nFound Education:")
        for education_info in found_education:
            print(education_info)

    except FileNotFoundError:
        print("File not found. Please provide the correct path to the PDF file.")
    finally:
        # Close the PDF document
        if 'pdf_document' in locals():
            pdf_document.close()

# Route to handle resume file submission
@app.route('/submit/resume', methods=['POST'])
def submit_resume():
    if 'resume' not in request.files:
        return redirect(request.url)

    resume_file = request.files['resume']

    if resume_file.filename == '':
        return redirect(request.url)

    # Process the resume
    process_resume(resume_file, df_experience)  # Assuming you want to update the experience DataFrame

    # Redirect to a specific page after processing the resume
    return redirect(url_for('profile', selected_candidate_type='experience'))


if __name__ == '__main__':
    app.run(debug=True)
