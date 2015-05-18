from mongo_single import Mongo


class SlaveCtrl():
    def __init__(self):
        pass

    def switch_ctrl(self):
        pass

    def code_ctrl(self):
        result = []
        for project in Mongo.get().projects.find({}, {'_id': 1, 'code': 1, 'name': 1}):
            result.append(project)
        return result


if __name__ == '__main__':
    ctrl = SlaveCtrl()
    print ctrl.code_ctrl()