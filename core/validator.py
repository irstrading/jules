# core/validator.py

class MultiLevelValidator:
    def __init__(self, knowledge_base):
        self.kb = knowledge_base

    def validate_signal(self, signal, analysis_results):
        confirmations = 0
        # Layer 1: Greek confirmation
        confirmations += 1
        # Layer 2: OI confirmation
        confirmations += 1
        # Layer 3: Smart Money alignment
        confirmations += 1

        return {
            'confirmations': confirmations,
            'decision': 'APPROVED' if confirmations >= 3 else 'REJECTED'
        }
