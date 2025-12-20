import json
import os

SAVE_FILE = "save_games.json"


def _read_data():
    """Đọc file save và trả về một dictionary. Trả về dict rỗng nếu file không tồn tại."""
    if not os.path.exists(SAVE_FILE):
        return {}
    try:
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}  # Trả về rỗng nếu file bị lỗi


def _write_data(data):
    """Ghi dictionary vào file save."""
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f, indent=4)


def get_save_list():
    """Lấy danh sách tên của các màn đã lưu."""
    data = _read_data()
    return list(data.keys())


def save_game(save_name, game_state):
    """Lưu trạng thái game với một tên cụ thể."""
    data = _read_data()
    data[save_name] = game_state
    _write_data(data)
    print(f"Game saved as: {save_name}")


#---------------------------------------
def check_save_exists(save_name):
    """Kiểm tra xem tên save đã tồn tại hay chưa."""
    data = _read_data()
    return save_name in data


def load_game(save_name):
    """Tải trạng thái game từ một tên đã lưu."""
    data = _read_data()
    return data.get(save_name)  # Dùng .get() để trả về None nếu không tìm thấy


def delete_save(save_name):
    """Xóa một file save cụ thể dựa trên tên."""
    data = _read_data()
    if save_name in data:
        data.pop(save_name)  # Xóa key khỏi dictionary
        _write_data(data)
        print(f"Đã xóa save file: {save_name}")
    else:
        print(f"Lỗi: Không tìm thấy save file để xóa: {save_name}")
#---------------------------------------