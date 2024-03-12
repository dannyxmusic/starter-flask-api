from flask import Flask, request
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, daniel!'


@app.route('/submit-form', methods=['POST'])
def submit_form():
    # Check if the request contains form data
    if request.method == 'POST':
        # Parse form data from the request
        form_data = request.form.to_dict()

        email = form_data.get('Please Enter your Email Address:')
        ease_of_transition = form_data.get(
            "How would you rate the ease of transitioning and implementation to TPC's services from your previous payroll provider?")
        iSolved_software = form_data.get(
            "How user-friendly do you find iSolved, TPC's HR and payroll software?")
        previous_payroll_provider = form_data.get(
            "Who was your previous Payroll Provider?")
        satisfaction_over_previous = form_data.get(
            "How would you rate your satisfaction for TPC over your previous payroll provider?")
        tpc_customer_service = form_data.get(
            "ow would you rate your experience with TPC's customer service in addressing your inquiries and concerns?")
        number_of_employees = form_data.get(
            "How many employees does your company currently process payroll for?")
        would_you_recommend = form_data.get(
            "How inclined are you to recommend Grant Stuart and TPC's services to another business?")
        additional_feedback = form_data.get(
            "Please share your experience or any additional feedback you have regarding your experience with Grant Stuart and TPC.")

        # Return a response to indicate successful processing
        return 'Form data received successfully!', 200
    else:
        # Return an error response for unsupported request methods
        return 'Method not allowed', 405


if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
