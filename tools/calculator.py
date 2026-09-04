def calculate(operation, numbers):
    """
    Perform basic mathematical calculations.
    """

    if not numbers:
        return {
            "success": False,
            "error": "No numbers provided."
        }

    try:
        numbers = [float(number) for number in numbers]

        if operation == "add":
            result = sum(numbers)

        elif operation == "subtract":
            result = numbers[0]

            for number in numbers[1:]:
                result -= number

        elif operation == "multiply":
            result = 1

            for number in numbers:
                result *= number

        elif operation == "divide":
            result = numbers[0]

            for number in numbers[1:]:
                if number == 0:
                    return {
                        "success": False,
                        "error": "Cannot divide by zero."
                    }

                result /= number

        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }

        # Return integer instead of 9.0
        if result.is_integer():
            result = int(result)

        return {
            "success": True,
            "operation": operation,
            "numbers": numbers,
            "result": result
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }