# ============================================================
# HAMMU ASSISTANT CONTEXT
# ============================================================

class AssistantContext:
    def __init__(self):
        # ----------------------------------------------------
        # Browser / Search context
        # ----------------------------------------------------

        self.last_search_engine = None
        self.last_search_query = None
        self.last_search_results = []

        self.last_tool = None
        self.last_tool_result = None

        # ----------------------------------------------------
        # Conversation context
        # ----------------------------------------------------

        self.conversation_history = []

        # Keep only the latest few messages.
        # This prevents the prompt from becoming too large.
        self.max_history = 10

    # ========================================================
    # SEARCH CONTEXT
    # ========================================================

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

    # ========================================================
    # CONVERSATION CONTEXT
    # ========================================================

    def add_user_message(self, message):
        """
        Add a user message to the current conversation.
        """

        if not message:
            return

        self.conversation_history.append({
            "role": "user",
            "content": str(message)
        })

        self._trim_history()

    def add_assistant_message(self, message):
        """
        Add HAMMU's response to the current conversation.
        """

        if not message:
            return

        self.conversation_history.append({
            "role": "assistant",
            "content": str(message)
        })

        self._trim_history()

    def get_conversation_history(self):
        """
        Return the current conversation history.
        """

        return list(self.conversation_history)

    def clear_conversation(self):
        """
        Clear the current conversation session.
        """

        self.conversation_history.clear()

    def _trim_history(self):
        """
        Keep only the most recent messages.
        """

        if len(self.conversation_history) > self.max_history:
            self.conversation_history = (
                self.conversation_history[-self.max_history:]
            )


# ============================================================
# ONE CONTEXT SHARED BY THE WHOLE ASSISTANT SESSION
# ============================================================

context = AssistantContext()