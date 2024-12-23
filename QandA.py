from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transformers import pipeline
import time

# Initialize QA pipeline
qa_model = pipeline("question-answering", model="deepset/roberta-base-squad2")

def setup_driver():
    """Setup and configure Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--limited-sandbox')# Overcome limited resource problems
    chrome_options.add_argument('--disable-dev-shm-usage')# Overcome limited resource problems
    chrome_options.add_argument('--disable-gpu')# Applicable to windows os only
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def get_form_questions(driver, form_url):
    """Extract questions from Google Form"""
    driver.get(form_url)
    questions = []
    # Wait for questions to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "freebirdFormviewerComponentsQuestionBaseTitle"))
    )
    # Get all question elements
    question_elements = driver.find_elements(By.CLASS_NAME, "freebirdFormviewerComponentsQuestionBaseTitle")
    return [q.text for q in question_elements]

def answer_questions(questions, context):
    """Generate answers using transformer model"""
    answers = []
    for question in questions:
        result = qa_model(question=question, context=context)
        answers.append(result['answer'])
    return answers

def submit_answers(driver, answers):
    """Fill and submit the form"""
    # Find all text input fields
    input_fields = driver.find_elements(By.CLASS_NAME, "quantumWizTextinputPaperinputInput")
    
    # Fill each answer
    for field, answer in zip(input_fields, answers):
        field.send_keys(answer)
    
    # Submit form
    submit_button = driver.find_element(By.CLASS_NAME, "appsMaterialWizButtonPaperbuttonLabel")
    submit_button.click()

def main():
    # Replace with your Google Form URL
    form_url = "YOUR_GOOGLE_FORM_URL"
    
    # Context for the QA model (replace with relevant text)
    context = """Your context text here. This should be the reference material 
              that contains information to answer the form questions."""
    
    try:
        driver = setup_driver()
        questions = get_form_questions(driver, form_url)
        answers = answer_questions(questions, context)
        submit_answers(driver, answers)
        print("Form submitted successfully!")
        time.sleep(10)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()