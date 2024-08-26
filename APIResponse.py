from flask import jsonify


class APIResponse:

    def __init__(self):
        self.successful_responses = 0
        self.failure_responses = 0

    def generate_response_s(self, message, content=None):

        self.successful_responses += 1

        if content:
            return jsonify({"message": message, "content": content})

        return jsonify({"message": message})

    def generate_response_f(self, error_message):

        self.failure_responses += 1

        return jsonify({"error_message": error_message})
