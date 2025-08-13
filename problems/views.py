# problems/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from users.views import session_valid_required
from .models import Problem, Topic, TestCase, Submission
from .utils import compile_and_run
from .ai_review import AICodeReviewer

#  View to show problem list
@login_required
@session_valid_required
@never_cache
def problem_list(request):
    topic_filter = request.GET.get('topic')
    topics = Topic.objects.all()

    if topic_filter:
        problems = Problem.objects.filter(topic__name=topic_filter)
    else:
        problems = Problem.objects.all()

    return render(request, 'problems/problem_list.html', {
        'problems': problems,
        'topics': topics,
        'selected_topic': topic_filter
    })

#  View to show problem details & handle submissions
@login_required
@never_cache
def problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    output = ''
    error = ''
    status = ''
    test_results = []

    if request.method == 'POST':
        code = request.POST.get('code')
        language = request.POST.get('language')
        run_sample = request.POST.get('run_sample')
        
        # Check if this is an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Debug: Print request details
        print(f"DEBUG: POST request received. Code length: {len(code) if code else 0}, Language: {language}, Run sample: {run_sample}")
        print(f"DEBUG: Is AJAX: {is_ajax}")
        print(f"DEBUG: Headers: {dict(request.headers)}")

        if not code or not language:
            error = 'Please provide both code and language.'
            # Return JSON response for AJAX requests even when validation fails
            if is_ajax:
                return JsonResponse({
                    'output': '',
                    'error': error,
                    'status': 'Error',
                    'test_results': [],
                })
        else:
            testcases = TestCase.objects.filter(problem=problem)
            
            # Check if there are test cases
            if not testcases.exists():
                if is_ajax:
                    return JsonResponse({
                        'output': '',
                        'error': 'No test cases found for this problem.',
                        'status': 'Error',
                        'test_results': [],
                    })
                else:
                    error = 'No test cases found for this problem.'
            else:
                if run_sample:
                    # Run only first 2 test cases for sample testing
                    testcases = testcases[:2]
                    all_passed = True
                    test_results = []  # Reset test results for sample tests
                
                    for i, testcase in enumerate(testcases):
                        out, err = compile_and_run(code, language, testcase.input_data)
                        if err:
                            error_lines = [
                                f"Compilation/Runtime Error on Test Case {i+1}",
                                f"Input: {testcase.input_data}",
                                f"Error Details:",
                                f"{err}"
                            ]
                            error = "\n".join(error_lines)
                            all_passed = False
                            break
                        elif out.strip() != testcase.output_data.strip():
                            error_lines = [
                                f"Wrong Answer on Test Case {i+1}",
                                f"Input: {testcase.input_data}",
                                f"Expected Output: {testcase.output_data}",
                                f"Your Output: {out}",
                                f"Status: FAILED"
                            ]
                            error = "\n".join(error_lines)
                            all_passed = False
                            break
                        else:
                            test_results.append({
                                'testcase_id': testcase.id,
                                'input_data': testcase.input_data,
                                'expected_output': testcase.output_data,
                                'status': 'PASSED',
                                'output': out
                            })
                    
                    if all_passed:
                        # Show the actual output from all test cases
                        if test_results:
                            output_lines = ["Sample Test Cases Results:"]
                            for i, result in enumerate(test_results, 1):
                                output_lines.append(f"\nTest Case {i}:")
                                output_lines.append(f"Input: {result['input_data']}")
                                output_lines.append(f"Expected: {result['expected_output']}")
                                output_lines.append(f"Output: {result['output']}")
                                output_lines.append("Status: PASSED")
                            output = "\n".join(output_lines)
                        else:
                            output = "All sample test cases passed!"
                        status = 'Sample Tests Passed'
                else:
                    # Run all test cases for submission
                    all_passed = True
                    test_results = []  # Initialize test results for full submission
                    
                    for testcase in testcases:
                        out, err = compile_and_run(code, language, testcase.input_data)
                        if err:
                            error_lines = [
                                f"Compilation/Runtime Error",
                                f"Input: {testcase.input_data}",
                                f"Error Details:",
                                f"{err}"
                            ]
                            error = "\n".join(error_lines)
                            all_passed = False
                            # Add failed test case to results
                            test_results.append({
                                'testcase_id': testcase.id,
                                'input_data': testcase.input_data,
                                'expected_output': testcase.output_data,
                                'status': 'ERROR',
                                'output': f"Error: {err}"
                            })
                            break
                        elif out.strip() != testcase.output_data.strip():
                            error_lines = [
                                f"Wrong Answer",
                                f"Input: {testcase.input_data}",
                                f"Expected Output: {testcase.output_data}",
                                f"Your Output: {out}"
                            ]
                            error = "\n".join(error_lines)
                            all_passed = False
                            # Add failed test case to results
                            test_results.append({
                                'testcase_id': testcase.id,
                                'input_data': testcase.input_data,
                                'expected_output': testcase.output_data,
                                'status': 'FAILED',
                                'output': out
                            })
                            break
                        else:
                            # Add passed test case to results
                            test_results.append({
                                'testcase_id': testcase.id,
                                'input_data': testcase.input_data,
                                'expected_output': testcase.output_data,
                                'status': 'PASSED',
                                'output': out
                            })
                    
                    # Save the submission
                    result = 'AC' if all_passed else 'WA'
                    Submission.objects.create(
                        user=request.user,
                        problem=problem,
                        language=language,
                        code=code,
                        status=result
                    )
                    
                    if all_passed:
                        output = "All test cases passed! Solution submitted successfully."
                        status = 'Accepted'
                    else:
                        status = 'Wrong Answer'
        
        # Return JSON response for AJAX requests
        if is_ajax:
            try:
                # Debug: Print what we're about to return
                print(f"DEBUG: AJAX request detected. Output: {output}, Error: {error}, Status: {status}")
                print(f"DEBUG: Test results count: {len(test_results)}")
                
                # Ensure all data is JSON serializable
                response_data = {
                    'output': str(output) if output else '',
                    'error': str(error) if error else '',
                    'status': str(status) if status else '',
                    'test_results': []
                }
                
                # Safely convert test_results to JSON serializable format
                if test_results:
                    for result in test_results:
                        if isinstance(result, dict):
                            response_data['test_results'].append({
                                k: str(v) if v is not None else '' 
                                for k, v in result.items()
                            })
                        else:
                            response_data['test_results'].append(str(result))
                
                print(f"DEBUG: Returning JSON response: {response_data}")
                return JsonResponse(response_data)
            except Exception as e:
                print(f"DEBUG: Exception in JSON response: {str(e)}")
                return JsonResponse({
                    'output': '',
                    'error': f'Server error: {str(e)}',
                    'status': 'Error',
                    'test_results': [],
                })
    
    return render(request, 'problems/problem_detail.html', {
        'problem': problem,
        'output': output,
        'error': error,
        'status': status,
        'test_results': test_results,
    })


