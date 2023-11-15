class IdGenerator:
    unique_id = 0

    @staticmethod
    def get_unique_id():
        IdGenerator.unique_id += 1
        return IdGenerator.unique_id