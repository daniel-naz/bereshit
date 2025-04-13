class Moon:
    RADIUS = 3475*1000
    ACC = 1.622  # m/s² (Gravity on Moon's surface)
    EQ_SPEED  = 1700

    @staticmethod
    def get_acc(speed):
        n = abs(speed) / Moon.EQ_SPEED
        acc = (1 - n) * Moon.ACC
        return max(acc, 0)  # Ensures acceleration is never 