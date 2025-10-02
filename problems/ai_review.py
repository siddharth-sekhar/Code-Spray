import os
import google.generativeai as genai
from django.conf import settings

class AICodeReviewer:
    def __init__(self):
        # Initialize Google Gemini client
        api_key = "AIzaSyDoWsr6Qu54a0FkpR6Z5AQEMpI_Af9MyfE"
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def review_code(self, code, language, problem_description, test_case_results, failed_test_cases):
        """
        Review code and provide suggestions for improvement
        
        Args:
            code (str): The user's code
            language (str): Programming language (cpp, python, java, c)
            problem_description (str): Problem description
            test_case_results (list): List of test case results
            failed_test_cases (list): List of failed test cases
        
        Returns:
            dict: AI review response with suggestions
        """
        try:
            # Create a comprehensive prompt for code review
            prompt = self._create_review_prompt(
                code, language, problem_description, 
                test_case_results, failed_test_cases
            )
            
            # Generate AI response
            response = self.model.generate_content(prompt)
            
            return {
                'success': True,
                'review': response.text,
                'suggestions': self._extract_suggestions(response.text)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'review': 'Unable to generate AI review at the moment. Please try again later.'
            }
    
    def _create_review_prompt(self, code, language, problem_description, test_case_results, failed_test_cases):
        """Create a comprehensive prompt for code review"""
        
        language_names = {
            'cpp': 'C++',
            'c': 'C',
            'python': 'Python',
            'java': 'Java'
        }
        
        lang_name = language_names.get(language, language)
        
        prompt = f"""
You are an expert programming tutor helping a student fix their code. Please analyze the following code and provide helpful suggestions.

PROBLEM DESCRIPTION:
{problem_description}

PROGRAMMING LANGUAGE: {lang_name}

STUDENT'S CODE:
```{language}
{code}
```

TEST CASE RESULTS:
{self._format_test_results(test_case_results)}

FAILED TEST CASES:
{self._format_failed_tests(failed_test_cases)}

Please provide:
1. A brief analysis of what might be causing the test case failures
2. Specific suggestions to fix the code
3. A corrected version of the code (if possible)
4. General tips for improving the solution

Keep your response helpful, encouraging, and educational. Focus on the specific issues causing the test failures.
"""
        return prompt
    
    def _format_test_results(self, test_case_results):
        """Format test case results for the prompt"""
        if not test_case_results:
            return "No test case results available."
        
        formatted = []
        for i, result in enumerate(test_case_results, 1):
            formatted.append(f"Test Case {i}: {result.get('status', 'Unknown')}")
            if result.get('output'):
                formatted.append(f"  Output: {result['output']}")
        
        return "\n".join(formatted)
    
    def _format_failed_tests(self, failed_test_cases):
        """Format failed test cases for the prompt"""
        if not failed_test_cases:
            return "No failed test cases."
        
        formatted = []
        for test_case in failed_test_cases:
            formatted.append(f"- Input: {test_case.get('input_data', 'N/A')}")
            formatted.append(f"  Expected: {test_case.get('output_data', 'N/A')}")
            formatted.append(f"  Got: {test_case.get('actual_output', 'N/A')}")
        
        return "\n".join(formatted)
    
    def _extract_suggestions(self, review_text):
        """Extract key suggestions from the AI review"""
        # Simple extraction - you can enhance this later
        lines = review_text.split('\n')
        suggestions = []
        
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '4.', '-', '•')) and len(line) > 10:
                suggestions.append(line)
        
        return suggestions[:5]  # Return top 5 suggestions