@csrf_exempt
@login_required
@session_valid_required
def ai_code_review(request):
    """AI code review endpoint"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    try:
        # Get data from request
        data = request.POST
        code = data.get('code', '')
        language = data.get('language', '')
        problem_id = data.get('problem_id', '')
        
        if not all([code, language, problem_id]):
            return JsonResponse({'error': 'Missing required parameters'}, status=400)
        
        # Get problem details
        problem = get_object_or_404(Problem, id=problem_id)
        
        # Get test case results from the request
        test_case_results = []
        failed_test_cases = []
        
        # Parse test case results from the request
        for key, value in data.items():
            if key.startswith('test_result_'):
                parts = value.split('|')
                if len(parts) >= 4:
                    test_case_results.append({
                        'testcase_id': parts[0],
                        'status': parts[1],
                        'input_data': parts[2],
                        'expected_output': parts[3],
                        'actual_output': parts[4] if len(parts) > 4 else ''
                    })
                    
                    # Add to failed test cases if status is not PASSED
                    if parts[1] != 'PASSED':
                        failed_test_cases.append({
                            'testcase_id': parts[0],
                            'input_data': parts[2],
                            'output_data': parts[3],
                            'actual_output': parts[4] if len(parts) > 4 else ''
                        })
        
        # Initialize AI reviewer and get review
        ai_reviewer = AICodeReviewer()
        review_result = ai_reviewer.review_code(
            code=code,
            language=language,
            problem_description=problem.description,
            test_case_results=test_case_results,
            failed_test_cases=failed_test_cases
        )
        
        return JsonResponse(review_result)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'review': 'An error occurred while generating the AI review. Please try again.'
        }, status=500)
