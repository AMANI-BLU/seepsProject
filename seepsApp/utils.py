import io
import re
from PyPDF2 import PdfReader

def extract_questions_with_choices_from_pdf(pdf_file):
    questions_with_choices = []
    try:
        # Read the content of the uploaded file into memory
        pdf_content = io.BytesIO(pdf_file.read())
        pdf_reader = PdfReader(pdf_content)
        
        # Initialize variables to store question and choices
        question = None
        choices = []

        for page_num in range(len(pdf_reader.pages)):
            page_text = pdf_reader.pages[page_num].extract_text().strip()
            
            # Split the page text into lines
            lines = page_text.split('\n')
            for line in lines:
                # Check if the line starts with a digit followed by a dot, comma, or a closing parenthesis
                question_match = re.match(r'^(\d+)[\.\),]|^(\d+)\) (.+)$', line)
                if question_match:
                    # If there is an existing question, save it along with its choices
                    if question is not None:
                        questions_with_choices.append({'question': question, 'choices': choices})
                        # Reset the variables for the next question
                        question = None
                        choices = []
                    
                    # Set the current line as the new question
                    question = line.lstrip('1234567890.(), ')
                elif question is not None:
                    # Check if the line starts with a letter followed by a closing parenthesis, dot, or comma
                    choice_match = re.match(r'^\s*([A-Z]|[a-z])[\.\),] (.+)$', line)
                    if choice_match:
                        # Add the choice to the list of choices
                        choices.append(choice_match.group(2).strip())

        # Add the last question with its choices to the list
        if question is not None:
            questions_with_choices.append({'question': question, 'choices': choices})

    except Exception as e:
        print(f"Error extracting questions with choices from PDF: {e}")

    return questions_with_choices
