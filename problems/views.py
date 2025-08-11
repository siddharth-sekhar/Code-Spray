# problems/views.py

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Problem, Topic, TestCase, Submission
from .utils import compile_and_run

#  View to show problem list
@login_required
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

        if not code or not language:
            error = 'Please provide both code and language.'
        else:
            testcases = TestCase.objects.filter(problem=problem)
            
            if run_sample:
                # Run only first 2 test cases for sample testing
                testcases = testcases[:2]
                all_passed = True
                
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
                        break
                
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
                return JsonResponse({
                    'output': output,
                    'error': error,
                    'status': status,
                    'test_results': test_results,
                })
            except Exception as e:
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
