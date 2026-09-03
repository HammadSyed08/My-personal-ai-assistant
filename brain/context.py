# ============================================================
# HAMMU ASSISTANT CONTEXT
# ============================================================

class AssistantContext:
    def __init__(self):
        self.last_search_engine = None
        self.last_search_query = None
        self.last_search_results = []

        self.last_tool = None
        self.last_tool_result = None

    def save_search(self, engine, query, results):
        self.last_search_engine = engine
        self.last_search_query = query
        self.last_search_results = results or []

    def get_search_result(self, index):
        """
        index is 1-based:
        1 = first result
        2 = second result
        3 = third result
        """

        if not self.last_search_results:
            return None

        position = index - 1

        if position < 0 or position >= len(self.last_search_results):
            return None

        return self.last_search_results[position]


# One context shared by the whole assistant session
context = AssistantContext()