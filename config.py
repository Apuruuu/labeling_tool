class Config(object):
    MOUSE_OVER_POINT = 10 # コントロールポイントの範囲
    MOUSE_OVER_Limited = 10 # 区域选择时的容许
    ADD_POINT_Limited = 50 # 新增点的容许

    GUI_REFRESH_RATE = 10 # GUIのフレームレート

    KEY_MAP = {
        'ESC': 27,
        'Enter': 13,
        'Up': 82,
        'Down': 84,
        'Left': 81,
        'Right': 83,
        'Space': 32,
        'Backspace': 8,
        'Delete': 255,
        'Home': 80,
        'End': 87,
        'PageUp': 85,
        'PageDown': 86,
    }

    EXTENSION_FILTER = ['.jpg', '.bmp']
    LOG_FILE_PATH = 'logs'