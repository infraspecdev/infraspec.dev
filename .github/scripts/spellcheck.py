import openai
import os
import sys
import logging
import json

class Logger:
    @staticmethod
    def configure(log_level=None):
        log_level = log_level or os.getenv("LOG_LEVEL", "ERROR").upper()
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        logging.basicConfig(level=levels.get(log_level, logging.ERROR),
                            format='%(asctime)s - %(levelname)s - %(message)s')

class FileHandler:
    @staticmethod
    def read_file(file_path):
        try:
            with open(file_path, 'r') as file:
                return file.readlines()
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            return None
        except Exception as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None

    @staticmethod
    def save_result(file_name, result):
        try:
            with open("spell_check_result_with_lines.json", "a") as result_file:
                result_file.write(f"Results for {file_name}:\n{result}\n\n")
        except Exception as e:
            logging.error(f"Error saving result for {file_name}: {e}")

    @staticmethod
    def load_result(file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                return content
        except Exception as e:
            logging.error(f"Error loading result file: {e}")
            return None

class SpellChecker:
    def __init__(self):
        self.api_key = self.get_api_key()
        openai.api_key = self.api_key

    @staticmethod
    def get_api_key():
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logging.error("OPENAI_API_KEY environment variable not set.")
            sys.exit(1)
        return api_key

    def check_spelling_with_line_numbers(self, numbered_content):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant checking spelling and grammar."},
                    {"role": "user", "content": (
                        "You are a helpful assistant that checks and corrects only spelling and grammar issues in markdown files, "
                        "without altering any other content such as indentation, line numbers, or formatting.\n"
                        "For each line provided, return a JSON object with the following fields only if the category is not 'none':\n"
                        "- original_text: contains the original line content\n"
                        "- suggested_text: contains the corrected line with correct grammar and spelling\n"
                        "- line_number: the exact line number of the original md file\n"
                        "- category: either 'spelling issue', 'grammar issue', or 'both'\n\n"
                        "Only include entries where the category is 'spelling issue', 'grammar issue', or 'both'.\n"
                        "If a line has no issues, do not return it.\n"
                        "If a line has no issues, return a message in json saying everything looks good to me 🎉.\n\n"
                        "Here are the lines:\n"
                        f"{''.join(numbered_content)}"
                    )}
                ],
                max_tokens=16000
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            logging.error(f"Error during OpenAI API request: {e}")
            return None

class SpellCheckProcessor:
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.spell_checker = SpellChecker()

    def inject_line_numbers(self, lines):
        return [f"{idx + 1}: {line.strip()}" for idx, line in enumerate(lines)]

    def process_files(self):
        for file_path in self.file_paths:
            file_lines = FileHandler.read_file(file_path)
            if file_lines:
                logging.info(f"Processing file: {file_path}")
                numbered_content = self.inject_line_numbers(file_lines)
                result = self.spell_checker.check_spelling_with_line_numbers(numbered_content)
                if result:
                    FileHandler.save_result(file_path, result)
                else:
                    logging.error(f"Failed to get spell check result for {file_path}")
            else:
                logging.error(f"Skipping file {file_path} due to read error.")

class PRChecker:
    @staticmethod
    def should_fail_pr(result_file_path):
        try:
            with open(result_file_path, 'r') as result_file:
                content = result_file.read()
                
                result_blocks = content.split("Results for")
                fail_pr = False
                
                for block in result_blocks[1:]:
                    if "```json" in block:
                        json_block = block.split("```json")[1].strip().rstrip("```").strip()
                        if not json_block:
                            continue

                        try:
                            result_json = json.loads(json_block)
                        except json.JSONDecodeError as e:
                            logging.error(f"JSON decode error: {e} in block: {json_block}")
                            continue

                        if isinstance(result_json, dict) and "message" in result_json:
                            continue

                        if isinstance(result_json, list):
                            for entry in result_json:
                                category = entry.get("category", "")
                                if category in ["spelling issue", "both"]:
                                    logging.info(f"Found {category} in line {entry.get('line_number')}.")
                                    fail_pr = True
                                    break
                return fail_pr
        except Exception as e:
            logging.error(f"Error checking PR result file: {e}")
            return True 

def main():
    Logger.configure()
    
    if len(sys.argv) < 2:
        logging.error("Please provide at least one file to process.")
        sys.exit(1)

    processor = SpellCheckProcessor(sys.argv[1:])
    processor.process_files()

    result_file_path = "spell_check_result_with_lines.json"
    if PRChecker.should_fail_pr(result_file_path):
        logging.error("Spelling issues found. Failing the PR.")
        sys.exit(1)
    else:
        logging.info("No spelling issues found, PR can pass.")
        sys.exit(0)

if __name__ == "__main__":
    main()
