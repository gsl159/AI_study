class ConvergenceController:
    """
    Level 5.3 工业级停止控制器
    """
    def __init__(self, max_iters=6, threshold=0.92, min_delta=0.03):
        self.max_iters = max_iters
        self.threshold = threshold
        self.min_delta = min_delta
        self.history = []
        self.iters = 0

    def should_continue(self, current_confidence: float) -> bool:
        self.iters += 1
        if self.iters >= self.max_iters:
            return False
        if current_confidence >= self.threshold:
            return False
        
        # 计算 Delta
        if len(self.history) > 0:
            delta = abs(current_confidence - self.history[-1])
            if delta < self.min_delta:
                return False
        
        self.history.append(current_confidence)
        return True
